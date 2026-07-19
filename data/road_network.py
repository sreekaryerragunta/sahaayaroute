"""
Simplified Bengaluru road network.

NOTE ON DATA HONESTY: A full OSM road graph (via OSMnx/Overpass) would be ideal,
but Overpass/OSM endpoints aren't reachable from this sandbox's network allowlist.
Instead, this module encodes a simplified graph of ~25 major, real, well-known
Bengaluru junctions/areas (with real approximate coordinates) and the arterial
roads connecting them. This is a reasonable weekend-scope stand-in for a full
road graph -- in a production build (e.g. inside Antigravity with full internet
access), swap this module for an OSMnx pull of the real graph; everything
downstream (routing, congestion model) works the same way.
"""

import networkx as nx

# Major junctions / areas, real approximate coordinates
NODES = {
    "SilkBoard":     (12.9172, 77.6228),
    "KRPuram":       (13.0075, 77.6960),
    "Marathahalli":  (12.9569, 77.7011),
    "Hebbal":        (13.0358, 77.5970),
    "Yeshwantpur":   (13.0284, 77.5533),
    "Majestic":      (12.9767, 77.5713),
    "MGRoad":        (12.9758, 77.6045),
    "Koramangala":   (12.9352, 77.6245),
    "BTM":           (12.9166, 77.6101),
    "JPNagar":       (12.9077, 77.5851),
    "Jayanagar":     (12.9250, 77.5828),
    "Banashankari":  (12.9250, 77.5460),
    "Rajajinagar":   (12.9911, 77.5528),
    "Malleshwaram":  (13.0069, 77.5730),
    "Indiranagar":   (12.9719, 77.6412),
    "Whitefield":    (12.9698, 77.7500),
    "ElectronicCity": (12.8452, 77.6602),
    "Bannerghatta":  (12.8895, 77.5978),
    "Yelahanka":     (13.1007, 77.5963),
    "HSRLayout":     (12.9121, 77.6446),
    "OuterRingRoadE": (12.9600, 77.6900),
    "Domlur":        (12.9611, 77.6387),
    "Airport":       (13.1986, 77.7066),
    "Basavanagudi":  (12.9422, 77.5735),
    "RTNagar":       (13.0230, 77.5940),
}

# Arterial road connections (real, well-known corridors), base_km, base_minutes_free_flow
EDGES = [
    ("SilkBoard", "BTM", 3.5, 8),
    ("SilkBoard", "HSRLayout", 4.0, 9),
    ("SilkBoard", "Bannerghatta", 3.0, 7),
    ("BTM", "Koramangala", 3.0, 7),
    ("BTM", "JPNagar", 2.5, 6),
    ("Koramangala", "HSRLayout", 3.5, 8),
    ("Koramangala", "Indiranagar", 4.5, 10),
    ("Koramangala", "Domlur", 4.0, 9),
    ("Indiranagar", "Domlur", 2.0, 5),
    ("Domlur", "OuterRingRoadE", 3.0, 7),
    ("OuterRingRoadE", "Marathahalli", 3.5, 8),
    ("Marathahalli", "Whitefield", 6.0, 13),
    ("Marathahalli", "KRPuram", 5.5, 12),
    ("KRPuram", "Whitefield", 6.5, 14),
    ("KRPuram", "Hebbal", 9.0, 18),
    ("Indiranagar", "MGRoad", 3.0, 7),
    ("MGRoad", "Majestic", 4.5, 10),
    ("Majestic", "Rajajinagar", 3.5, 8),
    ("Majestic", "Malleshwaram", 3.0, 7),
    ("Malleshwaram", "Yeshwantpur", 3.5, 8),
    ("Malleshwaram", "Hebbal", 5.5, 12),
    ("Rajajinagar", "Yeshwantpur", 3.0, 7),
    ("Yeshwantpur", "Hebbal", 4.5, 10),
    ("Hebbal", "Yelahanka", 7.0, 14),
    ("Hebbal", "RTNagar", 3.0, 7),
    ("Hebbal", "Airport", 22.0, 35),
    ("RTNagar", "Malleshwaram", 3.0, 7),
    ("Majestic", "Basavanagudi", 3.5, 8),
    ("Basavanagudi", "Jayanagar", 2.5, 6),
    ("Jayanagar", "JPNagar", 2.5, 6),
    ("Jayanagar", "Banashankari", 3.0, 7),
    ("Banashankari", "JPNagar", 2.5, 6),
    ("JPNagar", "Bannerghatta", 4.0, 9),
    ("Bannerghatta", "ElectronicCity", 9.0, 18),
    ("HSRLayout", "ElectronicCity", 7.5, 15),
    ("SilkBoard", "ElectronicCity", 8.5, 17),
    ("MGRoad", "Domlur", 4.0, 9),
]

# Chronic bottleneck junctions (known from real Bengaluru traffic patterns)
# These get an extra congestion penalty during peak hours
CHRONIC_BOTTLENECKS = {"SilkBoard", "KRPuram", "Marathahalli", "Hebbal", "Majestic"}


def build_graph():
    G = nx.Graph()
    for name, (lat, lon) in NODES.items():
        G.add_node(name, lat=lat, lon=lon)
    for u, v, km, mins in EDGES:
        G.add_edge(u, v, distance_km=km, base_minutes=mins)
    return G


def nearest_node(lat, lon):
    """Find nearest network node to a given lat/lon (used to snap hospitals/incidents to graph)."""
    best, best_d = None, float("inf")
    for name, (nlat, nlon) in NODES.items():
        d = (nlat - lat) ** 2 + (nlon - lon) ** 2
        if d < best_d:
            best, best_d = name, d
    return best
