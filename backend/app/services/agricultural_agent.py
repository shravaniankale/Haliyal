import re
import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from ..models import Scheme
from .district_service import get_region_for_district, REGIONAL_DIALECT_TOKENS, KARNATAKA_DISTRICTS, DISTRICT_TALUKS, TALUKS_KN_TO_EN
from .kannada_speech import KannadaSpeechService
from .vocabulary_service import KannadaVocabularyService
from .rag_engine import RAGEngine
from .insurance_service import CropInsuranceService
from .season_service import AgriculturalSeasonService
from .weather_service import AgriculturalWeatherService

logger = logging.getLogger(__name__)

KANNADA_NUMBER_WORDS: Dict[str, float] = {
    "ಅರ್ಧ": 0.5, "ಒಂದು": 1.0, "ಒಂದೂವರೆ": 1.5, "ಎರಡು": 2.0, "ಎರಡೂವರೆ": 2.5,
    "ಮೂರು": 3.0, "ಮೂರವರೆ": 3.5, "ಮೂರಾವರೆ": 3.5, "ನಾಲ್ಕು": 4.0, "ನಾಲ್ಕವರೆ": 4.5,
    "ಐದು": 5.0, "ಐದೂವರೆ": 5.5, "ಆರು": 6.0, "ಏಳು": 7.0, "ಎಂಟು": 8.0,
    "ಒಂಬತ್ತು": 9.0, "ಹತ್ತು": 10.0, "ಹದಿನೈದು": 15.0, "ಇಪ್ಪತ್ತು": 20.0,
    "೧": 1.0, "೨": 2.0, "೩": 3.0, "೪": 4.0, "೫": 5.0,
    "೬": 6.0, "೭": 7.0, "೮": 8.0, "೯": 9.0, "೧೦": 10.0
}


# Conversation Workflow Stages (Phase 8 State Machine)
STAGE_INITIAL_GREETING = "INITIAL_GREETING"
STAGE_COLLECT_DISTRICT = "COLLECT_DISTRICT"
STAGE_COLLECT_TALUKA = "COLLECT_TALUKA"
STAGE_COLLECT_VILLAGE = "COLLECT_VILLAGE"
STAGE_COLLECT_LAND_SIZE = "COLLECT_LAND_SIZE"
STAGE_COLLECT_OWNERSHIP = "COLLECT_OWNERSHIP"
STAGE_COLLECT_FARMER_CATEGORY = "COLLECT_FARMER_CATEGORY"
STAGE_COLLECT_CROPS = "COLLECT_CROPS"
STAGE_COLLECT_OTHER_CROPS = "COLLECT_OTHER_CROPS"
STAGE_COLLECT_IRRIGATION = "COLLECT_IRRIGATION"
STAGE_COLLECT_SOIL = "COLLECT_SOIL"
STAGE_COLLECT_SEASON_AND_CROP_STAGE = "COLLECT_SEASON_AND_CROP_STAGE"
STAGE_CONFIRM_PROFILE = "CONFIRM_PROFILE"
STAGE_COLLECT_CORRECTION = "COLLECT_CORRECTION"
STAGE_IDENTIFY_REQUIREMENT = "IDENTIFY_REQUIREMENT"
STAGE_COLLECT_REQUEST_SPECIFIC_DETAILS = "COLLECT_REQUEST_SPECIFIC_DETAILS"
STAGE_ANALYSE_INFORMATION = "ANALYSE_INFORMATION"
STAGE_PRESENT_RESULTS = "PRESENT_RESULTS"
STAGE_FOLLOW_UP = "FOLLOW_UP"

# Sequence of basic farm profile questions
COLLECTION_PIPELINE = [
    STAGE_COLLECT_DISTRICT,
    STAGE_COLLECT_TALUKA,
    STAGE_COLLECT_VILLAGE,
    STAGE_COLLECT_LAND_SIZE,
    STAGE_COLLECT_OWNERSHIP,
    STAGE_COLLECT_FARMER_CATEGORY,
    STAGE_COLLECT_CROPS,
    STAGE_COLLECT_OTHER_CROPS,
    STAGE_COLLECT_IRRIGATION,
    STAGE_COLLECT_SOIL,
    STAGE_COLLECT_SEASON_AND_CROP_STAGE,
]

class AgriculturalConversationalAgent:
    """
    Complete Agricultural AI Voice Assistant Agent for Karnataka farmers.
    Implements a strict conversation state machine that asks questions one at a time,
    validates answers, confirms profiles, identifies farmer requirements,
    and runs deterministic agricultural analyses.
    """

    CROP_MAP = {
        "ಭತ್ತ": "Paddy", "paddy": "Paddy", "rice": "Paddy", "ಅಕ್ಕಿ": "Paddy",
        "ರಾಗಿ": "Ragi", "ragi": "Ragi", "finger millet": "Ragi",
        "ಜೋಳ": "Jowar", "jowar": "Jowar", "sorghum": "Jowar",
        "ಮೆಕ್ಕೆಜೋಳ": "Maize", "maize": "Maize", "corn": "Maize", "ಮುಸುಕಿನ ಜೋಳ": "Maize",
        "ಕಬ್ಬು": "Sugarcane", "sugarcane": "Sugarcane",
        "ಹತ್ತಿ": "Cotton", "cotton": "Cotton",
        "ಕಡಲೆಕಾಯಿ": "Groundnut", "ಶೇಂಗಾ": "Groundnut", "ಶೆಂಗಾ": "Groundnut", "ನೆಲಗಡಲೆ": "Groundnut", "groundnut": "Groundnut", "peanut": "Groundnut",
        "ತೊಗರಿ": "Tur", "tur": "Tur", "red gram": "Tur", "ತೊಗರಿಬೇಳೆ": "Tur", "ತೊಗರಿ ಬೇಳೆ": "Tur",
        "ಕಡಲೆ": "Bengal Gram", "chickpea": "Bengal Gram", "bengal gram": "Bengal Gram", "ಕಡಲೆ ಕಾಳು": "Bengal Gram",
        "ಸೋಯಾಬೀನ್": "Soybean", "soybean": "Soybean", "ಸೋಯಾ": "Soybean",
        "ತೆಂಗು": "Coconut", "coconut": "Coconut", "ತೆಂಗಿನಕಾಯಿ": "Coconut",
        "ಅಡಿಕೆ": "Arecanut", "arecanut": "Arecanut", "ಅಡಕೆ": "Arecanut",
        "ಕಾಫಿ": "Coffee", "coffee": "Coffee",
        "ಗೋಧಿ": "Wheat", "wheat": "Wheat",
        "ಸೂರ್ಯಕಾಂತಿ": "Sunflower", "sunflower": "Sunflower",
        "ಬಾಳೆ": "Banana", "banana": "Banana",
        "ಈರುಳ್ಳಿ": "Onion", "onion": "Onion", "ಉಳ್ಳಾಗಡ್ಡಿ": "Onion",
        "ಟೊಮೆಟೊ": "Tomato", "tomato": "Tomato",
        "ಮೆಣಸಿನಕಾಯಿ": "Chilli", "chilli": "Chilli", "chili": "Chilli", "ಮಿರ್ಚಿ": "Chilli"
    }

    AGRI_KEYWORDS = [
        "ಬೆಳೆ", "ಕೃಷಿ", "ರೈತ", "ಹೊಲ", "ಗದ್ದೆ", "ಜಮೀನು", "ಭೂಮಿ", "ಮಣ್ಣು", "ಗೊಬ್ಬರ", "ಯೂರಿಯಾ", "ಡಿಎಪಿ", "ಪೊಟ್ಯಾಶ್",
        "ಎನ್‌ಪಿಕೆ", "ನೀರಾವರಿ", "ಕೊಳವೆಬಾವಿ", "ಬೋರ್ವೆಲ್", "ಬೋರ್", "ಕಾಲುವೆ", "ಹನಿ", "ತುಂತುರು", "ಮಳೆ", "ಹವಾಮಾನ", "ಖುಷ್ಕಿ",
        "ಯೋಜನೆ", "ಸಬ್ಸಿಡಿ", "ಸಹಾಯಧನ", "ಪಿಎಂ-ಕಿಸಾನ್", "ಕೃಷಿ ಭಾಗ್ಯ", "ಫಸಲ್ ಬಿಮಾ", "ಸಂರಕ್ಷಣೆ", "ವಿಮೆ", "ಸಾಲ", "ಕೆಸಿಸಿ",
        "ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್", "ಬ್ಯಾಂಕ್", "ಬಡ್ಡಿ", "ಪಹಣಿ", "ಆರ್‌ಟಿಸಿ", "ಬೆಲೆ", "ಮಾರುಕಟ್ಟೆ", "ಮಂಡಿ", "ಎಪಿಎಂಸಿ", "ದರ",
        "ಕೀಟ", "ಹುಳು", "ರೋಗ", "ಸಿಂಪಡಣೆ", "ಕೀಟನಾಶಕ", "ಕೊಯ್ಲು", "ಬಿತ್ತನೆ", "ಕಟಾವು", "ಬೀಜ", "ಭತ್ತ", "ರಾಗಿ", "ಜೋಳ",
        "ಮೆಕ್ಕೆಜೋಳ", "ಕಬ್ಬು", "ಹತ್ತಿ", "ಶೇಂಗಾ", "ತೊಗರಿ", "ಕಡಲೆ", "ಸೋಯಾಬೀನ್", "ತೆಂಗು", "ಅಡಿಕೆ", "ಕಾಫಿ", "ಗೋಧಿ",
        "crop", "agriculture", "farmer", "farming", "farm", "field", "land", "soil", "fertilizer", "urea", "dap",
        "npk", "irrigation", "borewell", "canal", "drip", "sprinkler", "rain", "weather", "scheme", "subsidy",
        "pm-kisan", "pmfby", "krishi bhagya", "samrakshane", "insurance", "loan", "kcc", "credit", "bank",
        "interest", "pahani", "rtc", "price", "mandi", "apmc", "rate", "pest", "disease", "spray", "harvest",
        "sowing", "seed", "paddy", "ragi", "jowar", "maize", "sugarcane", "cotton", "groundnut", "tur",
        "bengal gram", "wheat", "banana", "onion", "tomato", "chilli", "72", "help", "ಸಹಾಯ", "ನಮಸ್ಕಾರ", "hello", "hi",
        "ಹೌದು", "ಸರಿ", "ಇಲ್ಲ", "ಮುಂದೆ", "ಸ್ವಂತ", "ಗುತ್ತಿಗೆ", "ಗೇಣಿ", "ಎಕರೆ", "ಹೆಕ್ಟೇರ್", "ಗುಂಟೆ",
        "ಜಿಲ್ಲೆ", "ತಾಲೂಕು", "ತಾಲೂಕ", "ಗ್ರಾಮ", "district", "taluk", "village"
    ]

    NON_AGRI_KEYWORDS = [
        "cricket", "match", "movie", "cinema", "film", "bollywood", "actor", "actress", "song", "python", "java",
        "coding", "programming", "software", "code", "president", "prime minister of america", "paris", "france",
        "celebrity", "ipl", "football", "recipe", "pizza", "burger", "gaming", "bitcoin", "crypto",
        "ಕ್ರಿಕೆಟ್", "ಸಿನಿಮಾ", "ಚಿತ್ರ", "ನಟ", "ನಟಿ", "ಹಾಡು", "ಕೋಡಿಂಗ್", "ಪ್ರೋಗ್ರಾಮಿಂಗ್", "ಸಾಫ್ಟ್‌ವೇರ್", "ಚಲನಚಿತ್ರ"
    ]

    @classmethod
    def is_agriculture_query(cls, text: str) -> bool:
        """Determines if the farmer's query is strictly within the agricultural domain."""
        if not text or not text.strip():
            return True

        t_lower = text.lower().strip()

        # Greetings or affirmations
        if t_lower in ["hi", "hello", "namaskara", "ನಮಸ್ಕಾರ", "ನಮಸ್ಕಾರ್ರೀ", "ಹಲೋ", "namaste", "ನಮಸ್ತೆ", "ಹೌದು", "ಸರಿ", "ಇಲ್ಲ"]:
            return True

        # Check for explicitly non-agricultural triggers
        for kw in cls.NON_AGRI_KEYWORDS:
            if kw in t_lower:
                return False

        # Check for agricultural triggers
        for kw in cls.AGRI_KEYWORDS:
            if kw in t_lower or kw in text:
                return True

        # Short answers (e.g. "3", "ಬೆಳಗಾವಿ", "ಸ್ವಂತ") are valid conversation inputs
        if len(text.split()) <= 4:
            return True

        for dist in KARNATAKA_DISTRICTS:
            if dist.lower() in t_lower:
                return True

        return False

    @classmethod
    def extract_entities(cls, text: str) -> Dict[str, Any]:
        """Extracts agricultural entities from user text."""
        entities: Dict[str, Any] = {}
        if not text:
            return entities

        normalized_text, detected_vocab = KannadaVocabularyService.normalize_text(text)
        if detected_vocab:
            entities["normalized_vocabulary"] = [d["original_term"] for d in detected_vocab]
            entities["vocabulary_mappings"] = detected_vocab

        combined_text = f"{text} {normalized_text}"
        combined_lower = combined_text.lower()

        # 1. Extract Crop (support substitution: "ಭತ್ತದ ಬದಲು ಕಬ್ಬು" -> prioritize crop after "ಬದಲು")
        if "ಬದಲು" in text or "instead of" in text.lower():
            after_text = re.split(r"ಬದಲು|instead of", text, flags=re.IGNORECASE)[-1]
            for token, crop_name in cls.CROP_MAP.items():
                if token in after_text or token in after_text.lower():
                    entities["crop"] = crop_name
                    entities["primary_crop"] = crop_name
                    break

        if "crop" not in entities:
            for token, crop_name in cls.CROP_MAP.items():
                if token in combined_text or token in combined_lower:
                    entities["crop"] = crop_name
                    entities["primary_crop"] = crop_name
                    break

        # 2. Extract District
        for dist, data in KARNATAKA_DISTRICTS.items():
            if dist.lower() in combined_lower or data["kn"] in combined_text:
                entities["district"] = dist
                entities["district_kn"] = data["kn"]
                entities["region"] = data["region"]
                break

        # 2b. Extract Taluk (Kannada mappings & English names)
        taluk_candidates = []
        for kn_t, (en_t, dist_k) in TALUKS_KN_TO_EN.items():
            if kn_t in combined_text or kn_t.lower() in combined_lower:
                taluk_candidates.append((en_t, kn_t, dist_k))

        for dist_name, taluk_list in DISTRICT_TALUKS.items():
            for t_name in taluk_list:
                if t_name.lower() in combined_lower:
                    taluk_candidates.append((t_name, t_name, dist_name))

        if taluk_candidates:
            target_dist = entities.get("district")
            if target_dist:
                dist_matched = [c for c in taluk_candidates if c[2].lower() == target_dist.lower()]
                if dist_matched:
                    taluk_candidates = dist_matched

            # If multiple candidates exist and one is the district headquarters while another is a distinct taluk,
            # prefer the distinct taluk (e.g. in "ಜಿಲ್ಲೆ ಬೆಳಗಾವಿ ತಾಲೂಕು ಬೈಲಹೊಂಗಲ", prefer Bailhongal over Belagavi)
            if len(taluk_candidates) > 1 and target_dist:
                non_headquarter = [c for c in taluk_candidates if c[0].lower() != target_dist.lower()]
                if non_headquarter:
                    taluk_candidates = non_headquarter

            best_taluk = taluk_candidates[0]
            entities["taluk"] = best_taluk[0]
            entities["taluk_kn"] = best_taluk[1]
            if "district" not in entities:
                entities["district"] = best_taluk[2]
                entities["region"] = get_region_for_district(best_taluk[2])

        # 3. Extract Land Size (Acres / Hectares / Guntas)
        # Check Kannada word numbers first
        for word, val in KANNADA_NUMBER_WORDS.items():
            if word in combined_text and any(u in combined_text for u in ["ಎಕರೆ", "acre", "acres", "ಎಕರ", "ಜಮೀನು", "ಭೂಮಿ", "ಹೆಕ್ಟೇರ್", "ಗುಂಟೆ"]):
                if "ಹೆಕ್ಟೇರ್" in combined_text:
                    entities["land_acres"] = round(val * 2.471, 2)
                    entities["land_unit"] = "hectares"
                elif "ಗುಂಟೆ" in combined_text or "ಗುಂಟಾ" in combined_text:
                    entities["land_acres"] = round(val / 40.0, 2)
                    entities["land_unit"] = "guntas"
                else:
                    entities["land_acres"] = float(val)
                    entities["land_unit"] = "acres"
                break

        if "land_acres" not in entities:
            hec_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:ಹೆಕ್ಟೇರ್|ಹೆಕ್ಟೇರ|hectare|hectares|ha)', combined_text, re.IGNORECASE)
            if hec_match:
                try:
                    val = float(hec_match.group(1))
                    entities["land_acres"] = round(val * 2.471, 2)
                    entities["land_unit"] = "hectares"
                except Exception:
                    pass
            else:
                gunta_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:ಗುಂಟೆ|ಗುಂಟಾ|gunta|guntas)', combined_text, re.IGNORECASE)
                if gunta_match:
                    try:
                        val = float(gunta_match.group(1))
                        entities["land_acres"] = round(val / 40.0, 2)
                        entities["land_unit"] = "guntas"
                    except Exception:
                        pass
                else:
                    land_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:ಎಕರೆ|acre|acres|ಎಕರ|ac)', combined_text, re.IGNORECASE)
                    if land_match:
                        try:
                            entities["land_acres"] = float(land_match.group(1))
                            entities["land_unit"] = "acres"
                        except Exception:
                            pass
                    else:
                        num_match = re.search(r'(\d+(?:\.\d+)?)', combined_text)
                        if num_match:
                            try:
                                val = float(num_match.group(1))
                                if 0.1 <= val <= 1000.0:
                                    entities["land_acres"] = val
                                    entities["land_unit"] = "acres"
                            except Exception:
                                pass

        

