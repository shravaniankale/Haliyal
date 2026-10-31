import logging
import requests
from typing import Dict, Any, Optional, List
from .district_service import get_district_info, DISTRICT_TALUKS

logger = logging.getLogger(__name__)

WEATHER_CODE_MAP = {
    0: ("Clear Sky", "ಸ್ವಚ್ಛ ಆಕಾಶ", "☀️"),
    1: ("Mainly Clear", "ಹೆಚ್ಚಾಗಿ ಸ್ವಚ್ಛ ಆಕಾಶ", "🌤️"),
    2: ("Partly Cloudy", "ಭಾಗಶಃ ಮೋಡ ಕವಿದ ವಾತಾವರಣ", "⛅"),
    3: ("Overcast", "ದಟ್ಟ ಮೋಡ ಕವಿದ ವಾತಾವರಣ", "☁️"),
    45: ("Foggy", "ಮಂಜು ಮುಸುಕಿದ ವಾತಾವರಣ", "🌫️"),
    51: ("Light Drizzle", "ಲಘು ತುಂತುರು ಮಳೆ", "🌦️"),
    53: ("Moderate Drizzle", "ಮಧ್ಯಮ ತುಂತುರು ಮಳೆ", "🌧️"),
    55: ("Dense Drizzle", "ದಟ್ಟ ತುಂತುರು ಮಳೆ", "🌧️"),
    61: ("Slight Rain", "ಹಗುರ ಮಳೆ", "🌦️"),
    63: ("Moderate Rain", "ಸಾಧಾರಣ ಮಳೆ", "🌧️"),
    65: ("Heavy Rain", "ಭಾರೀ ಮಳೆ", "⛈️"),
    80: ("Rain Showers", "ಮಳೆಯ ಸಿಂಚನ", "🌦️"),
    81: ("Moderate Showers", "ಮಳೆಯ ಝರಿ", "🌧️"),
    82: ("Violent Showers", "ಪ್ರಚಂಡ ಮಳೆ", "⛈️"),
    95: ("Thunderstorm", "ಗುಡುಗು ಸಹಿತ ಮಳೆ", "⚡")
}

# Coastal Karnataka Geography Mapping
COASTAL_DISTRICTS = {"Dakshina Kannada", "Udupi", "Uttara Kannada"}

COASTAL_PLAIN_TALUKS = {
    # Dakshina Kannada shoreline/estuary
    "Mangaluru", "Bantwal", "Moodbidri",
    # Udupi shoreline/estuary
    "Udupi", "Kundapura", "Byndoor", "Brahmavara", "Kaup",
    # Uttara Kannada shoreline/estuary
    "Karwar", "Ankola", "Kumta", "Honnavar", "Bhatkal"
}

WESTERN_GHATS_FOOTHILL_TALUKS = {
    # Dakshina Kannada Ghats
    "Belthangady", "Puttur", "Sullia", "Kadaba",
    # Udupi Ghats
    "Karkala", "Hebri",
    # Uttara Kannada Ghats
    "Sirsi", "Siddapur", "Yellapur", "Joida", "Haliyal"
}

COASTAL_RIVERS = {
    "Dakshina Kannada": ["Netravati (ನೇತ್ರಾವತಿ)", "Kumaradhara (ಕುಮಾರಧಾರ)", "Gurupura/Phalguni (ಗುರುಪುರ)", "Nandini (ನಂದಿನಿ)"],
    "Udupi": ["Swarna (ಸ್ವರ್ಣಾ)", "Sita (ಸೀತಾ)", "Varahi (ವಾರಾಹಿ)", "Souparnika (ಸೌಪರ್ಣಿಕಾ)", "Chakra (ಚಕ್ರಾ)"],
    "Uttara Kannada": ["Sharavathi (ಶರಾವತಿ)", "Kali (ಕಾಳಿ)", "Aghanashini (ಅಘನಾಶಿನಿ)", "Gangavali (ಗಂಗಾವಳಿ)", "Bedthi (ಬೇಡ್ತಿ)"]
}

