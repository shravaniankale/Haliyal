"""
KRISHI MITRA - TARGETED VERIFICATION FOR FEATURE 1 & FEATURE 2
Feature 1: Comprehensive Government Agricultural Scheme Catalogue & 2-Stage Recommendation Engine
Feature 2: Coastal Weather, Heavy-Rain and Flood-Risk Intelligence
"""
import sys
import os

# Set working directory to project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal
from backend.app.models import Scheme
from backend.app.schemas import EligibilityCheckRequest
from backend.app.services.eligibility_engine import DeterministicEligibilityEngine
from backend.app.services.weather_service import AgriculturalWeatherService
from backend.app.services.agricultural_agent import AgriculturalConversationalAgent

def verify_feature_1_schemes_and_engine():
    print("\n" + "="*70)
    print("VERIFYING FEATURE 1: GOVERNMENT SCHEMES CATALOGUE & 2-STAGE ENGINE")
    print("="*70)

    db = SessionLocal()
    try:
        schemes = db.query(Scheme).all()
        print(f"[1.1] Scheme Count: {len(schemes)} total schemes in SQLite DB.")
        assert len(schemes) >= 20, f"Expected at least 20 schemes, found {len(schemes)}"

        # Check required schema fields
        for s in schemes:
            assert s.scheme_id, f"Missing scheme_id on {s.scheme_name}"
            assert s.scheme_name, f"Missing scheme_name on {s.scheme_id}"
            assert s.scheme_name_kn, f"Missing scheme_name_kn on {s.scheme_id}"
            assert s.scheme_category, f"Missing scheme_category on {s.scheme_id}"
            assert s.scheme_type, f"Missing scheme_type on {s.scheme_id}"
            assert s.current_status in ["Active", "Inactive", "Suspended", "Verification Required"], \
                f"Invalid current_status {s.current_status} on {s.scheme_id}"
            assert s.official_url, f"Missing official_url on {s.scheme_id}"
            assert s.verification_date, f"Missing verification_date on {s.scheme_id}"

        print("  ✓ All schemes have complete metadata, categorization, source citations and status.")

        # Test Verification Required schemes
        verification_schemes = [s for s in schemes if s.current_status == "Verification Required"]
        print(f"[1.2] Verification Required Schemes: {[s.scheme_id for s in verification_schemes]}")
        assert len(verification_schemes) >= 2, "Expected at least 2 Verification Required schemes (CM-Kisan, Punyakoti)"

        # Test Stage A: Similarity Scoring (0.0 to 1.0)
        req_paddy = EligibilityCheckRequest(
            district="Dakshina Kannada",
            crop="Paddy",
            land_acres=2.5,
            land_ownership="Own",
            farmer_category="Small & Marginal",
            irrigation_type="Rainfed"
        )

        pmfby = next(s for s in schemes if s.scheme_id == "PMFBY")
        sim_score, reason_en, reason_kn = DeterministicEligibilityEngine.calculate_similarity_score(pmfby, req_paddy)
        print(f"[1.3] Stage A Similarity Score for PMFBY: {sim_score:.2f}")
        print(f"      Reason EN: {reason_en}")
        print(f"      Reason KN: {reason_kn}")
        assert 0.0 <= sim_score <= 1.0, "Similarity score must be bounded between 0.0 and 1.0"
        assert sim_score >= 0.7, "Paddy farmer should have high similarity for PMFBY"

        # Check that high similarity DOES NOT establish eligibility (Strict Stage B separation)
        # Create an over-sized land farmer (35 acres) for a scheme with max 5 acres (e.g., DEMO-IRRIG-01)
        req_large = EligibilityCheckRequest(
            district="Belagavi",
            crop="Paddy",
            land_acres=35.0, # Exceeds max_land_acres (5.0)
            land_ownership="Own",
            farmer_category="Large",
            irrigation_type="Rainfed"
        )
        res_large = DeterministicEligibilityEngine.evaluate_all(schemes, req_large)
        irrig_res = next(r for r in res_large.results if r.scheme_id == "DEMO-IRRIG-01")
        print(f"[1.4] Large Farmer (35 acres) DEMO-IRRIG-01 Evaluation:")
        print(f"      Stage A Similarity: {irrig_res.similarity_score:.2f}")
        print(f"      Stage B Status: {irrig_res.status} | Badge: {irrig_res.eligibility_badge}")
        print(f"      Explanation EN: {irrig_res.explanation}")
        print(f"      Explanation KN: {irrig_res.explanation_kn}")
        # Ensure similarity didn't force PASS
        assert irrig_res.similarity_score > 0.0, "Similarity score reflects profile relevance"
        assert irrig_res.status == "FAIL", "Stage B status must be FAIL when land criteria fails!"
        assert irrig_res.eligibility_badge == "NOT ELIGIBLE", \
            "High relevance must NOT establish eligibility when deterministic criteria fails!"

        # Check Verification Required badge assignment
        cm_kisan_res = next(r for r in res_large.results if r.scheme_id == "KA-CM-KISAN")
        print(f"[1.5] KA-CM-KISAN Status: {cm_kisan_res.status} | Badge: {cm_kisan_res.eligibility_badge}")
        assert cm_kisan_res.eligibility_badge == "VERIFICATION REQUIRED", \
            "Schemes with current_status='Verification Required' must have VERIFICATION REQUIRED badge"

        # Check Insufficient Information handling
        req_incomplete = EligibilityCheckRequest(
            district="Udupi",
            crop="Paddy",
            land_acres=None
        )
        res_incomplete = DeterministicEligibilityEngine.evaluate_all(schemes, req_incomplete)
        unknown_schemes = [r for r in res_incomplete.results if r.eligibility_badge == "INSUFFICIENT INFORMATION"]
        print(f"[1.6] Incomplete Profile -> Schemes with INSUFFICIENT INFORMATION: {len(unknown_schemes)}")
        assert len(unknown_schemes) > 0, "Missing fields must produce INSUFFICIENT INFORMATION badges"

        print("  ✓ Feature 1 schemes and 2-stage recommendation engine verified successfully!")
    finally:
        db.close()

