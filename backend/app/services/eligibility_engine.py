import json
from typing import Dict, List, Any, Optional
from ..schemas import EligibilityCheckRequest, EligibilityItemResult, EligibilityResponse
from ..models import Scheme

class DeterministicEligibilityEngine:
    """
    Transparent, rule-based deterministic evaluation engine for agricultural schemes.
    Prevents hallucinated eligibility claims and delivers explainable PASS/FAIL/UNKNOWN results.
    """

    @classmethod
    def evaluate_scheme(cls, scheme: Scheme, request: EligibilityCheckRequest) -> EligibilityItemResult:
        matched: List[str] = []
        failing: List[str] = []
        missing: List[str] = []

        farmer_district = request.district.strip().title()
        farmer_crop = request.crop.strip().title()
        farmer_land = request.land_acres
        farmer_ownership = request.land_ownership.strip().title() if request.land_ownership else None
        farmer_category = request.farmer_category.strip() if request.farmer_category else "General"
        farmer_irrigation = request.irrigation_type.strip() if request.irrigation_type else "Rainfed"

        # Parse scheme criteria
        try:
            eligible_crops = json.loads(scheme.eligible_crops) if scheme.eligible_crops else ["All"]
        except Exception:
            eligible_crops = ["All"]

        try:
            eligible_categories = json.loads(scheme.eligible_farmer_categories) if scheme.eligible_farmer_categories else ["All"]
        except Exception:
            eligible_categories = ["All"]

        try:
            req_docs = json.loads(scheme.required_documents) if scheme.required_documents else []
        except Exception:
            req_docs = []

        # 1. Evaluate Crop Rule
        if "All" in eligible_crops:
            matched.append(f"Crop '{farmer_crop}' is eligible under broad crop coverage.")
        else:
            normalized_eligible = [c.lower() for c in eligible_crops]
            if farmer_crop.lower() in normalized_eligible:
                matched.append(f"Crop '{farmer_crop}' is explicitly notified for this scheme.")
            else:
                failing.append(f"Crop '{farmer_crop}' is not covered. Eligible crops: {', '.join(eligible_crops)}.")

        # 2. Evaluate Land Area Rule
        if scheme.max_land_acres is not None:
            if farmer_land is None:
                missing.append("Land holding size in acres is required to confirm land threshold.")
            elif farmer_land <= scheme.max_land_acres:
                matched.append(f"Land holding of {farmer_land} acres satisfies the maximum limit of {scheme.max_land_acres} acres.")
            else:
                failing.append(f"Land holding of {farmer_land} acres exceeds the scheme maximum ceiling of {scheme.max_land_acres} acres.")

        if scheme.min_land_acres is not None:
            if farmer_land is None:
                if "Land holding size in acres is required to confirm land threshold." not in missing:
                    missing.append("Land holding size in acres is required.")
            elif farmer_land >= scheme.min_land_acres:
                matched.append(f"Land holding satisfies the minimum requirement of {scheme.min_land_acres} acres.")
            else:
                failing.append(f"Land holding of {farmer_land} acres is below minimum required {scheme.min_land_acres} acres.")

        # 3. Evaluate Land Ownership Rule
        if scheme.required_ownership and scheme.required_ownership != "Any":
            if not farmer_ownership:
                missing.append("Land ownership status (Own land or Tenant / Leased) is required.")
            elif farmer_ownership.lower() == scheme.required_ownership.lower():
                matched.append(f"Land ownership '{farmer_ownership}' meets the mandatory requirement.")
            else:
                failing.append(f"Scheme requires '{scheme.required_ownership}' ownership, but farmer indicated '{farmer_ownership}'.")

        # 4. Evaluate Farmer Category Rule
        if "All" not in eligible_categories:
            norm_cats = [c.lower() for c in eligible_categories]
            if farmer_category.lower() in norm_cats:
                matched.append(f"Farmer category '{farmer_category}' qualifies under targeted categories.")
            else:
                # If scheme specifically targets small & marginal and land <= 5 acres, auto match
                if "small & marginal" in norm_cats and (farmer_land is not None and farmer_land <= 5.0):
                    matched.append(f"Landholding of {farmer_land} acres qualifies as Small & Marginal farmer.")
                else:
                    failing.append(f"Scheme is targeted to: {', '.join(eligible_categories)}. Stated category is '{farmer_category}'.")

        # 5. Determine Final Evaluation Status
        if failing:
            status = "FAIL"
            explanation = f"Not currently applicable: {failing[0]}"
            explanation_kn = f"ಅರ್ಹತೆ ಹೊಂದಿಲ್ಲ: {cls._translate_reason_kn(failing[0])}"
        elif missing:
            status = "UNKNOWN"
            explanation = f"Eligibility cannot be confirmed yet. Please provide: {', '.join(missing)}."
            explanation_kn = f"ಮಾಹಿತಿ ಅಪೂರ್ಣವಾಗಿದೆ. ದಯವಿಟ್ಟು {cls._translate_missing_kn(missing)} ವಿವರಗಳನ್ನು ಒದಗಿಸಿ."
        else:
            status = "PASS"
            explanation = f"Potentially Eligible! Meets all verified scheme criteria. Subject to government scrutiny."
            explanation_kn = f"ಅರ್ಹತೆಯ ಮಾನದಂಡಗಳನ್ನು ಪೂರೈಸಿದ್ದೀರಿ! ಅಗತ್ಯ ದಾಖಲೆಗಳೊಂದಿಗೆ ಅಧಿಕೃತ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಬಹುದು."

        return EligibilityItemResult(
            scheme_id=scheme.scheme_id,
            scheme_name=scheme.scheme_name,
            scheme_name_kn=scheme.scheme_name_kn,
            scheme_type=scheme.scheme_type,
            department=scheme.department,
            status=status,
            explanation=explanation,
            explanation_kn=explanation_kn,
            matched_conditions=matched,
            failing_conditions=failing,
            missing_information=missing,
            required_documents=req_docs,
            benefit_details=scheme.benefit_details,
            benefit_details_kn=scheme.benefit_details_kn,
            official_url=scheme.official_url,
            verification_status=scheme.verification_status
        )

    @staticmethod
    def _translate_reason_kn(reason: str) -> str:
        if "exceeds" in reason.lower():
            return "ಕೃಷಿ ಭೂಮಿಯ ವಿಸ್ತೀರ್ಣವು ಯೋಜನೆಯ ಗರಿಷ್ಠ ಮಿತಿಗಿಂತ ಹೆಚ್ಚಾಗಿದೆ."
        if "below minimum" in reason.lower():
            return "ಕೃಷಿ ಭೂಮಿ ಕನಿಷ್ಠ ಅಗತ್ಯಕ್ಕಿಂತ ಕಡಿಮೆಯಾಗಿದೆ."
        if "not covered" in reason.lower():
            return "ಈ ಬೆಳೆಯು ಪ್ರಸ್ತುತ ಯೋಜನೆಯ ಅಧಿಸೂಚನೆಯಲ್ಲಿ ಸೇರಿಲ್ಲ."
        if "ownership" in reason.lower():
            return "ಭೂಮಿಯ ಮಾಲೀಕತ್ವದ ಷರತ್ತು ಪೂರೈಸಲಾಗಿಲ್ಲ (ಸ್ವಂತ ಭೂಮಿ ಕಡ್ಡಾಯ)."
        return "ಯೋಜನೆಯ ನಿಯಮಾವಳಿಗಳಿಗೆ ಹೊಂದಾಣಿಕೆಯಾಗುತ್ತಿಲ್ಲ."

    @staticmethod
    def _translate_missing_kn(missing_list: List[str]) -> str:
        parts = []
        for m in missing_list:
            if "Land holding" in m:
                parts.append("ಜಮೀನಿನ ಎಕರೆ ವಿಸ್ತೀರ್ಣ")
            elif "ownership" in m:
                parts.append("ಭೂಮಿಯ ಮಾಲೀಕತ್ವ (ಸ್ವಂತ/ಗೇಣಿ)")
            else:
                parts.append("ಅಗತ್ಯ ಮಾಹಿತಿ")
        return ", ".join(parts)

    @classmethod
    def evaluate_all(cls, schemes: List[Scheme], request: EligibilityCheckRequest) -> EligibilityResponse:
        results: List[EligibilityItemResult] = []
        eligible_count = 0

        for scheme in schemes:
            if not scheme.active_status:
                continue
            item = cls.evaluate_scheme(scheme, request)
            if item.status == "PASS":
                eligible_count += 1
            results.append(item)

        # Sort: PASS first, then UNKNOWN, then FAIL
        order = {"PASS": 0, "UNKNOWN": 1, "FAIL": 2}
        results.sort(key=lambda x: order.get(x.status, 3))

        return EligibilityResponse(
            total_evaluated=len(results),
            eligible_count=eligible_count,
            results=results
        )
