"""
Simulates hourly hospital occupancy (% beds full) for every hospital over N days.

Since no public live bed-occupancy feed exists for Bengaluru hospitals, this
generates statistically realistic synthetic ground truth using:
  - a baseline occupancy level per hospital (bigger/government hospitals run hotter)
  - diurnal seasonality (ERs fill up evenings, admissions clear early morning)
  - weekly seasonality (weekends busier due to accidents/trauma)
  - random surge events (accidents, mass events) that spike occupancy and decay
  - gaussian noise

This is the "digital twin" standing in for a real-time hospital data feed.
"""

import numpy as np
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.hospitals import HOSPITALS

RNG = np.random.default_rng(42)

N_DAYS = 45
HOURS = N_DAYS * 24


def simulate_hospital_series(hospital):
    # baseline occupancy: bigger public hospitals + trauma centers run hotter
    base = 0.55
    if hospital["type"].startswith("government"):
        base += 0.15
    if hospital["trauma"]:
        base += 0.08
    base = min(base, 0.85)

    t = np.arange(HOURS)
    hour_of_day = t % 24
    day_of_week = (t // 24) % 7  # 5,6 = weekend

    # diurnal pattern: peaks in evening (18-22h), trough early morning (3-6h)
    diurnal = 0.08 * np.sin((hour_of_day - 6) / 24 * 2 * np.pi)

    # weekend bump (more trauma/accident admissions)
    weekend_bump = np.where(day_of_week >= 5, 0.05, 0.0)

    # slow trend (occupancy creeping up over the period, e.g. seasonal illness wave)
    trend = 0.05 * (t / HOURS)

    occupancy = base + diurnal + weekend_bump + trend

    # random surge events (accidents / mass casualty / disease outbreak clusters)
    n_surges = RNG.poisson(1.2 * N_DAYS / 10)
    for _ in range(n_surges):
        start = RNG.integers(0, HOURS)
        magnitude = RNG.uniform(0.10, 0.30)
        duration = RNG.integers(3, 14)
        decay = np.exp(-np.arange(HOURS - start) / max(duration, 1))
        occupancy[start:] += magnitude * decay[: HOURS - start]

    # noise
    occupancy += RNG.normal(0, 0.02, size=HOURS)
    occupancy = np.clip(occupancy, 0.05, 0.99)

    return occupancy


def build_dataset():
    records = []
    for h in HOSPITALS:
        series = simulate_hospital_series(h)
        for hour_idx, occ in enumerate(series):
            records.append({
                "hospital_id": h["id"],
                "hospital_name": h["name"],
                "hour_idx": hour_idx,
                "hour_of_day": hour_idx % 24,
                "day_of_week": (hour_idx // 24) % 7,
                "occupancy": occ,
            })
    return pd.DataFrame(records)


if __name__ == "__main__":
    df = build_dataset()
    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "occupancy_timeseries.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} rows to {out_path}")
    print(df.groupby("hospital_name")["occupancy"].mean().sort_values(ascending=False))
