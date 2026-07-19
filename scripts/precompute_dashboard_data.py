import os, sys, json
import numpy as np
import pandas as pd
import torch
import networkx as nx

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.hospitals import HOSPITALS
from data.road_network import build_graph, NODES, CHRONIC_BOTTLENECKS
from models.capacity_forecaster import CapacityLSTM, LOOKBACK, predict_with_uncertainty
from models.traffic_gnn import TrafficGNN, normalized_adjacency, prepare_static_node_features
from models.recommend import (
    load_capacity_model, load_traffic_model, build_congestion_weighted_graph,
)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def precompute_capacity_by_hour_daytype(capacity_model, occupancy_df):
    """For each (hour_of_day, day_type) pick a representative window and forecast next-hour occupancy."""
    out = {}
    for hour_of_day in range(24):
        for day_type in [0, 1]:
            # find a target_hour_idx in the series matching this hour_of_day/day_type, deep enough for lookback
            candidates = occupancy_df[
                (occupancy_df.hour_of_day == hour_of_day) &
                ((occupancy_df.day_of_week >= 5).astype(int) == day_type) &
                (occupancy_df.hour_idx >= LOOKBACK + 24)
            ]
            if len(candidates) == 0:
                continue
            target_hour_idx = int(candidates.iloc[len(candidates) // 2].hour_idx)

            per_hospital = {}
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
                mean, std = predict_with_uncertainty(capacity_model, x_t, n_samples=15)
                per_hospital[h["id"]] = {
                    "occ": float(mean[0, 0]),
                    "std": float(std[0, 0]),
                }
            out[f"{hour_of_day}_{day_type}"] = per_hospital
    return out


def precompute_routing_by_hour_daytype(traffic_model, G, node_order, idx, A_norm, static_feats):
    """For each (hour, day_type), build the congestion-weighted graph and compute shortest travel time
    from every network node to every hospital's nearest node."""
    from data.road_network import nearest_node
    hospital_nodes = {h["id"]: nearest_node(h["lat"], h["lon"]) for h in HOSPITALS}

    out = {}
    for hour in range(24):
        for day_type in [0, 1]:
            Gw = build_congestion_weighted_graph(traffic_model, G, node_order, idx, A_norm, static_feats, hour, day_type)
            lengths = dict(nx.all_pairs_dijkstra_path_length(Gw, weight="travel_minutes"))
            key = f"{hour}_{day_type}"
            out[key] = {}
            for origin in node_order:
                out[key][origin] = {
                    hid: round(lengths[origin].get(hnode, 999.0), 1)
                    for hid, hnode in hospital_nodes.items()
                }
    return out


def precompute_distance_matrix(G, node_order):
    """Static shortest-path distance (km) from every node to every hospital, independent of time/congestion."""
    from data.road_network import nearest_node
    hospital_nodes = {h["id"]: nearest_node(h["lat"], h["lon"]) for h in HOSPITALS}
    lengths = dict(nx.all_pairs_dijkstra_path_length(G, weight="distance_km"))
    out = {}
    for origin in node_order:
        out[origin] = {hid: round(lengths[origin].get(hnode, -1), 1) for hid, hnode in hospital_nodes.items()}
    return out


def main():
    occupancy_df = pd.read_csv(os.path.join(BASE, "data", "occupancy_timeseries.csv"))
    capacity_model = load_capacity_model()
    traffic_model, G, node_order, idx, A_norm, static_feats = load_traffic_model()

    print("Precomputing capacity forecasts...")
    capacity_by_hour = precompute_capacity_by_hour_daytype(capacity_model, occupancy_df)

    print("Precomputing traffic-aware routing...")
    routing_by_hour = precompute_routing_by_hour_daytype(traffic_model, G, node_order, idx, A_norm, static_feats)

    print("Precomputing distance matrix...")
    distance_matrix = precompute_distance_matrix(G, node_order)

    dashboard_data = {
        "hospitals": HOSPITALS,
        "nodes": {name: {"lat": lat, "lon": lon} for name, (lat, lon) in NODES.items()},
        "bottlenecks": list(CHRONIC_BOTTLENECKS),
        "capacity_by_hour_daytype": capacity_by_hour,
        "routing_by_hour_daytype": routing_by_hour,
        "distance_matrix": distance_matrix,
    }

    def default(o):
        if isinstance(o, (np.floating, np.integer)):
            return float(o)
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

    out_path = os.path.join(BASE, "data", "dashboard_data.json")
    with open(out_path, "w") as f:
        json.dump(dashboard_data, f, default=default)
    print(f"Saved dashboard data to {out_path} ({os.path.getsize(out_path) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
