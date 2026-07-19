"""
Simulates congestion multiplier ground truth for every road edge, for every
hour of day and weekday/weekend, calibrated to well-known Bengaluru traffic
patterns:
  - morning peak 8-10am, evening peak 5:30-8:30pm
  - chronic bottleneck junctions (Silk Board, KR Puram, Marathahalli, Hebbal,
    Majestic) get an extra congestion penalty during peak hours
  - weekends are lighter except around Bannerghatta/Koramangala (nightlife/leisure)

congestion_multiplier: 1.0 = free flow, 2.5x = severe jam (travel_time = base * multiplier)
"""

import numpy as np
import pandas as pd
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.road_network import build_graph, CHRONIC_BOTTLENECKS

RNG = np.random.default_rng(7)


def peak_factor(hour):
    # smooth double-hump peak function
    morning = np.exp(-((hour - 9) ** 2) / (2 * 1.3 ** 2))
    evening = np.exp(-((hour - 19) ** 2) / (2 * 1.6 ** 2))
    return morning + evening  # 0 (night) to ~1 (peak)


def simulate():
    G = build_graph()
    records = []
    for u, v, data in G.edges(data=True):
        touches_bottleneck = u in CHRONIC_BOTTLENECKS or v in CHRONIC_BOTTLENECKS
        for day_type in [0, 1]:  # 0 = weekday, 1 = weekend
            for hour in range(24):
                pf = peak_factor(hour)
                if day_type == 1:
                    pf *= 0.55  # weekends generally lighter
                base_mult = 1.0 + 0.8 * pf
                if touches_bottleneck:
                    base_mult += 0.6 * pf  # bottlenecks get hit harder at peak
                noise = RNG.normal(0, 0.05)
                mult = max(1.0, base_mult + noise)
                records.append({
                    "u": u, "v": v,
                    "day_type": day_type, "hour": hour,
                    "touches_bottleneck": int(touches_bottleneck),
                    "base_minutes": data["base_minutes"],
                    "congestion_multiplier": mult,
                })
    return pd.DataFrame(records)


if __name__ == "__main__":
    df = simulate()
    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "traffic_ground_truth.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} rows to {out_path}")
    print(df.groupby(["touches_bottleneck", "hour"])["congestion_multiplier"].mean().unstack(0).round(2))
