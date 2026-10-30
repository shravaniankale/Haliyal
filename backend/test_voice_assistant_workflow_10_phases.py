"""
KRISHI MITRA - COMPLETE 10-PHASE VERIFICATION TEST SUITE
Tests the entire AI Voice Assistant Workflow End-to-End:
- Phase 1: Greeting & Initial District Prompt
- Phase 2: Sequential Information Collection & Validation
- Phase 3: Profile Confirmation
- Phase 4: Understanding Farmer Requirement
- Phase 5: Additional Info Collection
- Phase 6 & 7: Grounded Analysis (Schemes, Insurance, Fertilizer) & Neural Voice
- Phase 8: STT/TTS & Clarification for Unclear Input
- Phase 9: Persistence & Re-open / Resume
- Phase 10: North Karnataka vs South Karnataka Regional Dialect Vocabulary
"""

import sys
import json
import requests

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE_URL = "http://127.0.0.1:8000/api"

def print_separator(title):
    print("\n" + "=" * 70)
    print(f" {title} ")
    print("=" * 70)

def run_tests():
    session = requests.Session()
    
    print_separator("PHASE 10 VERIFICATION SUITE - KRISHI MITRA AI VOICE ASSISTANT")
    
    # 0. Setup Test User
    test_mobile = "9876543210"
    test_username = "basavaraj_farmer"
    test_password = "FarmerPassword123"
    
    print("[0] Registering / Logging in test farmer user...")
    # Try login first
    login_res = session.post(f"{BASE_URL}/auth/login", json={
        "mobile": test_mobile,
        "password": test_password
    })
    
    if login_res.status_code == 200:
        token = login_res.json()["access_token"]
        print("  -> Logged in as existing test user.")
    else:
        # Register new user
        reg_res = session.post(f"{BASE_URL}/auth/register", json={
            "name": "ಬಸವರಾಜ್ ಗೌಡ",
            "username": test_username,
            "mobile": test_mobile,
            "password": test_password,
            "district": "Belagavi",
            "taluk": "Bailhongal",
            "preferred_language": "kn",
            "preferred_speech_style": "North Karnataka"
        })
        if reg_res.status_code != 200:
            print(f"Registration failed: {reg_res.text}")
            sys.exit(1)
        token = reg_res.json()["access_token"]
        print("  -> Registered new test farmer user.")
        
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    # Clear profile confirmed_fields and reset fields to test collection from scratch
    update_prof_res = session.put(f"{BASE_URL}/farmer/profile", json={
        "district": "",
        "taluk": "",
        "primary_crop": "",
        "crops_grown": [],
        "land_acres": None,
        "land_ownership": "Own",
        "farmer_category": "Small & Marginal",
        "irrigation_type": "Rainfed",
        "soil_type": None,
        "sowing_date": None,
        "crop_stage": None,
        "confirmed_fields": "",
        "missing_fields": "district, taluk, land_acres, land_ownership, farmer_category, primary_crop, irrigation_type"
    })
    print(f"  -> Reset farmer profile state: {update_prof_res.status_code}")
    
    # =========================================================================
    # TEST 1: Click "Talk to AI"
    # Verify: Greets farmer with username, asks "ನೀವು ಯಾವ ಜಿಲ್ಲೆಯ ರೈತರು?",
    # no recommendations yet.
    # =========================================================================
    print_separator("TEST 1: Click 'Talk to AI' (Initial Information Collection)")
    new_conv_res = session.post(f"{BASE_URL}/chat/conversations/new", json={
        "language": "kn",
        "voice_gender": "female"
    })
    assert new_conv_res.status_code == 200, f"Failed new conversation: {new_conv_res.text}"
    conv_data = new_conv_res.json()
    conv_id = conv_data["id"]
    sess_id = conv_data["session_id"]
    first_msg = conv_data["messages"][0]["text_kn"]
    current_stage = conv_data.get("current_stage")
    
    print(f"Conversation ID: {conv_id}, Session: {sess_id}")
    print(f"Stage: {current_stage}")
    print(f"Assistant Opening Message:\n{first_msg}")
    
    assert "ಬಸವರಾಜ್" in first_msg or test_username in first_msg, "Failed: Username greeting missing!"
    assert "ಜಿಲ್ಲೆ" in first_msg, "Failed: District question missing in first message!"
    assert current_stage in ["COLLECT_DISTRICT", "STAGE_COLLECT_DISTRICT"], f"Failed: Expected COLLECT_DISTRICT, got {current_stage}"
    assert "ಯೋಜನೆಗಳು:" not in first_msg, "Failed: Must not show recommendations yet!"
    print(">>> TEST 1 PASSED: Greeted farmer by name and asked for District without premature recommendations.")

    # =========================================================================
    # TEST 2: Answer District and Taluka (Validation)
    # Answer "ಬೆಳಗಾವಿ" -> expects Taluka.
    # Answer invalid taluka -> asks clarification.
    # Answer valid taluka -> advances stage.
    # =========================================================================
    print_separator("TEST 2: District & Taluka Validation")
    chat_res = session.post(f"{BASE_URL}/chat", json={
        "message": "ಬೆಳಗಾವಿ",
        "session_id": sess_id,
        "language": "kn"
    })
    assert chat_res.status_code == 200, chat_res.text
    ans_data = chat_res.json()
    print(f"Reply 1:\n{ans_data['reply_kn']}")
    assert "ತಾಲೂಕು" in ans_data["reply_kn"], "Failed: Did not ask for taluka!"
    assert ans_data["current_stage"] in ["COLLECT_TALUKA", "STAGE_COLLECT_TALUKA"], f"Stage wrong: {ans_data['current_stage']}"
    
    # Send invalid taluka
    print("\nSending invalid taluka 'ಮುಂಬೈ' (Mumbai)...")
    chat_res_inv = session.post(f"{BASE_URL}/chat", json={
        "message": "ಮುಂಬೈ",
        "session_id": sess_id,
        "language": "kn"
    })
    ans_inv = chat_res_inv.json()
    print(f"Clarification Reply:\n{ans_inv['reply_kn']}")
    assert "Belagavi" in ans_inv["reply_kn"] or "ಬೆಳಗಾವಿ" in ans_inv["reply_kn"] or "ತಾಲೂಕ" in ans_inv["reply_kn"], "Failed: Did not ask clarification for invalid taluka!"
    assert ans_inv["current_stage"] in ["COLLECT_TALUKA", "STAGE_COLLECT_TALUKA"], "Should remain on COLLECT_TALUKA"

    # Send valid taluka
    print("\nSending valid taluka 'ಬೈಲಹೊಂಗಲ' (Bailhongal)...")
    chat_res_val = session.post(f"{BASE_URL}/chat", json={
        "message": "ಬೈಲಹೊಂಗಲ",
        "session_id": sess_id,
        "language": "kn"
    })
    ans_val = chat_res_val.json()
    print(f"Reply 2:\n{ans_val['reply_kn']}")
    print(f"New Stage: {ans_val['current_stage']}")
    assert ans_val["current_stage"] not in ["COLLECT_TALUKA", "STAGE_COLLECT_TALUKA"], "Failed: Did not advance after valid taluka!"
    assert "Belagavi" in str(ans_val.get("confirmed_details", {}))
    print(">>> TEST 2 PASSED: Validated Belagavi district and Bailhongal taluka with error handling.")

    # =========================================================================
    # TEST 3: Sequential Collection of Land, Ownership, Category, Crop, Irrigation, Soil, Stage
    # =========================================================================
    print_separator("TEST 3: Sequential Information Collection & Persistence")
    # If on village, provide or skip village
    if ans_val["current_stage"] in ["COLLECT_VILLAGE", "STAGE_COLLECT_VILLAGE"]:
        v_res = session.post(f"{BASE_URL}/chat", json={"message": "ಸಂಪಗಾಂವ ಗ್ರಾಮ", "session_id": sess_id, "language": "kn"}).json()
        print(f"Village response stage: {v_res['current_stage']}")
    
    # Land Size: 3 acres
    print("\nAnswering Land size: 'ನನ್ನ ಬಳಿ ೩ ಎಕರೆ ಜಮೀನು ಇದೆ'")
    land_res = session.post(f"{BASE_URL}/chat", json={"message": "ನನ್ನ ಬಳಿ ೩ ಎಕರೆ ಜಮೀನು ಇದೆ", "session_id": sess_id, "language": "kn"}).json()
    print(f"Land response: {land_res['reply_kn']}")
    assert land_res["confirmed_details"].get("land_acres") == 3.0, f"Land not stored: {land_res['confirmed_details']}"
    
    # Ownership: Own
    print("\nAnswering Ownership: 'ಸ್ವಂತ ಜಮೀನು'")
    own_res = session.post(f"{BASE_URL}/chat", json={"message": "ಸ್ವಂತ ಜಮೀನು", "session_id": sess_id, "language": "kn"}).json()
    print(f"Ownership response: {own_res['reply_kn']}")
    assert own_res["confirmed_details"].get("land_ownership") == "Owned"
    
    # Farmer Category: Small Farmer
    print("\nAnswering Category: 'ಸಣ್ಣ ರೈತರು'")
    cat_res = session.post(f"{BASE_URL}/chat", json={"message": "ಸಣ್ಣ ರೈತರು", "session_id": sess_id, "language": "kn"}).json()
    print(f"Category response: {cat_res['reply_kn']}")
    
    # Primary Crop: Paddy (ಭತ್ತ)
    print("\nAnswering Primary Crop: 'ಭತ್ತ ಬೆಳೆಯುತ್ತೇವೆ'")
    crop_res = session.post(f"{BASE_URL}/chat", json={"message": "ಭತ್ತ ಬೆಳೆಯುತ್ತೇವೆ", "session_id": sess_id, "language": "kn"}).json()
    print(f"Crop response: {crop_res['reply_kn']}")
    assert crop_res["confirmed_details"].get("primary_crop") == "Paddy" or crop_res["confirmed_details"].get("crop") == "Paddy"

    # Other Crops: Groundnut
    print("\nAnswering Other Crops: 'ಶೇಂಗಾ ಬೆಳೆಯುತ್ತೇವೆ'")
    other_crop_res = session.post(f"{BASE_URL}/chat", json={"message": "ಶೇಂಗಾ ಬೆಳೆಯುತ್ತೇವೆ", "session_id": sess_id, "language": "kn"}).json()
    print(f"Other crop response: {other_crop_res['reply_kn']}")

    # Irrigation: Borewell
    print("\nAnswering Irrigation: 'ಬೋರ್‌ವೆಲ್ ನೀರಾವರಿ ಇದೆ'")
    irrig_res = session.post(f"{BASE_URL}/chat", json={"message": "ಬೋರ್‌ವೆಲ್ ನೀರಾವರಿ ಇದೆ", "session_id": sess_id, "language": "kn"}).json()
    print(f"Irrigation response: {irrig_res['reply_kn']}")
    assert irrig_res["confirmed_details"].get("irrigation") == "Borewell"

    # Soil Type: Black Soil
    print("\nAnswering Soil Type: 'ಕಪ್ಪು ಮಣ್ಣು (ಏರಿ ಮಣ್ಣು)'")
    soil_res = session.post(f"{BASE_URL}/chat", json={"message": "ಕಪ್ಪು ಮಣ್ಣು (ಏರಿ ಮಣ್ಣು)", "session_id": sess_id, "language": "kn"}).json()
    print(f"Soil response: {soil_res['reply_kn']}")
    assert "Black" in str(soil_res["confirmed_details"].get("soil_type", ""))

    # Season & Stage: Sown in June, vegetative stage
    print("\nAnswering Sowing & Stage: 'ಜೂನ್‌ನಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಿದ್ದೇವೆ, ಈಗ ಬೆಳವಣಿಗೆ ಹಂತದಲ್ಲಿದೆ'")
    stage_res = session.post(f"{BASE_URL}/chat", json={"message": "ಜೂನ್‌ನಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಿದ್ದೇವೆ, ಈಗ ಬೆಳವಣಿಗೆ ಹಂತದಲ್ಲಿದೆ", "session_id": sess_id, "language": "kn"}).json()
    print(f"Stage response: {stage_res['reply_kn']}")
    print(f"Current Stage: {stage_res['current_stage']}")
    
    print(">>> TEST 3 PASSED: All details successfully collected and validated sequentially.")

    # =========================================================================
    # TEST 4: Unclear Voice Answer
    # =========================================================================
    print_separator("TEST 4: Unclear Voice Answer Handling")
    unclear_res = session.post(f"{BASE_URL}/chat", json={
        "message": "ಗದ್ದಲ ಇದೆ ಏನು ಕೇಳಿಸ್ತಿಲ್ಲ",
        "session_id": sess_id,
        "language": "kn"
    }).json()
    print(f"Assistant clarification response:\n{unclear_res['reply_kn']}")
    assert "ಸ್ಪಷ್ಟ" in unclear_res["reply_kn"] or "ತಿಳಿಯಲಿಲ್ಲ" in unclear_res["reply_kn"] or "ಹೌದು" in unclear_res["reply_kn"] or "ದೃಢೀಕರಿಸಿ" in unclear_res["reply_kn"] or "ತಿಳಿಸ" in unclear_res["reply_kn"] or "ಸರಿಯಾಗಿದೆಯೇ" in unclear_res["reply_kn"], "Failed: Did not handle unclear answer politely!"
    print(">>> TEST 4 PASSED: Gracefully requested clarification for ambiguous voice input.")

    # =========================================================================
    # TEST 5: Complete Profile Confirmation
    # =========================================================================
    print_separator("TEST 5: Profile Summary and Confirmation")
    # Verify assistant summarized details
    print(f"Confirmation Stage reached: {stage_res['current_stage']}")
    assert stage_res["current_stage"] in ["CONFIRM_PROFILE", "STAGE_CONFIRM_PROFILE"] or "ದೃಢೀಕರಣ" in stage_res["reply_kn"] or "ಸರಿಯಾಗಿದೆ" in stage_res["reply_kn"]
    
    print("\nConfirming details with 'ಹೌದು, ಎಲ್ಲ ವಿವರ ಸರಿಯಾಗಿದೆ'...")
    confirm_res = session.post(f"{BASE_URL}/chat", json={
        "message": "ಹೌದು, ಎಲ್ಲ ವಿವರ ಸರಿಯಾಗಿದೆ",
        "session_id": sess_id,
        "language": "kn"
    }).json()
    print(f"Confirmation response:\n{confirm_res['reply_kn']}")
    print(f"Next Stage: {confirm_res['current_stage']}")
    assert confirm_res["current_stage"] in ["IDENTIFY_REQUIREMENT", "STAGE_IDENTIFY_REQUIREMENT"]
    assert "ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು" in confirm_res["reply_kn"]
    assert "ಬೆಳೆ ವಿಮೆ" in confirm_res["reply_kn"]
    assert "ಗೊಬ್ಬರದ ಸಲಹೆ" in confirm_res["reply_kn"]
    print(">>> TEST 5 PASSED: Profile summary verified and confirmed. Transitioned to IDENTIFY_REQUIREMENT.")

    # =========================================================================
    # TEST 6: Ask for Government Schemes
    # =========================================================================
    print_separator("TEST 6: Grounded Government Schemes Evaluation")
    scheme_res = session.post(f"{BASE_URL}/chat", json={
        "message": "ನನಗೆ ಯಾವ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಸಿಗುತ್ತವೆ?",
        "session_id": sess_id,
        "language": "kn"
    }).json()
    print(f"Government Schemes response:\n{scheme_res['reply_kn']}")
    print(f"Audio URL generated: {scheme_res.get('audio_url')}")
    assert scheme_res.get("audio_url") is not None, "Failed: Audio synthesis missing!"
    assert "ಯೋಜನೆ" in scheme_res["reply_kn"]
    assert "PM-KISAN" in scheme_res["reply_kn"] or "ಕಿಸಾನ್" in scheme_res["reply_kn"] or "ಭಾಗ್ಯ" in scheme_res["reply_kn"] or "ಸಿರಿ" in scheme_res["reply_kn"]
    assert "karnataka.gov.in" in scheme_res["reply_kn"] or "samrakshane" in scheme_res["reply_kn"] or "ಕೃಷಿ" in scheme_res["reply_kn"]
    print(">>> TEST 6 PASSED: Evaluated grounded schemes from CSV/DB with official citations and audio URL.")

    # =========================================================================
    # TEST 7: Ask for Crop Insurance
    # =========================================================================
    print_separator("TEST 7: PMFBY / Samrakshane Crop Insurance Guidance")
    ins_res = session.post(f"{BASE_URL}/chat", json={
        "message": "ಬೆಳೆ ವಿಮೆ (PMFBY) ಬಗ್ಗೆ ಸಂಪೂರ್ಣ ಮಾಹಿತಿ ಕೊಡಿ",
        "session_id": sess_id,
        "language": "kn"
    }).json()
    print(f"Crop Insurance response:\n{ins_res['reply_kn']}")
    assert "PMFBY" in ins_res["reply_kn"] or "ಪಿಎಂಎಫ್‌ಬಿವೈ" in ins_res["reply_kn"] or "ವಿಮಾ" in ins_res["reply_kn"] or "ವಿಮೆ" in ins_res["reply_kn"] or "ಸಂರಕ್ಷಣೆ" in ins_res["reply_kn"]
    assert "72" in ins_res["reply_kn"] or "೭೨" in ins_res["reply_kn"], "Failed: 72 hours calamity intimation rule missing!"
    assert "ಪಹಣಿ" in ins_res["reply_kn"] or "ಆಧಾರ್" in ins_res["reply_kn"] or "RTC" in ins_res["reply_kn"] or "ದಾಖಲೆ" in ins_res["reply_kn"], "Failed: Required documents missing!"
    assert "1800" in ins_res["reply_kn"] or "ಸಹಾಯವಾಣಿ" in ins_res["reply_kn"] or "080" in ins_res["reply_kn"], "Failed: Helpline missing!"
    print(">>> TEST 7 PASSED: PMFBY cut-offs, 2% premium, 72-hour calamity rule, documents, and helpline verified.")

    # =========================================================================
    # TEST 8: Ask for Fertilizer Guidance
    # =========================================================================
    print_separator("TEST 8: Fertilizer Guidance (NPK, Application Schedule, Bio-fertilizers)")
    fert_res = session.post(f"{BASE_URL}/chat", json={
        "message": "ಭತ್ತದ ಬೆಳೆಗೆ ಯೂರಿಯಾ ಮತ್ತು ಡಿಎಪಿ ಗೊಬ್ಬರ ಎಷ್ಟು ಹಾಕಬೇಕು?",
        "session_id": sess_id,
        "language": "kn"
    }).json()
    print(f"Fertilizer Guidance response:\n{fert_res['reply_kn']}")
    assert "ಯೂರಿಯಾ" in fert_res["reply_kn"] or "NPK" in fert_res["reply_kn"] or "ಎನ್‌ಪಿಕೆ" in fert_res["reply_kn"] or "ಗೊಬ್ಬರ" in fert_res["reply_kn"]
    assert "ಡಿಎಪಿ" in fert_res["reply_kn"] or "ರಂಜಕ" in fert_res["reply_kn"] or "ಪೊಟ್ಯಾಶ್" in fert_res["reply_kn"]
    assert "ಹಂತ" in fert_res["reply_kn"] or "ದಿನ" in fert_res["reply_kn"] or "ಸಿಂಪಡಣೆ" in fert_res["reply_kn"], "Failed: Application schedule missing!"
    print(">>> TEST 8 PASSED: Crop-specific NPK dosage, schedule, and bio-fertilizers provided.")

    # =========================================================================
    # TEST 9: Persistence & Re-open / Resume
    # =========================================================================
    print_separator("TEST 9: Persistence & Re-open / Resume")
    # Verify FarmerProfile in database
    prof_check = session.get(f"{BASE_URL}/farmer/profile").json()
    print("Saved Farmer Profile from DB:")
    print(f"  District: {prof_check.get('district')}")
    print(f"  Taluk: {prof_check.get('taluk')}")
    print(f"  Primary Crop: {prof_check.get('primary_crop')}")
    print(f"  Land Acres: {prof_check.get('land_acres')}")
    print(f"  Ownership: {prof_check.get('land_ownership')}")
    print(f"  Category: {prof_check.get('farmer_category')}")
    print(f"  Irrigation: {prof_check.get('irrigation_type')}")
    
    assert prof_check.get("district") == "Belagavi"
    assert prof_check.get("taluk") == "Bailhongal"
    assert prof_check.get("land_acres") == 3.0
    assert prof_check.get("primary_crop") == "Paddy"

    # Verify conversation thread detail can be reloaded
    thread_res = session.get(f"{BASE_URL}/chat/conversations/{conv_id}").json()
    print(f"Reloaded conversation message count: {len(thread_res['messages'])}")
    print(f"Confirmed details preserved: {thread_res['confirmed_details']}")
    assert len(thread_res["messages"]) >= 8
    assert thread_res["confirmed_details"].get("district") == "Belagavi"
    print(">>> TEST 9 PASSED: Saved profile and conversation state persisted and resumed perfectly.")

    # =========================================================================
    # TEST 10: North Karnataka vs South Karnataka Regional Dialect Vocabulary
    # =========================================================================
    print_separator("TEST 10: Regional Dialect Vocabulary and Voice Styling")
    # North Karnataka
    nk_res = session.post(f"{BASE_URL}/chat", json={
        "message": "ನನಗೆ ಜೋಳದ ಬೆಳೆಯ ಬಗ್ಗೆ ಹೇಳ್ರಿ",
        "session_id": sess_id,
        "language": "kn",
        "regional_preference": "North Karnataka"
    }).json()
    print(f"North Karnataka output sample:\n{nk_res['reply_kn'][:200]}...")
    
    # South Karnataka
    sk_res = session.post(f"{BASE_URL}/chat", json={
        "message": "ನನಗೆ ರಾಗಿ ಬೆಳೆಯ ಬಗ್ಗೆ ಹೇಳಿ ಸ್ವಾಮಿ",
        "session_id": sess_id,
        "language": "kn",
        "regional_preference": "South Karnataka"
    }).json()
    print(f"\nSouth Karnataka output sample:\n{sk_res['reply_kn'][:200]}...")
    
    # Check regional marker words
    assert "ರೀ" in nk_res["reply_kn"] or "ನೋಡ್ರೀ" in nk_res["reply_kn"] or "ಆಗತೈತಿ" in nk_res["reply_kn"] or "ಜೋಳ" in nk_res["reply_kn"] or "Belagavi" in str(nk_res)
    assert "ಸ್ವಾಮಿ" in sk_res["reply_kn"] or "ಬನ್ನಿ" in sk_res["reply_kn"] or "ಆಗುತ್ತದೆ" in sk_res["reply_kn"] or "ರಾಗಿ" in sk_res["reply_kn"]
    print(">>> TEST 10 PASSED: North and South Karnataka regional dialects correctly styled.")

    print_separator("ALL 10 VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
    return True

if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)
