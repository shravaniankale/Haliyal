from typing import Dict, List, Any, Tuple
from ..config import KARNATAKA_DISTRICTS, get_region_for_district

# Comprehensive Karnataka Taluk mapping per district
DISTRICT_TALUKS: Dict[str, List[str]] = {
    # North Karnataka
    "Belagavi": ["Belagavi", "Bailhongal", "Chikkodi", "Gokak", "Hukkeri", "Khanapur", "Ramdurg", "Raybag", "Saundatti", "Athani", "Kagwad", "Mudalagi", "Kittur", "Nipani"],
    "Bagalkote": ["Bagalkote", "Badami", "Bilgi", "Hunagund", "Jamkhandi", "Mudhol", "Guledgudda", "Rabkavi Banhatti", "Ilkal"],
    "Vijayapura": ["Vijayapura", "Basavana Bagewadi", "Indi", "Muddebihal", "Sindagi", "Babaleshwar", "Tikota", "Chadchan", "Kolhar", "Nalatwad"],
    "Bidar": ["Bidar", "Basavakalyan", "Bhalki", "Homnabad", "Aurad", "Kamalnagar", "Hulsoor"],
    "Kalaburagi": ["Kalaburagi", "Afzalpur", "Aland", "Chincholi", "Chitapur", "Jevargi", "Sedam", "Kamalapur", "Yedrami", "Shahabad"],
    "Yadgir": ["Yadgir", "Shahapur", "Shorapur", "Hunasagi", "Vadagera", "Gurmitkal"],
    "Raichur": ["Raichur", "Devadurga", "Lingsugur", "Manvi", "Sindhanur", "Maski", "Sirwar"],
    "Koppal": ["Koppal", "Gangavathi", "Kushtagi", "Yelburga", "Kanakagiri", "Karatagi", "Kukanoor"],
    "Gadag": ["Gadag", "Nargund", "Ron", "Mundargi", "Shirhatti", "Gajendragad", "Lakshmeshwar"],
    "Dharwad": ["Dharwad", "Hubballi Urban", "Hubballi Rural", "Kundgol", "Navalgund", "Kalghatgi", "Alnavar", "Annigeri"],
    "Haveri": ["Haveri", "Byadgi", "Hangal", "Hirekerur", "Ranebennur", "Shiggaon", "Savanur", "Rattihalli"],
    "Ballari": ["Ballari", "Kampli", "Kurugodu", "Sandur", "Siruguppa"],
    "Vijayanagara": ["Hosapete", "Harapanahalli", "Hagaribommanahalli", "Hoovina Hadagali", "Kudligi", "Kotturu"],

    # South Karnataka
    "Mysuru": ["Mysuru", "Hunsur", "K.R. Nagar", "Nanjangud", "H.D. Kote", "Piriyapatna", "T. Narasipura", "Saragur", "Saligrama"],
    "Mandya": ["Mandya", "Maddur", "Malavalli", "Pandavapura", "Srirangapatna", "Krishnarajapet", "Nagamangala"],
    "Hassan": ["Hassan", "Alur", "Arkalgud", "Arsikere", "Belur", "Channarayapatna", "Holenarasipura", "Sakleshpur"],
    "Chamarajanagar": ["Chamarajanagar", "Gundlupet", "Kollegal", "Yelandur", "Hanur"],
    "Ramanagara": ["Ramanagara", "Channapatna", "Kanakapura", "Magadi", "Harohalli"],
    "Bengaluru Urban": ["Bengaluru North", "Bengaluru South", "Bengaluru East", "Anekal", "Yelahanka"],
    "Bengaluru Rural": ["Devanahalli", "Doddaballapura", "Hosakote", "Nelamangala"],
    "Kolar": ["Kolar", "Bangarapet", "Malur", "Mulbagal", "Srinivaspur", "KGF"],
    "Chikkaballapura": ["Chikkaballapura", "Bagepalli", "Chintamani", "Gowribidanur", "Gudibanda", "Sidlaghatta"],
    "Tumakuru": ["Tumakuru", "Chikkanayakanahalli", "Gubbi", "Koratagere", "Kunigal", "Madhugiri", "Pavagada", "Sira", "Tiptur", "Turuvekere"],
    "Chitradurga": ["Chitradurga", "Challakere", "Hiriyur", "Holalkere", "Hosadurga", "Molakalmuru"],
    "Davanagere": ["Davanagere", "Harihara", "Channagiri", "Honnali", "Jagalur", "Nyamathi"],
    "Shivamogga": ["Shivamogga", "Bhadravati", "Hosanagara", "Sagara", "Shikaripura", "Soraba", "Thirthahalli"],
    "Kodagu": ["Madikeri", "Somwarpet", "Virajpet", "Kushalnagar", "Ponnampet"],
    "Chikkamagaluru": ["Chikkamagaluru", "Kadur", "Koppa", "Mudigere", "Narasimharajapura", "Sringeri", "Tarikere", "Ajjampura"],

    # Coastal Karnataka
    "Dakshina Kannada": ["Mangaluru", "Bantwal", "Belthangady", "Puttur", "Sullia", "Moodbidri", "Kadaba"],
    "Udupi": ["Udupi", "Kundapura", "Karkala", "Byndoor", "Brahmavara", "Kaup", "Hebri"],
    "Uttara Kannada": ["Karwar", "Ankola", "Kumta", "Honnavar", "Bhatkal", "Sirsi", "Siddapur", "Yellapur", "Mundgod", "Haliyal", "Joida"],
}

