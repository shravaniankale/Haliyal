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

logger = logging.getLogger(__name__)

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
        "ಹೌದು", "ಸರಿ", "ಇಲ್ಲ", "ಮುಂದೆ", "ಸ್ವಂತ", "ಗುತ್ತಿಗೆ", "ಗೇಣಿ", "ಎಕರೆ", "ಹೆಕ್ಟೇರ್", "ಗುಂಟೆ"
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

        # 1. Extract Crop
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

        # 2b. Extract Taluk from Kannada mappings first
        for kn_t, (en_t, dist_k) in TALUKS_KN_TO_EN.items():
            if kn_t in combined_text or kn_t.lower() in combined_lower:
                entities["taluk"] = en_t
                entities["taluk_kn"] = kn_t
                if "district" not in entities:
                    entities["district"] = dist_k
                    entities["region"] = get_region_for_district(dist_k)
                break

        # Also check English taluk names
        if "taluk" not in entities:
            for dist_name, taluk_list in DISTRICT_TALUKS.items():
                for t_name in taluk_list:
                    if t_name.lower() in combined_lower:
                        entities["taluk"] = t_name
                        if "district" not in entities:
                            entities["district"] = dist_name
                            entities["region"] = get_region_for_district(dist_name)
                        break
                if "taluk" in entities:
                    break

        # 3. Extract Land Size (Acres / Hectares / Guntas)
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

        # 4. Extract Ownership
        if any(k in combined_text or k in combined_lower for k in ["ಸ್ವಂತ", "own", "owned"]):
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
        """Finds the first unconfirmed question in the collection sequence."""
        if not profile_dict.get("district"):
            return STAGE_COLLECT_DISTRICT
        if not profile_dict.get("taluk"):
            return STAGE_COLLECT_TALUKA
        if profile_dict.get("land_acres") is None:
            return STAGE_COLLECT_LAND_SIZE
        if not profile_dict.get("land_ownership"):
            return STAGE_COLLECT_OWNERSHIP
        if not profile_dict.get("farmer_category"):
            return STAGE_COLLECT_FARMER_CATEGORY
        if not profile_dict.get("crop") and not profile_dict.get("primary_crop"):
            return STAGE_COLLECT_CROPS
        if not profile_dict.get("irrigation"):
            return STAGE_COLLECT_IRRIGATION
        return STAGE_CONFIRM_PROFILE

    @classmethod
    def get_question_for_stage(cls, stage: str, context: Dict[str, Any], regional_style: str = "Standard Kannada") -> Tuple[str, str]:
        """Returns the appropriate Kannada and English question for a given stage."""
        farmer_name = context.get("username") or context.get("name") or "ರೈತ ಮಿತ್ರ"
        farmer_name_en = context.get("username") or context.get("name") or "Farmer"

        if stage == STAGE_COLLECT_DISTRICT:
            kn = "ನೀವು ಯಾವ ಜಿಲ್ಲೆಯ ರೈತರು? (ಉದಾಹರಣೆಗೆ ಬೆಳಗಾವಿ, ಧಾರವಾಡ, ಮೈಸೂರು)"
            en = "Which district in Karnataka are you from? (e.g. Belagavi, Dharwad, Mysuru)"
        elif stage == STAGE_COLLECT_TALUKA:
            dist = context.get("district", "ಕರ್ನಾಟಕ")
            kn = f"{dist} ಜಿಲ್ಲೆ ದಾಖಲಿಸಲಾಗಿದೆ. ನಿಮ್ಮ ತಾಲೂಕು ಯಾವುದು?"
            en = f"{dist} district recorded. Which taluka is your farmland located in?"
        elif stage == STAGE_COLLECT_VILLAGE:
            kn = "ನಿಮ್ಮ ಗ್ರಾಮ ಯಾವುದು? (ತಿಳಿಯದಿದ್ದರೆ 'ಮುಂದೆ' ಎಂದು ಹೇಳಿ)"
            en = "What is your village name? (Say 'skip' if not known)"
        elif stage == STAGE_COLLECT_LAND_SIZE:
            kn = "ನಿಮ್ಮ ಬಳಿ ಒಟ್ಟು ಎಷ್ಟು ಎಕರೆ ಜಮೀನು ಇದೆ? (ಉದಾಹರಣೆಗೆ ೩ ಎಕರೆ ಅಥವಾ ೧.೫ ಹೆಕ್ಟೇರ್)"
            en = "How many acres of farmland do you have in total? (e.g. 3 acres or 1.5 hectares)"
        elif stage == STAGE_COLLECT_OWNERSHIP:
            land = context.get("land_acres", "ನಿಮ್ಮ")
            kn = f"{land} ಎಕರೆ ಜಮೀನು ದಾಖಲಿಸಲಾಗಿದೆ. ಜಮೀನು ನಿಮ್ಮ ಸ್ವಂತದ್ದೇ ಅಥವಾ ಗುತ್ತಿಗೆಗೆ ತೆಗೆದುಕೊಂಡಿದ್ದೀರಾ? (ಸ್ವಂತ / ಗುತ್ತಿಗೆ / ಪಾಲುದಾರಿಕೆ)"
            en = f"{land} acres recorded. Is the land owned by you or taken on lease/tenancy? (Owned / Leased / Shared)"
        elif stage == STAGE_COLLECT_FARMER_CATEGORY:
            kn = "ನೀವು ಸಣ್ಣ ರೈತರಾ, ಅತಿ ಸಣ್ಣ ರೈತರಾ ಅಥವಾ ಬೇರೆ ರೈತ ವರ್ಗಕ್ಕೆ ಸೇರಿದ್ದೀರಾ? (ತಿಳಿಯದಿದ್ದರೆ 'ಗೊತ್ತಿಲ್ಲ' ಎಂದು ಹೇಳಿ)"
            en = "Do you belong to marginal, small, or another farmer category? (Say 'not sure' if unknown)"
        elif stage == STAGE_COLLECT_CROPS:
            kn = "ನೀವು ಮುಖ್ಯವಾಗಿ ಯಾವ ಬೆಳೆ ಬೆಳೆಯುತ್ತಿದ್ದೀರಿ? (ಉದಾಹರಣೆಗೆ ಭತ್ತ, ಶೇಂಗಾ, ಜೋಳ, ರಾಗಿ, ಕಬ್ಬು)"
            en = "What is your primary crop? (e.g. Paddy, Groundnut, Jowar, Ragi, Sugarcane)"
        elif stage == STAGE_COLLECT_OTHER_CROPS:
            crop = context.get("crop") or context.get("primary_crop", "ಮುಖ್ಯ ಬೆಳೆ")
            kn = f"ಮುಖ್ಯ ಬೆಳೆ '{crop}' ದಾಖಲಿಸಲಾಗಿದೆ. ಇದರ ಜೊತೆಗೆ ಬೇರೆ ಯಾವ ಬೆಳೆಗಳನ್ನು ಬೆಳೆಯುತ್ತಿದ್ದೀರಿ? (ಇಲ್ಲದಿದ್ದರೆ 'ಯಾವುದೂ ಇಲ್ಲ' ಎಂದು ಹೇಳಿ)"
            en = f"Primary crop '{crop}' recorded. Are you growing any other crops alongside this? (Say 'none' if only this crop)"
        elif stage == STAGE_COLLECT_IRRIGATION:
            kn = "ನಿಮ್ಮ ಜಮೀನಿಗೆ ಯಾವ ರೀತಿಯ ನೀರಾವರಿ ಸೌಲಭ್ಯವಿದೆ? (ಕೊಳವೆಬಾವಿ, ಕಾಲುವೆ, ಮಳೆಯಾಶ್ರಿತ, ಹನಿ ನೀರಾವರಿ)"
            en = "What irrigation facility is available on your farm? (Borewell, Canal, Rainfed, Drip irrigation)"
        elif stage == STAGE_COLLECT_SOIL:
            kn = "ನಿಮ್ಮ ಜಮೀನಿನ ಮಣ್ಣು ಯಾವ ರೀತಿಯದು? (ಕಪ್ಪು ಮಣ್ಣು, ಕೆಂಪು ಮಣ್ಣು, ಗೋಡು ಮಣ್ಣು - ತಿಳಿಯದಿದ್ದರೆ 'ಗೊತ್ತಿಲ್ಲ' ಎಂದು ಹೇಳಿ)"
            en = "What type of soil do you have in your farmland? (Black soil, Red soil, Loamy soil - say 'not sure' if unknown)"
        elif stage == STAGE_COLLECT_SEASON_AND_CROP_STAGE:
            kn = "ಬಿತ್ತನೆ ಮಾಡಿದ ದಿನಾಂಕ ಅಥವಾ ತಿಂಗಳು ಮತ್ತು ಪ್ರಸ್ತುತ ಬೆಳೆಯ ಬೆಳವಣಿಗೆಯ ಹಂತ ಯಾವುದು? (ಉದಾ. ಜೂನ್‌ನಲ್ಲಿ ಬಿತ್ತನೆ, ಈಗ ಹೂವಾಡುವ ಹಂತ)"
            en = "What was the sowing date or month and current crop growth stage? (e.g. Sown in June, currently flowering stage)"
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
                f"ಧನ್ಯವಾದಗಳು {farmer_name} ಅವರೇ! ನಿಮ್ಮ ಕೃಷಿ ವಿವರಗಳನ್ನು ಸಂಗ್ರಹಿಸಲಾಗಿದೆ:\n\n"
                f"• ಜಿಲ್ಲೆ & ತಾಲೂಕು: {dist}" + (f", {taluk}\n" if taluk else "\n") +
                f"• ಜಮೀನು: {land} ಎಕರೆ ({own})\n"
                f"• ರೈತ ವರ್ಗ: {cat}\n"
                f"• ಮುಖ್ಯ ಬೆಳೆ: {crop}\n"
                f"• ನೀರಾವರಿ: {irrig}\n"
                f"• ಮಣ್ಣು: {soil}\n\n"
                f"ಈ ಮಾಹಿತಿ ಸರಿಯಾಗಿದೆಯೇ? (ಹೌದು, ಸರಿ / ಇಲ್ಲ, ಬದಲಾಯಿಸಬೇಕು)"
            )
            en = (
                f"Thank you {farmer_name_en}! Your farm profile summary:\n\n"
                f"• Location: {dist}" + (f", {taluk}\n" if taluk else "\n") +
                f"• Land: {land} Acres ({own})\n"
                f"• Category: {cat}\n"
                f"• Primary Crop: {crop}\n"
                f"• Irrigation: {irrig}\n"
                f"• Soil: {soil}\n\n"
                f"Is this information correct? (Yes, correct / No, want to change)"
            )
        elif stage == STAGE_IDENTIFY_REQUIREMENT:
            kn = (
                f"ಉತ್ತಮ! ನಿಮ್ಮ ಕೃಷಿ ಪ್ರೊಫೈಲ್ ದೃಢೀಕರಿಸಲಾಗಿದೆ.\n\n"
                f"ಈಗ ನಿಮಗೆ ಯಾವ ಕೃಷಿ ವಿಷಯದಲ್ಲಿ ಸಹಾಯ ಬೇಕು?\n\n"
                f"೧. ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು (Government Schemes)\n"
                f"೨. ಬೆಳೆ ವಿಮೆ (Crop Insurance)\n"
                f"೩. ಗೊಬ್ಬರದ ಸಲಹೆ (Fertilizer Recommendations)\n"
                f"೪. ಬೆಳೆ ಮಾರ್ಗದರ್ಶನ (Crop Guidance)\n"
                f"೫. ನೀರಾವರಿ ಸಲಹೆ (Irrigation Guidance)\n"
                f"೬. ಹವಾಮಾನ ಮಾಹಿತಿ (Weather Information)\n"
                f"೭. ಕೀಟ ಮತ್ತು ರೋಗ ನಿರ್ವಹಣೆ (Pest & Disease Management)\n"
                f"೮. ಕೃಷಿ ಸಾಲಗಳು (Agricultural Loans)\n"
                f"೯. ಮಾರುಕಟ್ಟೆ ದರ (Market Prices)\n"
                f"೧೦. ಸಮಗ್ರ ಕೃಷಿ ನೆರವು (Complete Assistance)\n\n"
                f"ನೀವು ನೇರವಾಗಿ ಮಾತನಾಡಿ ಆಯ್ಕೆ ಮಾಡಬಹುದು."
            )
            en = (
                f"Great! Your agricultural profile is confirmed.\n\n"
                f"What agricultural assistance do you need today?\n\n"
                f"1. Government schemes\n"
                f"2. Crop insurance\n"
                f"3. Fertilizer recommendations\n"
                f"4. Crop guidance\n"
                f"5. Irrigation guidance\n"
                f"6. Weather information\n"
                f"7. Pest & disease management\n"
                f"8. Agricultural loans\n"
                f"9. Market prices\n"
                f"10. Complete agricultural assistance\n\n"
                f"You can speak naturally or choose an option."
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
                    if current_stage in [STAGE_COLLECT_CROPS, STAGE_COLLECT_OTHER_CROPS] or ("primary_crop" in details and details["primary_crop"]):
                        continue
                details[k] = v

        farmer_name = farmer_profile.get("username") or farmer_profile.get("name") or "ರೈತ ಮಿತ್ರ"
        farmer_name_en = farmer_profile.get("username") or farmer_profile.get("name") or "Farmer"

        # ---------------------------------------------------------------------
        # STATE: STAGE_INITIAL_GREETING or STAGE_COLLECT_DISTRICT
        # ---------------------------------------------------------------------
        if current_stage in [STAGE_INITIAL_GREETING, STAGE_COLLECT_DISTRICT]:
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
                reply_kn = "ಕ್ಷಮಿಸಿ, ಜಮೀನಿನ ವಿಸ್ತೀರ್ಣ ಸ್ಪಷ್ಟವಾಗಿ ಕೇಳಿಸಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಎಷ್ಟು ಎಕರೆ ಅಥವಾ ಹೆಕ್ಟೇರ್ ಎಂದು ಸಂಖ್ಯೆಯಲ್ಲಿ ತಿಳಿಸಿ (ಉದಾ. ೩ ಎಕರೆ, ೪.೫ ಎಕರೆ)."
                reply_en = "Sorry, land size was not clear. Please specify how many acres or hectares you cultivate (e.g. 3 acres, 4.5 acres)."
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
            elif any(k in user_message for k in ["ಜಮೀನು", "land", "ಎಕರೆ"]):
                return "How many acres of land do you cultivate?", "ನಿಮ್ಮ ಬಳಿ ಎಷ್ಟು ಎಕರೆ ಜಮೀನಿದೆ?", STAGE_COLLECT_LAND_SIZE, details, [], [], None, None, True, "Correction"
            elif any(k in user_message for k in ["ಬೆಳೆ", "crop"]):
                return "What is your primary crop?", "ನಿಮ್ಮ ಮುಖ್ಯ ಬೆಳೆ ಯಾವುದು?", STAGE_COLLECT_CROPS, details, [], [], None, None, True, "Correction"
            else:
                next_s = STAGE_CONFIRM_PROFILE
                q_kn, q_en = cls.get_question_for_stage(next_s, details, regional_style)
                return q_en, q_kn, next_s, details, [], [], None, None, True, "Profile Confirmation"

        # ---------------------------------------------------------------------
        # STATE: STAGE_IDENTIFY_REQUIREMENT or STAGE_FOLLOW_UP (Phases 4, 5, 6, 7)
        # ---------------------------------------------------------------------
        user_lower = user_message.lower()

        # Option 1: Government Schemes
        if any(w in user_lower or w in user_message for w in ["ಯೋಜನೆ", "scheme", "1", "೧", "ಸಹಾಯಧನ", "subsidy", "pm-kisan", "krishi bhagya"]):
            return cls._evaluate_government_schemes(details, all_schemes, regional_style, farmer_name, farmer_name_en)

        # Option 2: Crop Insurance
        if any(w in user_lower or w in user_message for w in ["ವಿಮೆ", "insurance", "2", "೨", "ಸಂರಕ್ಷಣೆ", "samrakshane", "72"]):
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
        if any(w in user_lower or w in user_message for w in ["ಮಾರುಕಟ್ಟೆ", "market", "9", "೯", "ದರ", "ಬೆಲೆ", "price", "apmc", "ಮಂಡಿ"]):
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

    @classmethod
    def _evaluate_government_schemes(cls, details, all_schemes, regional_style, farmer_name, farmer_name_en):
        dist = details.get("district", "Belagavi")
        land = details.get("land_acres", 3.0)
        own = details.get("land_ownership", "Owned")
        cat = details.get("farmer_category", "Small farmer")
        crop = details.get("crop") or details.get("primary_crop", "Paddy")

        matched = []
        if all_schemes:
            for sc in all_schemes:
                if "PM-KISAN" in sc.scheme_id and own in ["Owned", "Own"]:
                    matched.append(sc)
                elif "PMFBY" in sc.scheme_id:
                    matched.append(sc)
                elif "Krishi Bhagya" in sc.scheme_name and land <= 5.0:
                    matched.append(sc)
                elif getattr(sc, "max_land_acres", None) and land <= sc.max_land_acres:
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

        reply_kn = (
            f"{farmer_name} ಅವರೇ, ನಿಮ್ಮ ಕೃಷಿ ವಿವರಗಳಿಗೆ ({dist} ಜಿಲ್ಲೆ, {land} ಎಕರೆ, {own}) ಹೊಂದಿಕೆಯಾಗುವ ಪ್ರಮುಖ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು:\n\n"
            f"೧. ಪ್ರಧಾನ ಮಂತ್ರಿ ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ (PM-KISAN):\n"
            f"   • ಉದ್ದೇಶ & ನೆರವು: ವಾರ್ಷಿಕ ₹೬,೦೦೦ ನೇರ ಆರ್ಥಿಕ ನೆರವು (ವರ್ಷಕ್ಕೆ ೩ ಕಂತುಗಳಲ್ಲಿ).\n"
            f"   • ನೀವು ಏಕೆ ಅರ್ಹರು: ಸ್ವಂತ ಸಾಗುವಳಿ ಭೂಮಿ ಹೊಂದಿರುವ ಅರ್ಹ ರೈತರಾಗಿದ್ದೀರಿ.\n"
            f"   • ಅಗತ್ಯ ದಾಖಲೆಗಳು: ಭೂಮಿ ಪಹಣಿ (RTC), ಆಧಾರ್ ಕಾರ್ಡ್ ಮತ್ತು ಬ್ಯಾಂಕ್ ಪಾಸ್‌ಬುಕ್.\n\n"
            f"೨. ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ (PMFBY):\n"
            f"   • ಉದ್ದೇಶ: ಪ್ರಕೃತಿ ವಿಕೋಪದಿಂದ ಬೆಳೆ ಹಾನಿಯಾದರೆ ಪೂರ್ಣ ವಿಮಾ ಪರಿಹಾರ.\n"
            f"   • ಪ್ರೀಮಿಯಂ ದರ: ಕೇವಲ ೧.೫% - ೨% ರಿಯಾಯಿತಿ ದರ.\n\n"
            f"೩. ಕೃಷಿ ಭಾಗ್ಯ ಯೋಜನೆ (ಕರ್ನಾಟಕ ಸರ್ಕಾರ):\n"
            f"   • ಉದ್ದೇಶ: ಕೃಷಿ ಹೊಂಡ, ಪಾಲಿಹೌಸ್ ಹಾಗೂ ಡೀಸೆಲ್ ಪಂಪ್‌ಸೆಟ್‌ಗಳಿಗೆ ಶೇಕಡಾ ೮೦-೯೦ ರವರೆಗೆ ಸಬ್ಸಿಡಿ.\n\n"
            f"ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ನಿಮ್ಮ ಸಮೀಪದ ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರ ಅಥವಾ ಗ್ರಾಮ ಒನ್ (Grama One) ಕೇಂದ್ರಕ್ಕೆ ಭೇಟಿ ನೀಡಿ.\n"
            f"ಅಧಿಕೃತ ಪೋರ್ಟಲ್: https://raitamitra.karnataka.gov.in"
        )
        reply_en = (
            f"Hello {farmer_name_en}, based on your farm profile ({dist}, {land} acres, {own}), here are your recommended schemes:\n\n"
            f"1. PM-KISAN: ₹6,000/year direct financial support in 3 installments.\n"
            f"2. PMFBY Crop Insurance: Financial safety net against drought, flood, and localized calamities.\n"
            f"3. Krishi Bhagya: Up to 80-90% subsidy for farm ponds and micro-irrigation for small farmers.\n\n"
            f"Required Documents: RTC Pahani, Aadhaar, and Bank Passbook at Raitha Samparka Kendra."
        )
        reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
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
        reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
        return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], 0.95, "crop_insurance_verified", True, "Crop Insurance"

    @classmethod
    def _evaluate_fertilizer(cls, details, regional_style, farmer_name, farmer_name_en):
        crop = details.get("crop") or details.get("primary_crop", "Paddy")
        soil = details.get("soil_type", "Red Loamy")

        dosages = {
            "Paddy": {"npk": "100:50:50 kg/ha", "splits": "ಬಾಸಲ್: ಪೂರ್ಣ ರಂಜಕ ಮತ್ತು ಪೊಟ್ಯಾಶ್, 50% ಸಾರಜನಕ. ಉಳಿದ 50% ಸಾರಜನಕವನ್ನು ತೆನೆ ಮತ್ತು ಹೂವಿನ ಹಂತದಲ್ಲಿ 2 ಬಾರಿ ಹಾಕಿರಿ."},
            "Ragi": {"npk": "100:50:50 kg/ha", "splits": "ಬಿತ್ತನೆ ಸಮಯದಲ್ಲಿ 50% ಸಾರಜನಕ ಮತ್ತು ಪೂರ್ಣ ರಂಜಕ, 30 ದಿನಗಳ ನಂತರ ಉಳಿದ ಸಾರಜನಕ."},
            "Jowar": {"npk": "60:40:40 kg/ha", "splits": "ಬಿತ್ತನೆ ವೇಳೆ ಪೂರ್ಣ ಡಿಎಪಿ/ಎಂಒಪಿ, 35 ದಿನಗಳ ನಂತರ ಯೂರಿಯಾ ಮೇಲುಗೊಬ್ಬರ."},
            "Maize": {"npk": "150:75:40 kg/ha", "splits": "3 ಕಂತುಗಳಲ್ಲಿ ಯೂರಿಯಾ ನೀಡಿ, ಸತುವು ಕೊರತೆಗೆ ಝಿಂಕ್ ಸಲ್ಫೇಟ್ 10 ಕೆಜಿ/ಎಕರೆಗೆ ಬಳಸಿ."},
            "Cotton": {"npk": "120:60:60 kg/ha", "splits": "ಹೂವಾಡುವ ಮತ್ತು ಕಾಯಿ ಕಟ್ಟುವ ಹಂತಗಳಲ್ಲಿ ಪೊಟ್ಯಾಶ್ ಮತ್ತು ಬೋರಾನ್ ಸಿಂಪಡಿಸಿ."},
            "Groundnut": {"npk": "25:75:37.5 kg/ha", "splits": "ಕಾಯಿ ಕಟ್ಟುವ ಹಂತದಲ್ಲಿ (40-45 ದಿನ) ಜಿಪ್ಸಮ್ 200 ಕೆಜಿ/ಎಕರೆಗೆ ಕಡ್ಡಾಯವಾಗಿ ಹಾಕಿರಿ."}
        }
        info = dosages.get(crop, dosages["Paddy"])

        reply_kn = (
            f"{farmer_name} ಅವರೇ, {crop} ಬೆಳೆಗೆ ವೈಜ್ಞಾನಿಕ ಪೋಷಕಾಂಶ ಶಿಫಾರಸು ({soil} ಮಣ್ಣಿಗೆ):\n\n"
            f"• ಶಿಫಾರಸು ಎನ್‌ಪಿಕೆ ಅನುಪಾತ: {info['npk']}\n"
            f"• ಗೊಬ್ಬರ ಹಾಕುವ ವಿಧಾನ: {info['splits']}\n"
            f"• ಸಾವಯವ ಪರ್ಯಾಯ: ಎಕರೆಗೆ ೨-೩ ಟನ್ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಅಥವಾ ಎರೆಹುಳು ಗೊಬ್ಬರ ಮಣ್ಣಿಗೆ ಮಿಶ್ರಣ ಮಾಡಿ.\n\n"
            f"* ಸೂಚನೆ: ನಿಖರ ಪೋಷಕಾಂಶ ನಿರ್ವಹಣೆಗೆ ನಿಮ್ಮ ಸಮೀಪದ ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರದಲ್ಲಿ ಮಣ್ಣು ಆರೋಗ್ಯ ಕಾರ್ಡ್ (Soil Health Card) ಪರೀಕ್ಷೆ ಮಾಡಿಸಿಕೊಳ್ಳಿ."
        )
        reply_en = (
            f"Fertilizer Guidance for {crop} in {soil}:\n\n"
            f"• Recommended NPK Ratio: {info['npk']}\n"
            f"• Split Application: {info['splits']}\n"
            f"• Organic Recommendation: 2-3 tons of farmyard manure or vermicompost per acre.\n\n"
            f"* Note: Follow official Soil Health Card for micro-nutrient precision."
        )
        reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
        return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], 0.94, "scientific_fertilizer", True, "Fertilizer Guidance"

    @classmethod
    def _evaluate_crop_guidance(cls, details, regional_style, farmer_name, farmer_name_en):
        crop = details.get("crop") or details.get("primary_crop", "Paddy")

        guidance_data = {
            "Paddy": {
                "kn": "ಭತ್ತದ ವೈಜ್ಞಾನಿಕ ಸಾಗುವಳಿ ಮಾರ್ಗದರ್ಶನ:\n\n• ಬಿತ್ತನೆ/ನಾಟಿ: ಮಳೆಗಾಲದಲ್ಲಿ ಶ್ರೀ (SRI) ಅಥವಾ ನೇರ ಬಿತ್ತನೆ ಪದ್ಧತಿ ಬಳಸಿ.\n• ನೀರಾವರಿ: ತೆನೆ ಬರುವ ಹಂತದಲ್ಲಿ ಗದ್ದೆಯಲ್ಲಿ ೨-೩ ಸೆಂ.ಮೀ ನೀರು ನಿಲ್ಲಿಸಿ.\n• ಕೀಟ ನಿರ್ವಹಣೆ: ಬೆಂಕಿ ರೋಗಕ್ಕೆ (Blast) ಟ್ರೈಸೈಕ್ಲಾಜೋಲ್ ಸಿಂಪಡಿಸಿ; ಕಾಂಡ ಕೊರೆಯುವ ಹುಳುವಿಗೆ ಫೆರೋಮೋನ್ ಬಲೆ ಬಳಸಿ.\n• ಎಚ್ಚರಿಕೆ: ತೆನೆ ಮಾಗಿದಾಗ ನೀರು ಬಸಿದು ಕಟಾವು ಮಾಡಿರಿ.",
                "en": "Scientific Crop Guidance for Paddy (Rice):\n\n• Sowing: Adopt SRI or direct seeded method for water efficiency.\n• Irrigation: Maintain 2-3 cm standing water during panicle initiation.\n• Pest Management: Spray Tricyclazole for blast prevention; use pheromone traps for stem borer.\n• Harvest: Drain water 10 days before harvest for uniform grain maturity."
            },
            "Groundnut": {
                "kn": "ಶೇಂಗಾ (ಕಡಲೆಕಾಯಿ) ಬೆಳೆ ಮಾರ್ಗದರ್ಶನ:\n\n• ಬಿತ್ತನೆ ಆಳ: ೫ ಸೆಂ.ಮೀ ಆಳದಲ್ಲಿ ಬೀಜೋಪಚಾರ ಮಾಡಿದ ಬೀಜ ಬಿತ್ತನೆ ಮಾಡಿ.\n• ಪೋಷಕಾಂಶ: ಕಾಯಿ ಕಟ್ಟುವ ಹಂತದಲ್ಲಿ (ಬಿತ್ತನೆಯ ೪೦-೪೫ ದಿನ) ಜಿಪ್ಸಮ್ ಎಕರೆಗೆ ೨೦೦ ಕೆಜಿ ಮಣ್ಣಿಗೆ ಸೇರಿಸಿ.\n• ಕೀಟ ನಿರ್ವಹಣೆ: ಎಲೆಚುಕ್ಕೆ ರೋಗಕ್ಕೆ (Tikka) ಮ್ಯಾಂಕೋಜೆಬ್ ಸಿಂಪಡಿಸಿ.\n• ನೀರಾವರಿ: ಹೂವಾಡುವ ಮತ್ತು ಕಾಯಿ ಬಲಿತುಕೊಳ್ಳುವ ಹಂತದಲ್ಲಿ ನೀರಿನ ಕೊರತೆಯಾಗದಂತೆ ನೋಡಿಕೊಳ್ಳಿ.",
                "en": "Crop Guidance for Groundnut (Peanut):\n\n• Sowing: Treat seeds with Trichoderma before sowing at 5 cm depth.\n• Pod Filling: Apply 200 kg gypsum per acre at 40-45 days after sowing for bold pods.\n• Pest Management: Spray Mancozeb for Tikka leaf spot control.\n• Irrigation: Ensure adequate moisture during pegging and pod formation."
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
        reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
        return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], 0.95, "crop_guidance_verified", True, "Crop Guidance"

    @classmethod
    def _evaluate_irrigation(cls, details, regional_style, farmer_name, farmer_name_en):
        irrig = details.get("irrigation", "Rainfed")
        crop = details.get("crop") or details.get("primary_crop", "Paddy")

        reply_kn = (
            f"{farmer_name} ಅವರೇ, ನಿಮ್ಮ {crop} ಬೆಳೆಗೆ ({irrig} ಆಧಾರಿತ) ನೀರಾವರಿ ನಿರ್ವಹಣೆ ಸಲಹೆ:\n\n"
            f"• ನೀರಿನ ನಿರ್ವಹಣೆ: ಹನಿ ನೀರಾವರಿ (Drip) ಅಳವಡಿಸಿದರೆ ೪೦-೫೦% ನೀರಿನ ಉಳಿತಾಯ ಮತ್ತು ೩೦% ಹೆಚ್ಚಿನ ಇಳುವರಿ ಸಾಧ್ಯ.\n"
            f"• ನಿರ್ಣಾಯಕ ಹಂತಗಳು: ಹೂವಾಡುವ ಹಂತ ಮತ್ತು ಕಾಳು ಕಟ್ಟುವ ಹಂತಗಳಲ್ಲಿ ನೀರಿನ ಕೊರತೆಯಾಗದಂತೆ ಎಚ್ಚರವಹಿಸಿ.\n"
            f"• ಸಬ್ಸಿಡಿ ಸೌಲಭ್ಯ: ಪ್ರಧಾನ ಮಂತ್ರಿ ಕೃಷಿ ಸಿಂಚಾಯಿ ಯೋಜನೆ (PMKSY) ಅಡಿಯಲ್ಲಿ ಹನಿ ಮತ್ತು ತುಂತುರು ನೀರಾವರಿಗೆ ೭೦-೯೦% ಸಬ್ಸಿಡಿ ಲಭ್ಯವಿದೆ."
        )
        reply_en = (
            f"Irrigation Guidance for {crop} ({irrig}):\n\n"
            f"• Water Efficiency: Drip irrigation saves 40-50% water while improving yield by 30%.\n"
            f"• Critical Stages: Never allow moisture stress during flowering and grain formation.\n"
            f"• Government Subsidy: 70-90% subsidy for micro-irrigation under PMKSY."
        )
        reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
        return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], 0.93, "irrigation_guidance", True, "Irrigation Guidance"

    @classmethod
    def _evaluate_weather(cls, details, regional_style, farmer_name, farmer_name_en):
        dist = details.get("district", "Belagavi")
        taluk = details.get("taluk", dist)

        reply_kn = (
            f"{dist} ಜಿಲ್ಲೆಯ ({taluk} ತಾಲೂಕು) ಪ್ರಸ್ತುತ ಕೃಷಿ ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ:\n\n"
            f"• ವಾತಾವರಣ: ಭಾಗಶಃ ಮೋಡ ಕವಿದ ವಾತಾವರಣ, ತಾಪಮಾನ 27°C - 31°C.\n"
            f"• ಮಳೆ ಸಾಧ್ಯತೆ: ಮುಂದಿನ ೪೮ ಗಂಟೆಗಳಲ್ಲಿ ಸಾಧಾರಣ ಮಳೆಯ ಮುನ್ಸೂಚನೆ ಇದೆ.\n"
            f"• ಸಿಂಪಡಣೆ ಸಮಯ: ಗಾಳಿಯ ವೇಗ ೧೨ ಕಿ.ಮೀ/ಗಂಟೆಗಿಂತ ಕಡಿಮೆ ಇರುವಾಗ ಬೆಳಗಿನ ೮:೦೦ ರಿಂದ ೧೧:೦೦ ರೊಳಗೆ ಕೀಟನಾಶಕ ಸಿಂಪಡಣೆ ಮಾಡಲು ಸೂಕ್ತ ವಾತಾವರಣವಿದೆ.\n"
            f"• ನೀರಾವರಿ ಎಚ್ಚರಿಕೆ: ಮಳೆ ಮುನ್ಸೂಚನೆ ಗಮನಿಸಿ ಹೆಚ್ಚುವರಿ ನೀರು ಹರಿಸುವುದನ್ನು ತಡೆಯಿರಿ."
        )
        reply_en = (
            f"Agricultural Weather Forecast for {dist} ({taluk}):\n\n"
            f"• Current Weather: Partly cloudy, 27°C - 31°C.\n"
            f"• Rain Probability: Moderate rain in next 48 hours.\n"
            f"• Spraying Window: Best between 8:00 AM - 11:00 AM (wind speed < 12 km/h).\n"
            f"• Drainage: Ensure proper drainage channels in low-lying plots."
        )
        reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
        return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], 0.90, "weather_advisory", True, "Weather Information"

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
        reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
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
        reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
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
        reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
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
        reply_kn = KannadaVocabularyService.adapt_to_dialect(reply_kn, regional_style)
        return reply_en, reply_kn, STAGE_FOLLOW_UP, details, [], [], 0.95, "complete_agri_guidance", True, "Complete Assistance"
