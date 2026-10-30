import datetime
from typing import Dict, Any, Optional, List
from .season_service import AgriculturalSeasonService
from .district_service import DISTRICT_TALUKS, get_district_info

# Notified Crops in Karnataka PMFBY Samrakshane
NOTIFIED_CROPS_KARNATAKA = {
    "Paddy": {"kn": "ಭತ್ತ", "type": "Food Crop", "kharif_rate": 2.0, "rabi_rate": 1.5, "unit": "Gram Panchayat"},
    "Ragi": {"kn": "ರಾಗಿ", "type": "Food Crop", "kharif_rate": 2.0, "rabi_rate": 1.5, "unit": "Gram Panchayat"},
    "Jowar": {"kn": "ಜೋಳ", "type": "Food Crop", "kharif_rate": 2.0, "rabi_rate": 1.5, "unit": "Hobli / GP"},
    "Maize": {"kn": "ಮೆಕ್ಕೆಜೋಳ", "type": "Food Crop", "kharif_rate": 2.0, "rabi_rate": 1.5, "unit": "Gram Panchayat"},
    "Groundnut": {"kn": "ಕಡಲೆಕಾಯಿ (ಶೇಂಗಾ)", "type": "Oilseed", "kharif_rate": 2.0, "rabi_rate": 1.5, "unit": "Gram Panchayat"},
    "Cotton": {"kn": "ಹತ್ತಿ", "type": "Commercial Crop", "kharif_rate": 5.0, "rabi_rate": 5.0, "unit": "Hobli"},
    "Tur": {"kn": "ತೊಗರಿ", "type": "Pulse", "kharif_rate": 2.0, "rabi_rate": 2.0, "unit": "Gram Panchayat"},
    "Sugarcane": {"kn": "ಕಬ್ಬು", "type": "Commercial Crop", "kharif_rate": 5.0, "rabi_rate": 5.0, "unit": "Hobli"},
    "Soybean": {"kn": "ಸೋಯಾಬೀನ್", "type": "Oilseed", "kharif_rate": 2.0, "rabi_rate": 2.0, "unit": "Gram Panchayat"},
    "Bengal Gram": {"kn": "ಕಡಲೆ (ಚಿಕ್ ಪೀ)", "type": "Rabi Pulse", "kharif_rate": None, "rabi_rate": 1.5, "unit": "Gram Panchayat"},
    "Wheat": {"kn": "ಗೋಧಿ", "type": "Rabi Cereal", "kharif_rate": None, "rabi_rate": 1.5, "unit": "Hobli / GP"},
    "Sunflower": {"kn": "ಸೂರ್ಯಕಾಂತಿ", "type": "Oilseed", "kharif_rate": 2.0, "rabi_rate": 1.5, "unit": "Hobli"}
}