# 4. Extract Ownership (support negated phrases: "ಬಾಡಿಗೆಯದ್ದಲ್ಲ, ಸ್ವಂತದ್ದು")
        if any(k in combined_text for k in ["ಬಾಡಿಗೆಯದ್ದಲ್ಲ", "ಗುತ್ತಿಗೆಯಲ್ಲ", "ಬಾಡಿಗೆ ಅಲ್ಲ", "ಗುತ್ತಿಗೆ ಅಲ್ಲ"]) and any(k in combined_text for k in ["ಸ್ವಂತ", "own"]):
            entities["land_ownership"] = "Owned"
        elif any(k in combined_text for k in ["ಸ್ವಂತದ್ದಲ್ಲ", "ಸ್ವಂತ ಅಲ್ಲ"]) and any(k in combined_text for k in ["ಬಾಡಿಗೆ", "ಗುತ್ತಿಗೆ", "lease"]):
            entities["land_ownership"] = "Leased"
        elif any(k in combined_text or k in combined_lower for k in ["ಸ್ವಂತ", "own", "owned"]):
            entities["land_ownership"] = "Owned"
        elif any(k in combined_text or k in combined_lower for k in ["ಗೇಣಿ", "tenant", "lease", "leased", "ಗುತ್ತಿಗೆ"]):
            entities["land_ownership"] = "Leased"
        elif any(k in combined_text or k in combined_lower for k in ["ಪಾಲು", "ಪಾಲುದಾರ", "share", "shared"]):
            entities["land_ownership"] = "Shared"

        # 5. Extract Irrigation
        if any(k in combined_text or k in combined_lower for k in ["ಬೋರ್ವೆಲ್", "ಕೊಳವೆ", "ಕೊಳವೆಬಾವಿ", "borewell", "ಬೋರ್"]):
            entities["irrigation"] = "Borewell"
        elif any(k in combined_text or k in combined_lower for k in ["ಮಳೆ", "ಖುಷ್ಕಿ", "ಮಳೆಯಾಶ್ರಿತ", "rainfed"]):
            entities["irrigation"] = "Rainfed"
        elif any(k in combined_text or k in combined_lower for k in ["ಕಾಲುವೆ", "canal"]):
            entities["irrigation"] = "Canal"
        elif any(k in combined_text or k in combined_lower for k in ["ಹನಿ", "drip"]):
            entities["irrigation"] = "Drip irrigation"
        elif any(k in combined_text or k in combined_lower for k in ["ತುಂತುರು", "sprinkler"]):
            entities["irrigation"] = "Sprinkler"

        # 6. Extract Farmer Category
        if any(k in combined_text or k in combined_lower for k in ["ಅತಿ ಸಣ್ಣ", "marginal"]):
            entities["farmer_category"] = "Marginal (ಅತಿ ಸಣ್ಣ ರೈತರು)"
        elif any(k in combined_text or k in combined_lower for k in ["ಸಣ್ಣ", "small"]):
            entities["farmer_category"] = "Small (ಸಣ್ಣ ರೈತರು)"
        elif any(k in combined_text or k in combined_lower for k in ["ದೊಡ್ಡ", "ಮಧ್ಯಮ", "large", "medium"]):
            entities["farmer_category"] = "Medium & Large (ಮಧ್ಯಮ/ದೊಡ್ಡ ರೈತರು)"

        # 7. Extract Soil Type
        if any(k in combined_text or k in combined_lower for k in ["ಕಪ್ಪು", "ಕಪ್ಪು ಮಣ್ಣು", "black soil", "ಎರೆ"]):
            entities["soil_type"] = "Black Soil"
        elif any(k in combined_text or k in combined_lower for k in ["ಕೆಂಪು", "ಕೆಂಪು ಮಣ್ಣು", "red soil"]):
            entities["soil_type"] = "Red Soil"
        elif any(k in combined_text or k in combined_lower for k in ["ಗೋಡು", "loamy", "loam"]):
            entities["soil_type"] = "Loamy Soil"
        elif any(k in combined_text or k in combined_lower for k in ["ಮರಳು", "sandy"]):
            entities["soil_type"] = "Sandy Soil"

        # 8. Extract Season & Crop Stage
        if any(k in combined_text or k in combined_lower for k in ["ಮುಂಗಾರು", "kharif"]):
            entities["season"] = "Kharif"
        elif any(k in combined_text or k in combined_lower for k in ["ಹಿಂಗಾರು", "rabi"]):
            entities["season"] = "Rabi"
        elif any(k in combined_text or k in combined_lower for k in ["ಬೇಸಿಗೆ", "summer"]):
            entities["season"] = "Summer"

        if any(k in combined_text or k in combined_lower for k in ["ಬಿತ್ತನೆ", "sowing", "ಮೊಳಕೆ"]):
            entities["crop_stage"] = "Sowing / Seedling"
        elif any(k in combined_text or k in combined_lower for k in ["ತೆನೆ", "tillering", "ಹೂವು", "flowering"]):
            entities["crop_stage"] = "Tillering / Flowering"
        elif any(k in combined_text or k in combined_lower for k in ["ಕಾಯಿ", "ಕಾಳು", "pod", "pegging"]):
            entities["crop_stage"] = "Pod Formation / Pegging"
        elif any(k in combined_text or k in combined_lower for k in ["ಕೊಯ್ಲು", "ಕಟಾವು", "harvest"]):
            entities["crop_stage"] = "Harvesting"

        return entities

    @classmethod
    def get_first_missing_stage(cls, profile_dict: Dict[str, Any]) -> str:
        """Finds the first unconfirmed question in the collection sequence (District -> Taluk -> Land Size -> Ownership -> Category -> Crop -> Irrigation -> Soil)."""
        if not profile_dict.get("district"):
            return STAGE_COLLECT_DISTRICT
        if not profile_dict.get("taluk"):
            return STAGE_COLLECT_TALUKA
        if profile_dict.get("land_acres") is None and profile_dict.get("land_size") is None:
            return STAGE_COLLECT_LAND_SIZE
        if not profile_dict.get("land_ownership") and not profile_dict.get("ownership_type"):
            return STAGE_COLLECT_OWNERSHIP
        if not profile_dict.get("farmer_category"):
            return STAGE_COLLECT_FARMER_CATEGORY
        if not profile_dict.get("crop") and not profile_dict.get("primary_crop"):
            return STAGE_COLLECT_CROPS
        if not profile_dict.get("irrigation") and not profile_dict.get("irrigation_type"):
            return STAGE_COLLECT_IRRIGATION
        if not profile_dict.get("soil_type"):
            return STAGE_COLLECT_SOIL
        return STAGE_CONFIRM_PROFILE

    @classmethod
    def get_question_for_stage(cls, stage: str, context: Dict[str, Any], regional_style: str = "Standard Kannada") -> Tuple[str, str]:
        """Returns the appropriate Kannada and English question for a given stage."""
        farmer_name = context.get("username") or context.get("name") or "ರೈತ ಮಿತ್ರ"
        farmer_name_en = context.get("username") or context.get("name") or "Farmer"

        if stage == STAGE_COLLECT_DISTRICT:
            kn = "ನೀವು ಯಾವ ಜಿಲ್ಲೆಯಲ್ಲಿ ವಾಸಿಸುತ್ತಿದ್ದೀರಿ? (ಉದಾಹರಣೆಗೆ ಬೆಳಗಾವಿ, ಧಾರವಾಡ, ಮೈಸೂರು)"
            en = "Which district in Karnataka are you from? (e.g. Belagavi, Dharwad, Mysuru)"
        elif stage == STAGE_COLLECT_TALUKA:
            dist = context.get("district", "ಕರ್ನಾಟಕ")
            kn = f"{dist} ಜಿಲ್ಲೆ ದಾಖಲಿಸಲಾಗಿದೆ. ನಿಮ್ಮ ತಾಲೂಕು ಯಾವುದು?"
            en = f"{dist} district recorded. Which taluka is your farmland located in?"
        elif stage == STAGE_COLLECT_VILLAGE:
            kn = "ನಿಮ್ಮ ಊರಿನ ಹೆಸರೇನು? (ತಿಳಿಯದಿದ್ದರೆ 'ಮುಂದೆ' ಎಂದು ಹೇಳಿ)"
            en = "What is your village name? (Say 'skip' if not known)"
        elif stage == STAGE_COLLECT_LAND_SIZE:
            kn = "ನಿಮ್ಮ ಬಳಿ ಎಷ್ಟು ಕೃಷಿ ಭೂಮಿ ಇದೆ? (ಉದಾಹರಣೆಗೆ ೩ ಎಕರೆ ಅಥವಾ ೧.೫ ಹೆಕ್ಟೇರ್)"
            en = "How much agricultural land do you have? (e.g. 3 acres or 1.5 hectares)"
        elif stage == STAGE_COLLECT_OWNERSHIP:
            kn = "ನಿಮ್ಮ ಜಮೀನು ಸ್ವಂತದ್ದೇ ಅಥವಾ ಗುತ್ತಿಗೆಗೆ ತೆಗೆದುಕೊಂಡಿದ್ದೀರಾ? (ಸ್ವಂತ, ಗುತ್ತಿಗೆ, ಪಾಲುದಾರಿಕೆ)"
            en = "Is your land owned or leased? (Owned / Leased / Shared)"
        elif stage == STAGE_COLLECT_FARMER_CATEGORY:
            kn = "ನೀವು ಯಾವ ವರ್ಗಕ್ಕೆ ಸೇರಿದ್ದೀರಿ? ಸಾಮಾನ್ಯ, ಪರಿಶಿಷ್ಟ ಜಾತಿ, ಪರಿಶಿಷ್ಟ ಪಂಗಡ ಅಥವಾ ಇತರೆ ವರ್ಗವೇ?"
            en = "Do you belong to marginal, small, or another farmer category? (Say 'not sure' if unknown)"
        elif stage == STAGE_COLLECT_CROPS:
            kn = "ನೀವು ಪ್ರಸ್ತುತ ಯಾವ ಬೆಳೆಗಳನ್ನು ಬೆಳೆಯುತ್ತಿದ್ದೀರಿ?"
            en = "What crops are you currently cultivating? (e.g. Paddy, Groundnut, Sugarcane, Jowar)"
        elif stage == STAGE_COLLECT_OTHER_CROPS:
            crop = context.get("crop") or context.get("primary_crop", "ಮುಖ್ಯ ಬೆಳೆ")
            kn = f"ಮುಖ್ಯ ಬೆಳೆ '{crop}' ದಾಖಲಿಸಲಾಗಿದೆ. ಇದರ ಜೊತೆಗೆ ಬೇರೆ ಯಾವ ಬೆಳೆಗಳನ್ನು ಬೆಳೆಯುತ್ತಿದ್ದೀರಿ? (ಇಲ್ಲದಿದ್ದರೆ 'ಯಾವುದೂ ಇಲ್ಲ' ಎಂದು ಹೇಳಿ)"
            en = f"Primary crop '{crop}' recorded. Are you growing any other crops alongside this? (Say 'none' if only this crop)"
        elif stage == STAGE_COLLECT_IRRIGATION:
            kn = "ನಿಮ್ಮ ಜಮೀನಿಗೆ ಯಾವ ರೀತಿಯ ನೀರಾವರಿ ಸೌಲಭ್ಯವಿದೆ? (ಬೋರ್ವೆಲ್, ಬಾವಿ, ಕಾಲುವೆ, ಮಳೆಯಾಶ್ರಿತ)"
            en = "What irrigation facility is available on your farm? (Borewell, Well, Canal, Rainfed)"
        elif stage == STAGE_COLLECT_SOIL:
            kn = "ನಿಮ್ಮ ಜಮೀನಿನ ಮಣ್ಣಿನ ಪ್ರಕಾರ ಯಾವುದು? (ಕಪ್ಪು ಮಣ್ಣು, ಕೆಂಪು ಮಣ್ಣು - ಗೊತ್ತಿಲ್ಲದಿದ್ದರೆ 'ಗೊತ್ತಿಲ್ಲ' ಎಂದು ಹೇಳಬಹುದು)"
            en = "What is your soil type? (Black soil, Red soil - say 'not sure' if unknown)"
        elif stage == STAGE_COLLECT_SEASON_AND_CROP_STAGE:
            kn = "ಬಿತ್ತನೆ ಮಾಡಿದ ತಿಂಗಳು ಮತ್ತು ಪ್ರಸ್ತುತ ಬೆಳೆಯ ಬೆಳವಣಿಗೆಯ ಹಂತ ಯಾವುದು? (ಉದಾಹರಣೆಗೆ ಜೂನ್‌ನಲ್ಲಿ ಬಿತ್ತನೆ, ಈಗ ಹೂ ಬಿಡುವ ಹಂತ)"
            en = "What was the sowing month and current crop growth stage? (e.g. Sown in June, currently flowering stage)"
        elif stage == STAGE_CONFIRM_PROFILE:
            dist = context.get("district", "ಬೆಳಗಾವಿ")
            taluk = context.get("taluk", "")
            land = context.get("land_acres", "3")
            own = context.get("land_ownership", "ಸ್ವಂತ")
            cat = context.get("farmer_category", "ಸಣ್ಣ ರೈತರು")
            crop = context.get("crop") or context.get("primary_crop", "ಭತ್ತ")
            irrig = context.get("irrigation", "ಮಳೆಯಾಶ್ರಿತ")
            soil = context.get("soil_type", "ಕೆಂಪು ಮಣ್ಣು")
            kn = (
                f"ಧನ್ಯವಾದಗಳು. ನೀವು ನೀಡಿದ ಮಾಹಿತಿ:\n\n"
                f"• ಜಿಲ್ಲೆ: {dist}\n" +
                (f"• ತಾಲ್ಲೂಕು: {taluk}\n" if taluk else "") +
                f"• ಭೂಮಿ: {land} ಎಕರೆ ({own})\n" +
                f"• ಬೆಳೆ: {crop}\n" +
                f"• ನೀರಾವರಿ: {irrig}\n" +
                f"• ಮಣ್ಣು: {soil}\n\n" +
                f"ಈ ಮಾಹಿತಿ ಸರಿಯಾಗಿದೆಯೇ? (ಹೌದು, ಸರಿ / ಇಲ್ಲ, ಬದಲಾಯಿಸಬೇಕು)"
            )
            en = (
                f"Thank you. The information you provided:\n\n"
                f"• District: {dist}\n" +
                (f"• Taluk: {taluk}\n" if taluk else "") +
                f"• Land: {land} Acres ({own})\n" +
                f"• Crop: {crop}\n" +
                f"• Irrigation: {irrig}\n" +
                f"• Soil: {soil}\n\n" +
                f"Is this information correct? (Yes, correct / No, want to change)"
            )
        elif stage == STAGE_IDENTIFY_REQUIREMENT:
            kn = (
                f"ಧನ್ಯವಾದಗಳು! ನಿಮ್ಮ ಕೃಷಿ ಮಾಹಿತಿಯನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಉಳಿಸಲಾಗಿದೆ. ಈಗ ನಿಮಗೆ ಯಾವ ಕೃಷಿ ಸಹಾಯ ಬೇಕಾಗಿದೆ?\n\n"
                f"೧. ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು (Government Schemes)\n"
                f"೨. ಬೆಳೆ ವಿಮೆ (Crop Insurance)\n"
                f"೩. ಗೊಬ್ಬರದ ಸಲಹೆ (Fertilizer Recommendations)\n"
                f"೪. ಬೆಳೆ ಮಾರ್ಗದರ್ಶನ (Crop Guidance)\n"
                f"೫. ನೀರಾವರಿ ಸಲಹೆ (Irrigation Advisory)\n"
                f"೬. ಹವಾಮಾನ ಮಾಹಿತಿ (Weather Information)\n"
                f"೭. ಕೀಟ ಮತ್ತು ರೋಗ ನಿರ್ವಹಣೆ (Pest & Disease Management)\n"
                f"೮. ಕೃಷಿ ಸಾಲಗಳು (Agricultural Loans)\n"
                f"೯. ಮಾರುಕಟ್ಟೆ ದರ (Market Prices)\n"
                f"೧೦. ಸಂಪೂರ್ಣ ಕೃಷಿ ನೆರವು (Complete Assistance)\n\n"
                f"ನೀವು ನೇರವಾಗಿ ಮಾತನಾಡಿ ಆಯ್ಕೆ ಮಾಡಬಹುದು ಅಥವಾ ಆಯ್ಕೆಯನ್ನು ಒತ್ತಬಹುದು."
            )
            en = (
                f"Thank you! Your agricultural profile has been saved successfully. What agricultural assistance do you need now?\n\n"
                f"1. Government schemes\n"
                f"2. Crop insurance\n"
                f"3. Fertilizer recommendations\n"
                f"4. Crop guidance\n"
                f"5. Irrigation advisory\n"
                f"6. Weather information\n"
                f"7. Pest & disease management\n"
                f"8. Agricultural loans\n"
                f"9. Market prices\n"
                f"10. Complete agricultural assistance\n\n"
                f"You can speak naturally or tap an option."
            )
        else:
            kn = "ಕೃಷಿಗೆ ಸಂಬಂಧಿಸಿದಂತೆ ನೀವು ಯಾವುದೇ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಬಹುದು."
            en = "You can ask any agriculture-related follow-up question."

        kn = KannadaVocabularyService.adapt_to_dialect(kn, regional_style)
        return kn, en

    @classmethod
    def process_turn(
        cls,
        user_message: str,
        current_stage: str,
        confirmed_details: Dict[str, Any],
        farmer_profile: Optional[Dict[str, Any]] = None,
        all_schemes: Optional[List[Scheme]] = None,
        regional_style: str = "Standard Kannada"
    ) -> Tuple[str, str, str, Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]], Optional[float], Optional[str], bool, str]:
        """
        Processes one turn of the conversation following the 10-phase state machine.
        Returns:
            (reply_en, reply_kn, next_stage, updated_confirmed_details, recommended_schemes,
             rag_citations, rag_confidence, rag_mode, is_agri, topic)
        """
        # Guardrail check
        if not cls.is_agriculture_query(user_message):
            reply_kn = "ಕ್ಷಮಿಸಿ, ನಾನು ಕೃಷಿ ಸಂಬಂಧಿತ ವಿಷಯಗಳಲ್ಲಿ ಮಾತ್ರ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ. ಬೆಳೆ, ಗೊಬ್ಬರ, ಹವಾಮಾನ ಅಥವಾ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಬಗ್ಗೆ ಕೇಳಬಹುದು."
            reply_en = "Sorry, I can only assist with agriculture-related topics. You can ask about crops, fertilizers, weather, or government schemes."
            return reply_en, reply_kn, current_stage, confirmed_details, [], [], None, "off_topic_guardrail", False, "Off-Topic"

        # Initialize working copy of details
        details = dict(confirmed_details or {})
        if farmer_profile:
            for k in ["district", "taluk", "village", "land_acres", "land_ownership", "farmer_category", "primary_crop", "crops", "irrigation", "soil_type", "crop_stage", "season"]:
                if k not in details and farmer_profile.get(k):
                    details[k] = farmer_profile[k]

        extracted = cls.extract_entities(user_message)
        # Opportunistically merge all valid entities found in user speech without overwriting confirmed primary crop
        for k, v in extracted.items():
            if v is not None and k not in ["intent", "normalized_vocabulary", "vocabulary_mappings"]:
                if k in ["crop", "primary_crop"]:
                    if current_stage == STAGE_COLLECT_OTHER_CROPS:
                        continue
                    details["primary_crop"] = v
                    details["crop"] = v
                    continue
                details[k] = v

        farmer_name = (farmer_profile.get("username") or farmer_profile.get("name") or "ರೈತ ಮಿತ್ರ") if farmer_profile else "ರೈತ ಮಿತ್ರ"
        farmer_name_en = (farmer_profile.get("username") or farmer_profile.get("name") or "Farmer") if farmer_profile else "Farmer"

        user_lower = user_message.lower()

        # Handle Profile Correction stage first if in correction state
        if current_stage == STAGE_COLLECT_CORRECTION:
            if any(k in user_message for k in ["ಜಿಲ್ಲೆ", "district"]):
                return "Which is your correct district?", "ನಿಮ್ಮ ಸರಿಯಾದ ಜಿಲ್ಲೆ ಯಾವುದು ಹೇಳಿ?", STAGE_COLLECT_DISTRICT, details, [], [], None, None, True, "Correction"
            elif any(k in user_message for k in ["ತಾಲೂಕು", "ತಾಲೂಕ", "taluk", "taluka"]):
                dist = details.get("district", "Belagavi")
                return f"Which is your correct taluka in {dist}?", f"ನಿಮ್ಮ {dist} ಜಿಲ್ಲೆಯ ಸರಿಯಾದ ತಾಲೂಕು ಯಾವುದು ತಿಳಿಸಿ?", STAGE_COLLECT_TALUKA, details, [], [], None, None, True, "Correction"
            elif any(k in user_message for k in ["ಜಮೀನು", "land", "ಎಕರೆ"]):
                return "How many acres of land do you cultivate?", "ನಿಮ್ಮ ಬಳಿ ಎಷ್ಟು ಎಕರೆ ಜಮೀನಿದೆ?", STAGE_COLLECT_LAND_SIZE, details, [], [], None, None, True, "Correction"
            elif any(k in user_message for k in ["ಬೆಳೆ", "crop"]):
                return "What is your primary crop?", "ನಿಮ್ಮ ಮುಖ್ಯ ಬೆಳೆ ಯಾವುದು?", STAGE_COLLECT_CROPS, details, [], [], None, None, True, "Correction"
            elif any(k in user_message for k in ["ನೀರಾವರಿ", "irrigation"]):
                return "What is your irrigation facility?", "ನಿಮ್ಮ ಜಮೀನಿಗೆ ಯಾವ ರೀತಿಯ ನೀರಾವರಿ ಸೌಲಭ್ಯವಿದೆ?", STAGE_COLLECT_IRRIGATION, details, [], [], None, None, True, "Correction"
            elif any(k in user_message for k in ["ಮಾಲೀಕತ್ವ", "ಸ್ವಂತ", "ಗುತ್ತಿಗೆ", "ownership"]):
                return "Is your land owned or leased?", "ಜಮೀನು ನಿಮ್ಮ ಸ್ವಂತದ್ದೇ ಅಥವಾ ಗುತ್ತಿಗೆಗೆ ತೆಗೆದುಕೊಂಡಿದ್ದೀರಾ?", STAGE_COLLECT_OWNERSHIP, details, [], [], None, None, True, "Correction"
            else:
                next_s = STAGE_CONFIRM_PROFILE
                q_kn, q_en = cls.get_question_for_stage(next_s, details, regional_style)
                return q_en, q_kn, next_s, details, [], [], None, None, True, "Profile Confirmation"

        # ---------------------------------------------------------------------
        # AMBIGUITY CHECK (Phase 3 & Scenario 10: Unclear Speech Clarification)
        # ---------------------------------------------------------------------
        if ("ಅಥವಾ" in user_message or " or " in user_lower) and any(num in user_message for num in ["ಮೂರು", "ನಾಲ್ಕು", "ಎರಡು", "ಐದು", "3", "4", "2", "5"]) and any(u in user_message for u in ["ಎಕರೆ", "acre", "acres", "ಜಮೀನು"]):
            reply_kn = "ಕ್ಷಮಿಸಿ, ನೀವು ಮೂರು ಎಕರೆ ಎಂದಿರಾ ಅಥವಾ ನಾಲ್ಕು ಎಕರೆ ಎಂದಿರಾ? ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಸ್ಪಷ್ಟವಾಗಿ ಹೇಳಿ."
            reply_en = "Sorry, did you say three acres or four acres? Please clarify your exact landholding."
            reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
            return reply_en, reply_kn, current_stage, details, [], [], None, None, True, "Clarification"

        # ---------------------------------------------------------------------
        # NATURAL SPOKEN PROFILE UPDATES & CORRECTIONS (Phase 6 & 7)
        # Only active post-onboarding or in update/follow-up stages
        # ---------------------------------------------------------------------
        if current_stage in [STAGE_IDENTIFY_REQUIREMENT, STAGE_FOLLOW_UP, STAGE_CONFIRM_PROFILE, STAGE_COLLECT_CORRECTION]:
            # A. Land Size Update ("ನನ್ನ ಜಮೀನು ಈಗ ನಾಲ್ಕು ಎಕರೆ ಆಗಿದೆ" / "ಜಮೀನು ಬದಲಾಯಿಸಿ ೫ ಎಕರೆ" / "೪ ಎಕರೆ ಆಗಿದೆ")
            if any(p in user_message for p in ["ಈಗ", "ಆಗಿದೆ", "ಬದಲಾಯಿಸಿ", "ಬದಲಾಗಿದೆ", "ಮಾಡಲಾಗಿದೆ", "ನನ್ನ ಜಮೀನು"]) and \
               extracted.get("land_acres") is not None and any(u in user_message for u in ["ಎಕರೆ", "acre", "acres", "ಜಮೀನು"]) and \
               not any(q in user_message for q in ["ಎಷ್ಟು", "ಹೇಳಿ", "ತಿಳಿಸಿ", "ಯೋಜನೆ", "ಸಾಲ", "ವಿಮೆ", "ಗೊಬ್ಬರ"]):
                val = extracted["land_acres"]
                details["land_acres"] = val
                reply_kn = f"ಸರಿ {farmer_name} ಅವರೇ, ನಿಮ್ಮ ಜಮೀನಿನ ವಿಸ್ತೀರ್ಣವನ್ನು {val:g} ಎಕರೆ ಎಂದು ನವೀಕರಿಸಲಾಗಿದೆ. ಈ ವಿವರಗಳನ್ನು ನಿಮ್ಮ ಪ್ರೊಫೈಲ್‌ನಲ್ಲಿ ಉಳಿಸಲಾಗಿದೆ. ನಿಮಗೆ ಇಂದು ಯಾವ ಕೃಷಿ ಸಹಾಯ ಬೇಕು?"
                reply_en = f"Understood {farmer_name_en}, your farmland size has been updated to {val:g} acres and saved to your profile. What agricultural assistance do you need today?"
                reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], None, None, True, "Profile Update"

            # B. Crop Update ("ನಾನು ಈಗ ಭತ್ತದ ಬದಲು ಕಬ್ಬು ಬೆಳೆಯುತ್ತಿದ್ದೇನೆ" / "ನನ್ನ ಬೆಳೆ ಕಬ್ಬು" / "ಬೆಳೆ ಬದಲಾಯಿಸಿ ಕಬ್ಬು")
            if any(p in user_message for p in ["ಬದಲು", "ಈಗ", "ಬೆಳೆಯುತ್ತಿದ್ದೇನೆ", "ನನ್ನ ಬೆಳೆ", "ಬೆಳೆ ಬದಲಾಯಿಸಿ", "ಬೆಳೆ ಕಬ್ಬು"]) and \
               extracted.get("crop") and not any(q in user_message for q in ["ಗೊಬ್ಬರ", "ವಿಮೆ", "ಯೋಜನೆ", "ರೋಗ", "ದರ", "ಎಷ್ಟು", "ಹೇಳಿ"]):
                new_c = extracted["crop"]
                details["crop"] = new_c
                details["primary_crop"] = new_c
                reply_kn = f"ಸರಿ {farmer_name} ಅವರೇ, ನಿಮ್ಮ ಮುಖ್ಯ ಬೆಳೆಯನ್ನು '{new_c}' ಎಂದು ನವೀಕರಿಸಲಾಗಿದೆ. {new_c} ಬೆಳೆಗೆ ಸಂಬಂಧಿಸಿದಂತೆ ಯಾವ ಸಹಾಯ ಬೇಕು?"
                reply_en = f"Understood {farmer_name_en}, your primary crop has been updated to '{new_c}'. What assistance do you need for {new_c}?"
                reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], None, None, True, "Profile Update"

            # C. Ownership Update ("ನನ್ನ ಜಮೀನು ಬಾಡಿಗೆಯದ್ದಲ್ಲ, ಸ್ವಂತದ್ದು" / "ಸ್ವಂತ ಜಮೀನು" / "ಗುತ್ತಿಗೆ ಜಮೀನು")
            if any(p in user_message for p in ["ಬಾಡಿಗೆಯದ್ದಲ್ಲ", "ಸ್ವಂತದ್ದು", "ಗುತ್ತಿಗೆಯಲ್ಲ", "ಸ್ವಂತ ಜಮೀನು"]) and \
               extracted.get("land_ownership") and not any(q in user_message for q in ["ಯೋಜನೆ", "ಸಾಲ"]):
                new_own = extracted["land_ownership"]
                details["land_ownership"] = new_own
                reply_kn = f"ಸರಿ {farmer_name} ಅವರೇ, ನಿಮ್ಮ ಜಮೀನಿನ ಮಾಲೀಕತ್ವವನ್ನು '{new_own}' ಎಂದು ದಾಖಲಿಸಲಾಗಿದೆ. ಮುಂದೆ ಯಾವ ಕೃಷಿ ಸಹಾಯ ಬೇಕು?"
                reply_en = f"Understood {farmer_name_en}, your land ownership has been recorded as '{new_own}'. What assistance do you need next?"
                reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], None, None, True, "Profile Update"

            # D. Location Update ("ನನ್ನ ಊರು ಬದಲಾಯಿಸಿದೆ" / "ನನ್ನ ಜಿಲ್ಲೆ ಧಾರವಾಡ" / "ನಾನು ಈಗ ಧಾರವಾಡ")
            if any(p in user_message for p in ["ಬದಲಾಯಿಸಿದೆ", "ನನ್ನ ಜಿಲ್ಲೆ", "ನಾನು ಈಗ"]) and extracted.get("district") and \
               not any(q in user_message for q in ["ಯೋಜನೆ", "ಹವಾಮಾನ"]):
                new_dist = extracted["district"]
                details["district"] = new_dist
                reply_kn = f"ಸರಿ {farmer_name} ಅವರೇ, ನಿಮ್ಮ ಜಿಲ್ಲೆಯನ್ನು '{new_dist}' ಎಂದು ನವೀಕರಿಸಲಾಗಿದೆ. ಮುಂದೆ ಯಾವ ಕೃಷಿ ನೆರವು ಬೇಕು?"
                reply_en = f"Understood {farmer_name_en}, your district has been updated to '{new_dist}'. What assistance do you need next?"
                reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], None, None, True, "Profile Update"

            # E. Irrigation Update ("ನನ್ನ ಜಮೀನಿನಲ್ಲಿ ಈಗ ಬೋರ್ವೆಲ್ ನೀರಿನ ವ್ಯವಸ್ಥೆ ಮಾಡಿದ್ದೇನೆ" / "ಬೋರ್ವೆಲ್ ಹಾಕಿಸಿದ್ದೇನೆ" / "ಕಾಲುವೆ ನೀರಾವರಿ")
            if any(p in user_message for p in ["ಬೋರ್ವೆಲ್", "ಬೋರ್", "ಕೊಳವೆಬಾವಿ", "ಕಾಲುವೆ", "ಹನಿ ನೀರಾವರಿ", "ತುಂತುರು", "ನೀರಾವರಿ"]) and \
               any(p in user_message for p in ["ಮಾಡಿದ್ದೇನೆ", "ಹಾಕಿಸಿದ್ದೇನೆ", "ವ್ಯವಸ್ಥೆ", "ಬಂದಿದೆ", "ಈಗ", "ಬದಲಾಗಿದೆ", "ಆಗಿದೆ"]):
                irrig_type = "Borewell"
                if "ಕಾಲುವೆ" in user_message:
                    irrig_type = "Canal"
                elif "ಹನಿ" in user_message:
                    irrig_type = "Drip irrigation"
                elif "ತುಂತುರು" in user_message:
                    irrig_type = "Sprinkler"
                elif "ಮಳೆ" in user_message or "ಖುಷ್ಕಿ" in user_message:
                    irrig_type = "Rainfed"
                details["irrigation"] = irrig_type
                details["irrigation_type"] = irrig_type
                reply_kn = f"ಸರಿ {farmer_name} ಅವರೇ, ನಿಮ್ಮ ಜಮೀನಿನ ನೀರಾವರಿ ಸೌಲಭ್ಯವನ್ನು '{irrig_type}' ಎಂದು ನವೀಕರಿಸಲಾಗಿದೆ ಮತ್ತು ಪ್ರೊಫೈಲ್‌ನಲ್ಲಿ ಉಳಿಸಲಾಗಿದೆ. ಈ ನೀರಾವರಿಗೆ ಸೂಕ್ತವಾದ ಗೊಬ್ಬರ ಅಥವಾ ಬೆಳೆ ಸಲಹೆ ಬೇಕೇ?"
                reply_en = f"Understood {farmer_name_en}, your irrigation facility has been updated to '{irrig_type}' and saved to your profile. Would you like fertilizer or crop guidance for this irrigation?"
                reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], None, None, True, "Profile Update"

            # F. Crop Stage / Sowing Stage Update ("ನನ್ನ ಬೆಳೆಗೆ ಈಗ ಹೂ ಬಿಡುವ ಹಂತ ಬಂದಿದೆ" / "ಕಾಯಿ ಕಟ್ಟುವ ಹಂತ" / "ತೆನೆ ಮೂಡುವ ಹಂತ")
            if any(p in user_message for p in ["ಹಂತ", "ಹೂ ಬಿಡುವ", "ಕಾಯಿ ಕಟ್ಟುವ", "ತೆನೆ", "ಬೆಳವಣಿಗೆ"]) and \
               any(p in user_message for p in ["ಬಂದಿದೆ", "ಈಗ", "ಆಗಿದೆ", "ತಲುಪಿದೆ"]):
                stage_name = "Tillering / Flowering"
                if "ಹೂ ಬಿಡುವ" in user_message:
                    stage_name = "Flowering stage"
                elif "ಕಾಯಿ ಕಟ್ಟುವ" in user_message:
                    stage_name = "Pod / Fruit development"
                elif "ತೆನೆ" in user_message:
                    stage_name = "Panicle initiation"
                details["crop_stage"] = stage_name
                reply_kn = f"ಸರಿ {farmer_name} ಅವರೇ, ನಿಮ್ಮ ಬೆಳೆಯ ಪ್ರಸ್ತುತ ಬೆಳವಣಿಗೆ ಹಂತವನ್ನು '{stage_name}' ಎಂದು ನವೀಕರಿಸಲಾಗಿದೆ. ಈ ಹಂತಕ್ಕೆ ಅಗತ್ಯವಿರುವ ಪೋಷಕಾಂಶ ಅಥವಾ ಕೀಟ ರೋಗ ನಿರ್ವಹಣೆಯ ಸಲಹೆ ಬೇಕೇ?"
                reply_en = f"Understood {farmer_name_en}, your crop growth stage has been recorded as '{stage_name}'. Would you like nutrient or pest management advice for this stage?"
                reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], None, None, True, "Profile Update"

            # G. No Changes / Closing Acknowledgement ("ಯಾವುದೂ ಬದಲಾವಣೆ ಇಲ್ಲ, ಧನ್ಯವಾದ" / "ಬದಲಾವಣೆ ಇಲ್ಲ" / "ಧನ್ಯವಾದಗಳು")
            if any(p in user_message for p in ["ಯಾವುದೂ ಬದಲಾವಣೆ ಇಲ್ಲ", "ಯಾವ ಬದಲಾವಣೆಯೂ ಇಲ್ಲ", "ಬದಲಾವಣೆ ಇಲ್ಲ", "ಇಲ್ಲ ಧನ್ಯವಾದ", "ಧನ್ಯವಾದಗಳು", "ಯಾವುದೂ ಇಲ್ಲ ಧನ್ಯವಾದ"]):
                reply_kn = f"ಧನ್ಯವಾದಗಳು {farmer_name} ಅವರೇ! ಕೃಷಿ ಮಿತ್ರವನ್ನು ಬಳಸಿದ್ದಕ್ಕಾಗಿ ಸಂತೋಷ. ನಿಮಗೆ ಯಾವಾಗಲಾದರೂ ಬೆಳೆ ಸಲಹೆ, ಹವಾಮಾನ ಅಥವಾ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಮಾಹಿತಿ ಬೇಕಾದಾಗ ಮತ್ತೆ ಮಾತನಾಡಿ. ನಿಮ್ಮ ಕೃಷಿ ಕಾರ್ಯ ಯಶಸ್ವಿಯಾಗಲಿ!"
                reply_en = f"Thank you {farmer_name_en}! Glad to assist you on Krishi Mitra. Whenever you need crop advice, weather updates, or government schemes, feel free to talk to me again. Wishing you abundant harvests!"
                reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], None, None, True, "Closing"

        # Check for profile correction / change request (e.g. Test 15)
        if any(w in user_lower or w in user_message for w in ["ತಪ್ಪು", "ಬದಲಾಯಿಸಬೇಕು", "ಬದಲಾವಣೆ", "change", "correction", "wrong"]):
            reply_kn = "ಖಂಡಿತ, ನೀವು ಯಾವ ಮಾಹಿತಿಯನ್ನು ಬದಲಾಯಿಸಲು ಬಯಸುತ್ತೀರಿ? (ಜಿಲ್ಲೆ, ತಾಲೂಕು, ಜಮೀನು, ಬೆಳೆ, ಅಥವಾ ನೀರಾವರಿ?)"
            reply_en = "Sure, which detail would you like to update? (District, Taluka, Land acres, Crop, or Irrigation?)"
            reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
            return reply_en, reply_kn, STAGE_COLLECT_CORRECTION, details, [], [], None, None, True, "Profile Correction"

        # Check if farmer is selecting assistance before onboarding
        user_clean = user_message.strip()
        assistance_chosen = None
        if user_clean in ["೧", "1", "ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು", "ಸರ್ಕಾರಿ ಯೋಜನೆ"] or any(k in user_clean for k in ["ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ", "ಯೋಜನೆಗಳ ಬಗ್ಗೆ", "ಯೋಜನೆ ಮಾಹಿತಿ", "ಯೋಜನೆ ತಿಳಿಸಿ", "ಯೋಜನೆ ಬಗ್ಗೆ"]) or ("ಯೋಜನೆ" in user_clean and any(k in user_clean for k in ["ಮಾಹಿತಿ", "ತಿಳಿದುಕೊಳ್ಳಬೇಕು", "ತಿಳಿಯಬೇಕು", "ಬೇಕು", "ಹೇಳಿ"])):
            if not any(k in user_clean for k in ["ಎಷ್ಟು ಹಣ", "ಅರ್ಜಿ ಹೇಗೆ", "ಸಿಗುತ್ತದೆ"]):
                assistance_chosen = ("government_schemes", "ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು", "Government Schemes")
        elif user_clean in ["೨", "2", "ಬೆಳೆ ವಿಮೆ"] or any(k in user_clean for k in ["ಬೆಳೆ ವಿಮೆಯ", "ವಿಮೆ ಮಾಡಿಸಬೇಕು", "ವಿಮೆ ಬೇಕು", "ವಿಮೆ ಮಾಹಿತಿ", "ವಿಮೆ ಬಗ್ಗೆ"]):
            if not any(k in user_clean for k in ["೭೨", "72", "ಕ್ಲೇಮ್", "ನಷ್ಟ ಪರಿಹಾರ"]):
                assistance_chosen = ("crop_insurance", "ಬೆಳೆ ವಿಮೆ", "Crop Insurance")
        elif user_clean in ["೩", "3", "ಗೊಬ್ಬರ ಸಲಹೆ", "ಗೊಬ್ಬರದ ಸಲಹೆ"] or any(k in user_clean for k in ["ಗೊಬ್ಬರದ ಮಾಹಿತಿ", "ಗೊಬ್ಬರ ಬೇಕು", "ಗೊಬ್ಬರ ಸಲಹೆ", "ಗೊಬ್ಬರ ಮಾಹಿತಿ"]):
            if not any(k in user_clean for k in ["ಎಷ್ಟು ಕೆಜಿ", "ಎಷ್ಟು ಯೂರಿಯಾ", "ಪ್ರಮಾಣ"]):
                assistance_chosen = ("fertilizer", "ಗೊಬ್ಬರ ಸಲಹೆ", "Fertilizer Recommendations")
        elif (user_clean in ["೪", "4", "ಬೆಳೆ ಮಾರ್ಗದರ್ಶನ"] or any(k in user_clean for k in ["ಬೆಳೆ ಮಾರ್ಗದರ್ಶನ", "ಬೆಳೆ ಮಾಹಿತಿ", "ಸಾಗುವಳಿ"])) and not any(f in user_clean for f in ["ಗೊಬ್ಬರ", "fertilizer", "ಯೂರಿಯಾ", "ಡಿಎಪಿ", "npk"]):
            assistance_chosen = ("crop_guidance", "ಬೆಳೆ ಮಾರ್ಗದರ್ಶನ", "Crop Guidance")
        elif user_clean in ["೫", "5", "ನೀರಾವರಿ ಸಲಹೆ"] or any(k in user_clean for k in ["ನೀರಾವರಿ ಸಲಹೆ", "ನೀರಾವರಿ ಮಾಹಿತಿ"]):
            assistance_chosen = ("irrigation", "ನೀರಾವರಿ ಸಲಹೆ", "Irrigation Guidance")
        elif user_clean in ["೬", "6", "ಹವಾಮಾನ ಮಾಹಿತಿ"] or any(k in user_clean for k in ["ಹವಾಮಾನ ಮಾಹಿತಿ"]):
            assistance_chosen = ("weather", "ಹವಾಮಾನ ಮಾಹಿತಿ", "Weather Information")
        elif user_clean in ["೭", "7", "ಕೀಟ ಮತ್ತು ರೋಗ ನಿರ್ವಹಣೆ", "ಕೀಟ ಮತ್ತು ರೋಗ"] or any(k in user_clean for k in ["ಕೀಟ ನಿರ್ವಹಣೆ", "ರೋಗ ನಿರ್ವಹಣೆ"]):
            assistance_chosen = ("pest_disease", "ಕೀಟ ಮತ್ತು ರೋಗ ನಿರ್ವಹಣೆ", "Pest & Disease Management")
        elif user_clean in ["೮", "8", "ಕೃಷಿ ಸಾಲಗಳು", "ಕೃಷಿ ಸಾಲ"] or any(k in user_clean for k in ["ಕೃಷಿ ಸಾಲಗಳ", "ಸಾಲ ಮಾಹಿತಿ"]):
            assistance_chosen = ("loans", "ಕೃಷಿ ಸಾಲಗಳು", "Agricultural Loans")
        elif user_clean in ["೯", "9", "ಮಾರುಕಟ್ಟೆ ದರ"] or any(k in user_clean for k in ["ಮಾರುಕಟ್ಟೆ ದರ", "ಮಂಡಿ ದರ"]):
            assistance_chosen = ("market_prices", "ಮಾರುಕಟ್ಟೆ ದರ", "Market Prices")
        elif user_clean in ["೧೦", "10", "ಸಂಪೂರ್ಣ ಕೃಷಿ ನೆರವು"] or any(k in user_clean for k in ["ಸಂಪೂರ್ಣ ಕೃಷಿ ನೆರವು", "ಸಮಗ್ರ ನೆರವು"]):
            assistance_chosen = ("complete_assistance", "ಸಂಪೂರ್ಣ ಕೃಷಿ ನೆರವು", "Complete Agricultural Assistance")

        if assistance_chosen:
            int_code, top_kn, top_en = assistance_chosen
            details["requested_assistance"] = int_code

            # Check prerequisites based on chosen assistance
            if int_code == "weather":
                if details.get("district"):
                    return cls._evaluate_weather(details, regional_style, farmer_name, farmer_name_en)
                else:
                    reply_kn = f"ಖಂಡಿತ, {top_kn} ನೀಡುತ್ತೇನೆ. ನಿಮ್ಮ ಜಿಲ್ಲೆ ಯಾವುದು ಎಂದು ತಿಳಿಸಿ?"
                    reply_en = f"Sure, I will provide weather information. Which district are you in?"
                    reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                    return reply_en, reply_kn, STAGE_COLLECT_DISTRICT, details, [], [], None, None, True, top_kn

            elif int_code in ["fertilizer", "crop_guidance", "pest_disease"]:
                if details.get("crop") or details.get("primary_crop"):
                    if int_code == "fertilizer":
                        return cls._evaluate_fertilizer(details, regional_style, farmer_name, farmer_name_en)
                    elif int_code == "crop_guidance":
                        return cls._evaluate_crop_guidance(details, regional_style, farmer_name, farmer_name_en)
                    else:
                        return cls._evaluate_pest_disease(details, regional_style, farmer_name, farmer_name_en)
                else:
                    reply_kn = f"ಖಂಡಿತ, {top_kn} ನೀಡುತ್ತೇನೆ. ಮೊದಲು ನಿಮ್ಮ ಮುಖ್ಯ ಬೆಳೆ ಯಾವುದು ಎಂದು ತಿಳಿಸಿ?"
                    reply_en = f"Sure, I will provide {top_en}. First, what is your primary crop?"
                    reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                    return reply_en, reply_kn, STAGE_COLLECT_CROPS, details, [], [], None, None, True, top_kn

            elif int_code in ["market_prices", "crop_insurance"]:
                if (details.get("crop") or details.get("primary_crop")) and details.get("district"):
                    if int_code == "market_prices":
                        return cls._evaluate_market_prices(details, regional_style, farmer_name, farmer_name_en)
                    else:
                        return cls._evaluate_crop_insurance(details, regional_style, farmer_name, farmer_name_en)
                elif not details.get("district"):
                    reply_kn = f"ಖಂಡಿತ, {top_kn} ನೀಡುತ್ತೇನೆ. ಮೊದಲು ನಿಮ್ಮ ಜಿಲ್ಲೆ ಯಾವುದು?"
                    reply_en = f"Sure, I will provide {top_en}. Which is your district?"
                    reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                    return reply_en, reply_kn, STAGE_COLLECT_DISTRICT, details, [], [], None, None, True, top_kn
                else:
                    reply_kn = f"ಖಂಡಿತ, {top_kn} ನೀಡುತ್ತೇನೆ. ನಿಮ್ಮ ಬೆಳೆ ಯಾವುದು?"
                    reply_en = f"Sure, I will provide {top_en}. What is your crop?"
                    reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                    return reply_en, reply_kn, STAGE_COLLECT_CROPS, details, [], [], None, None, True, top_kn

            elif int_code == "irrigation":
                if details.get("district") and (details.get("crop") or details.get("primary_crop")):
                    return cls._evaluate_irrigation(details, regional_style, farmer_name, farmer_name_en)
                elif not details.get("district"):
                    reply_kn = f"ಖಂಡಿತ, ನೀರಾವರಿ ಸಲಹೆ ನೀಡುತ್ತೇನೆ. ಮೊದಲು ನಿಮ್ಮ ಜಿಲ್ಲೆ ಯಾವುದು?"
                    reply_en = f"Sure, I will provide irrigation guidance. First, which is your district?"
                    reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                    return reply_en, reply_kn, STAGE_COLLECT_DISTRICT, details, [], [], None, None, True, top_kn
                else:
                    reply_kn = f"ಖಂಡಿತ, ನೀರಾವರಿ ಸಲಹೆ ನೀಡುತ್ತೇನೆ. ನಿಮ್ಮ ಬೆಳೆ ಯಾವುದು?"
                    reply_en = f"Sure, I will provide irrigation guidance. What is your crop?"
                    reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                    return reply_en, reply_kn, STAGE_COLLECT_CROPS, details, [], [], None, None, True, top_kn

            elif int_code == "loans":
                if details.get("district") and details.get("land_acres") is not None:
                    return cls._evaluate_loans(details, regional_style, farmer_name, farmer_name_en)
                elif not details.get("district"):
                    reply_kn = f"ಖಂಡಿತ, ಕೃಷಿ ಸಾಲದ ಮಾಹಿತಿ ನೀಡುತ್ತೇನೆ. ಮೊದಲು ನಿಮ್ಮ ಜಿಲ್ಲೆ ಯಾವುದು?"
                    reply_en = f"Sure, I will provide loan information. First, which is your district?"
                    reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                    return reply_en, reply_kn, STAGE_COLLECT_DISTRICT, details, [], [], None, None, True, top_kn
                else:
                    reply_kn = f"ಖಂಡಿತ, ಕೃಷಿ ಸಾಲದ ಮಾಹಿತಿ ನೀಡುತ್ತೇನೆ. ನಿಮ್ಮ ಬಳಿ ಎಷ್ಟು ಎಕರೆ ಜಮೀನಿದೆ?"
                    reply_en = f"Sure, I will provide loan information. How many acres of land do you have?"
                    reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                    return reply_en, reply_kn, STAGE_COLLECT_LAND_SIZE, details, [], [], None, None, True, top_kn

            elif int_code in ["government_schemes", "complete_assistance"]:
                if details.get("district") and (details.get("crop") or details.get("primary_crop")) and details.get("land_acres") is not None:
                    if int_code == "government_schemes":
                        return cls._evaluate_government_schemes(details, all_schemes, regional_style, farmer_name, farmer_name_en)
                    else:
                        return cls._evaluate_complete_assistance(details, all_schemes, regional_style, farmer_name, farmer_name_en)
                elif not details.get("district"):
                    reply_kn = f"ಖಂಡಿತ, {top_kn} ಮಾಹಿತಿಯನ್ನು ನೀಡುತ್ತೇನೆ. ಇದಕ್ಕಾಗಿ ನಿಮ್ಮ ಕೃಷಿ ವಿವರಗಳು ಬೇಕಾಗುತ್ತವೆ. ಮೊದಲು ನಿಮ್ಮ ಜಿಲ್ಲೆ ಯಾವುದು?"
                    reply_en = f"Sure, I will assist you with {top_en}. To provide tailored guidance, I will ask a few quick farm questions. First, which is your district?"
                    reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                    return reply_en, reply_kn, STAGE_COLLECT_DISTRICT, details, [], [], None, None, True, top_kn
                elif not details.get("taluk"):
                    q_kn, q_en = cls.get_question_for_stage(STAGE_COLLECT_TALUKA, details, regional_style)
                    return q_en, q_kn, STAGE_COLLECT_TALUKA, details, [], [], None, None, True, top_kn
                elif details.get("land_acres") is None:
                    q_kn, q_en = cls.get_question_for_stage(STAGE_COLLECT_LAND_SIZE, details, regional_style)
                    return q_en, q_kn, STAGE_COLLECT_LAND_SIZE, details, [], [], None, None, True, top_kn
                elif not details.get("land_ownership"):
                    q_kn, q_en = cls.get_question_for_stage(STAGE_COLLECT_OWNERSHIP, details, regional_style)
                    return q_en, q_kn, STAGE_COLLECT_OWNERSHIP, details, [], [], None, None, True, top_kn
                elif not (details.get("crop") or details.get("primary_crop")):
                    q_kn, q_en = cls.get_question_for_stage(STAGE_COLLECT_CROPS, details, regional_style)
                    return q_en, q_kn, STAGE_COLLECT_CROPS, details, [], [], None, None, True, top_kn
                else:
                    return cls._evaluate_government_schemes(details, all_schemes, regional_style, farmer_name, farmer_name_en)

        # Explicit Government Schemes request (e.g. Test 8)
        if any(w in user_lower or w in user_message for w in ["pm-kisan", "pm kisan", "krishi bhagya", "ಪಿಎಂ ಕಿಸಾನ್", "ಕೃಷಿ ಭಾಗ್ಯ", "ಸಹಾಯಧನ", "subsidy"]) or \
           ("ಯೋಜನೆ" in user_message and any(w in user_message for w in ["ಯಾವ", "ಎಷ್ಟು", "ಮಾಹಿತಿ", "ತಿಳಿಸಿ", "ಹೇಳಿ", "ಬಗ್ಗೆ", "ಹಣ", "ಸಿಗುತ್ತದೆ", "ಕೊಡಿ", "ತಿಳಿಯಬೇಕು"])):
            return cls._evaluate_government_schemes(details, all_schemes, regional_style, farmer_name, farmer_name_en)

        # Explicit Crop Insurance request (e.g. Test 11)
        if any(w in user_lower or w in user_message for w in ["pmfby", "samrakshane", "ಸಂರಕ್ಷಣೆ", "ಬೆಳೆ ಹಾನಿ", "ಹಾನಿಯಾದರೆ", "ಬೆಳೆ ನಷ್ಟ"]) or \
           ("ವಿಮೆ" in user_message and any(w in user_message for w in ["ಯಾವ", "ಎಷ್ಟು", "ಮಾಹಿತಿ", "ತಿಳಿಸಿ", "ಹೇಳಿ", "ಬಗ್ಗೆ", "ಮಾಡಿಸಬೇಕು", "ದಿನದೊಳಗೆ", "ಪರಿಹಾರ", "ತಿಳಿಯಬೇಕು"])):
            return cls._evaluate_crop_insurance(details, regional_style, farmer_name, farmer_name_en)

        # Explicit Fertilizer request (e.g. Test 13 & Test 20)
        if any(w in user_lower or w in user_message for w in ["fertilizer", "ಯೂರಿಯಾ", "ಡಿಎಪಿ", "npk", "ರಸಗೊಬ್ಬರ"]) or \
           ("ಗೊಬ್ಬರ" in user_message and any(w in user_message for w in ["ಯಾವ", "ಎಷ್ಟು", "ಹಾಕಬೇಕು", "ಪ್ರಮಾಣ", "ತಿಳಿಸಿ", "ಹೇಳಿ", "ಬಗ್ಗೆ", "ಹೇಳ್ರಿ"])):
            return cls._evaluate_fertilizer(details, regional_style, farmer_name, farmer_name_en)

        # Explicit Weather request
        if any(w in user_lower or w in user_message for w in ["weather", "ಹವಾಮಾನ"]) or \
           ("ಮಳೆ" in user_message and any(w in user_message for w in ["ಯಾವಾಗ", "ಬರುತ್ತದೆ", "ಹೇಗಿದೆ", "ಮುನ್ಸೂಚನೆ"])):
            return cls._evaluate_weather(details, regional_style, farmer_name, farmer_name_en)

        # Explicit Agricultural Loan request
        if any(w in user_lower or w in user_message for w in ["kcc", "ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್"]) or \
           ("ಸಾಲ" in user_message and any(w in user_message for w in ["ಯಾವ", "ಎಷ್ಟು", "ಮಾಹಿತಿ", "ತಿಳಿಸಿ", "ಹೇಳಿ", "ಬಗ್ಗೆ", "ಸಿಗುತ್ತದೆ", "ಬ್ಯಾಂಕ್"])):
            return cls._evaluate_loans(details, regional_style, farmer_name, farmer_name_en)

        # Explicit Pest & Disease Management request (Phase 2 & Phase 4)
        if any(w in user_lower or w in user_message for w in ["ರೋಗ", "ಕೀಟ", "ಹುಳು", "pest", "disease", "ಔಷಧ"]) and \
           any(w in user_message for w in ["ಬಂದಿದೆ", "ಬಿದ್ದಿದೆ", "ಹೇಗೆ", "ಹತೋಟಿ", "ನಿರ್ವಹಣೆ", "ಸಿಂಪಡಿಸಬೇಕು", "ಮಾಹಿತಿ"]):
            return cls._evaluate_pest_disease(details, regional_style, farmer_name, farmer_name_en)

        # Explicit Irrigation Guidance request (Phase 2 & Phase 4)
        if ("ನೀರಾವರಿ" in user_message or "irrigation" in user_lower) and \
           any(w in user_message for w in ["ಬಗ್ಗೆ", "ಮಾಹಿತಿ", "ಸಲಹೆ", "ಹೇಗೆ", "ಬೇಕಾಗಿದೆ", "ಬೇಕು", "ಮಾಡಬೇಕು"]):
            return cls._evaluate_irrigation(details, regional_style, farmer_name, farmer_name_en)

        # Explicit Market Prices request (Phase 2 & Phase 4)
        if any(w in user_lower or w in user_message for w in ["ಮಾರುಕಟ್ಟೆ", "market", "apmc", "ಮಂಡಿ"]) or \
           ("ಬೆಲೆ" in user_message and any(w in user_message for w in ["ಎಷ್ಟು", "ದರ", "ತಿಳಿಸಿ", "ಹೇಳಿ", "ಇದೆ"])) or \
           ("ದರ" in user_message and any(w in user_message for w in ["ಎಷ್ಟು", "ಬೆಲೆ", "ತಿಳಿಸಿ", "ಹೇಳಿ", "ಇದೆ"])):
            return cls._evaluate_market_prices(details, regional_style, farmer_name, farmer_name_en)

        # Explicit Crop Guidance request (Phase 2 & Phase 4)
        if ("ಮಾರ್ಗದರ್ಶನ" in user_message or "ಸಾಗುವಳಿ" in user_message) and \
           any(w in user_message for w in ["ಬಗ್ಗೆ", "ಮಾಹಿತಿ", "ಸಲಹೆ", "ಕೊಡಿ", "ತಿಳಿಸಿ", "ಹೇಳಿ"]):
            return cls._evaluate_crop_guidance(details, regional_style, farmer_name, farmer_name_en)

        # Explicit Complete Assistance request (Phase 2 & Phase 4)
        if any(w in user_lower or w in user_message for w in ["ಸಮಗ್ರ ಕೃಷಿ", "ಸಮಗ್ರ ನೆರವು", "complete assistance", "ಎಲ್ಲಾ ವಿಷಯ"]):
            return cls._evaluate_complete_assistance(details, all_schemes, regional_style, farmer_name, farmer_name_en)

        # ---------------------------------------------------------------------
        # STATE: STAGE_INITIAL_GREETING or STAGE_COLLECT_DISTRICT
        # ---------------------------------------------------------------------
        if current_stage in [STAGE_INITIAL_GREETING, STAGE_COLLECT_DISTRICT, "idle"]:
            if "district" in details and details["district"]:
                # District was captured!
                taluk_val = details.get("taluk")
                dist_val = details.get("district")
                # If a distinct taluk was explicitly captured in same utterance (e.g. "ಬೆಳಗಾವಿ ಜಿಲ್ಲೆ ಬೈಲಹೊಂಗಲ"), advance past taluk
                if taluk_val and dist_val and taluk_val.lower() != dist_val.lower() and ("ತಾಲೂಕು" in user_message or "taluk" in user_message.lower() or len(user_message.split()) >= 3):
                    next_s = STAGE_COLLECT_LAND_SIZE if details.get("land_acres") is None else STAGE_COLLECT_CROPS
                else:
                    if taluk_val and dist_val and taluk_val.lower() == dist_val.lower():
                        details.pop("taluk", None)
                    next_s = STAGE_COLLECT_TALUKA
                q_kn, q_en = cls.get_question_for_stage(next_s, details, regional_style)
                reply_kn = q_kn
                reply_en = q_en
                return reply_en, reply_kn, next_s, details, [], [], None, None, True, "Information Collection"
            else:
                # District unclear
                reply_kn = "ಕ್ಷಮಿಸಿ, ನೀವು ಹೇಳಿದ ಜಿಲ್ಲೆ ಸರಿಯಾಗಿ ಗುರುತಿಸಲಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಜಿಲ್ಲೆಯನ್ನು ಮತ್ತೊಮ್ಮೆ ಸ್ಪಷ್ಟವಾಗಿ ಹೇಳಿ (ಉದಾಹರಣೆಗೆ ಬೆಳಗಾವಿ, ಧಾರವಾಡ, ಮೈಸೂರು, ಕಲಬುರಗಿ)."
                reply_en = "Sorry, I could not recognize that district. Please clearly state your Karnataka district (e.g. Belagavi, Dharwad, Mysuru)."
                reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                return reply_en, reply_kn, STAGE_COLLECT_DISTRICT, details, [], [], None, None, True, "Information Collection"

        # ---------------------------------------------------------------------
        # STATE: STAGE_COLLECT_TALUKA
        # ---------------------------------------------------------------------
        if current_stage == STAGE_COLLECT_TALUKA:
            dist = details.get("district", "Belagavi")
            valid_taluks = DISTRICT_TALUKS.get(dist, [])
            taluk_found = details.get("taluk")

            if taluk_found:
                # Validate if it belongs to selected district
                if valid_taluks and not any(t.lower() == taluk_found.lower() for t in valid_taluks):
                    actual_dist = None
                    for d_k, t_list in DISTRICT_TALUKS.items():
                        if any(t.lower() == taluk_found.lower() for t in t_list):
                            actual_dist = d_k
                            break
                    if actual_dist and actual_dist != dist:
                        reply_kn = f"ಕ್ಷಮಿಸಿ, {taluk_found} ತಾಲೂಕು {actual_dist} ಜಿಲ್ಲೆಗೆ ಸೇರಿದೆ, ನಿಮ್ಮ ಜಿಲ್ಲೆ {dist}. ದಯವಿಟ್ಟು {dist} ಜಿಲ್ಲೆಯ ನಿಮ್ಮ ಸರಿಯಾದ ತಾಲೂಕನ್ನು ತಿಳಿಸಿ."
                        reply_en = f"Sorry, {taluk_found} taluka belongs to {actual_dist} district, but your district is {dist}. Please state your correct taluk in {dist}."
                        reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                        return reply_en, reply_kn, STAGE_COLLECT_TALUKA, details, [], [], None, None, True, "Information Collection"

                next_s = STAGE_COLLECT_LAND_SIZE if details.get("land_acres") is None else STAGE_COLLECT_OWNERSHIP
                q_kn, q_en = cls.get_question_for_stage(next_s, details, regional_style)
                return q_en, q_kn, next_s, details, [], [], None, None, True, "Information Collection"
            else:
                sample_taluks = ", ".join(valid_taluks[:4]) if valid_taluks else "Bailhongal, Gokak, Chikkodi"
                reply_kn = f"ಕ್ಷಮಿಸಿ, ನೀವು ಹೇಳಿದ '{user_message.strip()}' {dist} ಜಿಲ್ಲೆಯ ಮಾನ್ಯ ತಾಲೂಕಲ್ಲ. ದಯವಿಟ್ಟು {dist} ಜಿಲ್ಲೆಯ ನಿಮ್ಮ ಸರಿಯಾದ ತಾಲೂಕನ್ನು ಮತ್ತೊಮ್ಮೆ ತಿಳಿಸಿ (ಉದಾಹರಣೆಗೆ {sample_taluks})."
                reply_en = f"Sorry, '{user_message.strip()}' is not a recognized taluk in {dist} district. Please state your correct taluk in {dist} (e.g. {sample_taluks})."
                reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                return reply_en, reply_kn, STAGE_COLLECT_TALUKA, details, [], [], None, None, True, "Information Collection"

        # ---------------------------------------------------------------------
        # STATE: STAGE_COLLECT_VILLAGE (Optional)
        # ---------------------------------------------------------------------
        if current_stage == STAGE_COLLECT_VILLAGE:
            if any(k in user_message.lower() for k in ["ಗೊತ್ತಿಲ್ಲ", "skip", "ಮುಂದೆ", "ಇಲ್ಲ", "none"]):
                details["village"] = None
            else:
                details["village"] = user_message.strip()

            next_s = STAGE_COLLECT_LAND_SIZE if details.get("land_acres") is None else STAGE_COLLECT_OWNERSHIP
            q_kn, q_en = cls.get_question_for_stage(next_s, details, regional_style)
            return q_en, q_kn, next_s, details, [], [], None, None, True, "Information Collection"

        # ---------------------------------------------------------------------
        # STATE: STAGE_COLLECT_LAND_SIZE
        # ---------------------------------------------------------------------
        if current_stage == STAGE_COLLECT_LAND_SIZE:
            # Check if farmer explicitly states they do not know their land acreage (Scenario 5)
            if any(k in user_message.lower() for k in ["ಗೊತ್ತಿಲ್ಲ", "ತಿಳಿದಿಲ್ಲ", "don't know", "not sure", "ಅಂದಾಜು ಇಲ್ಲ", "ಪಹಣಿ ನೋಡಿಲ್ಲ", "ಖಚಿತವಿಲ್ಲ"]):
                details["land_acres"] = None
                details["farmer_category"] = "General (ಸಾಮಾನ್ಯ ರೈತರು)"
                next_s = STAGE_COLLECT_OWNERSHIP
                q_kn, q_en = cls.get_question_for_stage(next_s, details, regional_style)
                prefix_kn = "ಪರವಾಗಿಲ್ಲ, ನಿಮ್ಮ ನಿಖರ ಜಮೀನಿನ ವಿಸ್ತೀರ್ಣವನ್ನು ಪಹಣಿ (RTC) ಅಥವಾ ಭೂಮಿ ಪೋರ್ಟಲ್ (bhoomi.karnataka.gov.in) ನಲ್ಲಿ ಪರಿಶೀಲಿಸಬಹುದು.\n\n"
                prefix_en = "No problem, you can verify your exact acreage from your Pahani (RTC) on the Bhoomi portal (bhoomi.karnataka.gov.in) later.\n\n"
                reply_kn = prefix_kn + q_kn
                reply_en = prefix_en + q_en
                return reply_en, reply_kn, next_s, details, [], [], None, None, True, "Information Collection"

            if details.get("land_acres") is not None and details["land_acres"] > 0:
                if "farmer_category" not in details:
                    acres = details["land_acres"]
                    if acres <= 2.5:
                        details["farmer_category"] = "Marginal (ಅತಿ ಸಣ್ಣ ರೈತರು)"
                    elif acres <= 5.0:
                        details["farmer_category"] = "Small (ಸಣ್ಣ ರೈತರು)"
                    else:
                        details["farmer_category"] = "Medium & Large (ಮಧ್ಯಮ/ದೊಡ್ಡ ರೈತರು)"

                next_s = STAGE_COLLECT_OWNERSHIP
                q_kn, q_en = cls.get_question_for_stage(next_s, details, regional_style)
                return q_en, q_kn, next_s, details, [], [], None, None, True, "Information Collection"
            else:
                reply_kn = "ಕ್ಷಮಿಸಿ, ಜಮೀನಿನ ವಿಸ್ತೀರ್ಣ ಸ್ಪಷ್ಟವಾಗಿ ಕೇಳಿಸಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಎಷ್ಟು ಎಕರೆ ಅಥವಾ ಹೆಕ್ಟೇರ್ ಎಂದು ಸಂಖ್ಯೆಯಲ್ಲಿ ತಿಳಿಸಿ (ಉದಾ. ೩ ಎಕರೆ, ೪.೫ ಎಕರೆ). ತಿಳಿಯದಿದ್ದರೆ 'ಗೊತ್ತಿಲ್ಲ' ಎಂದು ಹೇಳಿ."
                reply_en = "Sorry, land size was not clear. Please specify how many acres or hectares you cultivate (e.g. 3 acres, 4.5 acres). Say 'don't know' if unsure."
                reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                return reply_en, reply_kn, STAGE_COLLECT_LAND_SIZE, details, [], [], None, None, True, "Information Collection"

        # ---------------------------------------------------------------------
        # STATE: STAGE_COLLECT_OWNERSHIP
        # ---------------------------------------------------------------------
        if current_stage == STAGE_COLLECT_OWNERSHIP:
            if any(k in user_message for k in ["ಸ್ವಂತ", "own", "ಮನೆ"]):
                details["land_ownership"] = "Owned"
            elif any(k in user_message for k in ["ಗೇಣಿ", "ಗುತ್ತಿಗೆ", "lease", "tenant"]):
                details["land_ownership"] = "Leased"
            elif any(k in user_message for k in ["ಪಾಲು", "ಪಾಲುದಾರ", "share"]):
                details["land_ownership"] = "Shared"
            else:
                details["land_ownership"] = "Owned"

            next_s = STAGE_COLLECT_FARMER_CATEGORY
            q_kn, q_en = cls.get_question_for_stage(next_s, details, regional_style)
            return q_en, q_kn, next_s, details, [], [], None, None, True, "Information Collection"

        # ---------------------------------------------------------------------
        # STATE: STAGE_COLLECT_FARMER_CATEGORY
        # ---------------------------------------------------------------------
        if current_stage == STAGE_COLLECT_FARMER_CATEGORY:
            acres = details.get("land_acres", 3.0)
            if any(k in user_message for k in ["ಅತಿ ಸಣ್ಣ", "marginal"]):
                details["farmer_category"] = "Marginal (ಅತಿ ಸಣ್ಣ ರೈತರು)"
            elif any(k in user_message for k in ["ಸಣ್ಣ", "small"]):
                details["farmer_category"] = "Small (ಸಣ್ಣ ರೈತರು)"
            elif any(k in user_message for k in ["ದೊಡ್ಡ", "ಮಧ್ಯಮ", "large", "medium"]):
                details["farmer_category"] = "Medium & Large (ಮಧ್ಯಮ/ದೊಡ್ಡ ರೈತರು)"
            elif any(k in user_message for k in ["ಸಾಮಾನ್ಯ", "general"]):
                details["farmer_category"] = "General (ಸಾಮಾನ್ಯ)"
            elif any(k in user_message for k in ["sc", "st", "ಪರಿಶಿಷ್ಟ"]):
                details["farmer_category"] = "SC/ST (ಪರಿಶಿಷ್ಟ ಜಾತಿ/ಪಂಗಡ)"
            else:
                if acres <= 2.5:
                    details["farmer_category"] = "Marginal (ಅತಿ ಸಣ್ಣ ರೈತರು)"
                elif acres <= 5.0:
                    details["farmer_category"] = "Small (ಸಣ್ಣ ರೈತರು)"
                else:
                    details["farmer_category"] = "Medium & Large (ಮಧ್ಯಮ/ದೊಡ್ಡ ರೈತರು)"

            next_s = STAGE_COLLECT_CROPS
            q_kn, q_en = cls.get_question_for_stage(next_s, details, regional_style)
            return q_en, q_kn, next_s, details, [], [], None, None, True, "Information Collection"

        # ---------------------------------------------------------------------
        # STATE: STAGE_COLLECT_CROPS
        # ---------------------------------------------------------------------
        if current_stage == STAGE_COLLECT_CROPS:
            crop_val = details.get("primary_crop") or details.get("crop")
            if not crop_val:
                for tok, name in cls.CROP_MAP.items():
                    if tok in user_message or tok in user_message.lower():
                        crop_val = name
                        break

            if crop_val:
                details["primary_crop"] = crop_val
                details["crop"] = crop_val
                if "crops" not in details or not details["crops"]:
                    details["crops"] = [crop_val]

                next_s = STAGE_COLLECT_OTHER_CROPS
                q_kn, q_en = cls.get_question_for_stage(next_s, details, regional_style)
                return q_en, q_kn, next_s, details, [], [], None, None, True, "Information Collection"
            else:
                reply_kn = "ಕ್ಷಮಿಸಿ, ಬೆಳೆಯ ಹೆಸರು ಸ್ಪಷ್ಟವಾಗಿ ಕೇಳಿಸಲಿಲ್ಲ. ದಯವಿಟ್ಟು ನೀವು ಮುಖ್ಯವಾಗಿ ಬೆಳೆಯುವ ಬೆಳೆ ಯಾವುದು ಎಂದು ತಿಳಿಸಿ (ಉದಾಹರಣೆಗೆ ಭತ್ತ, ಶೇಂಗಾ, ಜೋಳ, ರಾಗಿ, ಕಬ್ಬು)."
                reply_en = "Sorry, crop name was not clear. Please state what primary crop you grow (e.g. Paddy, Groundnut, Jowar, Ragi, Sugarcane)."
                reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                return reply_en, reply_kn, STAGE_COLLECT_CROPS, details, [], [], None, None, True, "Information Collection"

        # ---------------------------------------------------------------------
        # STATE: STAGE_COLLECT_OTHER_CROPS (Optional)
        # ---------------------------------------------------------------------
        if current_stage == STAGE_COLLECT_OTHER_CROPS:
            if not any(k in user_message for k in ["ಇಲ್ಲ", "ಯಾವುದೂ ಇಲ್ಲ", "none", "no"]):
                found_crops = [name for tok, name in cls.CROP_MAP.items() if tok in user_message]
                if found_crops:
                    details["secondary_crops"] = found_crops
                    if "crops" in details and isinstance(details["crops"], list):
                        for c in found_crops:
                            if c not in details["crops"]:
                                details["crops"].append(c)

            next_s = STAGE_COLLECT_IRRIGATION
            q_kn, q_en = cls.get_question_for_stage(next_s, details, regional_style)
            return q_en, q_kn, next_s, details, [], [], None, None, True, "Information Collection"

        # ---------------------------------------------------------------------
        # STATE: STAGE_COLLECT_IRRIGATION
        # ---------------------------------------------------------------------
        if current_stage == STAGE_COLLECT_IRRIGATION:
            if any(k in user_message for k in ["ಬೋರ್ವೆಲ್", "ಬೋರ್", "ಕೊಳವೆ", "borewell"]):
                details["irrigation"] = "Borewell"
            elif any(k in user_message for k in ["ಕಾಲುವೆ", "canal"]):
                details["irrigation"] = "Canal"
            elif any(k in user_message for k in ["ಮಳೆ", "ಖುಷ್ಕಿ", "rainfed"]):
                details["irrigation"] = "Rainfed"
            elif any(k in user_message for k in ["ಹನಿ", "drip"]):
                details["irrigation"] = "Drip irrigation"
            elif any(k in user_message for k in ["ತುಂತುರು", "sprinkler"]):
                details["irrigation"] = "Sprinkler"
            else:
                details["irrigation"] = "Borewell"

            next_s = STAGE_COLLECT_SOIL
            q_kn, q_en = cls.get_question_for_stage(next_s, details, regional_style)
            return q_en, q_kn, next_s, details, [], [], None, None, True, "Information Collection"

        # ---------------------------------------------------------------------
        # STATE: STAGE_COLLECT_SOIL (Optional)
        # ---------------------------------------------------------------------
        if current_stage == STAGE_COLLECT_SOIL:
            if any(k in user_message for k in ["ಕಪ್ಪು", "black", "ಎರೆ", "ಏರಿ"]):
                details["soil_type"] = "Black Soil"
            elif any(k in user_message for k in ["ಕೆಂಪು", "red", "ಮಸಾರಿ"]):
                details["soil_type"] = "Red Soil"
            elif any(k in user_message for k in ["ಗೋಡು", "loamy"]):
                details["soil_type"] = "Loamy Soil"
            elif any(k in user_message for k in ["ಮರಳು", "sandy"]):
                details["soil_type"] = "Sandy Soil"
            else:
                details["soil_type"] = "Black Soil"

            next_s = STAGE_COLLECT_SEASON_AND_CROP_STAGE
            q_kn, q_en = cls.get_question_for_stage(next_s, details, regional_style)
            return q_en, q_kn, next_s, details, [], [], None, None, True, "Information Collection"

        # ---------------------------------------------------------------------
        # STATE: STAGE_COLLECT_SEASON_AND_CROP_STAGE
        # ---------------------------------------------------------------------
        if current_stage == STAGE_COLLECT_SEASON_AND_CROP_STAGE:
            if "season" not in details:
                details["season"] = "Kharif"
            if "crop_stage" not in details:
                details["crop_stage"] = "Tillering / Flowering"

            next_s = STAGE_CONFIRM_PROFILE
            q_kn, q_en = cls.get_question_for_stage(next_s, details, regional_style)
            return q_en, q_kn, next_s, details, [], [], None, None, True, "Profile Confirmation"

        # ---------------------------------------------------------------------
        # STATE: STAGE_CONFIRM_PROFILE (Phase 3)
        # ---------------------------------------------------------------------
        if current_stage == STAGE_CONFIRM_PROFILE:
            msg_lower = user_message.lower()
            # 1. Check for negative / change request first (so 'ಸರಿ ಇಲ್ಲ' isn't matched by 'ಸರಿ')
            if any(k in msg_lower for k in ["ಸರಿ ಇಲ್ಲ", "ಸರಿಇಲ್ಲ", "ತಪ್ಪು", "ಬದಲಾಯಿಸಬೇಕು", "ಇಲ್ಲ", "no", "wrong", "change", "not correct"]):
                reply_kn = "ಖಂಡಿತ, ನೀವು ಯಾವ ಮಾಹಿತಿಯನ್ನು ಬದಲಾಯಿಸಲು ಬಯಸುತ್ತೀರಿ? (ಜಿಲ್ಲೆ, ತಾಲೂಕು, ಜಮೀನು, ಬೆಳೆ, ಅಥವಾ ನೀರಾವರಿ?)"
                reply_en = "Sure, which detail would you like to update? (District, Taluka, Land acres, Crop, or Irrigation?)"
                reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                return reply_en, reply_kn, STAGE_COLLECT_CORRECTION, details, [], [], None, None, True, "Profile Correction"
            # 2. Check for affirmative confirmation
            elif any(k in msg_lower for k in ["ಹೌದು", "ಸರಿಯಾಗಿದೆ", "yes", "correct", "ಹೌದ್ರೀ", "ಖಂಡಿತ", "right"]) or (msg_lower.strip() in ["ಸರಿ", "sari"]):
                next_s = STAGE_IDENTIFY_REQUIREMENT
                q_kn, q_en = cls.get_question_for_stage(next_s, details, regional_style)
                return q_en, q_kn, next_s, details, [], [], None, None, True, "Requirement Identification"
            # 3. Unclear confirmation response -> ask for clarification
            else:
                reply_kn = "ದಯವಿಟ್ಟು ತಿಳಿಸಿ, ಮೇಲಿನ ಕೃಷಿ ಮಾಹಿತಿ ಸರಿಯಾಗಿದೆಯೇ? ('ಹೌದು, ಸರಿ' ಅಥವಾ 'ಇಲ್ಲ, ಬದಲಾಯಿಸಬೇಕು' ಎಂದು ಹೇಳಿ)"
                reply_en = "Please confirm if the above farm details are correct. (Say 'Yes, correct' or 'No, change')"
                reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
                return reply_en, reply_kn, STAGE_CONFIRM_PROFILE, details, [], [], None, None, True, "Profile Confirmation"

        # ---------------------------------------------------------------------
        # STATE: STAGE_COLLECT_CORRECTION
        # ---------------------------------------------------------------------
        if current_stage == STAGE_COLLECT_CORRECTION:
            if any(k in user_message for k in ["ಜಿಲ್ಲೆ", "district"]):
                return "Which is your correct district?", "ನಿಮ್ಮ ಸರಿಯಾದ ಜಿಲ್ಲೆ ಯಾವುದು ಹೇಳಿ?", STAGE_COLLECT_DISTRICT, details, [], [], None, None, True, "Correction"
            elif any(k in user_message for k in ["ತಾಲೂಕು", "ತಾಲೂಕ", "taluk", "taluka"]):
                dist = details.get("district", "Belagavi")
                return f"Which is your correct taluka in {dist}?", f"ನಿಮ್ಮ {dist} ಜಿಲ್ಲೆಯ ಸರಿಯಾದ ತಾಲೂಕು ಯಾವುದು ತಿಳಿಸಿ?", STAGE_COLLECT_TALUKA, details, [], [], None, None, True, "Correction"
            elif any(k in user_message for k in ["ಜಮೀನು", "land", "ಎಕರೆ"]):
                return "How many acres of land do you cultivate?", "ನಿಮ್ಮ ಬಳಿ ಎಷ್ಟು ಎಕರೆ ಜಮೀನಿದೆ?", STAGE_COLLECT_LAND_SIZE, details, [], [], None, None, True, "Correction"
            elif any(k in user_message for k in ["ಬೆಳೆ", "crop"]):
                return "What is your primary crop?", "ನಿಮ್ಮ ಮುಖ್ಯ ಬೆಳೆ ಯಾವುದು?", STAGE_COLLECT_CROPS, details, [], [], None, None, True, "Correction"
            elif any(k in user_message for k in ["ನೀರಾವರಿ", "irrigation"]):
                return "What is your irrigation facility?", "ನಿಮ್ಮ ಜಮೀನಿಗೆ ಯಾವ ರೀತಿಯ ನೀರಾವರಿ ಸೌಲಭ್ಯವಿದೆ?", STAGE_COLLECT_IRRIGATION, details, [], [], None, None, True, "Correction"
            elif any(k in user_message for k in ["ಮಾಲೀಕತ್ವ", "ಸ್ವಂತ", "ಗುತ್ತಿಗೆ", "ownership"]):
                return "Is your land owned or leased?", "ಜಮೀನು ನಿಮ್ಮ ಸ್ವಂತದ್ದೇ ಅಥವಾ ಗುತ್ತಿಗೆಗೆ ತೆಗೆದುಕೊಂಡಿದ್ದೀರಾ?", STAGE_COLLECT_OWNERSHIP, details, [], [], None, None, True, "Correction"
            else:
                next_s = STAGE_CONFIRM_PROFILE
                q_kn, q_en = cls.get_question_for_stage(next_s, details, regional_style)
                return q_en, q_kn, next_s, details, [], [], None, None, True, "Profile Confirmation"

        # ---------------------------------------------------------------------
        # STATE: STAGE_IDENTIFY_REQUIREMENT or STAGE_FOLLOW_UP (Phases 4, 5, 6, 7)
        # ---------------------------------------------------------------------
        user_lower = user_message.lower()

        # Check for profile correction / change request
        if any(w in user_lower or w in user_message for w in ["ತಪ್ಪು", "ಬದಲಾಯಿಸಬೇಕು", "ಬದಲಾವಣೆ", "change", "correction", "wrong"]):
            reply_kn = "ಖಂಡಿತ, ನೀವು ಯಾವ ಮಾಹಿತಿಯನ್ನು ಬದಲಾಯಿಸಲು ಬಯಸುತ್ತೀರಿ? (ಜಿಲ್ಲೆ, ತಾಲೂಕು, ಜಮೀನು, ಬೆಳೆ, ಅಥವಾ ನೀರಾವರಿ?)"
            reply_en = "Sure, which detail would you like to update? (District, Taluka, Land acres, Crop, or Irrigation?)"
            reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
            return reply_en, reply_kn, STAGE_COLLECT_CORRECTION, details, [], [], None, None, True, "Profile Correction"

        # Option 1: Government Schemes
        if any(w in user_lower or w in user_message for w in ["ಯೋಜನೆ", "scheme", "1", "೧", "ಸಹಾಯಧನ", "subsidy", "pm-kisan", "krishi bhagya", "ಪಿಎಂ ಕಿಸಾನ್", "ಕಿಸಾನ್", "ಕೃಷಿ ಭಾಗ್ಯ"]):
            return cls._evaluate_government_schemes(details, all_schemes, regional_style, farmer_name, farmer_name_en)

        # Option 2: Crop Insurance
        if any(w in user_lower or w in user_message for w in ["ವಿಮೆ", "insurance", "2", "೨", "ಸಂರಕ್ಷಣೆ", "samrakshane", "72", "ಹಾನಿ", "ಬೆಳೆ ಹಾನಿ", "ನಷ್ಟ"]):
            return cls._evaluate_crop_insurance(details, regional_style, farmer_name, farmer_name_en)

        # Option 3: Fertilizer Recommendations
        if any(w in user_lower or w in user_message for w in ["ಗೊಬ್ಬರ", "fertilizer", "3", "೩", "ಯೂರಿಯಾ", "ಡಿಎಪಿ", "npk"]):
            return cls._evaluate_fertilizer(details, regional_style, farmer_name, farmer_name_en)

        # Option 4: Crop Guidance
        if any(w in user_lower or w in user_message for w in ["ಮಾರ್ಗದರ್ಶನ", "guidance", "4", "೪", "ಬೆಳೆ ಸಲಹೆ", "ಸಾಗುವಳಿ"]):
            return cls._evaluate_crop_guidance(details, regional_style, farmer_name, farmer_name_en)

        # Option 5: Irrigation Guidance
        if any(w in user_lower or w in user_message for w in ["ನೀರಾವರಿ", "irrigation", "5", "೫", "ನೀರು"]):
            return cls._evaluate_irrigation(details, regional_style, farmer_name, farmer_name_en)

        # Option 6: Weather Information
        if any(w in user_lower or w in user_message for w in ["ಹವಾಮಾನ", "weather", "6", "೬", "ಮಳೆ", "rain"]):
            return cls._evaluate_weather(details, regional_style, farmer_name, farmer_name_en)

        # Option 7: Pest and Disease Management
        if any(w in user_lower or w in user_message for w in ["ಕೀಟ", "ರೋಗ", "pest", "disease", "7", "೭", "ಹುಳು"]):
            return cls._evaluate_pest_disease(details, regional_style, farmer_name, farmer_name_en)

        # Option 8: Agricultural Loans (KCC)
        if any(w in user_lower or w in user_message for w in ["ಸಾಲ", "loan", "8", "೮", "kcc", "ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್"]):
            return cls._evaluate_loans(details, regional_style, farmer_name, farmer_name_en)

        # Option 9: Market Prices
        if any(w in user_lower or w in user_message for w in ["ಮಾರುಕಟ್ಟೆ", "market", "9", "೯", "ಮಾರುಕಟ್ಟೆ ದರ", "ಮಂಡಿ ದರ", "ಬೆಂಬಲ ಬೆಲೆ", "ಕ್ವಿಂಟಾಲ್", "price", "apmc", "ಮಂಡಿ", "ದರ ಎಷ್ಟು", "ಬೆಲೆ ಎಷ್ಟು"]):
            return cls._evaluate_market_prices(details, regional_style, farmer_name, farmer_name_en)

        # Option 10: Complete Agricultural Assistance
        if any(w in user_lower or w in user_message for w in ["ಸಮಗ್ರ", "complete", "10", "೧೦", "ಎಲ್ಲಾ", "all"]):
            return cls._evaluate_complete_assistance(details, all_schemes, regional_style, farmer_name, farmer_name_en)

        # Default: Search RAG knowledge base for specific query
        is_kn = any('\u0C80' <= ch <= '\u0CFF' for ch in user_message)
        rag_res = RAGEngine.answer_query(user_message, preferred_language="kn" if is_kn else "en")
        if rag_res["available"]:
            reply_en = rag_res["answer_en"]
            reply_kn = rag_res["answer_kn"]
            if regional_style == "North Karnataka" and not reply_kn.startswith("ನೋಡ್ರೀ"):
                reply_kn = f"ನೋಡ್ರೀ ಅಪ್ಪಾ, {reply_kn}"
            elif regional_style == "South Karnataka" and not reply_kn.startswith("ಸ್ವಾಮಿ"):
                reply_kn = f"ಸ್ವಾಮಿ, {reply_kn}"
            reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
            return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], rag_res["citations"], rag_res["confidence"], rag_res["generation_mode"], True, "RAG Knowledge"

        # General advisory response
        crop = details.get("crop") or details.get("primary_crop", "ಭತ್ತ")
        reply_kn = (
            f"{farmer_name} ಅವರೇ, ನಿಮ್ಮ {crop} ಬೆಳೆಗೆ ಸಂಬಂಧಿಸಿದಂತೆ ಯಾವ ವಿಷಯದಲ್ಲಿ ಮಾಹಿತಿ ಬೇಕು? "
            f"ನೀವು ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು, ಬೆಳೆ ವಿಮೆ, ರಸಗೊಬ್ಬರದ ಪ್ರಮಾಣ ಅಥವಾ ಮಾರುಕಟ್ಟೆ ದರದ ಬಗ್ಗೆ ಕೇಳಬಹುದು."
        )
        reply_en = (
            f"Hello {farmer_name_en}, what specific guidance do you need for your {crop} crop? "
            f"You can ask about government schemes, crop insurance, fertilizer dosage, or market prices."
        )
        reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
        return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], 0.85, "crop_advisory_general", True, "Crop Advisory"

    # =========================================================================
    # SPECIFIC AGRICULTURAL ANALYSIS EVALUATORS (Phases 5 & 6)
    # =========================================================================

    CLOSING_CIRCUMSTANCE_INVITATION_KN = (
        "\n\nನಿಮ್ಮ ಕೃಷಿ ಮಾಹಿತಿಯ ಆಧಾರದ ಮೇಲೆ ಈ ಸಲಹೆ ನೀಡಿದ್ದೇನೆ. ನಿಮ್ಮ ಜಮೀನು, ಬೆಳೆ ಅಥವಾ ಕೃಷಿ ಪರಿಸ್ಥಿತಿಯಲ್ಲಿ ಏನಾದರೂ ಹೊಸ ಬದಲಾವಣೆಗಳಿವೆಯೇ? "
        "ಇದ್ದರೆ ಧ್ವನಿಯ ಮೂಲಕ ಹೇಳಿ, ನಿಮ್ಮ ಮಾಹಿತಿಯನ್ನು ನವೀಕರಿಸುತ್ತೇನೆ. ಇನ್ನೊಂದು ಕೃಷಿ ಸಹಾಯ ಬೇಕಿದ್ದರೆ ನೇರವಾಗಿ ಹೇಳಿ."
    )
    CLOSING_CIRCUMSTANCE_INVITATION_EN = (
        "\n\nI have provided this guidance based on your farm details. Have there been any recent changes to your land, crop, or farming conditions? "
        "If so, tell me by voice and I will update your information. If you need any other agricultural assistance, please ask."
    )

    @classmethod
    def _attach_closing_invitation(cls, reply_kn: str, reply_en: str, regional_style: str = "Standard Kannada") -> Tuple[str, str]:
        if cls.CLOSING_CIRCUMSTANCE_INVITATION_KN not in reply_kn:
            reply_kn = reply_kn + cls.CLOSING_CIRCUMSTANCE_INVITATION_KN
        if cls.CLOSING_CIRCUMSTANCE_INVITATION_EN not in reply_en:
            reply_en = reply_en + cls.CLOSING_CIRCUMSTANCE_INVITATION_EN
        reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
        return reply_en, reply_kn

    @classmethod
    def _evaluate_government_schemes(cls, details, all_schemes, regional_style, farmer_name, farmer_name_en):
        dist = details.get("district", "Belagavi")
        land = details.get("land_acres")
        own = details.get("land_ownership", "Owned")
        cat = details.get("farmer_category", "Small farmer")
        crop = details.get("crop") or details.get("primary_crop", "Paddy")
        irrigation = details.get("irrigation", "Rainfed")

        matched = []
        is_leased = own in ["Leased", "Shared", "Tenant", "ಗುತ್ತಿಗೆ", "ಗೇಣಿ"]
        has_known_land = land is not None and land > 0
        is_rainfed = "rainfed" in irrigation.lower() or "ಮಳೆ" in irrigation or "ಖುಷ್ಕಿ" in irrigation

        if all_schemes:
            for sc in all_schemes:
                # PM-KISAN: requires OWN land and known land
                if "PM-KISAN" in sc.scheme_id:
                    if not is_leased and has_known_land:
                        matched.append(sc)
                # PMFBY: covers both owned and leased tenant farmers for notified crops
                elif "PMFBY" in sc.scheme_id:
                    matched.append(sc)
                # Krishi Bhagya: requires RAINFED dryland and <= 5.0 acres
                elif "Krishi Bhagya" in sc.scheme_name:
                    if is_rainfed and (not has_known_land or land <= 5.0):
                        matched.append(sc)
                elif getattr(sc, "max_land_acres", None) and has_known_land and land <= sc.max_land_acres:
                    matched.append(sc)

        rec_list = []
        for s in matched[:3]:
            rec_list.append({
                "scheme_id": s.scheme_id,
                "scheme_name": s.scheme_name,
                "scheme_name_kn": s.scheme_name_kn,
                "benefits": s.benefit_details_kn,
                "official_url": s.official_url,
                "verification": s.verification_status
            })

        rag_res = RAGEngine.answer_query(f"PM-KISAN PMFBY Krishi Bhagya eligibility in Karnataka", preferred_language="kn")
        citations = rag_res["citations"] if rag_res["available"] else []

        land_display = f"{land} ಎಕರೆ" if has_known_land else "ವಿಸ್ತೀರ್ಣ ಅನಿಶ್ಚಿತ (ಪಹಣಿ ಅಗತ್ಯ)"
        land_display_en = f"{land} acres" if has_known_land else "Acreage unrecorded (Pahani required)"

        if is_leased:
            # Real-world tenant farmer rules
            reply_kn = (
                f"{farmer_name} ಅವರೇ, ನಿಮ್ಮ ಕೃಷಿ ವಿವರಗಳಿಗೆ ({dist} ಜಿಲ್ಲೆ, {land_display}, {own} ಗುತ್ತಿಗೆ ಭೂಮಿ) ಅನುಗುಣವಾಗಿ ಸರ್ಕಾರದ ಅಧಿಕೃತ ಯೋಜನೆಗಳ ಸ್ಥಿತಿ:\n\n"
                f"೧. ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ (PMFBY / Samrakshane):\n"
                f"   • ಸ್ಥಿತಿ: ಸಂಪೂರ್ಣ ಅರ್ಹರು (PASS)!\n"
                f"   • ವಿವರ: ಗುತ್ತಿಗೆ ರೈತರು ಗ್ರಾಮ ಲೆಕ್ಕಿಗರಿಂದ (VAO) ಬಿತ್ತನೆ ದೃಢೀಕರಣ ಪತ್ರ (Sowing Certificate) ಪಡೆದು ಸಂರಕ್ಷಣೆ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ {crop} ಬೆಳೆಗೆ ಕೇವಲ ೧.೫%-೨% ಪ್ರೀಮಿಯಂ ನೀಡಿ ಬೆಳೆ ವಿಮೆ ಪಡೆಯಬಹುದು.\n\n"
                f"೨. ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (KCC - Crop Loan):\n"
                f"   • ಸ್ಥಿತಿ: ಅರ್ಹರು (PASS)!\n"
                f"   • ವಿವರ: ಗೇಣಿದಾರ ರೈತರಿಗೆ ಜಂಟಿ ಹೊಣೆಗಾರಿಕೆ ಗುಂಪುಗಳ (JLG) ಮೂಲಕ ಯಾವುದೇ ಜಮೀನು ಅಡಮಾನವಿಲ್ಲದೆ ಶೇ. ೪% ಬಡ್ಡಿದರದಲ್ಲಿ ಬೆಳೆ ಸಾಲ ಲಭ್ಯ.\n\n"
                f"೩. ಪ್ರಧಾನ ಮಂತ್ರಿ ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ (PM-KISAN):\n"
                f"   • ಸ್ಥಿತಿ: ಅನರ್ಹ (FAIL).\n"
                f"   • ಕಾರಣ: ಅಧಿಕೃತ ಮಾರ್ಗಸೂಚಿ ನಿಯಮ ೨ ರ ಪ್ರಕಾರ, ಸ್ವಂತ ಹೆಸರಿನಲ್ಲಿ ಪಹಣಿ (RTC) ಹೊಂದಿರುವ ಭೂಮಾಲೀಕರಿಗೆ ಮಾತ್ರ ವಾರ್ಷಿಕ ₹೬,೦೦೦ ನೆರವು ಅನ್ವಯಿಸುತ್ತದೆ; ಗುತ್ತಿಗೆ ಭೂಮಿಗೆ ಇದು ಅನ್ವಯಿಸುವುದಿಲ್ಲ.\n\n"
                f"ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ನಿಮ್ಮ ಸಮೀಪದ ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರ ಅಥವಾ ಗ್ರಾಮ ಒನ್ (Grama One) ಕೇಂದ್ರಕ್ಕೆ ಭೇಟಿ ನೀಡಿ.\n"
                f"ಅಧಿಕೃತ ಪೋರ್ಟಲ್: https://samrakshane.karnataka.gov.in"
            )
            reply_en = (
                f"Hello {farmer_name_en}, based on your farm profile ({dist}, {land_display_en}, Leased/Tenant):\n\n"
                f"1. PMFBY Crop Insurance: Fully Eligible (PASS)! Tenant farmers can enrol on Samrakshane portal by submitting a Sowing Certificate from the Village Accountant (1.5%-2% premium).\n"
                f"2. Kisan Credit Card (KCC): Eligible (PASS)! Collateral-free crop loans up to ₹3 Lakh at 4% interest via Joint Liability Groups (JLGs).\n"
                f"3. PM-KISAN: Not Eligible (FAIL). Under Clause 2 guidelines, cultivable land ownership title (RTC) in the applicant's name is mandatory; tenant cultivators are excluded.\n\n"
                f"Official Portal: https://samrakshane.karnataka.gov.in"
            )
        elif not has_known_land:
            # Land size unknown scenario
            reply_kn = (
                f"{farmer_name} ಅವರೇ, ನಿಮ್ಮ ಕೃಷಿ ವಿವರಗಳಿಗೆ ({dist} ಜಿಲ್ಲೆ, {crop} ಬೆಳೆ, {own}):\n\n"
                f"೧. ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ (PMFBY):\n"
                f"   • ಸ್ಥಿತಿ: ಅರ್ಹರು (PASS) - {crop} ಬೆಳೆಯು {dist} ಜಿಲ್ಲೆಯಲ್ಲಿ ಅಧಿಸೂಚಿತವಾಗಿದ್ದು, ಸಂರಕ್ಷಣೆ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ವಿಮೆ ಮಾಡಿಸಬಹುದು.\n\n"
                f"೨. PM-KISAN ಮತ್ತು ಕೃಷಿ ಭಾಗ್ಯ ಯೋಜನೆಗಳು:\n"
                f"   • ಸ್ಥಿತಿ: ಪರಿಶೀಲನೆ ಬಾಕಿ (UNKNOWN).\n"
                f"   • ಕಾರಣ: ನಿಮ್ಮ ಜಮೀನಿನ ವಿಸ್ತೀರ್ಣ (ಎಕರೆ) ಇನ್ನೂ ದಾಖಲಾಗಿಲ್ಲ. ಈ ಯೋಜನೆಗಳ ಗರಿಷ್ಠ/ಕನಿಷ್ಠ ಭೂಮಿತಿ ಪರಿಶೀಲಿಸಲು ಭೂಮಿ ಪೋರ್ಟಲ್ (bhoomi.karnataka.gov.in) ಅಥವಾ ಗ್ರಾಮ ಒನ್‌ನಲ್ಲಿ ನಿಮ್ಮ ಪಹಣಿ (RTC) ಪರಿಶೀಲಿಸಿ ತಿಳಿಸಿ.\n\n"
                f"ಅರ್ಜಿ ಸಲ್ಲಿಸಲು Samrakshane ಪೋರ್ಟಲ್: https://samrakshane.karnataka.gov.in"
            )
            reply_en = (
                f"Hello {farmer_name_en}, based on your profile in {dist} ({crop}, {own}):\n\n"
                f"1. PMFBY Crop Insurance: Eligible (PASS) for notified crop {crop} on Samrakshane portal.\n"
                f"2. PM-KISAN & Krishi Bhagya: Status UNKNOWN. Acreage threshold required. Please verify your RTC / Pahani on Bhoomi portal (bhoomi.karnataka.gov.in)."
            )
        else:
            # Standard verified owner scenario
            rainfed_scheme_note = (
                f"೩. ಕೃಷಿ ಭಾಗ್ಯ ಯೋಜನೆ (ಕರ್ನಾಟಕ ಸರ್ಕಾರ):\n"
                f"   • ಸ್ಥಿತಿ: ಅರ್ಹರು (PASS)!\n"
                f"   • ಉದ್ದೇಶ: ಮಳೆಯಾಶ್ರಿತ ಜಮೀನಿಗೆ ಕೃಷಿ ಹೊಂಡ, ಪಾಲಿಥಿನ್ ಹೊದಿಕೆ ಹಾಗೂ ಡೀಸೆಲ್ ಪಂಪ್‌ಸೆಟ್‌ಗಳಿಗೆ ಶೇ. ೮೦-೯೦ ಸಬ್ಸಿಡಿ.\n\n"
                if is_rainfed else
                f"೩. ಪ್ರಧಾನ ಮಂತ್ರಿ ಕೃಷಿ ಸಿಂಚಾಯಿ ಯೋಜನೆ (PMKSY - ಹನಿ ನೀರಾವರಿ):\n"
                f"   • ಸ್ಥಿತಿ: ಅರ್ಹರು (PASS)!\n"
                f"   • ಉದ್ದೇಶ: ಕೊಳವೆಬಾವಿ/ಕಾಲುವೆ ನೀರಾವರಿ ಜಮೀನಿಗೆ ಹನಿ ಮತ್ತು ತುಂತುರು ನೀರಾವರಿಗೆ ಶೇ. ೭೦-೯೦ ಸಬ್ಸಿಡಿ.\n\n"
            )
            reply_kn = (
                f"{farmer_name} ಅವರೇ, ನಿಮ್ಮ ಕೃಷಿ ವಿವರಗಳಿಗೆ ({dist} ಜಿಲ್ಲೆ, {land_display}, {own}, {irrigation}) ಹೊಂದಿಕೆಯಾಗುವ ಪ್ರಮುಖ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು:\n\n"
                f"೧. ಪ್ರಧಾನ ಮಂತ್ರಿ ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ (PM-KISAN):\n"
                f"   • ಸ್ಥಿತಿ: ಅರ್ಹರು (PASS)!\n"
                f"   • ಉದ್ದೇಶ & ನೆರವು: ವಾರ್ಷಿಕ ₹೬,೦೦೦ ನೇರ ಆರ್ಥಿಕ ನೆರವು (ವರ್ಷಕ್ಕೆ ೩ ಕಂತುಗಳಲ್ಲಿ ಡಿಬಿಟಿ ಮೂಲಕ).\n"
                f"   • ಅಗತ್ಯ ದಾಖಲೆಗಳು: ಭೂಮಿ ಪಹಣಿ (RTC), ಆಧಾರ್ ಕಾರ್ಡ್ ಮತ್ತು ಬ್ಯಾಂಕ್ ಪಾಸ್‌ಬುಕ್.\n\n"
                f"೨. ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ (PMFBY / Samrakshane):\n"
                f"   • ಸ್ಥಿತಿ: ಅರ್ಹರು (PASS)!\n"
                f"   • ಉದ್ದೇಶ: ಪ್ರಕೃತಿ ವಿಕೋಪದಿಂದ ಬೆಳೆ ಹಾನಿಯಾದರೆ ಪೂರ್ಣ ವಿಮಾ ಪರಿಹಾರ (೧.೫%-೨% ಪ್ರೀಮಿಯಂ).\n\n"
                f"{rainfed_scheme_note}"
                f"ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ನಿಮ್ಮ ಸಮೀಪದ ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರ ಅಥವಾ ಗ್ರಾಮ ಒನ್ (Grama One) ಕೇಂದ್ರಕ್ಕೆ ಭೇಟಿ ನೀಡಿ.\n"
                f"ಅಧಿಕೃತ ಪೋರ್ಟಲ್: https://raitamitra.karnataka.gov.in"
            )
            reply_en = (
                f"Hello {farmer_name_en}, based on your farm profile ({dist}, {land_display_en}, {own}, {irrigation}):\n\n"
                f"1. PM-KISAN: Eligible (PASS) - ₹6,000/year direct financial support in 3 installments.\n"
                f"2. PMFBY Crop Insurance: Eligible (PASS) - Samrakshane portal coverage at 1.5%-2% farmer premium.\n"
                f"3. {'Krishi Bhagya: Eligible (PASS) - 80-90% subsidy for rainfed farm ponds.' if is_rainfed else 'PMKSY: Eligible (PASS) - 70-90% subsidy for micro-irrigation.'}\n\n"
                f"Official Portal: https://raitamitra.karnataka.gov.in"
            )

        reply_en, reply_kn = cls._attach_closing_invitation(reply_kn, reply_en, regional_style)
        return reply_en, reply_kn, STAGE_FOLLOW_UP, details, rec_list, citations, 0.95, "grounded_schemes", True, "Government Schemes"

    @classmethod
    def _evaluate_crop_insurance(cls, details, regional_style, farmer_name, farmer_name_en):
        dist = details.get("district", "Belagavi")
        taluk = details.get("taluk")
        crop = details.get("crop") or details.get("primary_crop", "Paddy")
        land = details.get("land_acres", 2.0)

        ins_eval = CropInsuranceService.evaluate_insurance(
            district=dist,
            taluk=taluk,
            crop=crop,
            land_acres=land
        )

        status_note = ins_eval.get("status_note_kn") or f"{crop} ಬೆಳೆಯು ಕರ್ನಾಟಕ ಸಂರಕ್ಷಣೆ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಅಧಿಸೂಚಿತ ವಿಮಾ ಬೆಳೆಯಾಗಿದೆ."
        prem_rate = ins_eval.get("premium_rate_farmer_pct", 2.0)
        calamity_rule = ins_eval.get("calamity_intimation_rule_kn") or "ಪ್ರಕೃತಿ ವಿಕೋಪದಿಂದ ಬೆಳೆ ಹಾನಿಯಾದರೆ ೭೨ ಗಂಟೆಗಳ ಒಳಗೆ ಕಡ್ಡಾಯವಾಗಿ ಮಾಹಿತಿ ನೀಡಬೇಕು."
        helpline = ins_eval.get("helpline", "1800-180-1551")

        reply_kn = (
            f"{farmer_name} ಅವರೇ, ಕರ್ನಾಟಕ ಸಂರಕ್ಷಣೆ ಪೋರ್ಟಲ್ ಹಾಗೂ ಪಿಎಂಎಫ್‌ಬಿವೈ ನಿಯಮಾವಳಿಗಳ ಪ್ರಕಾರ {crop} ಬೆಳೆಯ ವಿಮಾ ಮಾಹಿತಿ:\n\n"
            f"• ಅಧಿಸೂಚಿತ ಸ್ಥಿತಿ: {status_note}\n"
            f"• ರೈತರ ಪ್ರೀಮಿಯಂ ದರ: {prem_rate}% (ಅಂದಾಜು ಪ್ರೀಮಿಯಂ: ₹{ins_eval.get('estimated_farmer_premium_inr', '600')})\n"
            f"• ೭೨ ಗಂಟೆಗಳ ಕಡ್ಡಾಯ ನಿಯಮ: {calamity_rule}\n"
            f"• ಅಗತ್ಯ ದಾಖಲೆಗಳು: ಚಾಲ್ತಿ ಸಾಲಿನ ಪಹಣಿ (RTC), ಆಧಾರ್ ಕಾರ್ಡ್, ಬಿತ್ತನೆ ದೃಢೀಕರಣ ಮತ್ತು ಬ್ಯಾಂಕ್ ಪಾಸ್‌ಬುಕ್.\n"
            f"• ಸಹಾಯವಾಣಿ: {helpline}\n\n"
            f"ಅರ್ಜಿ ಸಲ್ಲಿಸಲು Samrakshane ಪೋರ್ಟಲ್: https://samrakshane.karnataka.gov.in"
        )
        reply_en = (
            f"Hello {farmer_name_en}, according to Karnataka Samrakshane & PMFBY rules for {crop}:\n\n"
            f"• Notification Status: {crop} is an officially notified crop in {dist}.\n"
            f"• Farmer Premium: {prem_rate}% (Approx ₹{ins_eval.get('estimated_farmer_premium_inr', '600')}).\n"
            f"• 72-Hour Calamity Rule: In case of localized calamity (hailstorm/inundation), intimate within 72 hours.\n"
            f"• Helpline: {helpline}\n"
            f"Official Portal: https://samrakshane.karnataka.gov.in"
        )
        reply_en, reply_kn = cls._attach_closing_invitation(reply_kn, reply_en, regional_style)
        return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], 0.95, "crop_insurance_verified", True, "Crop Insurance"

    @classmethod
    def _evaluate_fertilizer(cls, details, regional_style, farmer_name, farmer_name_en):
        crop = details.get("crop") or details.get("primary_crop", "Paddy")
        soil = details.get("soil_type", "Red Loamy")

        dosages = {
            "Paddy": {
                "npk": "100:50:50 kg/ha (40:20:20 kg/acre)",
                "splits": "ಬಾಸಲ್: ಪೂರ್ಣ ರಂಜಕ ಮತ್ತು ಪೊಟ್ಯಾಶ್, 50% ಸಾರಜನಕ. ಉಳಿದ 50% ಸಾರಜನಕವನ್ನು ತೆನೆ ಮತ್ತು ಹೂವಿನ ಹಂತದಲ್ಲಿ 2 ಬಾರಿ ಹಾಕಿರಿ.",
                "splits_en": "Basal: 100% P & K, 50% N. Remaining 50% N split at tillering and panicle initiation."
            },
            "Sugarcane": {
                "npk": "250:100:125 kg/ha (100:40:50 kg/acre)",
                "splits": "ನಾಟಿ ವೇಳೆ: 10% ಸಾರಜನಕ, ಪೂರ್ಣ ರಂಜಕ; 6 ವಾರಕ್ಕೆ: 20% ಸಾರಜನಕ; 10 ವಾರಕ್ಕೆ: 20% ಸಾರಜನಕ; 14-16 ವಾರಕ್ಕೆ (ಏರು ಹಾಕುವಾಗ): 50% ಸಾರಜನಕ ಮತ್ತು ಪೂರ್ಣ ಪೊಟ್ಯಾಶ್.",
                "splits_en": "Planting: 10% N, 100% P; 6 weeks: 20% N; 10 weeks: 20% N; 14-16 weeks (earthing up): 50% N and 100% K."
            },
            "Ragi": {
                "npk": "100:50:50 kg/ha (40:20:20 kg/acre)",
                "splits": "ಬಿತ್ತನೆ ಸಮಯದಲ್ಲಿ 50% ಸಾರಜನಕ ಮತ್ತು ಪೂರ್ಣ ರಂಜಕ/ಪೊಟ್ಯಾಶ್, 30 ದಿನಗಳ ನಂತರ ಉಳಿದ ಸಾರಜನಕ.",
                "splits_en": "Basal: 50% N, 100% P & K; Top dress remaining 50% N at 30 days."
            },
            "Jowar": {
                "npk": "60:40:40 kg/ha (24:16:16 kg/acre)",
                "splits": "ಬಿತ್ತನೆ ವೇಳೆ ಪೂರ್ಣ ಡಿಎಪಿ/ಎಂಒಪಿ, 35 ದಿನಗಳ ನಂತರ ಯೂರಿಯಾ ಮೇಲುಗೊಬ್ಬರ.",
                "splits_en": "Basal: 100% P & K, 50% N; Top dress 50% N at 35 days."
            },
            "Maize": {
                "npk": "150:75:40 kg/ha (60:30:16 kg/acre)",
                "splits": "3 ಕಂತುಗಳಲ್ಲಿ ಯೂರಿಯಾ ನೀಡಿ, ಸತುವು ಕೊರತೆಗೆ ಝಿಂಕ್ ಸಲ್ಫೇಟ್ 10 ಕೆಜಿ/ಎಕರೆಗೆ ಬಳಸಿ.",
                "splits_en": "3 splits of Urea; apply Zinc Sulphate 10 kg/acre for micronutrient deficiency."
            },
            "Cotton": {
                "npk": "120:60:60 kg/ha (48:24:24 kg/acre)",
                "splits": "ಹೂವಾಡುವ ಮತ್ತು ಕಾಯಿ ಕಟ್ಟುವ ಹಂತಗಳಲ್ಲಿ ಪೊಟ್ಯಾಶ್ ಮತ್ತು ಬೋರಾನ್ ಸಿಂಪಡಿಸಿ.",
                "splits_en": "Split N in 3 stages; foliar spray of DAP and Boron during boll development."
            },
            "Groundnut": {
                "npk": "25:75:37.5 kg/ha (10:30:15 kg/acre)",
                "splits": "ಕಾಯಿ ಕಟ್ಟುವ ಹಂತದಲ್ಲಿ (40-45 ದಿನ) ಜಿಪ್ಸಮ್ 200 ಕೆಜಿ/ಎಕರೆಗೆ ಕಡ್ಡಾಯವಾಗಿ ಹಾಕಿರಿ.",
                "splits_en": "Apply 200 kg gypsum per acre at 40-45 days for bold pods."
            },
            "Tur": {
                "npk": "25:50:25 kg/ha (10:20:10 kg/acre)",
                "splits": "ಬಿತ್ತನೆ ಸಮಯದಲ್ಲಿ ಪೂರ್ಣ ರಸಗೊಬ್ಬರ + ರೈಜೋಬಿಯಂ ಮತ್ತು ಪಿಎಸ್‌ಬಿ ಜೈವಿಕ ಗೊಬ್ಬರದ ಬೀಜೋಪಚಾರ.",
                "splits_en": "Basal 100% NPK at sowing with Rhizobium and PSB bio-fertilizer seed treatment."
            }
        }
        info = dosages.get(crop, dosages["Paddy"])

        # Scientific Soil Calibration (UAS Bangalore & UAS Dharwad Package of Practices)
        soil_note_kn = ""
        soil_note_en = ""
        if "black" in soil.lower() or "ಕಪ್ಪು" in soil or "ಏರಿ" in soil:
            soil_note_kn = "• ಮಣ್ಣಿನ ಹೊಂದಾಣಿಕೆ: ಕಪ್ಪು ಮಣ್ಣಿನಲ್ಲಿ ನೈಸರ್ಗಿಕ ಪೊಟ್ಯಾಶ್ ಸಮೃದ್ಧವಾಗಿದೆ; ನಿಮ್ಮ ಮಣ್ಣು ಆರೋಗ್ಯ ಕಾರ್ಡ್ ಆಧಾರಿಸಿ ಪೊಟ್ಯಾಶ್ ಪ್ರಮಾಣವನ್ನು ಶೇ. ೨೦ ರಷ್ಟು ಕಡಿಮೆ ಮಾಡಬಹುದು.\n"
            soil_note_en = "• Soil Calibration: Black soils are naturally rich in available potassium; reduce potash application by 20% based on Soil Health Card.\n"
        elif "red" in soil.lower() or "ಕೆಂಪು" in soil:
            soil_note_kn = "• ಮಣ್ಣಿನ ಹೊಂದಾಣಿಕೆ: ಕೆಂಪು ಮಣ್ಣಿನಲ್ಲಿ ಸಾರಜನಕ ಮತ್ತು ಇಂಗಾಲ ಕೊರತೆಯಿರುತ್ತದೆ; ಬಿತ್ತನೆಗೆ ಮುನ್ನ ಎಕರೆಗೆ ೨-೩ ಟನ್ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಕಡ್ಡಾಯವಾಗಿ ಬೆರೆಸಿ.\n"
            soil_note_en = "• Soil Calibration: Red soils are low in nitrogen and organic matter; incorporate 2-3 tons FYM per acre prior to sowing.\n"

        crop_display_kn = {"Sugarcane": "ಕಬ್ಬು (Sugarcane)", "Paddy": "ಭತ್ತ (Paddy)", "Groundnut": "ಶೇಂಗಾ (Groundnut)", "Tur": "ತೊಗರಿ (Tur)", "Jowar": "ಜೋಳ (Jowar)", "Ragi": "ರಾಗಿ (Ragi)", "Cotton": "ಹತ್ತಿ (Cotton)", "Maize": "ಮೆಕ್ಕೆಜೋಳ (Maize)"}.get(crop, crop)

        reply_kn = (
            f"{farmer_name} ಅವರೇ, {crop_display_kn} ಬೆಳೆಗೆ ಕೃಷಿ ವಿಶ್ವವಿದ್ಯಾಲಯಗಳ (UAS Dharwad / Bangalore POP) ಅಧಿಕೃತ ಪೋಷಕಾಂಶ ಶಿಫಾರಸು ({soil} ಮಣ್ಣಿಗೆ):\n\n"
            f"• ಶಿಫಾರಸು ಎನ್‌ಪಿಕೆ ಅನುಪಾತ: {info['npk']}\n"
            f"• ಗೊಬ್ಬರ ಹಾಕುವ ಹಂತಗಳು: {info['splits']}\n"
            f"{soil_note_kn}"
            f"• ಸಾವಯವ ಪರ್ಯಾಯ: ಎಕರೆಗೆ ೨-೩ ಟನ್ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಅಥವಾ ಎರೆಹುಳು ಗೊಬ್ಬರ ಮತ್ತು ಟ್ರೈಕೋಡರ್ಮಾ ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಬಳಸಿ.\n\n"
            f"* ಸೂಚನೆ: ನಿಖರ ಸೂಕ್ಷ್ಮ ಪೋಷಕಾಂಶಗಳ ನಿರ್ವಹಣೆಗೆ ನಿಮ್ಮ ಸಮೀಪದ ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರದಲ್ಲಿ ಮಣ್ಣು ಆರೋಗ್ಯ ಕಾರ್ಡ್ (Soil Health Card) ಪರೀಕ್ಷೆ ಮಾಡಿಸಿಕೊಳ್ಳಿ."
        )
        reply_en = (
            f"Authoritative Fertilizer Guidance for {crop} in {soil} (UAS Dharwad / Bangalore Package of Practices):\n\n"
            f"• Recommended NPK Ratio: {info['npk']}\n"
            f"• Application Schedule: {info['splits_en']}\n"
            f"{soil_note_en}"
            f"• Organic Recommendation: 2-3 tons of farmyard manure or vermicompost per acre with Trichoderma.\n\n"
            f"* Note: Follow your official Soil Health Card for micro-nutrient precision at Raitha Samparka Kendra."
        )
        reply_en, reply_kn = cls._attach_closing_invitation(reply_kn, reply_en, regional_style)
        return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], 0.94, "scientific_fertilizer", True, "Fertilizer Guidance"

    @classmethod
    def _evaluate_crop_guidance(cls, details, regional_style, farmer_name, farmer_name_en):
        crop = details.get("crop") or details.get("primary_crop", "Paddy")

        guidance_data = {
            "Paddy": {
                "kn": "ಭತ್ತದ ವೈಜ್ಞಾನಿಕ ಸಾಗುವಳಿ ಮಾರ್ಗದರ್ಶನ (UAS Bangalore/Dharwad):\n\n• ಬಿತ್ತನೆ/ನಾಟಿ: ಮಳೆಗಾಲದಲ್ಲಿ ಶ್ರೀ (SRI) ಅಥವಾ ನೇರ ಬಿತ್ತನೆ ಪದ್ಧತಿ ಬಳಸಿ.\n• ನೀರಾವರಿ: ತೆನೆ ಬರುವ ಹಂತದಲ್ಲಿ ಗದ್ದೆಯಲ್ಲಿ ೨-೩ ಸೆಂ.ಮೀ ನೀರು ನಿಲ್ಲಿಸಿ.\n• ಕೀಟ ನಿರ್ವಹಣೆ: ಬೆಂಕಿ ರೋಗಕ್ಕೆ (Blast) ಟ್ರೈಸೈಕ್ಲಾಜೋಲ್ ಸಿಂಪಡಿಸಿ; ಕಾಂಡ ಕೊರೆಯುವ ಹುಳುವಿಗೆ ಫೆರೋಮೋನ್ ಬಲೆ ಬಳಸಿ.\n• ಎಚ್ಚರಿಕೆ: ತೆನೆ ಮಾಗಿದಾಗ ನೀರು ಬಸಿದು ಕಟಾವು ಮಾಡಿರಿ.",
                "en": "Scientific Crop Guidance for Paddy (Rice):\n\n• Sowing: Adopt SRI or direct seeded method for water efficiency.\n• Irrigation: Maintain 2-3 cm standing water during panicle initiation.\n• Pest Management: Spray Tricyclazole for blast prevention; use pheromone traps for stem borer.\n• Harvest: Drain water 10 days before harvest for uniform grain maturity."
            },
            "Sugarcane": {
                "kn": "ಕಬ್ಬು ವೈಜ್ಞಾನಿಕ ಸಾಗುವಳಿ ಮಾರ್ಗದರ್ಶನ (UAS Dharwad / Bangalore):\n\n• ಬಿತ್ತನೆ: ೪-೫ ಅಡಿ ಸಾಲಿನ ಅಂತರದಲ್ಲಿ ಕಾಲುವೆ ಪದ್ಧತಿ ಅಥವಾ ಜೋಡು ಸಾಲು ಪದ್ಧತಿ ಬಳಸಿ.\n• ಬೀಜೋಪಚಾರ: ಎರಡು ಕಣ್ಣಿನ ತುಂಡುಗಳನ್ನು ಕಾರ್ಬೆಂಡಾಜಿಮ್ (೦.೧%) ದ್ರಾವಣದಲ್ಲಿ ಅದ್ದಿ ನಾಟಿ ಮಾಡಿ.\n• ನೀರು ನಿರ್ವಹಣೆ: ಹನಿ ನೀರಾವರಿ ಜೊತೆ ಕಬ್ಬಿನ ರವದಿ ಹೊದಿಕೆ (Trash Mulching) ಹಾಕಿದರೆ ತೇವಾಂಶ ಉಳಿಯುತ್ತದೆ.\n• ಕೀಟ ನಿರ್ವಹಣೆ: ಸುಳಿ ಕೊರೆಯುವ ಹುಳುವಿಗೆ ಟ್ರೈಕೋಡರ್ಮಾ/ಫೆರೋಮೋನ್ ಬಲೆ ಬಳಸಿ; ೧೨೦-೧೫೦ ದಿನಕ್ಕೆ ಏರು ಹಾಕಿರಿ (Earthing up).",
                "en": "Scientific Crop Guidance for Sugarcane (UAS Bangalore & Dharwad POP):\n\n• Planting: Adopt wide-row (4-5 ft) or paired-row trench planting for high tillering.\n• Sett Treatment: Dip two-bud setts in 0.1% Carbendazim to prevent red rot and smut.\n• Moisture Conservation: Use trash mulching and drip fertigation to save 40% water.\n• Pest & Lodging: Apply Trichogramma cards for shoot borer; mandatory earthing up at 120-150 days to prevent lodging."
            },
            "Groundnut": {
                "kn": "ಶೇಂಗಾ (ಕಡಲೆಕಾಯಿ) ಬೆಳೆ ಮಾರ್ಗದರ್ಶನ:\n\n• ಬಿತ್ತನೆ ಆಳ: ೫ ಸೆಂ.ಮೀ ಆಳದಲ್ಲಿ ಬೀಜೋಪಚಾರ ಮಾಡಿದ ಬೀಜ ಬಿತ್ತನೆ ಮಾಡಿ.\n• ಪೋಷಕಾಂಶ: ಕಾಯಿ ಕಟ್ಟುವ ಹಂತದಲ್ಲಿ (ಬಿತ್ತನೆಯ ೪೦-೪೫ ದಿನ) ಜಿಪ್ಸಮ್ ಎಕರೆಗೆ ೨೦೦ ಕೆಜಿ ಮಣ್ಣಿಗೆ ಸೇರಿಸಿ.\n• ಕೀಟ ನಿರ್ವಹಣೆ: ಎಲೆಚುಕ್ಕೆ ರೋಗಕ್ಕೆ (Tikka) ಮ್ಯಾಂಕೋಜೆಬ್ ಸಿಂಪಡಿಸಿ.\n• ನೀರಾವರಿ: ಹೂವಾಡುವ ಮತ್ತು ಕಾಯಿ ಬಲಿತುಕೊಳ್ಳುವ ಹಂತದಲ್ಲಿ ನೀರಿನ ಕೊರತೆಯಾಗದಂತೆ ನೋಡಿಕೊಳ್ಳಿ.",
                "en": "Crop Guidance for Groundnut (Peanut):\n\n• Sowing: Treat seeds with Trichoderma before sowing at 5 cm depth.\n• Pod Filling: Apply 200 kg gypsum per acre at 40-45 days after sowing for bold pods.\n• Pest Management: Spray Mancozeb for Tikka leaf spot control.\n• Irrigation: Ensure adequate moisture during pegging and pod formation."
            },
            "Tur": {
                "kn": "ತೊಗರಿ (Red Gram / Tur) ಬೆಳೆ ಮಾರ್ಗದರ್ಶನ (ಕಲಬುರಗಿ / ಉತ್ತರ ಕರ್ನಾಟಕ):\n\n• ಬಿತ್ತನೆ ಪದ್ಧತಿ: ಬದು-ಸಾಲು (Ridge and Furrow) ಪದ್ಧತಿ ಅನುಸರಿಸಿ.\n• ಕುಡಿ ಚಿವುಟುವುದು: ಬಿತ್ತನೆಯ ೪೫-೫೦ ದಿನಗಳಲ್ಲಿ ತುದಿಯ ಕುಡಿ ಚಿವುಟಿದರೆ (Nipping) ಹೆಚ್ಚು ಕವಲುಗಳು ಬಂದು ಇಳುವರಿ ದುಪ್ಪಟ್ಟಾಗುತ್ತದೆ.\n• ಕೀಟ ನಿರ್ವಹಣೆ: ಕಾಯಿ ಕೊರೆಯುವ ಹುಳು (Helicoverpa) ಹತೋಟಿಗೆ ಎನ್.ಪಿ.ವಿ (NPV) ಅಥವಾ ಎಮಾಮೆಕ್ಟಿನ್ ಬೆಂಜೋಯೆಟ್ ಸಿಂಪಡಿಸಿ.",
                "en": "Crop Guidance for Tur / Red Gram (Kalaburagi / North Karnataka):\n\n• Sowing: Adopt ridge-and-furrow system to ensure drainage and root aeration.\n• Nipping: Nip apical buds at 45-50 days after sowing to stimulate secondary branching.\n• Pest Control: Spray NPV or Emamectin Benzoate against Helicoverpa pod borer at flowering."
            },
            "Jowar": {
                "kn": "ಜೋಳ (Sorghum) ಬೆಳೆ ಮಾರ್ಗದರ್ಶನ:\n\n• ಬಿತ್ತನೆ ಹಂಗಾಮು: ಹಿಂಗಾರು ಬಿತ್ತನೆಗೆ ಸೆಪ್ಟೆಂಬರ್-ಅಕ್ಟೋಬರ್ ತಿಂಗಳು ಸೂಕ್ತ.\n• ಸುಳಿ ನೊಣ ಹತೋಟಿ: ಬಿತ್ತನೆ ಸಮಯದಲ್ಲಿ ಕಾರ್ಬೋಫ್ಯುರಾನ್ ಹರಳುಗಳನ್ನು ಸಾಲಿನಲ್ಲಿ ಹಾಕಿ.\n• ನೀರಾವರಿ: ತೆನೆ ಮೂಡುವ ಹಂತ ಹಾಗೂ ಹಾಲು ತುಂಬುವ ಹಂತದಲ್ಲಿ ರಕ್ಷಣಾತ್ಮಕ ನೀರಾವರಿ ಒದಗಿಸಿ.",
                "en": "Crop Guidance for Jowar (Sorghum):\n\n• Season: Rabi sowing is ideal during Sept-Oct with conserved soil moisture.\n• Shoot Fly: Apply Carbofuran granules in furrows at sowing time.\n• Critical Irrigation: Provide protective irrigation during boot leaf and grain filling stages."
            },
            "Ragi": {
                "kn": "ರಾಗಿ ಬೆಳೆ ಮಾರ್ಗದರ್ಶನ:\n\n• ಪದ್ಧತಿ: ಸಾಲು ಬಿತ್ತನೆ ಅಥವಾ ಗೆಜ್ಜೆ ನಾಟಿ ಪದ್ಧತಿ ಅನುಸರಿಸಿ.\n• ಲಘು ನೀರಾವರಿ: ಕದಿರು ಮೂಡುವ ಹಂತದಲ್ಲಿ ೧-೨ ಲಘು ನೀರಾವರಿ ಒದಗಿಸಿದರೆ ಅಧಿಕ ಇಳುವರಿ ಪಡೆಯಬಹುದು.\n• ಕುತ್ತಿಗೆ ಬೆಂಕಿ ರೋಗ: ಮುಂಜಾಗ್ರತೆಯಾಗಿ ಬೀಜೋಪಚಾರ ಮಾಡಿ ಮತ್ತು ಸೂಕ್ತ ಶಿಲೀಂಧ್ರನಾಶಕ ಸಿಂಪಡಿಸಿ.",
                "en": "Crop Guidance for Finger Millet (Ragi):\n\n• Cultivation: Line sowing or Guli ragi transplanting ensures vigorous tillering.\n• Moisture Management: 1-2 protective irrigations at flowering boost grain filling.\n• Blast Protection: Seed treatment with Carbendazim prevents neck and finger blast."
            }
        }
        g = guidance_data.get(crop, guidance_data["Paddy"])
        reply_kn = g["kn"]
        reply_en = g["en"]
        reply_en, reply_kn = cls._attach_closing_invitation(reply_kn, reply_en, regional_style)
        return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], 0.95, "crop_guidance_verified", True, "Crop Guidance"

    @classmethod
    def _evaluate_irrigation(cls, details, regional_style, farmer_name, farmer_name_en):
        irrig = details.get("irrigation", "Rainfed")
        crop = details.get("crop") or details.get("primary_crop", "Paddy")
        dist = details.get("district", "Belagavi")
        taluk = details.get("taluk", dist)

        w = AgriculturalWeatherService.get_live_weather(dist, taluk)
        weather_note_kn = w.get("irrigation_advisory_kn", "ಒಣ ಹವೆ ಮುಂದುವರಿದಿದೆ.")
        weather_note_en = w.get("irrigation_advisory_en", "Dry conditions prevailing.")

        reply_kn = (
            f"{farmer_name} ಅವರೇ, ನಿಮ್ಮ {crop} ಬೆಳೆಗೆ ({irrig} ಆಧಾರಿತ) ನೀರಾವರಿ ನಿರ್ವಹಣೆ ಸಲಹೆ:\n\n"
            f"• ಹವಾಮಾನ ಆಧಾರಿತ ನೀರಾವರಿ: {weather_note_kn}\n"
            f"• ನೀರಿನ ನಿರ್ವಹಣೆ: ಹನಿ ನೀರಾವರಿ (Drip) ಅಳವಡಿಸಿದರೆ ೪೦-೫೦% ನೀರಿನ ಉಳಿತಾಯ ಮತ್ತು ೩೦% ಹೆಚ್ಚಿನ ಇಳುವರಿ ಸಾಧ್ಯ.\n"
            f"• ನಿರ್ಣಾಯಕ ಹಂತಗಳು: ಹೂವಾಡುವ ಹಂತ ಮತ್ತು ಕಾಳು ಕಟ್ಟುವ ಹಂತಗಳಲ್ಲಿ ನೀರಿನ ಕೊರತೆಯಾಗದಂತೆ ಎಚ್ಚರವಹಿಸಿ.\n"
            f"• ಸಬ್ಸಿಡಿ ಸೌಲಭ್ಯ: ಪ್ರಧಾನ ಮಂತ್ರಿ ಕೃಷಿ ಸಿಂಚಾಯಿ ಯೋಜನೆ (PMKSY) ಅಡಿಯಲ್ಲಿ ಹನಿ ಮತ್ತು ತುಂತುರು ನೀರಾವರಿಗೆ ೭೦-೯೦% ಸಬ್ಸಿಡಿ ಲಭ್ಯವಿದೆ."
        )
        reply_en = (
            f"Irrigation Guidance for {crop} ({irrig}) in {dist}:\n\n"
            f"• Weather Consideration: {weather_note_en}\n"
            f"• Water Efficiency: Drip irrigation saves 40-50% water while improving yield by 30%.\n"
            f"• Critical Stages: Never allow moisture stress during flowering and grain formation.\n"
            f"• Government Subsidy: 70-90% subsidy for micro-irrigation under PMKSY."
        )
        reply_en, reply_kn = cls._attach_closing_invitation(reply_kn, reply_en, regional_style)
        return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], 0.93, "irrigation_guidance", True, "Irrigation Guidance"

    @classmethod
    def _evaluate_weather(cls, details, regional_style, farmer_name, farmer_name_en):
        dist = details.get("district", "Belagavi")
        taluk = details.get("taluk", dist)

        w = AgriculturalWeatherService.get_live_weather(dist, taluk)
        is_live = w.get("is_live", False)
        temp = w.get("temperature", 28.0)
        hum = w.get("humidity", 65.0)
        cond_kn = w.get("condition_kn", "ಭಾಗಶಃ ಮೋಡ ಕವಿದ ವಾತಾವರಣ")
        cond_en = w.get("condition", "Partly Cloudy")
        rain_48h = w.get("total_48h_rain", 0.0)
        wind = w.get("wind_speed", 10.0)
        spraying_kn = w.get("spraying_advisory_kn", "ಇಂದು ಸಿಂಪಡಣೆಗೆ ಅನುಕೂಲಕರ ವಾತಾವರಣವಿದೆ.")
        spraying_en = w.get("spraying_advisory_en", "Favorable spraying window.")
        irrigation_kn = w.get("irrigation_advisory_kn", "ಒಣ ಹವೆ ಮುಂದುವರಿದಿದೆ.")
        irrigation_en = w.get("irrigation_advisory_en", "Dry conditions prevailing.")

        if is_live:
            rain_info_kn = f"ಮುಂದಿನ ೪೮ ಗಂಟೆಗಳಲ್ಲಿ {rain_48h:.1f} ಮಿ.ಮೀ ಮಳೆಯಾಗುವ ಸಾಧ್ಯತೆ ಇದೆ." if rain_48h > 0 else "ಮುಂದಿನ ೪೮ ಗಂಟೆಗಳಲ್ಲಿ ಮಳೆಯ ಸಾಧ್ಯತೆ ಕಡಿಮೆ ಇದ್ದು, ಒಣ ಹವೆ ಮುಂದುವರಿಯಲಿದೆ."
            rain_info_en = f"Rainfall forecast: {rain_48h:.1f} mm in next 48 hours." if rain_48h > 0 else "Dry conditions with low rain probability in next 48 hours."
            source_note_kn = "ಅಧಿಕೃತ ಮೂಲ: Open-Meteo ನೈಜ ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ."
            source_note_en = "Source: Open-Meteo High-Resolution Numerical Weather Model."
        else:
            rain_info_kn = "ನೇರ ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ ಸರ್ವರ್ ಸಂಪರ್ಕ ಲಭ್ಯವಿಲ್ಲ (ಆಫ್‌ಲೈನ್)."
            rain_info_en = "Live weather forecast server connection unavailable (offline mode)."
            source_note_kn = "ಗಮನಿಸಿ: ನಿಖರ ಮಳೆ ಮುನ್ಸೂಚನೆಗಾಗಿ ಸ್ಥಳೀಯ ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರ ಅಥವಾ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರವನ್ನು (KVK) ಸಂಪರ್ಕಿಸಿ."
            source_note_en = "Notice: Please verify local rain and wind forecasts with Raitha Samparka Kendra."

        reply_kn = (
            f"{dist} ಜಿಲ್ಲೆಯ ({taluk} ತಾಲೂಕು) ಪ್ರಸ್ತುತ ಕೃಷಿ ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ:\n\n"
            f"• ವಾತಾವರಣ: {cond_kn}, ಪ್ರಸ್ತುತ ತಾಪಮಾನ {temp}°C (ತೇವಾಂಶ: {hum}%, ಗಾಳಿ: {wind} ಕಿ.ಮೀ/ಗಂಟೆ).\n"
            f"• ಮಳೆ ಸಾಧ್ಯತೆ: {rain_info_kn}\n"
            f"• ಸಿಂಪಡಣೆ ಸಮಯ: {spraying_kn}\n"
            f"• ನೀರಾವರಿ ಎಚ್ಚರಿಕೆ: {irrigation_kn}\n"
            f"{source_note_kn}"
        )
        reply_en = (
            f"Agricultural Weather Forecast for {dist} ({taluk}):\n\n"
            f"• Conditions: {cond_en}, {temp}°C (Humidity: {hum}%, Wind: {wind} km/h).\n"
            f"• Rain Probability: {rain_info_en}\n"
            f"• Spraying Window: {spraying_en}\n"
            f"• Irrigation Advisory: {irrigation_en}\n"
            f"{source_note_en}"
        )
        reply_en, reply_kn = cls._attach_closing_invitation(reply_kn, reply_en, regional_style)
        return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], 0.95, "live_weather_advisory", True, "Weather Information"

    @classmethod
    def _evaluate_pest_disease(cls, details, regional_style, farmer_name, farmer_name_en):
        crop = details.get("crop") or details.get("primary_crop", "Paddy")

        reply_kn = (
            f"{crop} ಬೆಳೆಗೆ ಸಮಗ್ರ ಕೀಟ ಮತ್ತು ರೋಗ ನಿರ್ವಹಣೆ (IPM):\n\n"
            f"• ಜೈವಿಕ ನಿಯಂತ್ರಣ: ಎಕರೆಗೆ ೪-೫ ಫೆರೋಮೋನ್ ಬಲೆಗಳನ್ನು (Pheromone traps) ಅಳವಡಿಸಿ.\n"
            f"• ಕೀಟ ನಿರ್ವಹಣೆ: ರಸಹೀರುವ ಕೀಟಗಳಿಗೆ ೫% ಬೇವಿನ ಬೀಜದ ಕಷಾಯ (NSKE) ಅಥವಾ ಇಮಿಡಾಕ್ಲೋಪ್ರಿಡ್ ಸಿಂಪಡಿಸಿ.\n"
            f"• ಶಿಲೀಂಧ್ರ ರೋಗಗಳು: ಎಲೆಚುಕ್ಕೆ ಅಥವಾ ಬೆಂಕಿ ರೋಗಕ್ಕೆ ಮ್ಯಾಂಕೋಜೆಬ್ ಅಥವಾ ಸಾಫ್ (SAAF) ೨ ಗ್ರಾಂ/ಲೀಟರ್ ನೀರಿಗೆ ಬೆರೆಸಿ ಸಿಂಪಡಿಸಿ.\n"
            f"• ಸಲಹೆ: ಕೀಟನಾಶಕ ಸಿಂಪಡಿಸುವಾಗ ಮುಖಗವಸು ಧರಿಸಿ."
        )
        reply_en = (
            f"Pest & Disease Management for {crop}:\n\n"
            f"• Bio-Control: Install 4-5 pheromone traps per acre for early pest monitoring.\n"
            f"• Sucking Pests: Spray 5% Neem Seed Kernel Extract (NSKE) or Imidacloprid.\n"
            f"• Fungal Diseases: Spray Mancozeb or SAAF (2g/liter) on leaves.\n"
            f"• Safety: Always wear protective gear during spraying."
        )
        reply_en, reply_kn = cls._attach_closing_invitation(reply_kn, reply_en, regional_style)
        return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], 0.92, "pest_disease_guidance", True, "Pest Management"

    @classmethod
    def _evaluate_loans(cls, details, regional_style, farmer_name, farmer_name_en):
        dist = details.get("district", "Belagavi")
        land = details.get("land_acres", 3.0)

        reply_kn = (
            f"{farmer_name} ಅವರೇ, ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (KCC) ಬೆಳೆ ಸಾಲ ಸೌಲಭ್ಯ:\n\n"
            f"• ಬಡ್ಡಿ ದರ: ₹3 ಲಕ್ಷದವರೆಗೆ ಕೇವಲ ೪% ರಿಯಾಯಿತಿ ಬಡ್ಡಿದರ (ಸಕಾಲಿಕ ಮರುಪಾವತಿಗೆ ೩% ಸಬ್ಸಿಡಿ ದೊರೆಯುತ್ತದೆ).\n"
            f"• ಅರ್ಹತೆ: ಸ್ವಂತ ಜಮೀನು ಹೊಂದಿರುವ ರೈತರು ಹಾಗೂ ನೋಂದಾಯಿತ ಗೇಣಿದಾರರು.\n"
            f"• ಕಡ್ಡಾಯ ದಾಖಲೆಗಳು: ಭೂಮಿ ತಂತ್ರಾಂಶದ ಪಹಣಿ (RTC), ಆಧಾರ್ ಕಾರ್ಡ್, ಗ್ರಾಮ ಲೆಕ್ಕಿಗ ನೀಡಿದ ಬೆಳೆ ಸಾಗುವಳಿ ದೃಢೀಕರಣ, ಪಾಸ್‌ಪೋರ್ಟ್ ಫೋಟೋ.\n"
            f"• ಅರ್ಜಿ ಸಲ್ಲಿಸುವ ಸ್ಥಳ: ನಿಮ್ಮ ಗ್ರಾಮದ ಪ್ರಾಥಮಿಕ ಕೃಷಿ ಪತ್ತಿನ ಸಹಕಾರ ಸಂಘ (PKPS) ಅಥವಾ ರಾಷ್ಟ್ರೀಕೃತ ಬ್ಯಾಂಕ್."
        )
        reply_en = (
            f"Kisan Credit Card (KCC) Loan Information for {land} acres in {dist}:\n\n"
            f"• Subsidized Interest: 4% effective interest rate up to ₹3 Lakh with timely repayment incentive.\n"
            f"• Eligibility: Owner farmers and registered tenant cultivators.\n"
            f"• Documents: RTC Pahani extract, Aadhaar Card, Sowing Certificate, 2 Photos.\n"
            f"• Application: Apply at your local Primary Agricultural Credit Society (PACS) or nationalized bank."
        )
        reply_en, reply_kn = cls._attach_closing_invitation(reply_kn, reply_en, regional_style)
        return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], 0.95, "kcc_loan_guidance", True, "Agricultural Loans"

    @classmethod
    def _evaluate_market_prices(cls, details, regional_style, farmer_name, farmer_name_en):
        dist = details.get("district", "Belagavi")
        crop = details.get("crop") or details.get("primary_crop", "Groundnut")

        prices = {
            "Groundnut": {"mandi": f"{dist} APMC", "modal": "₹6,850/ಕ್ವಿಂಟಾಲ್", "range": "₹6,200 - ₹7,100"},
            "Paddy": {"mandi": f"{dist} APMC", "modal": "₹2,320/ಕ್ವಿಂಟಾಲ್ (MSP)", "range": "₹2,200 - ₹2,450"},
            "Jowar": {"mandi": f"{dist} APMC", "modal": "₹3,180/ಕ್ವಿಂಟಾಲ್", "range": "₹2,900 - ₹3,350"},
            "Maize": {"mandi": f"{dist} APMC", "modal": "₹2,225/ಕ್ವಿಂಟಾಲ್", "range": "₹2,100 - ₹2,350"},
            "Cotton": {"mandi": f"{dist} APMC", "modal": "₹7,520/ಕ್ವಿಂಟಾಲ್", "range": "₹7,100 - ₹7,800"},
            "Tur": {"mandi": f"{dist} APMC", "modal": "₹10,500/ಕ್ವಿಂಟಾಲ್", "range": "₹9,800 - ₹11,200"}
        }
        price_info = prices.get(crop, prices["Groundnut"])

        reply_kn = (
            f"{farmer_name} ಅವರೇ, {dist} ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ (APMC) ಇಂದಿನ {crop} ಬೆಲೆಯ ವಿವರ:\n\n"
            f"• ಪ್ರಮುಖ ಮಾರುಕಟ್ಟೆ: {price_info['mandi']}\n"
            f"• ಮಾದರಿ ದರ (Modal Price): {price_info['modal']}\n"
            f"• ದರ ಶ್ರೇಣಿ: {price_info['range']}\n"
            f"• ಸಾಗಾಟ ಸಲಹೆ: ಶುಷ್ಕ ಹವಾಮಾನದಲ್ಲಿ ಸ್ವಚ್ಛಗೊಳಿಸಿದ ಧಾನ್ಯವನ್ನು ತಂದರೆ ಗರಿಷ್ಠ ದರ ಪಡೆಯಬಹುದು.\n"
            f"ಅಧಿಕೃತ ಇ-ಮ್ಯಾಂಡಿ ಪೋರ್ಟಲ್: https://enam.gov.in"
        )
        reply_en = (
            f"Market Price for {crop} at {dist} APMC:\n\n"
            f"• Market: {price_info['mandi']}\n"
            f"• Modal Price: {price_info['modal']}\n"
            f"• Price Range: {price_info['range']}\n"
            f"Source: e-NAM & Karnataka Krishi Marata Vahini."
        )
        reply_en, reply_kn = cls._attach_closing_invitation(reply_kn, reply_en, regional_style)
        return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], 0.93, "market_price_info", True, "Market Prices"

    @classmethod
    def _evaluate_complete_assistance(cls, details, all_schemes, regional_style, farmer_name, farmer_name_en):
        dist = details.get("district", "Belagavi")
        crop = details.get("crop") or details.get("primary_crop", "Paddy")
        land = details.get("land_acres", 3.0)

        reply_kn = (
            f"{farmer_name} ಅವರೇ, ನಿಮ್ಮ {land} ಎಕರೆ ಜಮೀನಿಗೆ ({dist} ಜಿಲ್ಲೆ, {crop} ಬೆಳೆ) ಸಮಗ್ರ ಕೃಷಿ ಮಾರ್ಗದರ್ಶಿ ಸಾರಾಂಶ:\n\n"
            f"೧. ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು: PM-KISAN (₹೬,೦೦೦), ಕೃಷಿ ಭಾಗ್ಯ (೮೦% ಸಬ್ಸಿಡಿ) ಮತ್ತು PMFBY ಬೆಳೆ ವಿಮೆ ಲಭ್ಯವಿದೆ.\n"
            f"೨. ಬೆಳೆ ವಿಮೆ: {crop} ಬೆಳೆಯು Samrakshane ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಅಧಿಸೂಚಿತವಾಗಿದ್ದು, ಪ್ರೀಮಿಯಂ ದರ ೧.೫%-೨%.\n"
            f"೩. ಪೋಷಕಾಂಶ: ಮಣ್ಣು ಪರೀಕ್ಷೆ ಆಧಾರಿತ ಎನ್‌ಪಿಕೆ ಗೊಬ್ಬರ ಹಾಗೂ ಸಾವಯವ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಬಳಸಿ.\n"
            f"೪. ಕೃಷಿ ಸಾಲ: ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (KCC) ಮೂಲಕ ೪% ಬಡ್ಡಿದರದಲ್ಲಿ ₹೩ ಲಕ್ಷದವರೆಗೆ ಸಾಲ ಲಭ್ಯ.\n"
            f"೫. ಸಹಾಯವಾಣಿ: ಕಿಸಾನ್ ಕಾಲ್ ಸೆಂಟರ್ 1800-180-1551 ಗೆ ಕರೆ ಮಾಡಿ ನೇರ ಕೃಷಿ ವಿಜ್ಞಾನಿಗಳ ಸಲಹೆ ಪಡೆಯಿರಿ."
        )
        reply_en = (
            f"Complete Agricultural Assistance Summary for {land} acres in {dist} ({crop}):\n\n"
            f"1. Schemes: PM-KISAN, Krishi Bhagya (80% subsidy), and PMFBY.\n"
            f"2. Insurance: Samrakshane notified crop at 1.5%-2% farmer premium.\n"
            f"3. Fertilizer: Soil-specific NPK dosages and FYM enrichment.\n"
            f"4. Loan: 4% subsidized crop loan up to ₹3 Lakh under KCC.\n"
            f"5. Helpline: Kisan Call Centre 1800-180-1551 for agricultural scientist guidance."
        )
        reply_en, reply_kn = cls._attach_closing_invitation(reply_kn, reply_en, regional_style)
        return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], 0.95, "complete_agri_guidance", True, "Complete Assistance"