def verify_feature_2_coastal_weather():
    print("\n" + "="*70)
    print("VERIFYING FEATURE 2: COASTAL WEATHER & FLOOD RISK INTELLIGENCE")
    print("="*70)

    # 2.1 Micro-zone detection
    print("[2.1] Micro-Zone Classification:")
    geo1 = AgriculturalWeatherService.is_coastal_location("Dakshina Kannada", "Mangaluru")
    print(f"      Dakshina Kannada / Mangaluru -> is_coastal={geo1['is_coastal']}, Zone={geo1['zone']}")
    assert geo1['is_coastal'] is True and "Shoreline" in geo1['zone'], "Mangaluru should be Coastal Plain & Estuarine Shoreline"

    geo2 = AgriculturalWeatherService.is_coastal_location("Dakshina Kannada", "Belthangady")
    print(f"      Dakshina Kannada / Belthangady -> is_coastal={geo2['is_coastal']}, Zone={geo2['zone']}")
    assert geo2['is_coastal'] is True and "Western Ghats" in geo2['zone'], "Belthangady should be Western Ghats Foothills"

    geo3 = AgriculturalWeatherService.is_coastal_location("Uttara Kannada", "Haliyal")
    print(f"      Uttara Kannada / Haliyal -> is_coastal={geo3['is_coastal']}, Zone={geo3['zone']}")
    assert geo3['is_coastal'] is True and "Western Ghats" in geo3['zone'], "Haliyal should be Western Ghats / Coastal transition"

    geo4 = AgriculturalWeatherService.is_coastal_location("Belagavi", "Chikodi")
    print(f"      Belagavi / Chikodi -> is_coastal={geo4['is_coastal']}, Zone={geo4['zone']}")
    assert geo4['is_coastal'] is False and "Inland" in geo4['zone'], "Chikodi should not be coastal"

    # 2.2 Live weather integration for Coastal Karnataka
    print("[2.2] Live Weather Retrieval for Udupi / Kundapura:")
    w = AgriculturalWeatherService.get_live_weather("Udupi", "Kundapura")
    print(f"      Temp: {w.get('temperature')}°C, Rain 48h: {w.get('total_48h_rain')}mm, Is Live: {w.get('is_live')}")
    assert w.get("is_coastal") is True, "Udupi must be identified as coastal"
    assert "coastal_intelligence" in w, "coastal_intelligence must be attached to weather data"

    ci = w["coastal_intelligence"]
    print(f"      Risk Level: {ci.get('heavy_rain_risk_level')}")
    print(f"      Riverine Flood Prob: {ci.get('riverine_flood_probability')}")
    print(f"      Hydrological Distinction: {ci.get('rain_vs_flood_distinction_en')[:60]}...")
    assert ci.get("heavy_rain_risk_level") in ["LOW RISK", "MODERATE RISK", "HIGH RISK", "OFFICIAL FLOOD WARNING", "INSUFFICIENT WEATHER DATA"], \
        "Risk level must be one of the 5 defined levels"

    # 2.3 Verify separation between Heavy Rain and Riverine Flood Probability
    # Test synthetic extreme precipitation scenario
    extreme_heavy_rain = AgriculturalWeatherService.analyze_coastal_weather_and_flood_risk(
        district="Dakshina Kannada",
        taluk="Mangaluru",
        is_live=True,
        rain_current=25.0,
        rain_24h=85.0,
        rain_48h=110.0,
        wind_speed=45.0
    )
    print("\n[2.3] Extreme Rainfall Simulation (85mm, 45km/h wind):")
    print(f"      Heavy Rain Risk: {extreme_heavy_rain['heavy_rain_risk_level']}")
    print(f"      Riverine Flood Prob: {extreme_heavy_rain['riverine_flood_probability']}")
    print(f"      Hydrological Note: {extreme_heavy_rain['rain_vs_flood_distinction_en'][:80]}...")
    assert extreme_heavy_rain['heavy_rain_risk_level'] == "HIGH RISK", "85mm rain should trigger HIGH RISK"
    assert "does NOT automatically mean" in extreme_heavy_rain['rain_vs_flood_distinction_en'], \
        "Must clearly state heavy rain does not automatically equate to riverine flooding"

    # 2.4 Proactive PMFBY Insurance Advisory
    ins = extreme_heavy_rain["proactive_insurance_advisory"]
    print("\n[2.4] Proactive Insurance Advisory in Risk Analysis:")
    print(f"      Notified Status: {ins['notified_status_en']}")
    print(f"      Enrollment Window: {ins['enrollment_window_status_en']}")
    print(f"      72-Hour Calamity Rule: {ins['calamity_72h_rule_en']}")
    print(f"      Helpline: {ins['helpline']}")
    print(f"      Non-Retroactivity: {ins['non_retroactive_warning_en']}")
    assert "72" in ins['calamity_72h_rule_en'], "Must mandate 72-hour calamity intimation rule"
    assert "1800-180-1551" in ins['helpline'], "Must provide toll-free PMFBY helpline 1800-180-1551"
    assert "cannot be newly purchased" in ins['non_retroactive_warning_en'].lower(), "Must clarify insurance cannot be bought post-calamity"

    # 2.5 Crop Precautions for Paddy, Arecanut, Banana, Pepper
    crops = [c["crop"] for c in extreme_heavy_rain["crop_precautions"]]
    print(f"\n[2.5] Crop Precautions Provided for: {crops}")
    assert "Paddy" in crops, "Must include Paddy safeguards"
    assert "Arecanut" in crops, "Must include Arecanut safeguards"
    assert "Banana" in crops, "Must include Banana safeguards"
    assert "Pepper" in crops, "Must include Pepper safeguards"

    # 2.6 Spoken Kannada Advisory in Agricultural Conversational Agent
    print("\n[2.6] Agricultural Conversational Agent Coastal Spoken Kannada Advisory:")
    reply_en, reply_kn, stage, details, schemes_m, audio_s, conf, cat, has_aud, disp_title = \
        AgriculturalConversationalAgent._evaluate_weather(
            details={"district": "Dakshina Kannada", "taluk": "Bantwal", "primary_crop": "Arecanut"},
            regional_style="Standard",
            farmer_name="ರೈತ ಮಿತ್ರ",
            farmer_name_en="Farmer Mitra"
        )
    print("      Agent Kannada Spoken Snippet:")
    print("      " + reply_kn[:280].replace("\n", " "))
    assert "ದಕ್ಷಿಣ ಕನ್ನಡ" in reply_kn or "ಕರಾವಳಿ" in reply_kn, "Must mention district/coastal region"
    assert "೭೨ ಗಂಟೆ" in reply_kn or "72 ಗಂಟೆ" in reply_kn, "Spoken Kannada must emphasize 72-hour calamity notification rule"
    assert "1800-180-1551" in reply_kn, "Spoken Kannada must include toll-free helpline"
    assert "ಅಡಿಕೆ" in reply_kn, "Spoken Kannada must provide crop-specific precautions"

    print("  ✓ Feature 2 Coastal Weather & Flood Risk Intelligence verified successfully!")

if __name__ == "__main__":
    verify_feature_1_schemes_and_engine()
    verify_feature_2_coastal_weather()
    print("\n" + "="*70)
    print("ALL TARGETED VERIFICATION TESTS FOR FEATURE 1 & 2 PASSED (EXIT CODE 0)!")
    print("="*70)