class CropInsuranceService:
    """
    Intelligent PMFBY & Karnataka Samrakshane Crop Insurance Guidance.
    Strictly verifies officially notified crops, premium ceilings, and 72-hour claim norms.
    """

    @classmethod
    def evaluate_insurance(
        cls,
        district: str = "Belagavi",
        taluk: Optional[str] = None,
        crop: Optional[str] = "Paddy",
        season: Optional[str] = None,
        land_acres: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Evaluates crop insurance eligibility and guidelines under Karnataka Samrakshane.
        """
        # 1. Season context
        seasonal_info = AgriculturalSeasonService.analyze_season(district=district, crop=crop)
        active_season = season or seasonal_info["insurance_season"]

        # 2. Normalize crop
        crop_match = None
        crop_key = None
        if crop:
            c_input = crop.strip().lower()
            for k, v in NOTIFIED_CROPS_KARNATAKA.items():
                if k.lower() == c_input or v["kn"] in crop or c_input in k.lower():
                    crop_match = v
                    crop_key = k
                    break

        is_notified = crop_match is not None

        # 3. Premium rate determination
        premium_pct = 2.0
        if crop_match:
            if active_season == "Rabi":
                premium_pct = crop_match.get("rabi_rate") or 1.5
            else:
                premium_pct = crop_match.get("kharif_rate") or 2.0
        else:
            premium_pct = 2.0 if active_season == "Kharif" else 1.5

        # Sum insured scale of finance estimate (Karnataka DLTC benchmark per acre: approx ₹25,000 - ₹45,000)
        sum_insured_per_acre = 35000.0
        if crop_key in ["Sugarcane", "Cotton"]:
            sum_insured_per_acre = 55000.0
        elif crop_key in ["Bengal Gram", "Ragi", "Jowar"]:
            sum_insured_per_acre = 28000.0

        acres = land_acres if (land_acres and land_acres > 0) else 1.0
        total_sum_insured = sum_insured_per_acre * acres
        estimated_farmer_premium = (total_sum_insured * premium_pct) / 100.0

        # Verification note for unknown combinations
        status_note_en = (
            f"Crop '{crop_key or crop}' is an officially notified insurable crop under PMFBY Karnataka Samrakshane."
            if is_notified else
            f"Official notification for '{crop}' requires taluk-level gram panchayat verification on the Samrakshane portal."
        )
        status_note_kn = (
            f"'{crop_key or crop}' ಬೆಳೆಯು ಕರ್ನಾಟಕ ಸಂರಕ್ಷಣೆ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಅಧಿಸೂಚಿತ ವಿಮಾ ಬೆಳೆಯಾಗಿದೆ."
            if is_notified else
            f"'{crop}' ಬೆಳೆಗೆ ಸಂಬಂಧಿಸಿದ ಅಧಿಸೂಚನೆ ಲಭ್ಯತೆಯನ್ನು Samrakshane ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಗ್ರಾಮ ಪಂಚಾಯತ್ ಮಟ್ಟದಲ್ಲಿ ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಬೇಕು."
        )

        return {
            "district": district,
            "taluk": taluk,
            "crop": crop_key or crop or "Notified Agriculture Crops",
            "crop_kn": crop_match["kn"] if crop_match else "ಅಧಿಸೂಚಿತ ಬೆಳೆಗಳು",
            "is_notified": is_notified,
            "season": active_season,
            "insurance_unit": crop_match["unit"] if crop_match else "Gram Panchayat / Hobli",
            "premium_rate_farmer_pct": premium_pct,
            "estimated_sum_insured_inr": round(total_sum_insured, 2),
            "estimated_farmer_premium_inr": round(estimated_farmer_premium, 2),
            "government_subsidy_share": "Remaining 80% to 95% premium shared 50:50 by Central and Karnataka Government",
            "calamity_intimation_rule": "72 Hours (Mandatory 3 calendar days notification for localized calamities & post-harvest loss)",
            "calamity_intimation_rule_kn": "ಪ್ರಕೃತಿ ವಿಕೋಪ/ಆಲಿಕಲ್ಲು ಮಳೆಯಿಂದ ಬೆಳೆ ಹಾನಿಯಾದರೆ ೭೨ ಗಂಟೆಗಳ ಒಳಗೆ ಕಡ್ಡಾಯವಾಗಿ ಮಾಹಿತಿ ನೀಡಬೇಕು",
            "required_documents": [
                "Bhoomi Land Records RTC / Pahani extract",
                "Aadhaar Card (Mandatory)",
                "Bank Passbook linked with Aadhaar & IFSC",
                "Sowing Certificate / Self-Declaration of crop cultivation"
            ],
            "required_documents_kn": [
                "ಕರ್ನಾಟಕ ಭೂಮಿ ತಂತ್ರಾಂಶದ ಪಹಣಿ (RTC)",
                "ಆಧಾರ್ ಕಾರ್ಡ್",
                "ಆಧಾರ್ ಲಿಂಕ್ ಆಗಿರುವ ಬ್ಯಾಂಕ್ ಪಾಸ್‌ಬುಕ್ ಮತ್ತು IFSC ಕೋಡ್",
                "ಬೆಳೆ ಸಾಗುವಳಿ ಪ್ರಮಾಣಪತ್ರ"
            ],
            "official_portal_url": "https://samrakshane.karnataka.gov.in",
            "central_pmfby_url": "https://pmfby.gov.in",
            "helpline": "1800-180-1551 (Toll-Free) / 080-22212861",
            "status_note_en": status_note_en,
            "status_note_kn": status_note_kn
        }

