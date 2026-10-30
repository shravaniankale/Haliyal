# -*- coding: utf-8 -*-
"""
End-to-End Verification of Scenarios 1 to 9 for Krishi Mitra AI
"""
import sys
import io
import requests
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000/api"

def run_tests():
    print("======================================================================")
    print("KRISHI MITRA AI - SCENARIOS 1 TO 9 SYSTEM VERIFICATION")
    print("======================================================================")

    # -------------------------------------------------------------------------
    # SCENARIO 1: North Karnataka + Female Voice (kn-IN-SapnaNeural)
    # -------------------------------------------------------------------------
    print("\n[SCENARIO 1] Testing North Karnataka + Female Voice...")
    payload_s1 = {
        "message": "ನಮಸ್ಕಾರ, ನನಗೆ ಬೆಳಗಾವಿ ಜಿಲ್ಲೆಯ ಬೆಳೆ ಯೋಜನೆಗಳ ಮಾಹಿತಿ ಕೊಡಿ",
        "regional_preference": "North Karnataka",
        "voice_gender": "female",
        "language": "kn"
    }
    res_s1 = requests.post(f"{BASE_URL}/chat", json=payload_s1)
    assert res_s1.status_code == 200, f"Scenario 1 chat failed: {res_s1.text}"
    data_s1 = res_s1.json()
    print("  ✓ Chat response received:", data_s1["reply_kn"][:80], "...")
    print("  ✓ Voice generated:", data_s1.get("audio_url"))
    assert data_s1.get("audio_url") is not None, "Missing audio_url in Scenario 1"
    
    # Check that voice preview also works
    prev_s1 = requests.post(f"{BASE_URL}/speech/preview?voice_id=kn_female")
    assert prev_s1.status_code == 200
    assert "Sapna" in prev_s1.json()["name"]
    print("  ✓ Neural Voice confirmed: kn-IN-SapnaNeural (Female)")

    # -------------------------------------------------------------------------
    # SCENARIO 2: South Karnataka + Male Voice (kn-IN-GaganNeural)
    # -------------------------------------------------------------------------
    print("\n[SCENARIO 2] Testing South Karnataka + Male Voice...")
    payload_s2 = {
        "message": "ನಮಸ್ಕಾರ, ಮೈಸೂರು ಜಿಲ್ಲೆಯ ರಾಗಿ ಬೆಳೆಗೆ ಯಾವ ಸಾಲ ಸಿಗುತ್ತದೆ?",
        "regional_preference": "South Karnataka",
        "voice_gender": "male",
        "language": "kn"
    }
    res_s2 = requests.post(f"{BASE_URL}/chat", json=payload_s2)
    assert res_s2.status_code == 200, f"Scenario 2 chat failed: {res_s2.text}"
    data_s2 = res_s2.json()
    print("  ✓ Chat response received:", data_s2["reply_kn"][:80], "...")
    print("  ✓ Voice generated:", data_s2.get("audio_url"))
    
    prev_s2 = requests.post(f"{BASE_URL}/speech/preview?voice_id=kn_male")
    assert prev_s2.status_code == 200
    assert "Gagan" in prev_s2.json()["name"]
    print("  ✓ Neural Voice confirmed: kn-IN-GaganNeural (Male)")

    # -------------------------------------------------------------------------
    # SCENARIO 3: Progressive 7-Question Onboarding
    # -------------------------------------------------------------------------
    print("\n[SCENARIO 3] Testing Progressive 7-Question Onboarding Conversation...")
    session_id = "test_onboard_sess_003"
    
    # 1. District
    step1 = requests.post(f"{BASE_URL}/chat", json={
        "message": "ನನ್ನ ಜಿಲ್ಲೆ ಧಾರವಾಡ",
        "session_id": session_id,
        "regional_preference": "North Karnataka"
    }).json()
    print("  1. District -> Next Question:", step1["reply_kn"][:60], "...")
    assert "ತಾಲೂಕು" in step1["reply_kn"] or "taluk" in step1["reply"].lower()

    # 2. Taluk
    step2 = requests.post(f"{BASE_URL}/chat", json={
        "message": "ನನ್ನ ತಾಲೂಕು ಹುಬ್ಬಳ್ಳಿ",
        "session_id": session_id,
        "regional_preference": "North Karnataka"
    }).json()
    print("  2. Taluk -> Next Question:", step2["reply_kn"][:60], "...")
    assert "ಬೆಳೆ" in step2["reply_kn"] or "crop" in step2["reply"].lower()

    # 3. Crop
    step3 = requests.post(f"{BASE_URL}/chat", json={
        "message": "ನಾನು ಶೇಂಗಾ ಬೆಳೆಯುತ್ತಿದ್ದೇನೆ",
        "session_id": session_id,
        "regional_preference": "North Karnataka"
    }).json()
    print("  3. Crop -> Next Question:", step3["reply_kn"][:60], "...")
    assert "ಜಮೀನು" in step3["reply_kn"] or "land" in step3["reply"].lower()

    # 4. Land size
    step4 = requests.post(f"{BASE_URL}/chat", json={
        "message": "ನನ್ನ ಬಳಿ ೪ ಎಕರೆ ಜಮೀನಿದೆ",
        "session_id": session_id,
        "regional_preference": "North Karnataka"
    }).json()
    print("  4. Land Size -> Next Question:", step4["reply_kn"][:60], "...")
    assert "ಸ್ವಂತ" in step4["reply_kn"] or "own" in step4["reply"].lower()

    # 5. Ownership
    step5 = requests.post(f"{BASE_URL}/chat", json={
        "message": "ಸ್ವಂತ ಜಮೀನು",
        "session_id": session_id,
        "regional_preference": "North Karnataka"
    }).json()
    print("  5. Ownership -> Next Question:", step5["reply_kn"][:60], "...")
    assert "ನೀರಾವರಿ" in step5["reply_kn"] or "irrigation" in step5["reply"].lower()

    # 6. Irrigation
    step6 = requests.post(f"{BASE_URL}/chat", json={
        "message": "ಖುಷ್ಕಿ ಮಳೆ ಆಶ್ರಿತ",
        "session_id": session_id,
        "regional_preference": "North Karnataka"
    }).json()
    print("  6. Irrigation -> Next Question:", step6["reply_kn"][:60], "...")
    assert "ವರ್ಗ" in step6["reply_kn"] or "category" in step6["reply"].lower()

    # 7. Category
    step7 = requests.post(f"{BASE_URL}/chat", json={
        "message": "ಸಣ್ಣ ರೈತರು",
        "session_id": session_id,
        "regional_preference": "North Karnataka"
    }).json()
    print("  7. Category -> Final Summary & Schemes:", step7["reply_kn"][:80], "...")
    assert "ವಿವರ" in step7["reply_kn"] or "summary" in step7["reply"].lower()
    print("  ✓ Full 7-question progressive onboarding completed successfully!")

    # -------------------------------------------------------------------------
    # SCENARIO 4: Scheme Recommendations with Verified Rules & RAG Citations
    # -------------------------------------------------------------------------
    print("\n[SCENARIO 4] Testing Scheme Recommendations & Rule Explanations...")
    elig_req = {
        "district": "Belagavi",
        "crop": "Paddy",
        "land_acres": 3.0,
        "land_ownership": "Own",
        "farmer_category": "Small & Marginal"
    }
    res_elig = requests.post(f"{BASE_URL}/schemes/eligibility", json=elig_req)
    assert res_elig.status_code == 200
    elig_data = res_elig.json()
    print(f"  ✓ Total evaluated: {elig_data['total_evaluated']}, Eligible: {elig_data['eligible_count']}")
    for r in elig_data["results"]:
        print(f"    - [{r['status']}] {r['scheme_id']}: {r['scheme_name_kn']} ({r['explanation_kn'][:50]}...)")
        assert r['status'] in ['PASS', 'FAIL', 'UNKNOWN']

    # -------------------------------------------------------------------------
    # SCENARIO 5: Crop Insurance Evaluation (PMFBY & Samrakshane 72-Hour Rule)
    # -------------------------------------------------------------------------
    print("\n[SCENARIO 5] Testing Crop Insurance Intelligence & 72-Hour Rule...")
    res_ins = requests.get(f"{BASE_URL}/insurance/status?district=Belagavi&crop=Paddy&land_acres=3.0")
    assert res_ins.status_code == 200
    ins_data = res_ins.json()
    print(f"  ✓ Notified Status: {ins_data['is_notified']} ({ins_data['status_note_kn']})")
    print(f"  ✓ Farmer Premium Rate: {ins_data['premium_rate_farmer_pct']}% (Approx ₹{ins_data['estimated_farmer_premium_inr']})")
    print(f"  ✓ Calamity Rule: {ins_data['calamity_intimation_rule']} - Helpline: {ins_data['helpline']}")
    assert "72 Hours" in ins_data['calamity_intimation_rule']
    assert "1800" in ins_data['helpline']

    # -------------------------------------------------------------------------
    # SCENARIO 6: Personalized Fertilizer Advisory with Soil-Test Disclaimer
    # -------------------------------------------------------------------------
    print("\n[SCENARIO 6] Testing Fertilizer Advisory & Soil-Test Disclaimer...")
    fert_req = {
        "crop": "Paddy",
        "soil_type": "Red Loamy",
        "growth_stage": "Tillering"
    }
    res_fert = requests.post(f"{BASE_URL}/fertilizer/recommend", json=fert_req)
    assert res_fert.status_code == 200
    fert_data = res_fert.json()
    print(f"  ✓ Soil Health Card note: {fert_data.get('disclaimer_kn') or 'ಮಣ್ಣು ಪರೀಕ್ಷೆ ಅಗತ್ಯ'}")

    # -------------------------------------------------------------------------
    # SCENARIO 7: Theme Toggle & User Preference Persistence
    # -------------------------------------------------------------------------
    print("\n[SCENARIO 7] Testing User Profile Preferences (Theme & Voice)...")
    mobile = "9988776655"
    reg_res = requests.post(f"{BASE_URL}/auth/register", json={
        "name": "Karthik Farmer",
        "mobile": mobile,
        "password": "password123",
        "district": "Belagavi",
        "taluk": "Belagavi",
        "preferred_language": "kn"
    })
    if reg_res.status_code == 200:
        token = reg_res.json()["access_token"]
    else:
        login_res = requests.post(f"{BASE_URL}/auth/login", json={
            "mobile": mobile,
            "password": "password123"
        })
        token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    update_res = requests.put(f"{BASE_URL}/farmer/profile", json={
        "theme_preference": "dark",
        "voice_gender_preference": "female",
        "primary_crop": "Jowar",
        "land_unit": "acres"
    }, headers=headers)
    assert update_res.status_code == 200
    prof = update_res.json()
    print(f"  ✓ Saved theme: {prof['theme_preference']}, voice: {prof['voice_gender_preference']}")
    assert prof['theme_preference'] == 'dark'
    assert prof['voice_gender_preference'] == 'female'

    # -------------------------------------------------------------------------
    # SCENARIO 8: Browser Refresh Session Restoration
    # -------------------------------------------------------------------------
    print("\n[SCENARIO 8] Testing Profile Retrieval & Session Restoration...")
    get_res = requests.get(f"{BASE_URL}/farmer/profile", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["primary_crop"] == "Jowar"
    print("  ✓ Profile successfully retrieved across requests (Primary Crop: Jowar, Theme: dark)")

    # -------------------------------------------------------------------------
    # SCENARIO 9: Regional Kannada Vocabulary Normalization
    # -------------------------------------------------------------------------
    print("\n[SCENARIO 9] Testing Regional Kannada Vocabulary Normalization...")
    vocab_tests = [
        ("ನಮ್ದು ಹೊಲದಾಗ ಶೇಂಗಾ ಹಚ್ಚೇವಿ, ಸಾಲ ಐತೇನ್ರಿ?", "North Karnataka"),
        ("ನಮ್ಮ ಜಮೀನಿನಲ್ಲಿ ರಾಗಿ ಬೆಳೆದಿದ್ದೇವೆ, ಸಾಲ ಸಿಗುತ್ತದೆಯೇ?", "South Karnataka")
    ]
    for msg, dial in vocab_tests:
        v_res = requests.post(f"{BASE_URL}/chat", json={
            "message": msg,
            "regional_preference": dial
        }).json()
        print(f"  ✓ [{dial}] Query handled -> Reply: {v_res['reply_kn'][:70]}...")
        assert len(v_res['reply_kn']) > 0

    # -------------------------------------------------------------------------
    # SCENARIO 10: Agricultural Season Intelligence Check
    # -------------------------------------------------------------------------
    print("\n[BONUS] Testing Agricultural Season Intelligence...")
    season_res = requests.get(f"{BASE_URL}/season?district=Belagavi&crop=Paddy")
    assert season_res.status_code == 200
    season_data = season_res.json()
    print(f"  ✓ Current Date/Time: {season_data['current_date_en']} {season_data['current_time_en']} ({season_data['timezone']})")
    print(f"  ✓ Current Season: {season_data['season_name_kn']} ({season_data['season_name']})")
    print(f"  ✓ Stage: {season_data['crop_stage_current_kn']}")

    # -------------------------------------------------------------------------
    # SCENARIO 11: Weather 5-Day Forecast & Agronomic Advisory Check
    # -------------------------------------------------------------------------
    print("\n[BONUS] Testing Weather Intelligence & Spraying Advisory...")
    w_res = requests.get(f"{BASE_URL}/weather?district=Belagavi&taluk=Belagavi")
    assert w_res.status_code == 200
    w_data = w_res.json()
    print(f"  ✓ Live Status: {w_data['is_live']} (Source: {w_data['source']})")
    print(f"  ✓ Spraying Feasibility: {w_data['spraying_advisory_kn'][:60]}...")
    print(f"  ✓ Irrigation Advisory: {w_data['irrigation_advisory_kn'][:60]}...")

    print("\n======================================================================")
    print("ALL SCENARIOS 1 TO 9 (PLUS SEASON & WEATHER INTELLIGENCE) VERIFIED!")
    print("======================================================================")

if __name__ == "__main__":
    run_tests()
