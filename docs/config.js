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
  GEMINI_API_KEY: "", // <-- paste your Gemini API key here (see note below before pasting)
  GEMINI_MODEL: "gemini-3.5-flash", // update here if Google retires this model, check ai.google.dev/gemini-api/docs/changelog
};

// NOTE ON THE GEMINI KEY: GitHub's push protection blocks committing a
// "GCP API Key Bound to a Service Account" to any repo, public or private,
// because that key type generally carries broader backend permissions than
// a normal client-safe API key. If your key was created in Google Cloud
// Console tied to a service account, get a standard one instead from
// Google AI Studio (aistudio.google.com/apikey) -- those are meant for
// exactly this client-side use case. Paste it above locally; don't commit
// it to a public repo without first restricting it (HTTP referrer +
// API restriction) in Google Cloud Console, same as the Maps key.
