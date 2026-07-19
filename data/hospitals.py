"""
Bengaluru hospital directory.
Real hospital names, types, and approximate locations.

Verified fields (researched from official hospital sites / cross-checked sources):
  specialties, icu_beds, total_beds, emergency_phone -- where marked verified=True
Unverified fields are explicitly flagged so the app never presents a guess as fact.
IMPORTANT: emergency_phone should be re-confirmed before any real operational use --
numbers change, and this list was compiled from public web sources, not a hospital feed.
"""

"""
Bengaluru hospital directory.

IMPORTANT: All coordinates and place_id values below were verified against
Google Places (not estimated from memory). place_id is the authoritative
identifier Google Maps uses internally, navigation built from place_id is
immune to the lat/lon drift that caused incorrect routing in an earlier
version of this app. Two entries were corrected/renamed after verification:
"Columbia Asia Hospital Hebbal" is now branded "Manipal Hospital Hebbal"
(Columbia Asia's Indian hospitals were acquired by Manipal), and "KIMS
Hospital Hebbal" did not verify as an existing facility, replaced with the
real, verified "KIMS Hospital & Research Centre" (Basavanagudi).
"""

HOSPITALS = [
    {
        "id": "H01", "name": "Victoria Hospital", "type": "government",
        "lat": 12.9643083, "lon": 77.5754198, "place_id": "ChIJ54EQ1uIVrjsRHnL6tjMIfW4",
        "beds": 800, "icu_beds": None, "icu_verified": False,
        "trauma": True, "specialties": ["General Medicine", "General Surgery", "Trauma & Casualty", "Orthopedics", "Obstetrics & Gynaecology"],
        "emergency_phone": "080 2670 1150", "emergency_phone_verified": True,
        "note": "Major government tertiary hospital with a dedicated casualty/trauma department (Mahabodhi Burns and Casualty block).",
    },
    {
        "id": "H02", "name": "NIMHANS", "type": "government_specialty",
        "lat": 12.9387894, "lon": 77.5941391, "place_id": "ChIJy8adM7sVrjsRzsLeA3hCxTc",
        "beds": 646, "icu_beds": None, "icu_verified": False,
        "trauma": False, "specialties": ["Neurology", "Neurosurgery", "Psychiatry", "Mental Health Crisis Care"],
        "emergency_phone": "080 2699 5000", "emergency_phone_verified": True,
        "note": "India's premier neuro/psychiatric institute; not a general trauma center.",
    },
    {
        "id": "H03", "name": "Bowring & Lady Curzon Hospital", "type": "government",
        "lat": 12.9821629, "lon": 77.6042677, "place_id": "ChIJictGtGMWrjsRB6Qf8MRSiSo",
        "beds": 500, "icu_beds": None, "icu_verified": False,
        "trauma": True, "specialties": ["General Medicine", "General Surgery", "Trauma & Casualty", "Obstetrics & Gynaecology"],
        "emergency_phone": "084311 86388", "emergency_phone_verified": True,
        "note": "Government multi-specialty hospital in central Bengaluru (Shivaji Nagar).",
    },
    {
        "id": "H04", "name": "St. John's Medical College Hospital", "type": "private_teaching",
        "lat": 12.9295368, "lon": 77.6186969, "place_id": "ChIJTS8ROVEUrjsRjvSIzCm5w6E",
        "beds": 1200, "icu_beds": 90, "icu_verified": True,
        "trauma": True, "specialties": ["Cardiology", "Neurology", "Neurosurgery", "Oncology", "Gastroenterology", "Nephrology", "General Surgery", "Trauma & Mass Casualty Care"],
        "emergency_phone": "080 2206 5000", "emergency_phone_verified": True,
        "note": "1200-bed teaching hospital; ICU figure combines adult (35) + coronary (7) + paediatric (13) + neonatal (35) critical care units per hospital's published data.",
    },
    {
        "id": "H05", "name": "Manipal Hospital Old Airport Road", "type": "private",
        "lat": 12.9584571, "lon": 77.649039, "place_id": "ChIJayDGwMATrjsR3ceXkcPU2BI",
        "beds": 600, "icu_beds": 144, "icu_verified": True,
        "trauma": True, "specialties": ["Oncology", "Cardiac Sciences", "Neurosciences", "Gastroenterology", "Orthopaedics", "Organ Transplant", "Nephrology", "Urology"],
        "emergency_phone": "1800 102 4647", "emergency_phone_verified": True,
        "note": "Toll-free number is Manipal Hospitals' group-wide appointment/emergency line.",
    },
    {
        "id": "H06", "name": "Fortis Hospital Bannerghatta Rd", "type": "private",
        "lat": 12.8948217, "lon": 77.5986197, "place_id": "ChIJEfRVcCMVrjsRJZ6qMWbCCHM",
        "beds": 284, "icu_beds": 80, "icu_verified": True,
        "trauma": True, "specialties": ["Cardiac Sciences", "Neurology & Neurosurgery", "Gastroenterology", "Oncology", "Urology", "Orthopaedics", "Organ Transplant", "Robotic Surgery"],
        "emergency_phone": "96633 67253", "emergency_phone_verified": True,
        "note": "Emergency line per Fortis Healthcare's published hospital contact listing.",
    },
    {
        "id": "H07", "name": "Apollo Hospital Bannerghatta Rd", "type": "private",
        "lat": 12.8961976, "lon": 77.5985971, "place_id": "ChIJ9-3GUiEVrjsRhxoikQoujIM",
        "beds": 250, "icu_beds": 37, "icu_verified": True,
        "trauma": True, "specialties": ["Cardiology", "Oncology", "Neurosciences", "Orthopaedics", "Gastroenterology", "Organ Transplant", "Critical Care"],
        "emergency_phone": "080 6904 9765", "emergency_phone_verified": True,
        "note": "Main hospital line; ask specifically for Emergency on connecting.",
    },
    {
        "id": "H08", "name": "Narayana Health City", "type": "private",
        "lat": 12.8093547, "lon": 77.6951014, "place_id": "ChIJMeuXxpJtrjsR7OG82oDa3Xc",
        "beds": 1000, "icu_beds": None, "icu_verified": False,
        "trauma": True, "specialties": ["Cardiology", "Cardiac Surgery", "Neurology", "Neurosurgery", "Oncology", "Multi-organ Transplant"],
        "emergency_phone": "1800 309 0309", "emergency_phone_verified": True,
        "note": "Official emergency helpline per narayanahealth.org. Large multi-institution campus (cardiac, cancer, eye, multispecialty).",
    },
    {
        "id": "H09", "name": "Sakra World Hospital", "type": "private",
        "lat": 12.9323284, "lon": 77.6851884, "place_id": "ChIJLRq9dqYTrjsR217aIOhcAZs",
        "beds": 300, "icu_beds": None, "icu_verified": False,
        "trauma": False, "specialties": ["Multi-specialty", "Robotic Surgery", "Oncology", "Orthopaedics"],
        "emergency_phone": "080 4969 4969", "emergency_phone_verified": True,
        "note": "Main hospital contact number; confirm emergency routing when calling.",
    },
    {
        "id": "H10", "name": "Manipal Hospital Hebbal (formerly Columbia Asia)", "type": "private",
        "lat": 13.0509374, "lon": 77.5939248, "place_id": "ChIJ-d2lJo8XrjsRlge4yFlLCpM",
        "beds": 100, "icu_beds": None, "icu_verified": False,
        "trauma": False, "specialties": ["Multi-specialty", "General Surgery", "Paediatrics", "Obstetrics & Gynaecology"],
        "emergency_phone": "1800 102 4647", "emergency_phone_verified": True,
        "note": "Columbia Asia's Indian hospitals were acquired by Manipal Hospitals; this facility now operates under the Manipal brand at the same Kirloskar Business Park location.",
    },
    {
        "id": "H11", "name": "Vydehi Institute of Medical Sciences", "type": "private_teaching",
        "lat": 12.9757752, "lon": 77.7294426, "place_id": "ChIJIy4WaPYRrjsRBZfcU6n_l3o",
        "beds": 1000, "icu_beds": None, "icu_verified": False,
        "trauma": True, "specialties": ["General Medicine", "General Surgery", "Orthopaedics", "Cardiology", "Neurology", "Trauma Care"],
        "emergency_phone": "080 4906 9000", "emergency_phone_verified": True,
        "note": "Large teaching hospital in East Bengaluru (Whitefield).",
    },
    {
        "id": "H12", "name": "Aster CMI Hospital", "type": "private",
        "lat": 13.054497, "lon": 77.5915659, "place_id": "ChIJ0zFTdYkXrjsRLHNfpQq8LmI",
        "beds": 500, "icu_beds": None, "icu_verified": False,
        "trauma": True, "specialties": ["Neurosciences", "Cardiac Sciences", "Oncology", "Organ Transplant", "Critical Care"],
        "emergency_phone": "080 4342 0100", "emergency_phone_verified": True,
        "note": "Quaternary care hospital in North Bengaluru (Hebbal/Sahakar Nagar).",
    },
    {
        "id": "H13", "name": "Rajarajeswari Medical College Hospital", "type": "private_teaching",
        "lat": 12.8952343, "lon": 77.4619490, "place_id": "ChIJeza4Yg8-rjsRbz4rGXqTWuk",
        "beds": 800, "icu_beds": None, "icu_verified": False,
        "trauma": True, "specialties": ["General Medicine", "General Surgery", "Orthopaedics", "Obstetrics & Gynaecology"],
        "emergency_phone": "1800 4250 2222", "emergency_phone_verified": True,
        "note": "Teaching hospital in West Bengaluru (Kengeri, Mysore Road) -- this location was significantly corrected from an earlier estimate that placed it ~6km away.",
    },
    {
        "id": "H14", "name": "M S Ramaiah Memorial Hospital", "type": "private_teaching",
        "lat": 13.0283322, "lon": 77.5697841, "place_id": "ChIJbeV3d9wXrjsR0MkusbZE-zs",
        "beds": 1300, "icu_beds": None, "icu_verified": False,
        "trauma": True, "specialties": ["General Medicine", "General Surgery", "Cardiology", "Neurology", "Oncology", "Nephrology"],
        "emergency_phone": "080 6215 3400", "emergency_phone_verified": True,
        "note": "Large teaching hospital, North Bengaluru (New BEL Road).",
    },
    {
        "id": "H15", "name": "Jayadeva Institute of Cardiology", "type": "government_specialty",
        "lat": 12.91795, "lon": 77.5992213, "place_id": "ChIJPd7UYgYVrjsRuk4xpL5Q9ZE",
        "beds": 350, "icu_beds": None, "icu_verified": False,
        "trauma": False, "specialties": ["Cardiology", "Cardiac Surgery", "Cardiac Emergency & Cath Lab"],
        "emergency_phone": "080 2653 4600", "emergency_phone_verified": True,
        "note": "Government cardiac-specialty institute; the right destination specifically for cardiac emergencies, not general trauma.",
    },
    {
        "id": "H16", "name": "KIMS Hospital & Research Centre", "type": "private_teaching",
        "lat": 12.9565123, "lon": 77.574556, "place_id": "ChIJ1WI368AVrjsR-kq5egB1Aik",
        "beds": 900, "icu_beds": None, "icu_verified": False,
        "trauma": True, "specialties": ["General Medicine", "General Surgery", "Orthopaedics", "Cardiology"],
        "emergency_phone": "080 2671 5790", "emergency_phone_verified": True,
        "note": "Located in Basavanagudi -- this replaces an earlier, unverifiable 'KIMS Hospital Hebbal' entry that did not match any real facility.",
    },
]

# Universal, verified emergency numbers for Karnataka / India (confirmed via government/EMRI sources)
EMERGENCY_NUMBERS = {
    "ambulance_karnataka": {"number": "108", "label": "Karnataka Govt. Ambulance (GVK EMRI) — free, 24/7"},
    "unified_emergency_india": {"number": "112", "label": "India Unified Emergency Number (police/fire/medical)"},
}

