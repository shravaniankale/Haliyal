import re
import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from ..models import Scheme
from .district_service import get_region_for_district, REGIONAL_DIALECT_TOKENS, KARNATAKA_DISTRICTS
from .kannada_speech import KannadaSpeechService

logger = logging.getLogger(__name__)

class AgriculturalConversationalAgent:
    """
    Intelligent Agricultural AI Agent specialized for Karnataka farmers.
    Handles Natural Language Understanding (NLU), Entity Extraction, Context Memory,
    Deterministic Scheme Matching, Missing-Information Detection, and Regional Kannada Dialogue.
    """

    # Crop recognition keywords in Kannada and English
    CROP_MAP = {
        "ಭತ್ತ": "Paddy", "paddy": "Paddy", "rice": "Paddy",
        "ರಾಗಿ": "Ragi", "ragi": "Ragi", "finger millet": "Ragi",
        "ಜೋಳ": "Jowar", "jowar": "Jowar", "sorghum": "Jowar",
        "ಮೆಕ್ಕೆಜೋಳ": "Maize", "maize": "Maize", "corn": "Maize",
        "ಕಬ್ಬು": "Sugarcane", "sugarcane": "Sugarcane",
        "ಹತ್ತಿ": "Cotton", "cotton": "Cotton",
        "ಕಡಲೆಕಾಯಿ": "Groundnut", "ಶೇಂಗಾ": "Groundnut", "groundnut": "Groundnut", "peanut": "Groundnut",
        "ತೊಗರಿ": "Tur", "tur": "Tur", "red gram": "Tur", "ತೊಗರಿಬೇಳೆ": "Tur",
        "ಸೋಯಾಬೀನ್": "Soybean", "soybean": "Soybean",
        "ತೆಂಗು": "Coconut", "coconut": "Coconut",
        "ಅಡಿಕೆ": "Arecanut", "arecanut": "Arecanut",
        "ಕಾಫಿ": "Coffee", "coffee": "Coffee",
    }

    @classmethod
    def extract_entities(cls, text: str) -> Dict[str, Any]:
        """Extracts agricultural entities (Crop, District, Land Acres, Ownership, Problem)."""
        entities: Dict[str, Any] = {}
        text_lower = text.lower()

        # 1. Extract Crop
        for token, crop_name in cls.CROP_MAP.items():
            if token in text or token in text_lower:
                entities["crop"] = crop_name
                break

        # 2. Extract District
        for dist, data in KARNATAKA_DISTRICTS.items():
            if dist.lower() in text_lower or data["kn"] in text:
                entities["district"] = dist
                entities["district_kn"] = data["kn"]
                entities["region"] = data["region"]
                break

        # 3. Extract Land Size (Acres / Guntas)
        # Regex for numbers followed by acre / ಎಕರೆ / gunte / ಗುಂಟೆ
        land_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:ಎಕರೆ|acre|acres|ಎಕರ|ac)', text, re.IGNORECASE)
        if land_match:
            try:
                entities["land_acres"] = float(land_match.group(1))
            except Exception:
                pass
        else:
            # Check for standalone numbers if question mentions land
            if "ಜಮೀನು" in text or "ಭೂಮಿ" in text or "land" in text_lower:
                num_match = re.search(r'(\d+(?:\.\d+)?)', text)
                if num_match:
                    try:
                        entities["land_acres"] = float(num_match.group(1))
                    except Exception:
                        pass

        # 4. Extract Ownership
        if "ಸ್ವಂತ" in text or "own" in text_lower:
            entities["land_ownership"] = "Own"
        elif "ಗೇಣಿ" in text or "tenant" in text_lower or "lease" in text_lower:
            entities["land_ownership"] = "Tenant"

        # 5. Extract Irrigation
        if "ಬೋರ್ವೆಲ್" in text or "ಕೊಳವೆ" in text or "borewell" in text_lower:
            entities["irrigation"] = "Borewell"
        elif "ಮಳೆ" in text or "ಖುಷ್ಕಿ" in text or "rainfed" in text_lower:
            entities["irrigation"] = "Rainfed"
        elif "ಕಾಲುವೆ" in text or "canal" in text_lower:
            entities["irrigation"] = "Canal"

        # 6. Intent classification
        if any(w in text_lower or w in text for w in ["ಯೋಜನೆ", "scheme", "ಸಹಾಯಧನ", "subsidy", "pm-kisan", "pmfby"]):
            entities["intent"] = "scheme_query"
        elif any(w in text_lower or w in text for w in ["ಸಾಲ", "loan", "kcc", "ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್", "ಬ್ಯಾಂಕ್"]):
            entities["intent"] = "loan_query"
        elif any(w in text_lower or w in text for w in ["ಗೊಬ್ಬರ", "fertilizer", "ಯೂರಿಯಾ", "ಡಿಎಪಿ", "npk"]):
            entities["intent"] = "fertilizer_query"
        elif any(w in text_lower or w in text for w in ["ಹವಾಮಾನ", "weather", "ಮಳೆ", "rain"]):
            entities["intent"] = "weather_query"
        elif any(w in text_lower or w in text for w in ["ಬೆಲೆ", "ದರ", "price", "apmc", "ಮಾರ್ಕೆಟ್", "ಮಂಡಿ"]):
            entities["intent"] = "market_query"
        else:
            entities["intent"] = "crop_advisory"

        return entities

    @classmethod
    def generate_response(
        cls,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        farmer_profile: Optional[Dict[str, Any]] = None,
        all_schemes: Optional[List[Scheme]] = None,
        regional_style: str = "Standard Kannada"
    ) -> Tuple[str, str, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Processes conversation, detects context across turns, generates natural Kannada response
        adhering strictly to agricultural domain and regional speech rules.
        """
        # 1. Extract entities from current query
        current_entities = cls.extract_entities(user_message)

        # 2. Reconstruct context from history & profile
        merged_entities = {}
        if farmer_profile:
            if farmer_profile.get("district"):
                merged_entities["district"] = farmer_profile["district"]
            if farmer_profile.get("land_acres"):
                merged_entities["land_acres"] = farmer_profile["land_acres"]
            if farmer_profile.get("land_ownership"):
                merged_entities["land_ownership"] = farmer_profile["land_ownership"]
            if farmer_profile.get("regional_speech_preference"):
                regional_style = farmer_profile["regional_speech_preference"]

        # Scan previous history for remembered entities
        for msg in conversation_history:
            prev_entities = cls.extract_entities(msg.get("text", ""))
            for k, v in prev_entities.items():
                if k not in merged_entities:
                    merged_entities[k] = v

        # Overwrite with newest explicit inputs
        for k, v in current_entities.items():
            merged_entities[k] = v

        # Determine regional style from district if not explicitly locked
        if "district" in merged_entities and regional_style == "Standard Kannada":
            region = get_region_for_district(merged_entities["district"])
            regional_style = region if region in REGIONAL_DIALECT_TOKENS else "Standard Kannada"

        dialect_tokens = REGIONAL_DIALECT_TOKENS.get(regional_style, REGIONAL_DIALECT_TOKENS["Standard Kannada"])

        # Intent handling
        intent = merged_entities.get("intent", "crop_advisory")
        crop = merged_entities.get("crop")
        district = merged_entities.get("district")
        land = merged_entities.get("land_acres")
        ownership = merged_entities.get("land_ownership", "Own")

        recommended_schemes = []

        # Logic Branch 1: Missing information detection
        # If crop is mentioned, but district is unknown:
        if crop and not district:
            if regional_style == "North Karnataka":
                reply_kn = f"ಖುಷಿ ಆಯಿತು ನೋಡ್ರೀ, ನೀವು {crop} ಬೆಳಿತ್ಯೀರಾ. ನಿಮ್ದು ಯಾವ ಜಿಲ್ಲೆ ಅಪ್ಪಾ? ಬೆಳಗಾವಿ, ಧಾರವಾಡ, ವಿಜಯಪುರ ಅಥವಾ ಕಲಬುರಗಿನಾ? ಜಿಲ್ಲೆ ಹೇಳಿದ್ರೆ ಆ ಭಾಗಕ್ಕೆ ಸಿಗುವ ಯೋಜನೆ ತಿಳಿಸ್ತೇನಿ."
                reply_en = f"Great, you grow {crop}. Which district are you from? Sharing your district allows me to find schemes tailored to your region."
            else:
                reply_kn = f"ತಾವು {crop} ಬೆಳೆಯುತ್ತಿರುವುದು ಸಂತಸದ ವಿಷಯ. ತಾವು ಕರ್ನಾಟಕದ ಯಾವ ಜಿಲ್ಲೆಯವರು ಎಂದು ತಿಳಿಸಿ, ನಿಮ್ಮ ಜಿಲ್ಲೆಗೆ ಅನ್ವಯವಾಗುವ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳನ್ನು ಪರಿಶೀಲಿಸುತ್ತೇನೆ."
                reply_en = f"Understood that you cultivate {crop}. Please let me know your district so I can check applicable government schemes."
            return reply_en, reply_kn, [], merged_entities

        # If crop and district known, but land size unknown:
        if crop and district and land is None:
            if regional_style == "North Karnataka":
                reply_kn = f"ಹೌದ್ರೀ, {district} ಜಿಲ್ಲೆಯಾಗ {crop} ಬೆಳೀಲಿಕ್ಕೆ ಸರ್ಕಾರದ ಯೋಜನೆಗಳು ಸಿಗತಾವ ನೋಡ್ರೀ. ನಿಮ್ದು ಜಮೀನು ಎಷ್ಟು ಎಕರೆ ಐತಿ ಹೇಳ್ರಿ? ೫ ಎಕರೆ ಒಳಗೆ ಇದ್ರೆ ಸಣ್ಣ ಹಿಡುವಳಿದಾರರ ಹೆಚ್ಚುವರಿ ಸಬ್ಸಿಡಿ ಸಿಗತೈತಿ."
                reply_en = f"Got it, for {crop} in {district} district, several agricultural schemes exist. How many acres of cultivable land do you have?"
            else:
                reply_kn = f"ಖಂಡಿತ, {district} ಜಿಲ್ಲೆಯಲ್ಲಿ {crop} ಬೆಳೆಗೆ ಸೂಕ್ತವಾದ ಯೋಜನೆಗಳಿವೆ. ತಮ್ಮ ಬಳಿ ಎಷ್ಟು ಎಕರೆ ಜಮೀನು ಇದೆ ಎಂದು ದಯವಿಟ್ಟು ತಿಳಿಸಿ."
                reply_en = f"Certainly, there are eligible schemes for {crop} in {district}. How many acres of land do you hold?"
            return reply_en, reply_kn, [], merged_entities

        # Logic Branch 2: Complete profile - Recommend schemes with exact official evidence
        if crop and district and land is not None:
            # Find schemes from database
            matched_list = []
            if all_schemes:
                for sc in all_schemes:
                    # PM-KISAN check
                    if sc.scheme_id == "PM-KISAN" and ownership == "Own":
                        matched_list.append(sc)
                    # PMFBY check
                    elif sc.scheme_id == "PMFBY":
                        matched_list.append(sc)
                    # Krishi Bhagya
                    elif "Krishi Bhagya" in sc.scheme_name and land <= 5:
                        matched_list.append(sc)

            for s in matched_list[:3]:
                recommended_schemes.append({
                    "scheme_id": s.scheme_id,
                    "scheme_name": s.scheme_name,
                    "scheme_name_kn": s.scheme_name_kn,
                    "benefits": s.benefit_details_kn,
                    "official_url": s.official_url,
                    "verification": s.verification_status
                })

            if regional_style == "North Karnataka":
                reply_kn = (
                    f"ನೋಡ್ರೀ ಅಪ್ಪಾ, {district} ಜಿಲ್ಲೆಯಾಗ {land} ಎಕರೆ ಜಮೀನಲ್ಲಿ {crop} ಬೆಳೆಯುವ ನಿಮಗೆ "
                    f"ಪಿಎಂ-ಕಿಸಾನ್ (ವರ್ಷಕ್ಕೆ ₹6,000 ನೆರವು) ಮತ್ತು ಪ್ರಧಾನಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ (ಬೆಳೆ ವಿಮೆ) "
                    f"ನೇರವಾಗಿ ಅನ್ವಯ ಆಗತಾವ ನೋಡ್ರೀ! ನೀವು ಆಧಾರ್ ಕಾರ್ಡ್ ಮತ್ತು ಜಮೀನಿನ ಪಹಣಿ (RTC) ಇಟ್ಕೊಂಡು ಸಮೀಪದ ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರ ಅಥವಾ ಅಧಿಕೃತ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಅರ್ಜಿ ಹಾಕ್ರಿ."
                )
                reply_en = (
                    f"Based on your profile ({district} district, {land} acres, {crop}), you qualify for PM-KISAN (₹6,000/year direct transfer) "
                    f"and PMFBY (Pradhan Mantri Fasal Bima Yojana crop insurance). Please keep your Aadhaar and RTC (Pahani) ready to apply at Raitha Samparka Kendra or official portals."
                )
            else:
                reply_kn = (
                    f"ತಮ್ಮ ವಿವರಗಳ ಪ್ರಕಾರ ({district} ಜಿಲ್ಲೆ, {land} ಎಕರೆ, {crop} ಬೆಳೆ), ತಮಗೆ "
                    f"ಪಿಎಂ-ಕಿಸಾನ್ ಯೋಜನೆ ಹಾಗೂ ಪ್ರಧಾನಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆಯಡಿ ಬೆಳೆ ವಿಮೆ ಸೌಲಭ್ಯ ಲಭ್ಯವಿದೆ. "
                    f"ಆಧಾರ್ ಕಾರ್ಡ್ ಹಾಗೂ ಪಹಣಿ (RTC) ದಾಖಲೆಗಳೊಂದಿಗೆ ಅಧಿಕೃತ ಪೋರ್ಟಲ್ ಮೂಲಕ ಅರ್ಜಿ ಸಲ್ಲಿಸಬಹುದು."
                )
                reply_en = (
                    f"According to your details ({district} district, {land} acres, {crop}), you are eligible for PM-KISAN financial assistance "
                    f"and PMFBY comprehensive crop insurance. You can apply with your Aadhaar and RTC land records."
                )
            return reply_en, reply_kn, recommended_schemes, merged_entities

        # Logic Branch 3: General greetings and questions
        if "ನಮಸ್ಕಾರ" in user_message or "hello" in user_message.lower() or "hi" in user_message.lower():
            reply_kn = dialect_tokens["greeting"]
            reply_en = "Namaskara! Welcome to Krishi Mitra AI assistant. How can I assist you with government schemes, loans, or crop guidance today?"
            return reply_en, reply_kn, [], merged_entities

        if intent == "loan_query":
            if regional_style == "North Karnataka":
                reply_kn = "ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (KCC) ಮುಖಾಂತರ ರೈತರಿಗೆ ₹3 ಲಕ್ಷದವರೆಗೆ ಶೇ. 4% ಬಡ್ಡಿದರದಲ್ಲಿ ಅಲ್ಪಾವಧಿ ಬೆಳೆ ಸಾಲ ಸಿಗತೈತಿ ನೋಡ್ರೀ. ಬ್ಯಾಂಕ್ ಪಾಸ್‌ಬುಕ್ ಮತ್ತು ಪಹಣಿ ತಗೊಂಡು ಸಮೀಪದ ಗ್ರಾಮೀಣ ಬ್ಯಾಂಕ್‌ಗೆ ಭೇಟಿ ನೀಡಿ."
                reply_en = "Through Kisan Credit Card (KCC), farmers receive short-term crop loans up to ₹3 Lakh at an effective subsidized interest rate of 4% per annum upon prompt repayment."
            else:
                reply_kn = "ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (KCC) ಅಡಿಯಲ್ಲಿ ₹3 ಲಕ್ಷದವರೆಗೆ ಶೇ. 4% ರಿಯಾಯಿತಿ ಬಡ್ಡಿದರದಲ್ಲಿ ಬೆಳೆ ಸಾಲ ದೊರೆಯುತ್ತದೆ. ತಮ್ಮ ಪಹಣಿ ಮತ್ತು ಆಧಾರ್ ಕಾರ್ಡ್‌ನೊಂದಿಗೆ ಸ್ಥಳೀಯ ಬ್ಯಾಂಕ್ ಶಾಖೆಯನ್ನು ಸಂಪರ್ಕಿಸಿ."
                reply_en = "Under Kisan Credit Card (KCC), farmers get crop loans up to ₹3 Lakh at 4% subsidized interest rate with timely repayment."
            return reply_en, reply_kn, [], merged_entities

        # Default helpful fallback
        if regional_style == "North Karnataka":
            reply_kn = "ನಿಮ್ಮ ಕೃಷಿ ಪ್ರಶ್ನೆ ಅರ್ಥ ಆಯ್ತ್ರಿ ನೋಡ್ರೀ. ನೀವು ಯಾವ ಬೆಳೆ ಹಾಕ್ತೀರಿ ಮತ್ತು ಯಾವ ಜಿಲ್ಲೆಯವರು ಅಂತ ಹೇಳಿದ್ರೆ, ಸರ್ಕಾರದ ಸೂಕ್ತ ಯೋಜನೆ ಮತ್ತು ಸಾಲದ ಮಾಹಿತಿ ಪಕ್ಕಾ ಕೊಡ್ತೇನಿ."
            reply_en = "I understand your query. Please let me know which crop you cultivate and your district so I can provide accurate government scheme and loan assistance."
        else:
            reply_kn = "ತಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಗಮನಿಸಿದೆ. ತಾವು ಬೆಳೆಯುವ ಬೆಳೆ, ಜಮೀನಿನ ವಿಸ್ತೀರ್ಣ ಮತ್ತು ಜಿಲ್ಲೆಯ ವಿವರ ನೀಡಿದರೆ ನಿಖರವಾದ ಯೋಜನೆ ಹಾಗೂ ಬೆಳೆ ಮಾರ್ಗದರ್ಶನ ನೀಡುತ್ತೇನೆ."
            reply_en = "I noted your inquiry. Kindly share your crop, landholding acres, and district to receive transparent scheme eligibility details."

        return reply_en, reply_kn, [], merged_entities