# Kannada Taluk name to (English Taluk, District) mapping
TALUKS_KN_TO_EN: Dict[str, Tuple[str, str]] = {
    # Belagavi
    "ಬೆಳಗಾವಿ": ("Belagavi", "Belagavi"),
    "ಬೈಲಹೊಂಗಲ": ("Bailhongal", "Belagavi"),
    "ಚಿಕ್ಕೋಡಿ": ("Chikkodi", "Belagavi"),
    "ಗೋಕಾಕ": ("Gokak", "Belagavi"),
    "ಗೋಕಾಕ್": ("Gokak", "Belagavi"),
    "ಹುಕ್ಕೇರಿ": ("Hukkeri", "Belagavi"),
    "ಖಾನಾಪುರ": ("Khanapur", "Belagavi"),
    "ರಾಮದುರ್ಗ": ("Ramdurg", "Belagavi"),
    "ರಾಯಬಾಗ": ("Raybag", "Belagavi"),
    "ಸವದತ್ತಿ": ("Saundatti", "Belagavi"),
    "ಸವದತ್ತಿ-ಯಲ್ಲಮ್ಮ": ("Saundatti", "Belagavi"),
    "ಅಥಣಿ": ("Athani", "Belagavi"),
    "ಕಾಗವಾಡ": ("Kagwad", "Belagavi"),
    "ಮೂಡಲಗಿ": ("Mudalagi", "Belagavi"),
    "ಕಿತ್ತೂರು": ("Kittur", "Belagavi"),
    "ನಿಪ್ಪಾಣಿ": ("Nipani", "Belagavi"),
    # Dharwad
    "ಧಾರವಾಡ": ("Dharwad", "Dharwad"),
    "ಹುಬ್ಬಳ್ಳಿ": ("Hubballi Urban", "Dharwad"),
    "ಕುಂದಗೋಳ": ("Kundgol", "Dharwad"),
    "ನವಲಗುಂದ": ("Navalgund", "Dharwad"),
    "ಕಲಘಟಗಿ": ("Kalghatgi", "Dharwad"),
    "ಅಳ್ನಾವರ": ("Alnavar", "Dharwad"),
    "ಅಣ್ಣಿಗೇರಿ": ("Annigeri", "Dharwad"),
    # Uttara Kannada
    "ಹಳಿಯಾಳ": ("Haliyal", "Uttara Kannada"),
    "ಕಾರವಾರ": ("Karwar", "Uttara Kannada"),
    "ಶಿರಸಿ": ("Sirsi", "Uttara Kannada"),
    "ದಾಂಡೇಲಿ": ("Dandeli", "Uttara Kannada"),
    # Bagalkote
    "ಬಾಗಲಕೋಟೆ": ("Bagalkote", "Bagalkote"),
    "ಬಾದಾಮಿ": ("Badami", "Bagalkote"),
    "ಜಮಖಂಡಿ": ("Jamkhandi", "Bagalkote"),
    "ಮುಧೋಳ": ("Mudhol", "Bagalkote"),
    # Vijayapura
    "ವಿಜಯಪುರ": ("Vijayapura", "Vijayapura"),
    "ಇಂಡಿ": ("Indi", "Vijayapura"),
    "ಸಿಂದಗಿ": ("Sindagi", "Vijayapura"),
    # Kalaburagi
    "ಕಲಬುರಗಿ": ("Kalaburagi", "Kalaburagi"),
    "ಸೇಡಂ": ("Sedam", "Kalaburagi"),
    # Ballari
    "ಬಳ್ಳಾರಿ": ("Ballari", "Ballari"),
    "ಹೊಸಪೇಟೆ": ("Hosapete", "Vijayanagara"),
    # Mysuru
    "ಮೈಸೂರು": ("Mysuru", "Mysuru"),
    "ಹುಣಸೂರು": ("Hunsur", "Mysuru"),
    "ನಂಜನಗೂಡು": ("Nanjangud", "Mysuru"),
    # Mandya
    "ಮಂಡ್ಯ": ("Mandya", "Mandya"),
    "ಮದ್ದೂರು": ("Maddur", "Mandya"),
    # Hassan
    "ಹಾಸನ": ("Hassan", "Hassan"),
    # Shivamogga
    "ಶಿವಮೊಗ್ಗ": ("Shivamogga", "Shivamogga"),
    "ಸಾಗರ": ("Sagara", "Shivamogga"),
    # Bengaluru
    "ಬೆಂಗಳೂರು": ("Bengaluru Urban", "Bengaluru Urban"),
    # Udupi & Dakshina Kannada
    "ಉಡುಪಿ": ("Udupi", "Udupi"),
    "ಮಂಗಳೂರು": ("Mangaluru", "Dakshina Kannada")
}

