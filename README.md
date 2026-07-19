# SahaayaRoute
### AI-Powered Emergency Hospital Capacity Prediction & Ambulance Routing for Bengaluru

A working prototype of a system Bengaluru doesn't have today: real-time-style
hospital capacity forecasting combined with traffic-aware ambulance routing.

**Open `dashboard/sahaayaroute_dashboard.html` directly in a browser to try it.**
No server needed, everything is precomputed and embedded client-side.

---

## What's real vs simulated

| Data | Status |
|---|---|
| 16 Bengaluru hospitals: names, types, locations | Real |
| Hospital specialties, total bed counts | Real, sourced from each hospital's official site/public listings (see `data/hospitals.py` for per-hospital notes) |
| ICU bed counts | Real where marked `icu_verified: True`; explicitly marked "not public" otherwise, never guessed |
| Emergency contact numbers | Real where marked `emergency_phone_verified: True` (Manipal, Fortis, Apollo, Narayana Health, Sakra); explicitly shown as "No verified number" otherwise rather than fabricated |
| 108 (Karnataka ambulance) / 112 (India unified emergency) | Real, verified via government/EMRI sources, always shown in the app |
| Live traffic-based ETA + turn-by-turn navigation | **Real**, if you add a Google Maps Platform API key to `dashboard/config.js` (see below). Falls back to the simulated GNN model if no key is set. |
| Bengaluru road network (25 major junctions + arterial roads, incl. known chronic bottlenecks) | Real, simplified (see note below) — only used for the simulated-ETA fallback |
| Hospital occupancy / bed availability right now | **Simulated / estimated**, always labeled `EST` in the app. No public live feed of this exists anywhere in Bengaluru today. |

**Why hospital occupancy is still simulated, and why "train longer" won't fix that**: there is no public real-time bed/ICU feed for Bengaluru hospitals to train on or serve from, full stop. Even Delhi's official government system for this (HMIS + the "ICU Beds Saarthi" app) was under High Court audit in mid-2026 after a patient was denied an ICU bed despite the portal showing availability, and that's with actual hospital IT integration. Training the occupancy model longer, or on a full year of data, only improves its fit to the synthetic patterns this project generated; it can't create real-world accuracy because the ground truth it would need doesn't exist publicly. The **"Log a confirmed capacity check"** feature in the dashboard is the honest path to real accuracy: every time you call a hospital and log what they actually tell you, that becomes a real, timestamped data point. Enough of those, collected over time, is what you'd actually retrain on to make this real.

**Why simulate the road network too**: Overpass/OSM endpoints weren't reachable from the sandbox this was built in, so the graph is a hand-built simplification of ~25 major real junctions. This only matters if you don't add a Google Maps key, once you do, ETA and navigation both use real Google-calculated routes and this fallback isn't used.

---

## Enabling real live traffic + navigation

1. Go to console.cloud.google.com, create/select a project.
2. APIs & Services > Library > enable **Maps JavaScript API**.
3. APIs & Services > Credentials > Create Credentials > API key.
4. (Recommended) Restrict the key to your domain.
5. Open `dashboard/config.js` and paste your key into `GOOGLE_MAPS_API_KEY`.
6. Reopen `sahaayaroute_dashboard.html` (keep it in the same folder as `config.js`).

Once set, the sidebar's "ETA mode" banner switches from SIMULATED to LIVE,
and every hospital recommendation's ETA comes from Google's real traffic-aware
Directions service instead of the GNN. The "Navigate" button always uses a
real Google Maps deep link regardless of whether a key is set, since that
doesn't require one.

---

## Architecture

```
data/hospitals.py              -- real hospital directory
data/road_network.py           -- simplified real road network graph
scripts/simulate_occupancy.py  -- generates realistic hospital occupancy time series
scripts/simulate_traffic.py    -- generates realistic congestion ground truth
models/capacity_forecaster.py  -- Model A: LSTM, forecasts hospital occupancy
models/traffic_gnn.py          -- Model B: GNN, predicts congestion-adjusted travel time
models/recommend.py            -- combines A + B into ranked hospital recommendations
scripts/precompute_dashboard_data.py -- bakes all model outputs into dashboard_data.json
dashboard/template.html         -- dashboard UI (Leaflet map + recommendation panel)
dashboard/sahaayaroute_dashboard.html -- final dashboard with data embedded (OPEN THIS)
```

