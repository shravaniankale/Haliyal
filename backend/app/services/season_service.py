import datetime
from typing import Dict, Any, Optional

# Indian Standard Time (UTC+5:30)
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

class AgriculturalSeasonService:
    """
    Intelligent Agricultural Season & Karnataka Crop Calendar Service.
    Operates strictly in Asia/Kolkata timezone and combines temporal analysis
    with crop specifics and regional district calendars.
    """

    @classmethod
    def get_current_ist_time(cls) -> datetime.datetime:
        """Returns current wall-clock datetime in Asia/Kolkata timezone."""
        return datetime.datetime.now(IST)

    @classmethod
    def analyze_season(
        cls,
        district: Optional[str] = None,
        crop: Optional[str] = None,
        sowing_month: Optional[int] = None,
        crop_stage: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzes the current agricultural season for Karnataka based on Indian time,
        notified crop calendar, regional district characteristics, and sowing details.
        """
        now = cls.get_current_ist_time()
        month = now.month
        day = now.day
        year = now.year

        # Format display strings
        kannada_months = {
            1: "ಜನವರಿ", 2: "ಫೆಬ್ರವರಿ", 3: "ಮಾರ್ಚ್", 4: "ಏಪ್ರಿಲ್",
            5: "ಮೇ", 6: "ಜೂನ್", 7: "ಜುಲೈ", 8: "ಆಗಸ್ಟ್",
            9: "ಸೆಪ್ಟೆಂಬರ್", 10: "ಅಕ್ಟೋಬರ್", 11: "ನವೆಂಬರ್", 12: "ಡಿಸೆಂಬರ್"
        }
        kannada_days = {
            0: "ಸೋಮವಾರ", 1: "ಮಂಗಳವಾರ", 2: "ಬುಧವಾರ", 3: "ಗುರುವಾರ",
            4: "ಶುಕ್ರವಾರ", 5: "ಶನಿವಾರ", 6: "ಭಾನುವಾರ"
        }

        date_str_en = now.strftime("%d %B %Y")
        time_str_en = now.strftime("%I:%M %p IST")
        date_str_kn = f"{day} {kannada_months.get(month, '')} {year}, {kannada_days.get(now.weekday(), '')}"

        # Base season determination with Karnataka Agro-Climatic Calendar
        # Month 6-9: Primary Kharif
        # Month 10: Transition Kharif harvest / Rabi sowing
        # Month 11-2: Primary Rabi
        # Month 3-5: Summer / Pre-Kharif
        if 6 <= month <= 9:
            base_season = "Kharif"
            season_kn = "ಮುಂಗಾರು (Kharif)"
            stage = "Active Crop Growth / Monsoon Phase"
            stage_kn = "ಮುಂಗಾರು ಬೆಳೆ ಬೆಳವಣಿಗೆಯ ಹಂತ"
        elif month == 10:
            # Late October is the prime Karnataka transition
            base_season = "Kharif/Rabi Transition"
            season_kn = "ಹಿಂಗಾರು ಆರಂಭ / ಮುಂಗಾರು ಕಟಾವು (Kharif-Rabi Transition)"
            stage = "Kharif Harvesting & Rabi Sowing Window"
            stage_kn = "ಮುಂಗಾರು ಬೆಳೆ ಕಟಾವು ಮತ್ತು ಹಿಂಗಾರು ಬಿತ್ತನೆ ಕಾಲ"
        elif month in [11, 12, 1, 2]:
            base_season = "Rabi"
            season_kn = "ಹಿಂಗಾರು (Rabi)"
            stage = "Post-Monsoon Winter Cultivation"
            stage_kn = "ಹಿಂಗಾರು ಚಳಿಗಾಲದ ಬೆಳೆ ಸಾಗುವಳಿ ಹಂತ"
        else: # March, April, May
            base_season = "Summer"
            season_kn = "ಬೇಸಿಗೆ (Summer / Pre-Kharif)"
            stage = "Summer Irrigated / Land Preparation"
            stage_kn = "ಬೇಸಿಗೆ ನೀರಾವರಿ / ಮುಂಗಾರು ಪೂರ್ವ ಭೂಮಿ ಸಿದ್ಧತೆ"

        # Adapt using crop context if provided
        active_season = base_season
        if crop:
            c_lower = crop.lower()
            if any(rabi_c in c_lower for rabi_c in ["chickpea", "bengal gram", "ಕಡಲೆ", "wheat", "ಗೋಧಿ", "sunflower", "ಸೂರ್ಯಕಾಂತಿ", "rabi jowar", "ಹಿಂಗಾರು ಜೋಳ"]):
                active_season = "Rabi"
                season_kn = "ಹಿಂಗಾರು (Rabi)"
            elif any(kharif_c in c_lower for kharif_c in ["paddy", "ಭತ್ತ", "ragi", "ರಾಗಿ", "cotton", "ಹತ್ತಿ", "tur", "ತೊಗರಿ", "sugarcane", "ಕಬ್ಬು"]):
                if month in [10, 11] and (crop_stage == "Harvesting" or day > 15):
                    stage = "Maturity & Harvesting Window"
                    stage_kn = "ಬೆಳೆ ಮಾಗುವಿಕೆ ಮತ್ತು ಕಟಾವಿನ ಹಂತ"

        # District-specific context
        is_north_karnataka = False
        if district:
            from ..config import get_region_for_district
            is_north_karnataka = (get_region_for_district(district) == "North Karnataka")

        # Regional agricultural recommendations
        if active_season in ["Rabi", "Kharif/Rabi Transition"]:
            insurance_scheme_season = "Rabi"
            premium_rule = "1.5% for Food & Oilseeds (Bengal Gram, Rabi Jowar, Wheat)"
            premium_rule_kn = "ಆಹಾರ ಮತ್ತು ಎಣ್ಣೆಕಾಳು ಬೆಳೆಗಳಿಗೆ ಕೇವಲ 1.5% ಪ್ರೀಮಿಯಂ"
            advisory_en = (
                "Rabi crop sowing is in full progress across Karnataka. Farmers in North Karnataka dry zones "
                "(Belagavi, Dharwad, Vijayapura, Bagalkote) should prioritize Bengal Gram (Chickpea) and Rabi Jowar "
                "with seed treatment. Complete PMFBY Rabi crop insurance registration on Samrakshane before notified cut-off."
            )
            advisory_kn = (
                "ಕರ್ನಾಟಕದಲ್ಲಿ ಪ್ರಸ್ತುತ ಹಿಂಗಾರು (Rabi) ಬಿತ್ತನೆ ಕಾರ್ಯ ಚುರುಕಾಗಿದೆ. ಉತ್ತರ ಕರ್ನಾಟಕದ ರೈತರು ಕಡಲೆ ಮತ್ತು ಹಿಂಗಾರು ಜೋಳಕ್ಕೆ "
                "ಬೀಜೋಪಚಾರ ಮಾಡಿ ಬಿತ್ತನೆ ಮಾಡಬೇಕು. ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆಯಡಿ ಕರ್ನಾಟಕ ಸಂರಕ್ಷಣೆ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ನಿಗದಿತ ದಿನಾಂಕದೊಳಗೆ ನೋಂದಾಯಿಸಿಕೊಳ್ಳಿ."
            )
        elif active_season == "Kharif":
            insurance_scheme_season = "Kharif"
            premium_rule = "2.0% for Food & Oilseeds (Paddy, Ragi, Maize, Groundnut), 5.0% for Commercial (Cotton, Sugarcane)"
            premium_rule_kn = "ಆಹಾರ ಬೆಳೆಗಳಿಗೆ 2.0%, ವಾಣಿಜ್ಯ ಬೆಳೆಗಳಿಗೆ 5.0% ಪ್ರೀಮಿಯಂ"
            advisory_en = (
                "South-West Monsoon Kharif season. Ensure proper drainage in heavy soils. "
                "Monitor for pests like stem borer in paddy and fall armyworm in maize."
            )
            advisory_kn = (
                "ಮುಂಗಾರು ಬೆಳೆಗಳಿಗೆ ಸಕಾಲಿಕ ಕಳೆ ನಿರ್ವಹಣೆ ಮತ್ತು ರಸಗೊಬ್ಬರ ನಿರ್ವಹಣೆ ಮಾಡಿ. ಭತ್ತದಲ್ಲಿ ಕಾಂಡ ಕೊರೆಯುವ ಹುಳು ಹಾಗೂ ಮೆಕ್ಕೆಜೋಳದಲ್ಲಿ ಲದ್ದಿ ಹುಳು ಬಾಧೆ ಗಮನಿಸಿ."
            )
        else:
            insurance_scheme_season = "Summer"
            premium_rule = "Applicable for notified summer pulses and oilseeds"
            premium_rule_kn = "ಬೇಸಿಗೆ ದ್ವಿದಳ ಧಾನ್ಯ ಮತ್ತು ಎಣ್ಣೆಕಾಳುಗಳಿಗೆ ಅನ್ವಯ"
            advisory_en = (
                "Pre-monsoon land preparation and summer crop maintenance. Deep summer ploughing recommended "
                "to eradicate dormant weed seeds and soil-borne pathogens."
            )
            advisory_kn = (
                "ಮುಂಗಾರು ಪೂರ್ವ ಆಳವಾದ ಬೇಸಿಗೆ ಉಳುಮೆ ಮಾಡಿ. ಇದರಿಂದ ಮಣ್ಣಿನಲ್ಲಿರುವ ಕೀಟಗಳ ಕೋಶಗಳು ಮತ್ತು ಕಳೆ ಬೀಜಗಳು ನಾಶವಾಗುತ್ತವೆ."
            )

        return {
            "current_time_iso": now.isoformat(),
            "current_date_en": date_str_en,
            "current_date_kn": date_str_kn,
            "current_time_en": time_str_en,
            "season_code": active_season.lower().replace("/", "_").replace(" ", "_"),
            "season_name": active_season,
            "season_name_kn": season_kn,
            "crop_stage_current": stage,
            "crop_stage_current_kn": stage_kn,
            "insurance_season": insurance_scheme_season,
            "insurance_premium_guideline": premium_rule,
            "insurance_premium_guideline_kn": premium_rule_kn,
            "regional_advisory_en": advisory_en,
            "regional_advisory_kn": advisory_kn,
            "is_north_karnataka": is_north_karnataka,
            "timezone": "Asia/Kolkata (IST, UTC+05:30)"
        }

