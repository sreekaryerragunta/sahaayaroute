// Drop your Google Maps Platform API key below to enable REAL live-traffic ETA
// and turn-by-turn navigation. Leave it blank to keep using the simulated
// traffic model (GNN) for ETA estimates instead.
//
// How to get a key:
//   1. Go to console.cloud.google.com, create a project (or use an existing one)
//   2. APIs & Services > Library > enable "Maps JavaScript API"
//   3. APIs & Services > Credentials > Create Credentials > API key
//   4. (Recommended) Restrict the key to your domain / HTTP referrers
//   5. Paste it below
//
// With a key set, hospital ETAs shown in this app come from Google's live
// traffic-aware Directions service (drivingOptions.trafficModel = 'bestguess',
// departureTime = now) instead of the simulated GNN model.

const CONFIG = {
  GOOGLE_MAPS_API_KEY: "AIzaSyD93kF4s-YqVQugQoprifnDIyYHlzwcb-4",
};