class AgriculturalWeatherService:
    """
    Live and forecasted agro-meteorological service for Karnataka districts and taluks.
    Provides weather intelligence, spraying advisories, irrigation recommendations,
    and specialized Coastal Weather & Flood-Risk Intelligence.
    """

    @classmethod
    def is_coastal_location(cls, district: str, taluk: Optional[str] = None) -> Dict[str, Any]:
        """
        Determines whether a district/taluk is in Coastal Karnataka and classifies
        its geographical micro-zone (Coastal Plain & Estuary vs Western Ghats Foothills vs Inland).
        """
        dist_clean = district.strip().title()
        # Handle variations like "D.K.", "U.K."
        if "Dakshina" in dist_clean or "Mangalore" in dist_clean:
            dist_clean = "Dakshina Kannada"
        elif "Udupi" in dist_clean:
            dist_clean = "Udupi"
        elif "Uttara" in dist_clean or "Karwar" in dist_clean:
            dist_clean = "Uttara Kannada"

        is_coastal = dist_clean in COASTAL_DISTRICTS
        if not is_coastal:
            return {
                "is_coastal": False,
                "district": district,
                "taluk": taluk,
                "zone": "Inland Plateau",
                "zone_kn": "ಒಳನಾಡು ಬಯಲು ಸೀಮೆ",
                "major_rivers": []
            }

        t_clean = (taluk or "").strip().title()
        if t_clean in COASTAL_PLAIN_TALUKS:
            zone = "Coastal Plain & Estuarine Shoreline"
            zone_kn = "ಕರಾವಳಿ ಬಯಲು ಮತ್ತು ನದಿಮುಖಜ ತೀರ ಪ್ರದೇಶ"
        elif t_clean in WESTERN_GHATS_FOOTHILL_TALUKS:
            zone = "Western Ghats Foothills & Catchment"
            zone_kn = "ಪಶ್ಚಿಮ ಘಟ್ಟದ ತಪ್ಪಲು ಮತ್ತು ಜಲಾನಯನ ಪ್ರದೇಶ"
        else:
            # Default for district HQ or unlisted
            if dist_clean in ["Dakshina Kannada", "Udupi"]:
                zone = "Coastal Plain & Estuary"
                zone_kn = "ಕರಾವಳಿ ಬಯಲು ಮತ್ತು ನದಿಮುಖಜ ಪ್ರದೇಶ"
            else:
                zone = "Western Ghats Foothills & Coastal Transition"
                zone_kn = "ಪಶ್ಚಿಮ ಘಟ್ಟದ ತಪ್ಪಲು ಮತ್ತು ಕರಾವಳಿ ಪ್ರದೇಶ"

        rivers = COASTAL_RIVERS.get(dist_clean, [])

        return {
            "is_coastal": True,
            "district": dist_clean,
            "taluk": t_clean or dist_clean,
            "zone": zone,
            "zone_kn": zone_kn,
            "major_rivers": rivers
        }

    @classmethod
    def analyze_coastal_weather_and_flood_risk(
        cls,
        district: str,
        taluk: Optional[str] = None,
        is_live: bool = True,
        rain_current: float = 0.0,
        rain_24h: float = 0.0,
        rain_48h: float = 0.0,
        wind_speed: float = 10.0
    ) -> Dict[str, Any]:
        """
        Comprehensive Coastal Weather, Heavy-Rain and Flood-Risk Intelligence.
        - Produces strictly 1 of 5 Risk Levels:
          LOW RISK, MODERATE RISK, HIGH RISK, OFFICIAL FLOOD WARNING, INSUFFICIENT WEATHER DATA.
        - Scientifically separates Heavy-Rain Risk from Riverine Flood Probability.
        - Formulates proactive crop insurance (PMFBY / Samrakshane) guidance (including 72-hour notification rule).
        - Provides crop-specific drainage and agronomic precautions (Paddy, Arecanut, Banana, Pepper).
        """
        loc_geo = cls.is_coastal_location(district, taluk)
        if not loc_geo["is_coastal"]:
            return {"is_coastal": False}

        # 1. Determine 5-Level Heavy-Rain Risk & Riverine Flood Probability
        if not is_live:
            risk_level = "INSUFFICIENT WEATHER DATA"
            risk_level_kn = "ಹವಾಮಾನ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ (ನೆಟ್‌ವರ್ಕ್ ಆಫ್‌ಲೈನ್)"
            flood_prob = "Insufficient Weather Data"
            flood_prob_kn = "ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ"
            risk_desc_en = "Real-time meteorological feed is currently offline; live rain and flood risk cannot be verified."
            risk_desc_kn = "ನೈಜ ಹವಾಮಾನ ಸರ್ವರ್ ಸಂಪರ್ಕ ಲಭ್ಯವಿಲ್ಲದ ಕಾರಣ ಲೈವ್ ಮಳೆ ಮತ್ತು ಪ್ರವಾಹ ಅಪಾಯವನ್ನು ದೃಢೀಕರಿಸಲು ಸಾಧ್ಯವಾಗಿಲ್ಲ."
        elif rain_24h >= 115.5 or rain_48h >= 150.0:
            risk_level = "OFFICIAL FLOOD WARNING"
            risk_level_kn = "ಅಧಿಕೃತ ಪ್ರವಾಹ ಎಚ್ಚರಿಕೆ"
            flood_prob = "Critical Spate Warning (High Probability)"
            flood_prob_kn = "ತೀವ್ರ ನದಿ ಪ್ರವಾಹ ಮತ್ತು ಉಕ್ಕಿ ಹರಿಯುವ ಅಪಾಯ"
            risk_desc_en = f"Extreme rainfall forecast ({rain_24h:.1f} mm / 24h, {rain_48h:.1f} mm / 48h). High probability of river catchment spate, dam discharges, and low-lying field submersion."
            risk_desc_kn = f"ತೀವ್ರ ಪ್ರಚಂಡ ಮಳೆಯ ಮುನ್ಸೂಚನೆ ({rain_24h:.1f} ಮಿ.ಮೀ/೨೪ ಗಂಟೆ, {rain_48h:.1f} ಮಿ.ಮೀ/೪೮ ಗಂಟೆ). ನದಿಗಳು ಉಕ್ಕಿ ಹರಿಯುವ ಹಾಗೂ ಜಮೀನುಗಳು ಸಂಪೂರ್ಣ ಜಲಾವೃತವಾಗುವ ಗಂಭೀರ ಅಪಾಯವಿದೆ."
        elif rain_24h >= 64.5 or rain_48h >= 70.0:
            risk_level = "HIGH RISK"
            risk_level_kn = "ಹೆಚ್ಚಿನ ಮಳೆ ಅಪಾಯ"
            flood_prob = "High (Catchment Runoff Alert)"
            flood_prob_kn = "ಹೆಚ್ಚಿನ ಪ್ರವಾಹ ಸಾಧ್ಯತೆ (ಘಟ್ಟದ ನೀರಿನ ಹರಿವು)"
            risk_desc_en = f"Very heavy rainfall predicted ({rain_24h:.1f} mm / 24h). Significant surface waterlogging, soil saturation, and local stream overflow expected."
            risk_desc_kn = f"ಭಾರೀ ಮಳೆಯ ಮುನ್ಸೂಚನೆ ({rain_24h:.1f} ಮಿ.ಮೀ/೨೪ ಗಂಟೆ). ಗದ್ದೆಗಳಲ್ಲಿ ನೀರು ನಿಲ್ಲುವಿಕೆ ಹಾಗೂ ಸ್ಥಳೀಯ ಹಳ್ಳಗಳು ಉಕ್ಕಿ ಹರಿಯುವ ಹೆಚ್ಚಿನ ಅಪಾಯವಿದೆ."
        elif rain_24h >= 15.0 or rain_48h >= 30.0:
            risk_level = "MODERATE RISK"
            risk_level_kn = "ಮಧ್ಯಮ ಎಚ್ಚರಿಕೆ"
            flood_prob = "Moderate (Localized Field Inundation)"
            flood_prob_kn = "ಮಧ್ಯಮ ಮಟ್ಟ (ತಗ್ಗು ಜಮೀನುಗಳಲ್ಲಿ ನೀರು ಶೇಖರಣೆ)"
            risk_desc_en = f"Moderate to heavy showers ({rain_24h:.1f} mm / 24h, {rain_48h:.1f} mm / 48h). Localized ponding in low-lying plots; drainage outlets must remain operational."
            risk_desc_kn = f"ಮಧ್ಯಮದಿಂದ ಉತ್ತಮ ಮಳೆ ({rain_24h:.1f} ಮಿ.ಮೀ/೨೪ ಗಂಟೆ). ತಗ್ಗು ಪ್ರದೇಶಗಳಲ್ಲಿ ನೀರು ನಿಲ್ಲುವ ಸಾಧ್ಯತೆ ಇದ್ದು ಬಸಿಗಾಲುವೆಗಳನ್ನು ಸಿದ್ಧವಾಗಿಟ್ಟುಕೊಳ್ಳಿ."
        else:
            risk_level = "LOW RISK"
            risk_level_kn = "ಕಡಿಮೆ ಅಪಾಯ"
            flood_prob = "Low"
            flood_prob_kn = "ಕಡಿಮೆ ಸಾಧ್ಯತೆ"
            risk_desc_en = f"Normal coastal weather with light or isolated showers ({rain_24h:.1f} mm / 24h). No adverse waterlogging expected."
            risk_desc_kn = f"ಸಾಮಾನ್ಯ ಕರಾವಳಿ ಹವಾಮಾನ ({rain_24h:.1f} ಮಿ.ಮೀ/೨೪ ಗಂಟೆ). ಯಾವುದೇ ಪ್ರವಾಹ ಅಥವಾ ಗಂಭೀರ ನೀರು ನಿಲ್ಲುವಿಕೆಯ ಅಪಾಯವಿಲ್ಲ."

        # 2. Heavy-Rain vs Riverine Flood Distinction
        rain_vs_flood_en = (
            "IMPORTANT DISTINCTION: Heavy rainfall indicates localized precipitation and soil saturation within agricultural plots. "
            "In contrast, riverine flooding requires massive runoff accumulation from Western Ghats catchments, upstream reservoir discharges "
            "(e.g., Linganamakki, Kadra, Supa), and high-tide estuarine backflow. Heavy rainfall does NOT automatically mean confirmed river flooding."
        )
        rain_vs_flood_kn = (
            "ಪ್ರಮುಖ ವೈಜ್ಞಾನಿಕ ವ್ಯತ್ಯಾಸ: ಭಾರೀ ಮಳೆಯು ಜಮೀನಿನಲ್ಲಿ ಸ್ಥಳೀಯವಾಗಿ ನೀರು ನಿಲ್ಲುವುದನ್ನು (Waterlogging) ಸೂಚಿಸುತ್ತದೆ. "
            "ಆದರೆ ನದಿ ಪ್ರವಾಹವು (Riverine Flooding) ಪಶ್ಚಿಮ ಘಟ್ಟಗಳ ಜಲಾನಯನ ಪ್ರದೇಶದ ನೀರಿನ ಹರಿವು, ಜಲಾಶಯಗಳ ಹೊರಹರಿವು ಮತ್ತು ಸಮುದ್ರದ ಉಬ್ಬರವಿಳಿತವನ್ನು ಅವಲಂಬಿಸಿರುತ್ತದೆ. "
            "ಭಾರೀ ಮಳೆಯೆಂದರೆ ತಕ್ಷಣವೇ ಖಚಿತ ನದಿ ಪ್ರವಾಹ ಎಂದರ್ಥವಲ್ಲ."
        )

        # 3. Proactive Crop Insurance Advisory (PMFBY / Samrakshane)
        insurance_advisory = {
            "eligible_notified_crops": ["Paddy", "Arecanut", "Banana", "Black Pepper"],
            "notified_status_en": f"Paddy, Arecanut, Banana, and Pepper are officially notified insurable crops in {loc_geo['district']} under PMFBY / Samrakshane.",
            "notified_status_kn": f"{loc_geo['district']} ಜಿಲ್ಲೆಯಲ್ಲಿ ಭತ್ತ, ಅಡಿಕೆ, ಬಾಳೆ ಮತ್ತು ಕಾಳುಮೆಣಸು ಕರ್ನಾಟಕ ಸಂರಕ್ಷಣೆ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಅಧಿಕೃತವಾಗಿ ಅಧಿಸೂಚಿತ ವಿಮಾ ಬೆಳೆಗಳಾಗಿವೆ.",
            "enrollment_window_status_en": "Kharif PMFBY enrollment cutoff has closed for current seasonal sowing. Rabi & Summer PMFBY enrollment window active on Karnataka Samrakshane portal.",
            "enrollment_window_status_kn": "ಖಾರಿಫ್ ಹಂಗಾಮಿನ ಬೆಳೆ ವಿಮೆ ನೋಂದಣಿ ಅಂತಿಮ ದಿನಾಂಕ ಮುಕ್ತಾಯಗೊಂಡಿದೆ. ಹಿಂಗಾರು/ಬೇಸಿಗೆ ಬೆಳೆ ವಿಮೆ ನೋಂದಣಿ ಪ್ರಕ್ರಿಯೆ ಕರ್ನಾಟಕ ಸಂರಕ್ಷಣೆ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಚಾಲ್ತಿಯಲ್ಲಿದೆ.",
            "calamity_72h_rule_en": "MANDATORY 72-HOUR NOTIFICATION WINDOW: Existing insured farmers experiencing localized calamities (inundation, landslide, heavy torrential rain damage) must notify Karnataka Samrakshane within 72 hours via Crop Insurance App, Toll-Free Helpline 1800-180-1551, or Raitha Samparka Kendra.",
            "calamity_72h_rule_kn": "೭೨ ಗಂಟೆಗಳ ಕಡ್ಡಾಯ ನಿಯಮ: ಪ್ರಕೃತಿ ವಿಕೋಪದಿಂದ (ಪ್ರವಾಹ, ನೀರು ನಿಲ್ಲುವಿಕೆ, ಭೂಕುಸಿತ) ಬೆಳೆ ಹಾನಿಯಾದರೆ, ವಿಮೆ ಮಾಡಿಸಿರುವ ರೈತರು ೭೨ ಗಂಟೆಗಳ ಒಳಗೆ ಕ್ರಾಪ್ ಇನ್ಶೂರೆನ್ಸ್ ಆ್ಯಪ್, ಸಹಾಯವಾಣಿ 1800-180-1551 ಅಥವಾ ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರಕ್ಕೆ ಕಡ್ಡಾಯವಾಗಿ ಮಾಹಿತಿ ನೀಡಬೇಕು.",
            "non_retroactive_warning_en": "CRITICAL LEGAL NOTICE: Crop insurance CANNOT be newly purchased post-calamity for an already occurring or anticipated imminent flood loss.",
            "non_retroactive_warning_kn": "ಕಾನೂನು ಸೂಚನೆ: ಈಗಾಗಲೇ ಸಂಭವಿಸುತ್ತಿರುವ ಅಥವಾ ಸಂಭವಿಸಲಿರುವ ಪ್ರವಾಹ ನಷ್ಟಕ್ಕೆ ಮುಂಚಿತವಾಗಿ ಅಥವಾ ನಂತರದಲ್ಲಿ ಹೊಸದಾಗಿ ವಿಮೆ ಖರೀದಿಸಲು ನಿಯಮಗಳಲ್ಲಿ ಅವಕಾಶವಿಲ್ಲ.",
            "helpline": "1800-180-1551",
            "official_portal": "https://samrakshane.karnataka.gov.in"
        }

        # 4. Crop-Specific Agronomic & Drainage Precautions
        crop_precautions = [
            {
                "crop": "Paddy",
                "crop_kn": "ಭತ್ತ",
                "precaution_en": "Clear drainage outlets from field bunds immediately. Do not allow young tillering seedlings to remain submerged under stagnant water for more than 48 hours to avoid crown decay.",
                "precaution_kn": "ಗದ್ದೆಯ ಬದುವಿನ ಬಸಿಗಾಲುವೆ (ತೂಬು) ತೆರೆದು ನೀರು ಸರಾಗವಾಗಿ ಹರಿದುಹೋಗಲು ವ್ಯವಸ್ಥೆ ಮಾಡಿ. ಭತ್ತದ ಸಸಿಗಳು ೪೮ ಗಂಟೆಗಿಂತ ಹೆಚ್ಚು ಕಾಲ ನೀರಿನಲ್ಲಿ ಮುಳುಗದಂತೆ ನೋಡಿಕೊಳ್ಳಿ."
            },
            {
                "crop": "Arecanut",
                "crop_kn": "ಅಡಿಕೆ",
                "precaution_en": "Excavate deep drainage trenches between rows to avoid root suffocation and Mahali / Koleroga (fruit rot). Spray prophylactic 1% Bordeaux mixture during dry breaks in rain. Avoid stagnant water around tree basins.",
                "precaution_kn": "ಅಡಿಕೆ ಮರಗಳ ಬುಡದಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ಸಾಲುಗಳ ನಡುವೆ ಆಳವಾದ ಬಸಿಗಾಲುವೆಗಳನ್ನು ತೆರೆಯಿರಿ. ಕೊಳೆ ರೋಗ (ಮಹಾಲಿ) ತಡೆಗಟ್ಟಲು ಮಳೆಯ ಬಿಡುವಿನ ಸಮಯದಲ್ಲಿ ಶೇ. ೧% ಬೋರ್ಡೋ ದ್ರಾವಣವನ್ನು ಗೊನೆಗಳಿಗೆ ಸಿಂಪಡಿಸಿ."
            },
            {
                "crop": "Banana",
                "crop_kn": "ಬಾಳೆ",
                "precaution_en": "Provide bamboo or rope propping against heavy coastal wind gusts. Drain standing water rapidly to prevent pseudostem and rhizome rot (Erwinia / Corm rot).",
                "precaution_kn": "ಕರಾವಳಿಯ ಬಲವಾದ ಗಾಳಿಗೆ ಬಾಳೆ ಗಿಡಗಳು ಉರುಳದಂತೆ ಬಿದಿರಿನ ಆಸರೆ (ಮುಂಗಟ್ಟು) ನೀಡಿ. ಗೆಡ್ಡೆ ಕೊಳೆ ರೋಗ ತಡೆಯಲು ಗಿಡಗಳ ಬುಡದಿಂದ ಹೆಚ್ಚುವರಿ ನೀರನ್ನು ಕೂಡಲೇ ಹೊರಹಾಕಿ."
            },
            {
                "crop": "Pepper",
                "crop_kn": "ಕಾಳುಮೆಣಸು",
                "precaution_en": "Ensure excellent slope drainage around vine base to prevent Phytophthora foot rot (quick wilt). Remove mud splash from bottom runners and drench root zone with 0.2% Copper Oxychloride or Trichoderma.",
                "precaution_kn": "ಕಾಳುಮೆಣಸಿನ ಬಳ್ಳಿಯ ಬುಡದಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ಎಚ್ಚರವಹಿಸಿ (ಬುಡ ಕೊಳೆ ರೋಗ ತಡೆಗಟ್ಟಲು). ಬಳ್ಳಿಯ ಕೆಳಭಾಗಕ್ಕೆ ಮಣ್ಣಿನ ಸಿಂಚನ ತಾಗದಂತೆ ಸ್ವಚ್ಛಗೊಳಿಸಿ ಮತ್ತು ಬೋರ್ಡೋ ಅಥವಾ ಟ್ರೈಕೋಡರ್ಮಾದಿಂದ ಬುಡ ನೆನೆಸಿ."
            }
        ]

        return {
            "is_coastal": True,
            "district": loc_geo["district"],
            "taluk": loc_geo["taluk"],
            "zone": loc_geo["zone"],
            "zone_kn": loc_geo["zone_kn"],
            "major_rivers": loc_geo["major_rivers"],
            "heavy_rain_risk_level": risk_level,
            "heavy_rain_risk_level_kn": risk_level_kn,
            "riverine_flood_probability": flood_prob,
            "riverine_flood_probability_kn": flood_prob_kn,
            "risk_description_en": risk_desc_en,
            "risk_description_kn": risk_desc_kn,
            "rain_vs_flood_distinction_en": rain_vs_flood_en,
            "rain_vs_flood_distinction_kn": rain_vs_flood_kn,
            "proactive_insurance_advisory": insurance_advisory,
            "crop_precautions": crop_precautions
        }

    @classmethod
    def get_live_weather(cls, district: str = "Belagavi", taluk: Optional[str] = None) -> Dict[str, Any]:
        info = get_district_info(district)
        lat = info.get("latitude", 15.8497)
        lon = info.get("longitude", 74.4977)

        # Default fallback representation
        result = {
            "district": info.get("name", district),
            "district_kn": info.get("name_kn", "ಬೆಳಗಾವಿ"),
            "taluk": taluk or district,
            "is_live": False,
            "temperature": 28.0,
            "humidity": 65.0,
            "wind_speed": 10.0,
            "condition": "Partly Cloudy",
            "condition_kn": "ಭಾಗಶಃ ಮೋಡ ಕವಿದ ವಾತಾವರಣ",
            "total_48h_rain": 0.0,
            "spraying_advisory_kn": "ಗಾಳಿಯ ವೇಗ ಮತ್ತು ಹವಾಮಾನ ಅನುಕೂಲಕರವಾಗಿದ್ದು, ಬೆಳಿಗ್ಗೆ ಅಥವಾ ಸಂಜೆ ವೇಳೆ ಔಷಧಿ ಸಿಂಪಡಣೆ ಮಾಡಬಹುದು.",
            "spraying_advisory_en": "Wind and atmospheric conditions are suitable for foliar spraying in early morning or late evening.",
            "irrigation_advisory_kn": "ಒಣ ಹವೆ ಮುಂದುವರಿದಿದ್ದು, ಬೆಳೆಗಳಿಗೆ ಅಗತ್ಯಕ್ಕೆ ತಕ್ಕಂತೆ ಲಘು ನೀರಾವರಿ ಒದಗಿಸಿ.",
            "irrigation_advisory_en": "Dry conditions prevailing; provide regular protective irrigation as required by crop stage."
        }

        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code"
                f"&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max"
                f"&forecast_days=3&timezone=Asia%2FKolkata"
            )
            resp = requests.get(url, timeout=3.5)
            if resp.status_code == 200:
                data = resp.json()
                curr = data.get("current", {})
                daily = data.get("daily", {})

                temp = float(curr.get("temperature_2m", 28.0))
                hum = float(curr.get("relative_humidity_2m", 65.0))
                wind = float(curr.get("wind_speed_10m", 10.0))
                w_code = int(curr.get("weather_code", 1))

                cond_en, cond_kn, _ = WEATHER_CODE_MAP.get(w_code, ("Partly Cloudy", "ಭಾಗಶಃ ಮೋಡ ಕವಿದ ವಾತಾವರಣ", "⛅"))

                rain_sums = daily.get("precipitation_sum", [])
                rain_24h = float(rain_sums[0]) if rain_sums else 0.0
                rain_48h = sum([float(r) for r in rain_sums[:2]]) if len(rain_sums) >= 2 else rain_24h

                result["is_live"] = True
                result["temperature"] = temp
                result["humidity"] = hum
                result["wind_speed"] = wind
                result["condition"] = cond_en
                result["condition_kn"] = cond_kn
                result["total_48h_rain"] = round(rain_48h, 1)

                if rain_48h > 10.0:
                    result["spraying_advisory_kn"] = f"ಮುಂದಿನ ೪೮ ಗಂಟೆಗಳಲ್ಲಿ ಮಳೆಯಾಗುವ ({rain_48h:.1f} ಮಿ.ಮೀ) ಸಾಧ್ಯತೆ ಇರುವುದರಿಂದ ಕೀಟನಾಶಕ ಸಿಂಪಡಣೆಯನ್ನು ಮುಂದೂಡಿ."
                    result["spraying_advisory_en"] = f"Rainfall ({rain_48h:.1f} mm) predicted in the next 48 hours; postpone foliar pesticide/fungicide spraying."
                    result["irrigation_advisory_kn"] = "ಮಳೆಯ ಮುನ್ಸೂಚನೆ ಇರುವುದರಿಂದ ಜಮೀನಿನಲ್ಲಿ ನೀರಾವರಿ ನಿಲ್ಲಿಸಿ ಮತ್ತು ಬಸಿದು ಹೋಗಲು ಕಾಲುವೆ ತೆರೆಯಿರಿ."
                    result["irrigation_advisory_en"] = "Suspended irrigation recommended as natural rainfall is anticipated."
                elif wind > 18.0:
                    result["spraying_advisory_kn"] = "ಗಾಳಿಯ ವೇಗ ಹೆಚ್ಚಾಗಿರುವುದರಿಂದ (೧೮ ಕಿ.ಮೀ/ಗಂಟೆಗಿಂತ ಹೆಚ್ಚು) ಸಿಂಪಡಣೆ ಮಾಡಿದರೆ ಔಷಧ ನಷ್ಟವಾಗುತ್ತದೆ. ಶಾಂತ ಗಾಳಿ ಇರುವಾಗ ಸಿಂಪಡಿಸಿ."
                    result["spraying_advisory_en"] = "High wind speeds detected; avoid spraying to prevent spray drift losses."
                else:
                    result["spraying_advisory_kn"] = "ವಾತಾವರಣವು ಶಾಂತವಾಗಿದ್ದು, ಬೆಳಿಗ್ಗೆ ಅಥವಾ ಸಂಜೆ ವೇಳೆ ರೋಗ ಮತ್ತು ಕೀಟ ನಿರ್ವಹಣೆಗೆ ಸಿಂಪಡಿಸಲು ಸೂಕ್ತವಾಗಿದೆ."
                    result["spraying_advisory_en"] = "Calm winds and optimal humidity; excellent conditions for agricultural spraying."

                # Analyze Coastal Intelligence if coastal
                coastal_intel = cls.analyze_coastal_weather_and_flood_risk(
                    district=district,
                    taluk=taluk,
                    is_live=True,
                    rain_current=float(curr.get("precipitation", 0.0)),
                    rain_24h=rain_24h,
                    rain_48h=rain_48h,
                    wind_speed=wind
                )
                if coastal_intel["is_coastal"]:
                    result["is_coastal"] = True
                    result["coastal_intelligence"] = coastal_intel
                else:
                    result["is_coastal"] = False

        except Exception as e:
            logger.warning(f"Live weather fetch notice for {district}: {e}")
            coastal_intel = cls.analyze_coastal_weather_and_flood_risk(
                district=district,
                taluk=taluk,
                is_live=False,
                rain_current=0.0,
                rain_24h=0.0,
                rain_48h=0.0,
                wind_speed=10.0
            )
            if coastal_intel["is_coastal"]:
                result["is_coastal"] = True
                result["coastal_intelligence"] = coastal_intel
            else:
                result["is_coastal"] = False

        return result
