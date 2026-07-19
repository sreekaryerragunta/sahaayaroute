"""
Model A: Hospital Capacity Forecaster.

Given the last LOOKBACK hours of occupancy + time features for a hospital,
predict occupancy for the next HORIZON hours, with a simple uncertainty
estimate via MC-dropout at inference time.
"""

import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

LOOKBACK = 48
HORIZON = 6

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


class OccupancyDataset(Dataset):
    def __init__(self, df, hospital_ids):
        self.samples = []
        for hid in hospital_ids:
            sub = df[df.hospital_id == hid].sort_values("hour_idx")
            occ = sub["occupancy"].values
            hod = sub["hour_of_day"].values / 24.0
            dow = sub["day_of_week"].values / 7.0
            feats = np.stack([occ, hod, dow], axis=1)  # (T, 3)
            for i in range(len(feats) - LOOKBACK - HORIZON):
                x = feats[i : i + LOOKBACK]
                y = occ[i + LOOKBACK : i + LOOKBACK + HORIZON]
                self.samples.append((x.astype(np.float32), y.astype(np.float32)))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        x, y = self.samples[idx]
        return torch.tensor(x), torch.tensor(y)


class CapacityLSTM(nn.Module):
    def __init__(self, input_size=3, hidden_size=64, num_layers=2, horizon=HORIZON, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers=num_layers,
                             batch_first=True, dropout=dropout)
        self.dropout = nn.Dropout(dropout)
        self.head = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Linear(32, horizon),
            nn.Sigmoid(),  # occupancy is a 0-1 fraction
        )

    def forward(self, x):
        out, (h_n, c_n) = self.lstm(x)
        last = self.dropout(out[:, -1, :])
        return self.head(last)


def train_model(csv_path, save_path, epochs=15, batch_size=64, lr=1e-3):
    df = pd.read_csv(csv_path)
    hospital_ids = df.hospital_id.unique().tolist()

    # simple time-based split: first 80% of hours per hospital = train, rest = val
    max_hour = df.hour_idx.max()
    split_hour = int(max_hour * 0.8)
    train_df = df[df.hour_idx <= split_hour]
    val_df = df[df.hour_idx > split_hour - LOOKBACK - HORIZON]  # overlap ok for lookback context

    train_ds = OccupancyDataset(train_df, hospital_ids)
    val_ds = OccupancyDataset(val_df, hospital_ids)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    model = CapacityLSTM().to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()

    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        for x, y in train_loader:
            x, y = x.to(DEVICE), y.to(DEVICE)
            opt.zero_grad()
            pred = model(x)
            loss = loss_fn(pred, y)
            loss.backward()
            opt.step()
            train_loss += loss.item() * x.size(0)
        train_loss /= len(train_ds)

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(DEVICE), y.to(DEVICE)
                pred = model(x)
                val_loss += loss_fn(pred, y).item() * x.size(0)
        val_loss /= max(len(val_ds), 1)

        print(f"Epoch {epoch:2d}/{epochs}  train_mse={train_loss:.5f}  val_mse={val_loss:.5f}  "
              f"val_rmse_occupancy_pts={np.sqrt(val_loss)*100:.2f}%")

    torch.save(model.state_dict(), save_path)
    print(f"Saved model to {save_path}")
    return model


def predict_with_uncertainty(model, x, n_samples=20):
    """MC-dropout: keep dropout active at inference, sample multiple forward passes."""
    model.train()  # keep dropout on
    preds = []
    with torch.no_grad():
        for _ in range(n_samples):
            preds.append(model(x).cpu().numpy())
    preds = np.stack(preds, axis=0)  # (n_samples, batch, horizon)
    mean = preds.mean(axis=0)
    std = preds.std(axis=0)
    return mean, std


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base, "data", "occupancy_timeseries.csv")
    save_path = os.path.join(base, "models", "capacity_lstm.pt")
    train_model(csv_path, save_path, epochs=15)
