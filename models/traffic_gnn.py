"""
Model B: Traffic-Aware Congestion GNN.

Implements a small Graph Convolutional Network manually (adjacency
propagation via matrix multiply) so we don't need a heavy PyTorch Geometric
install for a weekend build. This is a legitimate GCN: node embeddings are
propagated over the real graph structure (2 hops), then an edge-level MLP
predicts the congestion multiplier for a given hour/day-type, conditioned on
the propagated embeddings of the edge's two endpoints.
"""

import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.road_network import build_graph, CHRONIC_BOTTLENECKS

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def normalized_adjacency(G, node_order):
    n = len(node_order)
    idx = {name: i for i, name in enumerate(node_order)}
    A = np.zeros((n, n), dtype=np.float32)
    for u, v in G.edges():
        A[idx[u], idx[v]] = 1.0
        A[idx[v], idx[u]] = 1.0
    A_hat = A + np.eye(n, dtype=np.float32)  # add self loops
    D = A_hat.sum(axis=1)
    D_inv_sqrt = np.diag(1.0 / np.sqrt(D))
    return D_inv_sqrt @ A_hat @ D_inv_sqrt, idx


class GCNLayer(nn.Module):
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.lin = nn.Linear(in_dim, out_dim)

    def forward(self, A_norm, X):
        # A_norm: (n, n), X: (n, in_dim)
        return torch.relu(self.lin(A_norm @ X))


class TrafficGNN(nn.Module):
    def __init__(self, n_nodes, node_feat_dim=4, embed_dim=16):
        super().__init__()
        self.node_embed = nn.Embedding(n_nodes, embed_dim)
        self.gcn1 = GCNLayer(embed_dim + node_feat_dim, 24)
        self.gcn2 = GCNLayer(24, 16)
        self.edge_mlp = nn.Sequential(
            nn.Linear(16 * 2 + 2, 32),  # 2 endpoint embeds + [hour_sin, hour_cos] + day_type folded in via +1
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
        )
        # extra day_type feature appended separately
        self.edge_mlp = nn.Sequential(
            nn.Linear(16 * 2 + 3, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Softplus(),  # multiplier >= 0, we add 1.0 floor at use-time
        )

    def propagate(self, A_norm, static_feats):
        n = A_norm.shape[0]
        ids = torch.arange(n, device=A_norm.device)
        X = torch.cat([self.node_embed(ids), static_feats], dim=1)
        h = self.gcn1(A_norm, X)
        h = self.gcn2(A_norm, h)
        return h  # (n, 16) node embeddings after 2-hop propagation

    def predict_edge(self, h, u_idx, v_idx, hour, day_type):
        hour_sin = torch.sin(2 * np.pi * hour / 24.0).unsqueeze(-1)
        hour_cos = torch.cos(2 * np.pi * hour / 24.0).unsqueeze(-1)
        day = day_type.unsqueeze(-1).float()
        feat = torch.cat([h[u_idx], h[v_idx], hour_sin, hour_cos, day], dim=-1)
        return 1.0 + self.edge_mlp(feat).squeeze(-1)


def prepare_static_node_features(G, node_order):
    feats = []
    for name in node_order:
        is_bottleneck = 1.0 if name in CHRONIC_BOTTLENECKS else 0.0
        lat, lon = G.nodes[name]["lat"], G.nodes[name]["lon"]
        degree = G.degree[name] / 6.0  # normalize roughly
        feats.append([is_bottleneck, lat - 12.97, lon - 77.60, degree])
    return torch.tensor(feats, dtype=torch.float32)


def train_traffic_gnn(csv_path, save_path, epochs=200, lr=5e-3):
    G = build_graph()
    node_order = list(G.nodes())
    A_norm_np, idx = normalized_adjacency(G, node_order)
    A_norm = torch.tensor(A_norm_np, device=DEVICE)
    static_feats = prepare_static_node_features(G, node_order).to(DEVICE)

    df = pd.read_csv(csv_path)
    u_idx = torch.tensor([idx[u] for u in df.u], device=DEVICE)
    v_idx = torch.tensor([idx[v] for v in df.v], device=DEVICE)
    hour = torch.tensor(df.hour.values, device=DEVICE, dtype=torch.float32)
    day_type = torch.tensor(df.day_type.values, device=DEVICE, dtype=torch.float32)
    target = torch.tensor(df.congestion_multiplier.values, device=DEVICE, dtype=torch.float32)

    model = TrafficGNN(n_nodes=len(node_order)).to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()

    n = len(df)
    perm = torch.randperm(n)
    split = int(n * 0.85)
    train_idx, val_idx = perm[:split], perm[split:]

    for epoch in range(1, epochs + 1):
        model.train()
        opt.zero_grad()
        h = model.propagate(A_norm, static_feats)
        pred = model.predict_edge(h, u_idx[train_idx], v_idx[train_idx], hour[train_idx], day_type[train_idx])
        loss = loss_fn(pred, target[train_idx])
        loss.backward()
        opt.step()

        if epoch % 20 == 0 or epoch == epochs:
            model.eval()
            with torch.no_grad():
                h = model.propagate(A_norm, static_feats)
                val_pred = model.predict_edge(h, u_idx[val_idx], v_idx[val_idx], hour[val_idx], day_type[val_idx])
                val_loss = loss_fn(val_pred, target[val_idx]).item()
            print(f"Epoch {epoch:3d}/{epochs}  train_mse={loss.item():.5f}  val_mse={val_loss:.5f}  "
                  f"val_rmse_multiplier={np.sqrt(val_loss):.3f}")

    torch.save({"state_dict": model.state_dict(), "node_order": node_order}, save_path)
    print(f"Saved traffic GNN to {save_path}")
    return model, node_order, A_norm, static_feats


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base, "data", "traffic_ground_truth.csv")
    save_path = os.path.join(base, "models", "traffic_gnn.pt")
    train_traffic_gnn(csv_path, save_path)
