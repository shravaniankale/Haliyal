import os
from typing import Dict, List, Any

# JWT / Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "krishi-mitra-hackfusion-2026-super-secret-key-kannada-ai")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Base Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(BASE_DIR, "static_audio")
DATA_DIR = os.path.join(BASE_DIR, "data")
SCHEME_DOCS_DIR = os.path.join(BASE_DIR, "scheme_documents")
CHROMA_PERSIST_DIR = os.path.join(BASE_DIR, "chroma_db")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SCHEME_DOCS_DIR, exist_ok=True)
os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

# LLM / Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# 31 Karnataka Districts Configuration with Regional Mapping and Coordinates
KARNATAKA_DISTRICTS: Dict[str, Dict[str, Any]] = {
    # North Karnataka (ಉತ್ತರ ಕರ್ನಾಟಕ)
    "Belagavi": {"kn": "ಬೆಳಗಾವಿ", "region": "North Karnataka", "lat": 15.8497, "lon": 74.4977, "apmc": "Belgaum"},
    "Bagalkote": {"kn": "ಬಾಗಲಕೋಟೆ", "region": "North Karnataka", "lat": 16.1817, "lon": 75.6958, "apmc": "Bagalkot"},
    "Vijayapura": {"kn": "ವಿಜಯಪುರ", "region": "North Karnataka", "lat": 16.8302, "lon": 75.7100, "apmc": "Bijapur"},
    "Bidar": {"kn": "ಬೀದರ್", "region": "North Karnataka", "lat": 17.9104, "lon": 77.5199, "apmc": "Bidar"},
    "Kalaburagi": {"kn": "ಕಲಬುರಗಿ", "region": "North Karnataka", "lat": 17.3297, "lon": 76.8343, "apmc": "Gulbarga"},
    "Yadgir": {"kn": "ಯಾದಗಿರಿ", "region": "North Karnataka", "lat": 16.7705, "lon": 77.1376, "apmc": "Yadgir"},
    "Raichur": {"kn": "ರಾಯಚೂರು", "region": "North Karnataka", "lat": 16.2120, "lon": 77.3439, "apmc": "Raichur"},
    "Koppal": {"kn": "ಕೊಪ್ಪಳ", "region": "North Karnataka", "lat": 15.3456, "lon": 76.1549, "apmc": "Koppal"},
    "Gadag": {"kn": "ಗದಗ", "region": "North Karnataka", "lat": 15.4298, "lon": 75.6267, "apmc": "Gadag"},
    "Dharwad": {"kn": "ಧಾರವಾಡ", "region": "North Karnataka", "lat": 15.4589, "lon": 75.0078, "apmc": "Hubli"},
    "Haveri": {"kn": "ಹಾವೇರಿ", "region": "North Karnataka", "lat": 14.7952, "lon": 75.3991, "apmc": "Haveri"},
    "Ballari": {"kn": "ಬಳ್ಳಾರಿ", "region": "North Karnataka", "lat": 15.1394, "lon": 76.9214, "apmc": "Bellary"},
    "Vijayanagara": {"kn": "ವಿಜಯನಗರ", "region": "North Karnataka", "lat": 15.2736, "lon": 76.3904, "apmc": "Hospet"},

    # South Karnataka (ದಕ್ಷಿಣ ಕರ್ನಾಟಕ)
    "Mysuru": {"kn": "ಮೈಸೂರು", "region": "South Karnataka", "lat": 12.2958, "lon": 76.6394, "apmc": "Mysore"},
    "Mandya": {"kn": "ಮಂಡ್ಯ", "region": "South Karnataka", "lat": 12.5244, "lon": 76.8969, "apmc": "Mandya"},
    "Hassan": {"kn": "ಹಾಸನ", "region": "South Karnataka", "lat": 13.0033, "lon": 76.1004, "apmc": "Hassan"},
    "Chamarajanagar": {"kn": "ಚಾಮರಾಜನಗರ", "region": "South Karnataka", "lat": 11.9261, "lon": 76.9437, "apmc": "Chamarajanagar"},
    "Ramanagara": {"kn": "ರಾಮನಗರ", "region": "South Karnataka", "lat": 12.7209, "lon": 77.2799, "apmc": "Ramanagara"},
    "Bengaluru Urban": {"kn": "ಬೆಂಗಳೂರು ನಗರ", "region": "South Karnataka", "lat": 12.9716, "lon": 77.5946, "apmc": "Bangalore"},
    "Bengaluru Rural": {"kn": "ಬೆಂಗಳೂರು ಗ್ರಾಮಾಂತರ", "region": "South Karnataka", "lat": 13.2382, "lon": 77.7126, "apmc": "Doddaballapur"},
    "Kolar": {"kn": "ಕೋಲಾರ", "region": "South Karnataka", "lat": 13.1367, "lon": 78.1291, "apmc": "Kolar"},
    "Chikkaballapura": {"kn": "ಚಿಕ್ಕಬಳ್ಳಾಪುರ", "region": "South Karnataka", "lat": 13.4325, "lon": 77.7275, "apmc": "Chintamani"},
    "Tumakuru": {"kn": "ತುಮಕೂರು", "region": "South Karnataka", "lat": 13.3379, "lon": 77.1173, "apmc": "Tumkur"},
    "Chitradurga": {"kn": "ಚಿತ್ರದುರ್ಗ", "region": "South Karnataka", "lat": 14.2251, "lon": 76.4024, "apmc": "Chitradurga"},
    "Davanagere": {"kn": "ದಾವಣಗೆರೆ", "region": "South Karnataka", "lat": 14.4644, "lon": 75.9218, "apmc": "Davanagere"},
    "Shivamogga": {"kn": "ಶಿವಮೊಗ್ಗ", "region": "South Karnataka", "lat": 13.9299, "lon": 75.5681, "apmc": "Shimoga"},

    # Coastal & Malnad Karnataka (ಕರಾವಳಿ / ಮಲೆನಾಡು)
    "Dakshina Kannada": {"kn": "ದಕ್ಷಿಣ ಕನ್ನಡ", "region": "Coastal Karnataka", "lat": 12.8703, "lon": 74.8806, "apmc": "Mangalore"},
    "Udupi": {"kn": "ಉಡುಪಿ", "region": "Coastal Karnataka", "lat": 13.3409, "lon": 74.7421, "apmc": "Udupi"},
    "Uttara Kannada": {"kn": "ಉತ್ತರ ಕನ್ನಡ", "region": "Coastal Karnataka", "lat": 14.8185, "lon": 74.1303, "apmc": "Sirsi"},
    "Kodagu": {"kn": "ಕೊಡಗು", "region": "Malnad Karnataka", "lat": 12.4244, "lon": 75.7382, "apmc": "Madikeri"},
    "Chikkamagaluru": {"kn": "ಚಿಕ್ಕಮಗಳೂರು", "region": "Malnad Karnataka", "lat": 13.3161, "lon": 75.7720, "apmc": "Chikmagalur"},
}

def get_region_for_district(district_name: str) -> str:
    """Helper returning regional grouping for a given Karnataka district."""
    normalized = district_name.strip().title()
    for name, data in KARNATAKA_DISTRICTS.items():
        if name.lower() == normalized.lower():
            return data["region"]
    return "Standard Kannada"