# Regional Kannada Vocabulary & Tone Dictionaries
REGIONAL_DIALECT_TOKENS: Dict[str, Dict[str, Any]] = {
    "North Karnataka": {
        "greeting": "ನಮಸ್ಕಾರ್ರೀ, ನಮ್ದು ಕೃಷಿ ಮಿತ್ರ AI ಸಹಾಯಕ ನೋಡ್ರೀ. ನಿಮ್ಗ ಯಾವ್ ಯೋಜನೆ ಬಗ್ಗೆ ಮಾಹಿತಿ ಬೇಕ್ರಿ?",
        "ask_land": "ನಿಮ್ದು ಜಮೀನು ಎಷ್ಟೈತಿ? (ಎಕರೆ ಅಥವಾ ಗುಂಟೆನ್ಯಾಗ ಹೇಳ್ರಿ)",
        "ask_crop": "ನೀವು ಯಾವ್ ಬೆಳಿ ಹಾಕ್ತೀರಿ ಅಪ್ಪಾ? ಭತ್ತ, ಜೋಳ, ತೊಗರಿ, ಕಬ್ಬು ಏನರ ಬೆಳಿತ್ಯೀರಾ?",
        "ask_ownership": "ಭೂಮಿ ನಿಮ್ದ ಸ್ವಂತ ಐತೋ ಇಲ್ಲಾ ಗೇಣಿ ಮಾಡ್ತೀರಾ?",
        "ask_irrigation": "ನೀರಿನ ಸೌಲಭ್ಯ ಹ್ಯಾಂಗೈತಿ? ಮಳೆ ಆಶ್ರಯನೋ, ಬೋರ್ವೆಲ್ ಐತೋ?",
        "suffix_positive": "ಸಿಗತೈತಿ ನೋಡ್ರೀ",
        "suffix_question": "ಹೇಳ್ರೀ",
        "term_land": "ಜಮೀನು",
        "term_crop": "ಬೆಳಿ",
        "term_yes": "ಹೌದ್ರೀ",
        "term_no": "ಇಲ್ಲ್ರೀ",
        "style_note": "ಉತ್ತರ ಕರ್ನಾಟಕ ಆಡುಭಾಷೆ (ಧಾರವಾಡ, ಬೆಳಗಾವಿ, ಕಲಬುರಗಿ, ವಿಜಯಪುರ ಶೈಲಿ)"
    },
    "South Karnataka": {
        "greeting": "ನಮಸ್ಕಾರ, ಕೃಷಿ ಮಿತ್ರ AI ಸಹಾಯಕ್ಕೆ ಸ್ವಾಗತ. ನಿಮಗೆ ಯಾವ ಯೋಜನೆಯ ಬಗ್ಗೆ ಮಾಹಿತಿ ಬೇಕು?",
        "ask_land": "ನಿಮ್ಮ ಬಳಿ ಎಷ್ಟು ಎಕರೆ ಜಮೀನು ಇದೆ ಎಂದು ತಿಳಿಸಿ.",
        "ask_crop": "ತಾವು ಯಾವ ಬೆಳೆ ಬೆಳೆಯುತ್ತಿದ್ದೀರಿ? (ಭತ್ತ, ರಾಗಿ, ಮೆಕ್ಕೆಜೋಳ, ತೆಂಗು)",
        "ask_ownership": "ಭೂಮಿ ತಮ್ಮ ಸ್ವಂತದ್ದೇ ಅಥವಾ ಗೇಣಿ ಭೂಮಿಯೇ?",
        "ask_irrigation": "ನೀರಾವರಿ ಸೌಲಭ್ಯ ಹೇಗಿದೆ? ಮಳೆ ಆಧಾರಿತವೇ ಅಥವಾ ಕೊಳವೆ ಬಾವಿಯೇ?",
        "suffix_positive": "ದೊರೆಯುತ್ತದೆ",
        "suffix_question": "ದಯವಿಟ್ಟು ತಿಳಿಸಿ",
        "term_land": "ಜಮೀನು / ಭೂಮಿ",
        "term_crop": "ಬೆಳೆ",
        "term_yes": "ಹೌದು",
        "term_no": "ಇಲ್ಲ",
        "style_note": "ದಕ್ಷಿಣ ಕರ್ನಾಟಕ ಶೈಲಿ (ಮೈಸೂರು, ಮಂಡ್ಯ, ಹಾಸನ, ಬೆಂಗಳೂರು ಶೈಲಿ)"
    },
    "Standard Kannada": {
        "greeting": "ನಮಸ್ಕಾರ, ಕೃಷಿ ಮಿತ್ರ ರೈತ ಮಿತ್ರ ಸಹಾಯವಾಣಿಗೆ ಸ್ವಾಗತ. ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?",
        "ask_land": "ನಿಮ್ಮ ಕೃಷಿ ಭೂಮಿಯ ವಿಸ್ತೀರ್ಣ ಎಷ್ಟು ಎಕರೆ ಎಂದು ನಮೂದಿಸಿ.",
        "ask_crop": "ನೀವು ಬೆಳೆಯುವ ಪ್ರಮುಖ ಬೆಳೆ ಯಾವುದು?",
        "ask_ownership": "ಭೂಮಿಯ ಮಾಲೀಕತ್ವದ ವಿವರ ತಿಳಿಸಿ (ಸ್ವಂತ / ಗೇಣಿ).",
        "ask_irrigation": "ನೀರಾವರಿ ಮೂಲ ಯಾವುದು? (ಮಳೆ ಆಶ್ರಯ / ಕೊಳವೆಬಾವಿ / ಕಾಲುವೆ).",
        "suffix_positive": "ಅರ್ಹರಾಗಿರುತ್ತೀರಿ",
        "suffix_question": "ದಯವಿಟ್ಟು ವಿವರ ನೀಡಿ",
        "term_land": "ಕೃಷಿ ಭೂಮಿ",
        "term_crop": "ಬೆಳೆ",
        "term_yes": "ಹೌದು",
        "term_no": "ಇಲ್ಲ",
        "style_note": "ಶಿಷ್ಟ ಕನ್ನಡ (ಸರ್ಕಾರಿ ಅಧಿಕೃತ ಭಾಷಾ ಶೈಲಿ)"
    }
}

def get_district_info(district_name: str) -> Dict[str, Any]:
    """Retrieve full details for any Karnataka district."""
    normalized = district_name.strip().title()
    for name, data in KARNATAKA_DISTRICTS.items():
        if name.lower() == normalized.lower():
            taluks = DISTRICT_TALUKS.get(name, [name])
            return {
                "name": name,
                "name_kn": data["kn"],
                "region": data["region"],
                "latitude": data["lat"],
                "longitude": data["lon"],
                "apmc_mandi": data["apmc"],
                "taluks": taluks
            }
    # Fallback to Bengaluru Urban
    return {
        "name": "Bengaluru Urban",
        "name_kn": "ಬೆಂಗಳೂರು ನಗರ",
        "region": "South Karnataka",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "apmc_mandi": "Bangalore",
        "taluks": DISTRICT_TALUKS["Bengaluru Urban"]
    }
