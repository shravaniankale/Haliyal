import json
from typing import Dict, List, Any, Optional, Tuple
from ..schemas import EligibilityCheckRequest, EligibilityItemResult, EligibilityResponse
from ..models import Scheme

class DeterministicEligibilityEngine:
    """
    Transparent 2-Stage Intelligent Recommendation & Deterministic Evaluation Engine.
    - Stage A: Profile similarity / relevance score (0.0 to 1.0) for ranking recommendations.
      (Relevance score is strictly for ranking and does NOT determine eligibility).
    - Stage B: Deterministic rule evaluation producing strictly PASS/FAIL/UNKNOWN/VERIFICATION REQUIRED.
      Prevents hallucinated eligibility claims and delivers explainable results in English & Kannada.
    """

    @classmethod
    def calculate_similarity_score(cls, scheme: Scheme, request: EligibilityCheckRequest) -> Tuple[float, str, str]:
        """
        Stage A: Intelligent Profile Similarity & Relevance Scoring (0.0 to 1.0).
        Computes how closely the scheme targets the farmer's attributes (crops, landholding, ownership, category, district).
        CRITICAL RULE: The similarity score is strictly for relevance ranking and recommendation;
        it does NOT establish or guarantee formal eligibility (which is handled by Stage B deterministic evaluation).
        """
        score = 0.0
        reasons_en = []
        reasons_kn = []

        farmer_district = request.district.strip().title()
        farmer_crop = request.crop.strip().title()
        farmer_land = request.land_acres
        farmer_ownership = request.land_ownership.strip().title() if request.land_ownership else "Own"
        farmer_category = request.farmer_category.strip() if request.farmer_category else "General"
        farmer_irrigation = request.irrigation_type.strip() if request.irrigation_type else "Rainfed"

        # 1. Crop Match Weight (up to 0.35)
        try:
            eligible_crops = json.loads(scheme.eligible_crops) if scheme.eligible_crops else ["All"]
        except Exception:
            eligible_crops = ["All"]

        if "All" in eligible_crops:
            score += 0.25
            reasons_en.append(f"broadly covers {farmer_crop}")
            reasons_kn.append(f"{farmer_crop} ಸೇರಿದಂತೆ ಎಲ್ಲಾ ಬೆಳೆಗಳಿಗೆ ಅನ್ವಯಿಸುತ್ತದೆ")
        else:
            norm_crops = [c.lower() for c in eligible_crops]
            if farmer_crop.lower() in norm_crops:
                score += 0.35
                reasons_en.append(f"specifically covers {farmer_crop}")
                reasons_kn.append(f"{farmer_crop} ಬೆಳೆಗೆ ನಿರ್ದಿಷ್ಟವಾಗಿ ಅಧಿಸೂಚಿಸಲಾಗಿದೆ")
            else:
                score += 0.05

        # 2. Land Size Weight (up to 0.25)
        if scheme.max_land_acres is None and scheme.min_land_acres is None:
            score += 0.20
            reasons_en.append("no land ceiling restriction")
            reasons_kn.append("ಭೂಮಿಯ ಮಿತಿ ನಿರ್ಬಂಧವಿಲ್ಲ")
        elif farmer_land is not None:
            min_ok = (scheme.min_land_acres is None or farmer_land >= scheme.min_land_acres)
            max_ok = (scheme.max_land_acres is None or farmer_land <= scheme.max_land_acres)
            if min_ok and max_ok:
                score += 0.25
                reasons_en.append(f"landholding of {farmer_land:g} acres fits eligibility thresholds")
                reasons_kn.append(f"ನಿಮ್ಮ {farmer_land:g} ಎಕರೆ ಜಮೀನು ಯೋಜನೆಯ ಮಿತಿಯಲ್ಲಿದೆ")
            else:
                score += 0.05
        else:
            score += 0.10

        # 3. Ownership Weight (up to 0.20)
        req_own = scheme.required_ownership or "Any"
        if req_own == "Any":
            score += 0.20
            reasons_en.append("open to both owners and tenant cultivators")
            reasons_kn.append("ಸ್ವಂತ ಹಾಗೂ ಗುತ್ತಿಗೆ ಜಮೀನು ಎರಡಕ್ಕೂ ಅನ್ವಯಿಸುತ್ತದೆ")
        elif farmer_ownership.lower() in ["own", "owned"] and req_own.lower() == "own":
            score += 0.20
            reasons_en.append("satisfies land ownership title")
            reasons_kn.append("ಸ್ವಂತ ಭೂಮಿ ಮಾನದಂಡಕ್ಕೆ ಸರಿಹೊಂದುತ್ತದೆ")
        elif farmer_ownership.lower() == req_own.lower():
            score += 0.20
            reasons_en.append(f"matches {farmer_ownership} tenure")
            reasons_kn.append(f"{farmer_ownership} ಭೂಮಾಲೀಕತ್ವಕ್ಕೆ ಹೊಂದಿಕೆಯಾಗುತ್ತದೆ")
        else:
            score += 0.05

        # 4. Location & Farmer Category Weight (up to 0.20)
        try:
            eligible_categories = json.loads(scheme.eligible_farmer_categories) if scheme.eligible_farmer_categories else ["All"]
        except Exception:
            eligible_categories = ["All"]

        if "All" in eligible_categories:
            score += 0.10
        else:
            norm_cats = [c.lower() for c in eligible_categories]
            if any(farmer_category.lower() in c for c in norm_cats):
                score += 0.10
                reasons_en.append(f"prioritizes {farmer_category} category")
                reasons_kn.append(f"{farmer_category} ವರ್ಗಕ್ಕೆ ಸರಿಹೊಂದುತ್ತದೆ")
            elif any("small" in c for c in norm_cats) and (farmer_land is not None and farmer_land <= 5.0):
                score += 0.10
                reasons_en.append("qualifies as Small & Marginal farmer")
                reasons_kn.append("ಸಣ್ಣ ಮತ್ತು ಅತಿ ಸಣ್ಣ ರೈತರ ವರ್ಗಕ್ಕೆ ಹೊಂದಾಣಿಕೆಯಾಗುತ್ತದೆ")
            else:
                score += 0.05

        loc_res = getattr(scheme, "location_restrictions", None) or "All Karnataka"
        if "All" in loc_res or farmer_district.lower() in loc_res.lower():
            score += 0.10
        else:
            score += 0.05

        final_score = round(min(1.0, max(0.20, score)), 2)

        match_reason_en = f"Matches your profile: {', '.join(reasons_en)} in {farmer_district}."
        match_reason_kn = f"ನಿಮ್ಮ ಕೃಷಿ ವಿವರಗಳಿಗೆ ಹೊಂದಾಣಿಕೆ: {farmer_district} ಜಿಲ್ಲೆಯಲ್ಲಿ {', '.join(reasons_kn)}."

        return final_score, match_reason_en, match_reason_kn

    @classmethod
    def evaluate_scheme(cls, scheme: Scheme, request: EligibilityCheckRequest) -> EligibilityItemResult:
        """
        Stage B: Deterministic Eligibility Evaluation.
        Evaluates exact conditions: PASS, FAIL, UNKNOWN, or VERIFICATION REQUIRED.
        """
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
            elif farmer_ownership.lower() in ["own", "owned"] and scheme.required_ownership.lower() == "own":
                matched.append(f"Land ownership '{farmer_ownership}' meets the mandatory requirement.")
            else:
                failing.append(f"Scheme requires '{scheme.required_ownership}' ownership, but farmer indicated '{farmer_ownership}'.")

        # 4. Evaluate Farmer Category Rule
        if "All" not in eligible_categories:
            norm_cats = [c.lower() for c in eligible_categories]
            fc_lower = farmer_category.lower()
            if any(fc_lower in cat or cat in fc_lower for cat in norm_cats):
                matched.append(f"Farmer category '{farmer_category}' qualifies under targeted categories.")
            elif any("small" in cat for cat in norm_cats) and (farmer_land is not None and farmer_land <= 5.0):
                matched.append(f"Landholding of {farmer_land} acres qualifies as Small & Marginal farmer.")
            elif "general" in norm_cats:
                matched.append(f"Farmer category '{farmer_category}' qualifies under General broad eligibility.")
            else:
                failing.append(f"Scheme is targeted to: {', '.join(eligible_categories)}. Stated category is '{farmer_category}'.")

        # Stage A: Calculate similarity score & match explanation
        sim_score, match_reason_en, match_reason_kn = cls.calculate_similarity_score(scheme, request)

        # Stage B: Determine Final Evaluation Status & Badge
        cur_status = getattr(scheme, "current_status", None) or "Active"
        verif_status = getattr(scheme, "verification_status", None) or "Verified"
        is_verification_required = (cur_status == "Verification Required" or verif_status == "Verification Required")

        if is_verification_required:
            status = "UNKNOWN"
            eligibility_badge = "VERIFICATION REQUIRED"
            explanation = f"Verification Required: This scheme is subject to state budgetary review or local quota verification. {scheme.description[:110]}..."
            explanation_kn = f"ಪರಿಶೀಲನೆ ಅಗತ್ಯವಿದೆ: ಈ ಯೋಜನೆಯು ಪ್ರಸ್ತುತ ರಾಜ್ಯ ಸರ್ಕಾರದ ಅನುದಾನ ಪರಿಶೀಲನೆಗೆ ಅಥವಾ ಸ್ಥಳೀಯ ಇಲಾಖೆಯ ಕೋಟಾಗೆ ಒಳಪಟ್ಟಿದೆ."
        elif failing:
            status = "FAIL"
            eligibility_badge = "NOT ELIGIBLE"
            explanation = f"Not currently applicable: {failing[0]}"
            explanation_kn = f"ಅರ್ಹತೆ ಹೊಂದಿಲ್ಲ: {cls._translate_reason_kn(failing[0])}"
        elif missing:
            status = "UNKNOWN"
            eligibility_badge = "INSUFFICIENT INFORMATION"
            explanation = f"Eligibility cannot be confirmed yet. Please provide: {', '.join(missing)}."
            explanation_kn = f"ಮಾಹಿತಿ ಅಪೂರ್ಣವಾಗಿದೆ. ದಯವಿಟ್ಟು {cls._translate_missing_kn(missing)} ವಿವರಗಳನ್ನು ಒದಗಿಸಿ."
        else:
            status = "PASS"
            eligibility_badge = "ELIGIBLE"
            explanation = f"Potentially Eligible! Meets all verified scheme criteria. Subject to government scrutiny."
            explanation_kn = f"ಅರ್ಹತೆಯ ಮಾನದಂಡಗಳನ್ನು ಪೂರೈಸಿದ್ದೀರಿ! ಅಗತ್ಯ ದಾಖಲೆಗಳೊಂದಿಗೆ ಅಧಿಕೃತ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಬಹುದು."

        return EligibilityItemResult(
            scheme_id=scheme.scheme_id,
            scheme_name=scheme.scheme_name,
            scheme_name_kn=scheme.scheme_name_kn,
            scheme_type=scheme.scheme_type,
            department=scheme.department,
            status=status,
            eligibility_badge=eligibility_badge,
            explanation=explanation,
            explanation_kn=explanation_kn,
            matched_conditions=matched,
            failing_conditions=failing,
            missing_information=missing,
            required_documents=req_docs,
            benefit_details=scheme.benefit_details,
            benefit_details_kn=scheme.benefit_details_kn,
            official_url=scheme.official_url,
            verification_status=scheme.verification_status,
            similarity_score=sim_score,
            match_reason=match_reason_en,
            match_reason_kn=match_reason_kn,
            scheme_category=getattr(scheme, "scheme_category", None) or "General Agriculture",
            application_period=getattr(scheme, "application_period", None) or "Open Throughout Year",
            source_reference=getattr(scheme, "source_document_title", None) or getattr(scheme, "source_url", None),
            last_verified_date=getattr(scheme, "verification_date", None) or "2026-10-25",
            current_status=cur_status
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
        if "targeted to" in reason.lower():
            return "ರೈತರ ವರ್ಗವು ಈ ಯೋಜನೆಗೆ ನಿಗದಿಪಡಿಸಿದ ಗುಂಪಿಗೆ ಹೊಂದಾಣಿಕೆಯಾಗುತ್ತಿಲ್ಲ."
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

        # Sort: PASS first, then UNKNOWN, then FAIL.
        # Within each status group, rank by Stage A similarity_score descending!
        order = {"PASS": 0, "UNKNOWN": 1, "FAIL": 2}
        results.sort(key=lambda x: (order.get(x.status, 3), -x.similarity_score))

        return EligibilityResponse(
            total_evaluated=len(results),
            eligible_count=eligible_count,
            results=results
        )
