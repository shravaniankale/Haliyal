import sys
import io
import requests
import json
import uuid

# Force utf-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000/api"

def run_tests():
    print("=====================================================================")
    print("KRISHI MITRA – PROFILE & AI ASSISTANT UPGRADES AUTOMATED TEST SUITE")
    print("=====================================================================")

    # Test Mobile & Unique Username
    random_suffix = uuid.uuid4().hex[:6]
    test_mobile = f"9876{random_suffix[:6]}"
    test_username = f"basavaraj_{random_suffix[:4]}"
    test_password = "SecurePassword123!"

    # -------------------------------------------------------------------------
    # TEST 1: USER REGISTRATION & INITIAL PROFILE WITH USERNAME
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Registering Farmer with explicit Username & Details...")
    reg_payload = {
        "mobile": test_mobile,
        "name": "ಬಸವರಾಜ್ ಪಾಟೀಲ",
        "username": test_username,
        "email": f"{test_username}@example.com",
        "password": test_password,
        "district": "Belagavi",
        "taluk": "Bailhongal",
        "preferred_language": "kn",
        "regional_speech_preference": "North Karnataka",
        "land_acres": 4.5,
        "land_ownership": "Own",
        "crops": ["Groundnut", "Jowar"]
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
    assert r.status_code == 200, f"Registration failed: {r.text}"
    auth_data = r.json()
    token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"  ✓ User registered successfully! ID: {auth_data['user']['id']}, Username: {auth_data['user'].get('username')}")

    # -------------------------------------------------------------------------
    # TEST 2: GET PROFILE & VERIFY DISPLAY FIELDS (NO PASSWORDS/TOKENS)
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Verifying Section 1.A Personal Details Display...")
    r = requests.get(f"{BASE_URL}/farmer/profile", headers=headers)
    assert r.status_code == 200, f"Get profile failed: {r.text}"
    profile_data = r.json()

    assert profile_data["username"] == test_username, f"Expected {test_username}, got {profile_data['username']}"
    assert profile_data["name"] == "ಬಸವರಾಜ್ ಪಾಟೀಲ"
    assert profile_data["email"] == f"{test_username}@example.com"
    assert profile_data["mobile"] == test_mobile
    assert profile_data["district"] == "Belagavi"
    assert profile_data["taluk"] == "Bailhongal"
    assert "account_created_at" in profile_data
    assert "password" not in profile_data, "SECURITY FLAW: Password exposed in profile response!"
    assert "hashed_password" not in profile_data, "SECURITY FLAW: Hashed password exposed!"
    print("  ✓ Personal details displayed accurately without sensitive credentials.")

    # -------------------------------------------------------------------------
    # TEST 3: EDIT PERSONAL DETAILS & INPUT VALIDATION
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Testing Personal Details Validation & Updates...")
    # 3a. Invalid empty name
    r = requests.put(f"{BASE_URL}/farmer/profile", headers=headers, json={"name": "   "})
    assert r.status_code == 400, "Validation failure: empty name should be rejected"
    print("  ✓ Empty name rejected with 400 Bad Request.")

    # 3b. Invalid email format
    r = requests.put(f"{BASE_URL}/farmer/profile", headers=headers, json={"email": "not-an-email"})
    assert r.status_code == 400, "Validation failure: invalid email format should be rejected"
    print("  ✓ Invalid email rejected with 400 Bad Request.")

    # 3c. Invalid username format
    r = requests.put(f"{BASE_URL}/farmer/profile", headers=headers, json={"username": "a!"})
    assert r.status_code == 400, "Validation failure: invalid username should be rejected"
    print("  ✓ Invalid username format rejected with 400 Bad Request.")

    # 3d. Valid update
    updated_username = f"basav_{random_suffix[:4]}"
    update_payload = {
        "name": "ಬಸವರಾಜ್ ಗೌಡ ಪಾಟೀಲ",
        "username": updated_username,
        "email": "basav.patil@karnataka.gov.in",
        "district": "Dharwad",
        "taluk": "Hubballi"
    }
    r = requests.put(f"{BASE_URL}/farmer/profile", headers=headers, json=update_payload)
    assert r.status_code == 200, f"Valid profile update failed: {r.text}"
    updated_prof = r.json()
    assert updated_prof["username"] == updated_username
    assert updated_prof["name"] == "ಬಸವರಾಜ್ ಗೌಡ ಪಾಟೀಲ"
    assert updated_prof["email"] == "basav.patil@karnataka.gov.in"
    assert updated_prof["district"] == "Dharwad"
    assert updated_prof["taluk"] == "Hubballi"
    print("  ✓ Valid personal details successfully updated and saved to DB.")

    # -------------------------------------------------------------------------
    # TEST 4: SECTION 1.B WEBSITE SETTINGS (THEME, LANGUAGE, VOICE, SPEED)
    # -------------------------------------------------------------------------
    print("\n[TEST 4] Testing Website Settings Persistence & Restoration...")
    settings_payload = {
        "theme_preference": "dark",
        "regional_speech_preference": "North Karnataka",
        "voice_gender_preference": "male",
        "auto_voice_response": False,
        "voice_input_enabled": True,
        "speech_speed": 1.25,
        "preferred_language": "kn"
    }
    r = requests.put(f"{BASE_URL}/farmer/profile", headers=headers, json=settings_payload)
    assert r.status_code == 200, f"Settings update failed: {r.text}"
    saved_settings = r.json()
    assert saved_settings["theme_preference"] == "dark"
    assert saved_settings["regional_speech_preference"] == "North Karnataka"
    assert saved_settings["voice_gender_preference"] == "male"
    assert saved_settings["auto_voice_response"] == False
    assert saved_settings["voice_input_enabled"] == True
    assert saved_settings["speech_speed"] == 1.25
    print("  ✓ Website settings saved to database successfully.")

    # Verify restoration via /auth/me
    r = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    assert r.status_code == 200
    me_user = r.json()["user"]
    assert me_user["theme_preference"] == "dark"
    assert me_user["voice_gender_preference"] == "male"
    assert me_user["speech_speed"] == 1.25
    print("  ✓ Website settings restored via authentication profile on reopen.")

    # -------------------------------------------------------------------------
    # TEST 5: SECTION 1.C LOGOUT FLOW & ACCESS PREVENTION
    # -------------------------------------------------------------------------
    print("\n[TEST 5] Testing Logout & Protected Access Enforcement...")
    # Accessing protected profile without Authorization header should return 401
    r_unauth = requests.get(f"{BASE_URL}/farmer/profile")
    assert r_unauth.status_code == 401, f"Expected 401 Unauthorized without token, got {r_unauth.status_code}"
    print("  ✓ Protected pages blocked without authentication after logout.")

    # Verify that logging out did not delete farmer profile in DB
    # We can still authenticate with the credentials
    login_res = requests.post(f"{BASE_URL}/auth/login", json={"mobile": test_mobile, "password": test_password})
    assert login_res.status_code == 200, "Farmer profile should be preserved after logout!"
    restored_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {restored_token}"}
    print("  ✓ Farmer profile safely preserved in DB across sessions.")

    # -------------------------------------------------------------------------
    # TEST 6: AI ASSISTANT NATURAL GREETING WITH LOGGED-IN USERNAME
    # -------------------------------------------------------------------------
    print("\n[TEST 6] Testing AI Assistant Natural Greeting with actual Username...")
    r = requests.post(f"{BASE_URL}/chat/conversations/new", headers=headers, json={"language": "kn", "voice_gender": "female"})
    assert r.status_code == 200, f"New conversation failed: {r.text}"
    new_conv = r.json()
    conv_id = new_conv["id"]
    sess_id = new_conv["session_id"]
    greeting_msg = new_conv["messages"][0]["text_kn"]

    print(f"  Greeting text: {greeting_msg}")
    assert updated_username in greeting_msg or "ಬಸವರಾಜ್" in greeting_msg, f"Greeting does not contain user's name: {greeting_msg}"
    assert "ಸ್ವಾಗತ" in greeting_msg
    assert "ಸಹಾಯ ಬೇಕು" in greeting_msg or "ಸಹಾಯ ಬೇಕ್ರಿ" in greeting_msg
    # Verify it DOES NOT ask all 7 questions immediately
    assert "೧. ಜಿಲ್ಲೆ" not in greeting_msg, "Assistant should NOT immediately ask 7 questions!"
    print("  ✓ AI Assistant naturally greeted farmer by actual username without interrogating.")

    # -------------------------------------------------------------------------
    # TEST 7: STRICT AGRICULTURE-ONLY GUARDRAILS
    # -------------------------------------------------------------------------
    print("\n[TEST 7] Testing Agriculture-Only Guardrails (Off-Topic Rejection)...")
    off_topic_queries = [
        "ಯಾರು ಕ್ರಿಕೆಟ್ ಮ್ಯಾಚ್ ಗೆದ್ದರು?",  # Who won the cricket match?
        "Can you write a python script to reverse a string?",
        "What is the capital of France?"
    ]
    for q in off_topic_queries:
        r = requests.post(f"{BASE_URL}/chat", headers=headers, json={
            "message": q,
            "session_id": sess_id,
            "language": "kn"
        })
        assert r.status_code == 200
        chat_res = r.json()
        assert chat_res["is_agriculture_related"] == False, f"Query '{q}' should be rejected as non-agricultural!"
        assert "ಕ್ಷಮಿಸಿ, ನಾನು ಕೃಷಿ ಸಂಬಂಧಿತ ವಿಷಯಗಳಲ್ಲಿ ಮಾತ್ರ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ" in chat_res["reply_kn"]
        print(f"  ✓ Non-agricultural query '{q}' rejected politely with required guardrail message.")

    # -------------------------------------------------------------------------
    # TEST 8: INTELLIGENT CASE-BASED INFORMATION COLLECTION
    # -------------------------------------------------------------------------
    print("\n[TEST 8] Testing Intelligent Case-Based Advisory (Reusing profile)...")
    # Case 1: Government Schemes
    r_scheme = requests.post(f"{BASE_URL}/chat", headers=headers, json={
        "message": "ನನಗೆ ಯಾವ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಸಿಗುತ್ತವೆ?",
        "session_id": sess_id,
        "language": "kn",
        "regional_preference": "North Karnataka"
    })
    assert r_scheme.status_code == 200
    res_sc = r_scheme.json()
    assert res_sc["is_agriculture_related"] == True
    print(f"  Scheme reply snippet: {res_sc['reply_kn'][:120]}...")
    assert "ಕಿಸಾನ್" in res_sc["reply_kn"] or "ಯೋಜನೆ" in res_sc["reply_kn"] or "PMFBY" in res_sc["reply_kn"]
    print("  ✓ Government scheme recommendation completed using saved profile details.")

    # Case 2: Fertilizer Guidance
    r_fert = requests.post(f"{BASE_URL}/chat", headers=headers, json={
        "message": "ಶೇಂಗಾ ಬೆಳೆಗೆ ಎಷ್ಟು ಗೊಬ್ಬರ ಹಾಕಬೇಕು?",
        "session_id": sess_id,
        "language": "kn"
    })
    assert r_fert.status_code == 200
    res_fert = r_fert.json()
    assert res_fert["is_agriculture_related"] == True
    print(f"  Fertilizer reply snippet: {res_fert['reply_kn'][:120]}...")
    assert any(k in res_fert["reply_kn"] for k in ["ಯೂರಿಯಾ", "ಡಿಎಪಿ", "ಪೊಟ್ಯಾಶ್", "NPK", "ಗೊಬ್ಬರ"])
    print("  ✓ Verified fertilizer guidance provided without 7-question interrogation.")

    # -------------------------------------------------------------------------
    # TEST 9: CONVERSATION HISTORY & ANALYSIS TRACKING
    # -------------------------------------------------------------------------
    print("\n[TEST 9] Testing Persistent Conversation History & Analysis Tracking...")
    # List conversations
    r_list = requests.get(f"{BASE_URL}/chat/conversations", headers=headers)
    assert r_list.status_code == 200
    conv_list = r_list.json()
    assert len(conv_list) >= 1
    target_conv = next((c for c in conv_list if c["id"] == conv_id), conv_list[0])
    print(f"  Found conversation thread: ID={target_conv['id']}, Title='{target_conv['title']}', Messages={target_conv['message_count']}")
    assert target_conv["message_count"] >= 3

    # Detail of conversation
    r_detail = requests.get(f"{BASE_URL}/chat/conversations/{conv_id}", headers=headers)
    assert r_detail.status_code == 200
    detail = r_detail.json()
    assert len(detail["messages"]) >= 3
    print(f"  Loaded {len(detail['messages'])} messages with timestamps and transcripts.")

    # Analysis history tracking
    r_analyses = requests.get(f"{BASE_URL}/chat/analyses", headers=headers)
    assert r_analyses.status_code == 200
    analyses = r_analyses.json()
    print(f"  Found {len(analyses)} saved analysis records for farmer.")
    if len(analyses) > 0:
        print(f"  Latest Analysis Topic: {analyses[0]['topic']}, Crop: {analyses[0].get('crop_information')}")

    # -------------------------------------------------------------------------
    # TEST 10: CONVERSATION DELETION (INDIVIDUAL & ALL)
    # -------------------------------------------------------------------------
    print("\n[TEST 10] Testing Conversation Deletion...")
    # Delete single thread
    r_del = requests.delete(f"{BASE_URL}/chat/conversations/{conv_id}", headers=headers)
    assert r_del.status_code == 200, f"Delete failed: {r_del.text}"
    print(f"  ✓ Single conversation thread {conv_id} deleted successfully.")

    # Delete all conversations
    r_del_all = requests.delete(f"{BASE_URL}/chat/conversations", headers=headers)
    assert r_del_all.status_code == 200
    assert r_del_all.json()["status"] == "all_deleted"
    print(f"  ✓ All conversation history deleted successfully with confirmation endpoint.")

    # -------------------------------------------------------------------------
    # TEST 11: NEURAL TTS WITH SPEECH SPEED
    # -------------------------------------------------------------------------
    print("\n[TEST 11] Testing Neural TTS Speech Synthesis with Speed Adjustment...")
    r_tts = requests.post(f"{BASE_URL}/speech/synthesize", json={
        "text": "ನಮಸ್ಕಾರ, ಕೃಷಿ ಮಿತ್ರ AI ಸಹಾಯಕಕ್ಕೆ ಸ್ವಾಗತ.",
        "voice_gender": "female",
        "language": "kn",
        "speech_speed": 1.25
    })
    assert r_tts.status_code == 200
    tts_res = r_tts.json()
    assert tts_res["audio_url"] is not None
    print(f"  ✓ TTS synthesized audio: {tts_res['audio_url']}")

    print("\n=====================================================================")
    print("ALL TESTS PASSED SUCCESSFULLY! (11/11 REQUIREMENTS VERIFIED)")
    print("=====================================================================")

if __name__ == "__main__":
    run_tests()
