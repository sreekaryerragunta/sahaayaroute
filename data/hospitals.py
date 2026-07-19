"""
Bengaluru hospital directory.
Real hospital names, types, and approximate locations.

Verified fields (researched from official hospital sites / cross-checked sources):
  specialties, icu_beds, total_beds, emergency_phone -- where marked verified=True
Unverified fields are explicitly flagged so the app never presents a guess as fact.
IMPORTANT: emergency_phone should be re-confirmed before any real operational use --
numbers change, and this list was compiled from public web sources, not a hospital feed.
"""

HOSPITALS = [
    {
        "id": "H01", "name": "Victoria Hospital", "type": "government",
        "lat": 12.9634, "lon": 77.5747, "beds": 800, "icu_beds": None, "icu_verified": False,
        "trauma": True, "specialties": ["General Medicine", "General Surgery", "Trauma & Casualty", "Orthopedics", "Obstetrics & Gynaecology"],
        "emergency_phone": None, "emergency_phone_verified": False,
        "note": "Major government tertiary hospital with a dedicated casualty/trauma department.",
    },
    {
        "id": "H02", "name": "NIMHANS", "type": "government_specialty",
        "lat": 12.9432, "lon": 77.5966, "beds": 646, "icu_beds": None, "icu_verified": False,
        "trauma": False, "specialties": ["Neurology", "Neurosurgery", "Psychiatry", "Mental Health Crisis Care"],
        "emergency_phone": None, "emergency_phone_verified": False,
        "note": "India's premier neuro/psychiatric institute; not a general trauma center.",
    },
    {
        "id": "H03", "name": "Bowring & Lady Curzon Hospital", "type": "government",
        "lat": 12.9829, "lon": 77.6086, "beds": 500, "icu_beds": None, "icu_verified": False,
        "trauma": True, "specialties": ["General Medicine", "General Surgery", "Trauma & Casualty", "Obstetrics & Gynaecology"],
        "emergency_phone": None, "emergency_phone_verified": False,
        "note": "Government multi-specialty hospital in central Bengaluru.",
    },
    {
        "id": "H04", "name": "St. John's Medical College Hospital", "type": "private_teaching",
        "lat": 12.9279, "lon": 77.6236, "beds": 1200, "icu_beds": 90, "icu_verified": True,
        "trauma": True, "specialties": ["Cardiology", "Neurology", "Neurosurgery", "Oncology", "Gastroenterology", "Nephrology", "General Surgery", "Trauma & Mass Casualty Care"],
        "emergency_phone": None, "emergency_phone_verified": False,
        "note": "1200-bed teaching hospital; ICU figure combines adult (35) + coronary (7) + paediatric (13) + neonatal (35) critical care units per hospital's published data.",
    },
    {
        "id": "H05", "name": "Manipal Hospital Old Airport Road", "type": "private",
        "lat": 12.9584, "lon": 77.6484, "beds": 600, "icu_beds": 144, "icu_verified": True,
        "trauma": True, "specialties": ["Oncology", "Cardiac Sciences", "Neurosciences", "Gastroenterology", "Orthopaedics", "Organ Transplant", "Nephrology", "Urology"],
        "emergency_phone": "1800 102 5555", "emergency_phone_verified": True,
        "note": "Toll-free number is the hospital's official appointment/emergency line per manipalhospitals.com.",
    },
    {
        "id": "H06", "name": "Fortis Hospital Bannerghatta Rd", "type": "private",
        "lat": 12.8895, "lon": 77.5978, "beds": 284, "icu_beds": 80, "icu_verified": True,
        "trauma": True, "specialties": ["Cardiac Sciences", "Neurology & Neurosurgery", "Gastroenterology", "Oncology", "Urology", "Orthopaedics", "Organ Transplant", "Robotic Surgery"],
        "emergency_phone": "96633 67253", "emergency_phone_verified": True,
        "note": "Emergency line per Fortis Healthcare's published hospital contact listing.",
    },
    {
        "id": "H07", "name": "Apollo Hospital Bannerghatta Rd", "type": "private",
        "lat": 12.8998, "lon": 77.5992, "beds": 250, "icu_beds": 37, "icu_verified": True,
        "trauma": True, "specialties": ["Cardiology", "Oncology", "Neurosciences", "Orthopaedics", "Gastroenterology", "Organ Transplant", "Critical Care"],
        "emergency_phone": "080-26304050", "emergency_phone_verified": True,
        "note": "Main hospital line per Apollo's official listing; ask specifically for Emergency on connecting.",
    },
    {
        "id": "H08", "name": "Narayana Health City", "type": "private",
        "lat": 12.8103, "lon": 77.6884, "beds": 1000, "icu_beds": None, "icu_verified": False,
        "trauma": True, "specialties": ["Cardiology", "Cardiac Surgery", "Neurology", "Neurosurgery", "Oncology", "Multi-organ Transplant"],
        "emergency_phone": "1800 309 0309", "emergency_phone_verified": True,
        "note": "Official emergency helpline per narayanahealth.org. Large multi-institution campus (cardiac, cancer, eye, multispecialty).",
    },
    {
        "id": "H09", "name": "Sakra World Hospital", "type": "private",
        "lat": 12.9256, "lon": 77.6963, "beds": 300, "icu_beds": None, "icu_verified": False,
        "trauma": False, "specialties": ["Multi-specialty", "Robotic Surgery", "Oncology", "Orthopaedics"],
        "emergency_phone": "080 4969 4969", "emergency_phone_verified": True,
        "note": "Main hospital contact number per official site; confirm emergency routing when calling.",
    },
    {
        "id": "H10", "name": "Columbia Asia Hospital Hebbal", "type": "private",
        "lat": 13.0459, "lon": 77.5960, "beds": 100, "icu_beds": None, "icu_verified": False,
        "trauma": False, "specialties": ["Multi-specialty", "General Surgery", "Paediatrics", "Obstetrics & Gynaecology"],
        "emergency_phone": None, "emergency_phone_verified": False,
        "note": "Smaller multi-specialty hospital; verify current emergency capability before routing critical trauma here.",
    },
    {
        "id": "H11", "name": "Vydehi Institute of Medical Sciences", "type": "private_teaching",
        "lat": 12.9698, "lon": 77.7500, "beds": 1000, "icu_beds": None, "icu_verified": False,
        "trauma": True, "specialties": ["General Medicine", "General Surgery", "Orthopaedics", "Cardiology", "Neurology", "Trauma Care"],
        "emergency_phone": None, "emergency_phone_verified": False,
        "note": "Large teaching hospital in East Bengaluru.",
    },
    {
        "id": "H12", "name": "Aster CMI Hospital", "type": "private",
        "lat": 13.0483, "lon": 77.5975, "beds": 500, "icu_beds": None, "icu_verified": False,
        "trauma": True, "specialties": ["Neurosciences", "Cardiac Sciences", "Oncology", "Organ Transplant", "Critical Care"],
        "emergency_phone": None, "emergency_phone_verified": False,
        "note": "Quaternary care hospital in North Bengaluru.",
    },
    {
        "id": "H13", "name": "Rajarajeswari Medical College Hospital", "type": "private_teaching",
        "lat": 12.8981, "lon": 77.5175, "beds": 800, "icu_beds": None, "icu_verified": False,
        "trauma": True, "specialties": ["General Medicine", "General Surgery", "Orthopaedics", "Obstetrics & Gynaecology"],
        "emergency_phone": None, "emergency_phone_verified": False,
        "note": "Teaching hospital in West Bengaluru.",
    },
    {
        "id": "H14", "name": "M S Ramaiah Memorial Hospital", "type": "private_teaching",
        "lat": 13.0290, "lon": 77.5680, "beds": 1300, "icu_beds": None, "icu_verified": False,
        "trauma": True, "specialties": ["General Medicine", "General Surgery", "Cardiology", "Neurology", "Oncology", "Nephrology"],
        "emergency_phone": None, "emergency_phone_verified": False,
        "note": "Large teaching hospital, North Bengaluru.",
    },
    {
        "id": "H15", "name": "Jayadeva Institute of Cardiology", "type": "government_specialty",
        "lat": 12.9186, "lon": 77.5992, "beds": 350, "icu_beds": None, "icu_verified": False,
        "trauma": False, "specialties": ["Cardiology", "Cardiac Surgery", "Cardiac Emergency & Cath Lab"],
        "emergency_phone": None, "emergency_phone_verified": False,
        "note": "Government cardiac-specialty institute; the right destination specifically for cardiac emergencies, not general trauma.",
    },
    {
        "id": "H16", "name": "KIMS Hospital Hebbal", "type": "private_teaching",
        "lat": 13.0387, "lon": 77.5933, "beds": 900, "icu_beds": None, "icu_verified": False,
        "trauma": True, "specialties": ["General Medicine", "General Surgery", "Orthopaedics", "Cardiology"],
        "emergency_phone": None, "emergency_phone_verified": False,
        "note": "Teaching hospital in North Bengaluru.",
    },
]

# Universal, verified emergency numbers for Karnataka / India (confirmed via government/EMRI sources)
EMERGENCY_NUMBERS = {
    "ambulance_karnataka": {"number": "108", "label": "Karnataka Govt. Ambulance (GVK EMRI) — free, 24/7"},
    "unified_emergency_india": {"number": "112", "label": "India Unified Emergency Number (police/fire/medical)"},
}

