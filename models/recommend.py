"""
Recommendation Engine: combines
  - Model A (LSTM) predicted hospital capacity
  - Model B (GNN) predicted traffic-aware ETA via shortest-path routing
  - emergency type match (trauma vs general)
into a ranked list of hospital recommendations for a given incident.
"""

import os
import sys
import numpy as np
import pandas as pd
import torch
import networkx as nx

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.hospitals import HOSPITALS
from data.road_network import build_graph, nearest_node
from models.capacity_forecaster import CapacityLSTM, LOOKBACK, HORIZON, predict_with_uncertainty
from models.traffic_gnn import TrafficGNN, normalized_adjacency, prepare_static_node_features

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def load_capacity_model():
    model = CapacityLSTM().to(DEVICE)
    model.load_state_dict(torch.load(os.path.join(BASE, "models", "capacity_lstm.pt"), map_location=DEVICE))
    return model


def load_traffic_model():
    G = build_graph()
    ckpt = torch.load(os.path.join(BASE, "models", "traffic_gnn.pt"), map_location=DEVICE)
    node_order = ckpt["node_order"]
    A_norm_np, idx = normalized_adjacency(G, node_order)
    A_norm = torch.tensor(A_norm_np, device=DEVICE)
    static_feats = prepare_static_node_features(G, node_order).to(DEVICE)
    model = TrafficGNN(n_nodes=len(node_order)).to(DEVICE)
    model.load_state_dict(ckpt["state_dict"])
    model.eval()
    return model, G, node_order, idx, A_norm, static_feats


def build_congestion_weighted_graph(traffic_model, G, node_order, idx, A_norm, static_feats, hour, day_type):
    """Runs the GNN once for a given hour/day_type and returns a graph with predicted travel times as edge weights."""
    with torch.no_grad():
        h = traffic_model.propagate(A_norm, static_feats)
        edges = list(G.edges(data=True))
        u_idx = torch.tensor([idx[u] for u, v, d in edges], device=DEVICE)
        v_idx = torch.tensor([idx[v] for u, v, d in edges], device=DEVICE)
        hour_t = torch.full((len(edges),), float(hour), device=DEVICE)
        day_t = torch.full((len(edges),), float(day_type), device=DEVICE)
        mult = traffic_model.predict_edge(h, u_idx, v_idx, hour_t, day_t).cpu().numpy()

    Gw = nx.Graph()
    for name in node_order:
        Gw.add_node(name, **G.nodes[name])
    for (u, v, d), m in zip(edges, mult):
        Gw.add_edge(u, v, travel_minutes=d["base_minutes"] * m, congestion_multiplier=float(m))
    return Gw


def predict_capacity_for_all_hospitals(capacity_model, occupancy_df, target_hour_idx):
    """Uses the most recent LOOKBACK hours before target_hour_idx to forecast the next HORIZON hours."""
    results = {}
    for h in HOSPITALS:
        sub = occupancy_df[occupancy_df.hospital_id == h["id"]].sort_values("hour_idx")
        window = sub[(sub.hour_idx < target_hour_idx) & (sub.hour_idx >= target_hour_idx - LOOKBACK)]
        if len(window) < LOOKBACK:
            continue
        occ = window["occupancy"].values
        hod = window["hour_of_day"].values / 24.0
        dow = window["day_of_week"].values / 7.0
        x = np.stack([occ, hod, dow], axis=1).astype(np.float32)
        x_t = torch.tensor(x).unsqueeze(0).to(DEVICE)
        mean, std = predict_with_uncertainty(capacity_model, x_t, n_samples=20)
        results[h["id"]] = {
            "predicted_occupancy_next_hour": float(mean[0, 0]),
            "predicted_occupancy_std": float(std[0, 0]),
            "predicted_occupancy_horizon": mean[0].tolist(),
        }
    return results


def recommend(incident_lat, incident_lon, emergency_type, hour, day_type,
              capacity_model, occupancy_df, target_hour_idx,
              traffic_model, G, node_order, idx, A_norm, static_feats, top_k=3):

    incident_node = nearest_node(incident_lat, incident_lon)
    Gw = build_congestion_weighted_graph(traffic_model, G, node_order, idx, A_norm, static_feats, hour, day_type)
    capacity_preds = predict_capacity_for_all_hospitals(capacity_model, occupancy_df, target_hour_idx)

    candidates = []
    for h in HOSPITALS:
        if emergency_type == "trauma" and not h["trauma"]:
            continue
        h_node = nearest_node(h["lat"], h["lon"])
        try:
            eta = nx.shortest_path_length(Gw, incident_node, h_node, weight="travel_minutes")
        except nx.NetworkXNoPath:
            continue
        cap = capacity_preds.get(h["id"])
        if cap is None:
            continue
        predicted_occ = cap["predicted_occupancy_next_hour"]
        predicted_available_frac = max(0.0, 1.0 - predicted_occ)
        # score: lower ETA better, higher availability better; weighted sum (normalized)
        score = (predicted_available_frac * 0.6) - (eta / 60.0 * 0.4)
        candidates.append({
            "hospital_id": h["id"],
            "hospital_name": h["name"],
            "eta_minutes": round(eta, 1),
            "predicted_occupancy_pct": round(predicted_occ * 100, 1),
            "predicted_occupancy_uncertainty_pct": round(cap["predicted_occupancy_std"] * 100, 1),
            "predicted_available_beds_est": round(predicted_available_frac * h["beds"]),
            "has_trauma_center": h["trauma"],
            "score": round(score, 4),
        })

    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates[:top_k]


if __name__ == "__main__":
    occupancy_df = pd.read_csv(os.path.join(BASE, "data", "occupancy_timeseries.csv"))
    capacity_model = load_capacity_model()
    traffic_model, G, node_order, idx, A_norm, static_feats = load_traffic_model()

    # example: incident near Silk Board, at hour 19 (evening peak), weekday, trauma case
    target_hour_idx = 1000  # arbitrary point deep enough into series for lookback
    result = recommend(
        incident_lat=12.9172, incident_lon=77.6228, emergency_type="trauma",
        hour=19, day_type=0,
        capacity_model=capacity_model, occupancy_df=occupancy_df, target_hour_idx=target_hour_idx,
        traffic_model=traffic_model, G=G, node_order=node_order, idx=idx, A_norm=A_norm, static_feats=static_feats,
    )
    for r in result:
        print(r)