## Models

**Model A — Capacity Forecaster (LSTM)**
- 2-layer LSTM (64 hidden units), trained on 45 days of simulated hourly occupancy per hospital
- Input: last 48 hours of occupancy + time-of-day + day-of-week
- Output: next 6 hours of predicted occupancy, with MC-dropout uncertainty estimates
- Validation RMSE: ~3.5 percentage points of occupancy

**Model B — Traffic GNN**
- 2-layer Graph Convolutional Network (implemented manually via normalized adjacency matrix propagation, no PyTorch Geometric dependency), trained on simulated congestion data across all road edges
- Learns node embeddings propagated over the real road graph structure, then predicts a congestion multiplier per edge conditioned on hour-of-day/day-type
- Predicted multipliers feed into Dijkstra shortest-path routing for realistic (not just distance-based) ETA
- Validation RMSE: ~0.05 on congestion multiplier (a 1.0-2.5x scale)

**Recommendation Engine**
- Combines predicted bed availability + predicted ETA + emergency-type match (trauma vs general) into a weighted ranking
- Surfaces top 3-4 hospitals with reasoning (ETA, predicted occupancy, estimated free beds)

---

## How to re-run the pipeline

```bash
pip install torch pandas numpy networkx --break-system-packages

python3 scripts/simulate_occupancy.py         # generates data/occupancy_timeseries.csv
python3 scripts/simulate_traffic.py           # generates data/traffic_ground_truth.csv
python3 models/capacity_forecaster.py         # trains & saves models/capacity_lstm.pt
python3 models/traffic_gnn.py                 # trains & saves models/traffic_gnn.pt
python3 models/recommend.py                   # sanity-check end-to-end recommendation
python3 scripts/precompute_dashboard_data.py  # bakes everything into data/dashboard_data.json

python3 -c "
import json
data_str = open('data/dashboard_data.json').read()
template = open('dashboard/template.html').read()
open('dashboard/sahaayaroute_dashboard.html', 'w').write(template.replace('__DATA_JSON__', data_str))
"
```

---

## Using this in Google Antigravity

This entire pipeline is designed to be extended. Good next prompts once you're
in Antigravity with full internet access:

1. **Swap in a real road network**: replace `data/road_network.py`'s hand-built
   graph with a real OSMnx pull of Bengaluru's road network. Everything
   downstream (the GNN, routing) works unchanged, it just operates on a
   richer graph.
2. **Add a real-time layer**: build a small ingestion endpoint (FastAPI) that
   could accept live occupancy updates from a hospital and feed them into
   Model A instead of the simulator, this is the seam where "prototype"
   becomes "production."
3. **Compare architectures**: train a Transformer encoder alongside the LSTM
   for Model A and compare validation performance, a good technical
   talking point for a portfolio write-up.
4. **Multi-incident contention**: extend the recommendation engine to handle
   multiple simultaneous incidents competing for the same hospital capacity,
   the stretch goal from the original spec.
5. **Deploy the dashboard**: host `sahaayaroute_dashboard.html` as a static
   site (Vercel/Netlify/GitHub Pages) since it has zero backend dependencies.

---

## Why this is a legitimate portfolio piece

- Solves a real, verified gap (no live Bengaluru hospital bed feed exists
  post-COVID), not an already-addressed problem.
- Uses deep learning in two genuinely different modalities: time-series
  forecasting (LSTM) and graph-structured learning (GNN), not one model
  wrapped in a nice UI.
- Explicit and honest about simulated vs real data, both in this README and
  in the dashboard's own "How This Works" panel.
- Has a clear, credible path from prototype to production (ABDM integration
  for hospital data, live traffic API for Model B).
