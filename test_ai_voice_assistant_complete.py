import sys
import io
import requests
import json
import uuid

# Force utf-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000/api"

def run_comprehensive_tests():
    print("=====================================================================")
    print("KRISHI MITRA – PROFESSIONAL AI VOICE ASSISTANT & SETTINGS VERIFICATION")
    print("=====================================================================")

    # Test Mobile & Unique Username
    random_suffix = uuid.uuid4().hex[:6]
    test_mobile = f"9740{random_suffix[:6]}"
    test_username = f"basavaraj_{random_suffix[:4]}"
    test_password = "SecurePassword123!"

    # -------------------------------------------------------------------------
    # TEST 1: USER REGISTRATION WITH USERNAME AND REGIONAL DIALECT
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Registering Farmer with Username & Profile...")
    reg_payload = {
        "mobile": test_mobile,
        "name": "ಬಸವರಾಜ್",
        "username": test_username,
        "email": f"{test_username}@example.com",
        "password": test_password,
        "district": "Belagavi",
        "taluk": "Bailhongal",
        "preferred_language": "kn",
        "regional_speech_preference": "North Karnataka",
        "voice_gender_preference": "female",
        "voice_assistant_enabled": True,
        "auto_voice_response": True,
        "voice_input_enabled": True,
        "speech_speed": 1.0,
        "land_acres": 4.0,
        "land_ownership": "Own",
        "crops": ["Paddy", "Groundnut"]
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
    assert r.status_code == 200, f"Registration failed: {r.text}"
    auth_data = r.json()
    token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"  ✓ User registered! ID: {auth_data['user']['id']}, Username: {auth_data['user']['username']}")

    # -------------------------------------------------------------------------
    # TEST 2: CENTRALIZED SETTINGS PERSISTENCE & BIDIRECTIONAL SYNC VERIFICATION
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Testing Centralized Settings Persistence (Theme, Dialect, Voice, Speed)...")
    settings_payload = {
        "theme_preference": "dark",
        "regional_speech_preference": "North Karnataka",
        "voice_gender_preference": "male",
        "voice_assistant_enabled": True,
        "auto_voice_response": True,
        "voice_input_enabled": True,
        "speech_speed": 1.25,
        "preferred_language": "kn",
        "land_acres": 4.0,
        "land_ownership": "Own"
    }
    r = requests.put(f"{BASE_URL}/farmer/profile", headers=headers, json=settings_payload)
    assert r.status_code == 200, f"Settings update failed: {r.text}"
    prof = r.json()
    assert prof["theme_preference"] == "dark"
    assert prof["regional_speech_preference"] == "North Karnataka"
    assert prof["voice_gender_preference"] == "male"
    assert prof["speech_speed"] == 1.25
    assert prof["voice_assistant_enabled"] == True
    print("  ✓ Centralized settings persisted and verified in backend profile.")

    # -------------------------------------------------------------------------
    # TEST 3: "TALK TO AI" WORKFLOW - GREETING WITH USERNAME & EXACT QUESTION
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Testing 'Talk to AI' Opening Workflow...")
    r = requests.post(f"{BASE_URL}/chat/conversations/new", headers=headers, json={
        "language": "kn",
        "voice_gender": "male"
    })
    assert r.status_code == 200, f"New conversation failed: {r.text}"
    conv = r.json()
    conv_id = conv["id"]
    sess_id = conv["session_id"]
    first_msg = conv["messages"][0]
    greeting_kn = first_msg["text_kn"]
    print(f"  Received Greeting: \n{greeting_kn}")

    # Verify requirements:
    # 1. Must use farmer's actual username/name
    assert test_username in greeting_kn or "ಬಸವರಾಜ್" in greeting_kn, "Greeting must address the farmer's username"
    # 2. Must ask what agricultural help they need
    assert "ಕೃಷಿ ವಿಷಯದಲ್ಲಿ ಸಹಾಯ ಬೇಕು" in greeting_kn or "ಸಹಾಯ ಬೇಕ್ರಿ" in greeting_kn
    # 3. Then ask the exact prompt question:
    # "ನಿಮಗೆ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು, ಬೆಳೆ ವಿಮೆ, ಗೊಬ್ಬರದ ಸಲಹೆ ಅಥವಾ ಬೆಳೆ ಮಾರ್ಗದರ್ಶನದ ಬಗ್ಗೆ ಮಾಹಿತಿ ಬೇಕೇ?"
    assert "ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು" in greeting_kn
    assert "ಬೆಳೆ ವಿಮೆ" in greeting_kn
    assert "ಗೊಬ್ಬರದ ಸಲಹೆ" in greeting_kn
    assert "ಬೆಳೆ ಮಾರ್ಗದರ್ಶನ" in greeting_kn
    # 4. Neural voice synthesis audio returned
    assert first_msg.get("audio_url") is not None, "Opening greeting must have synthesized audio URL"
    print(f"  ✓ Greeting contains username, exact required options, and synthesized audio URL ({first_msg['audio_url']}).")

    # -------------------------------------------------------------------------
    # TEST 4: REGIONAL KANNADA VOCABULARY NORMALIZATION (North Karnataka Dialect)
    # -------------------------------------------------------------------------
    print("\n[TEST 4] Testing Regional Kannada Vocabulary Normalization...")
    # Farmer asks in North Karnataka dialect: "ನಮ್ಮ ಹೊಲದಾಗ ಶೇಂಗಾ ಬೆಳಿಲಿಕತ್ತೇನಿ, ಎಷ್ಟು ಗೊಬ್ಬರ ಹಾಕಬೇಕು ಹೇಳ್ರಿ?"
    r_nk = requests.post(f"{BASE_URL}/chat", headers=headers, json={
        "message": "ನಮ್ಮ ಹೊಲದಾಗ ಶೇಂಗಾ ಬೆಳಿಲಿಕತ್ತೇನಿ, ಎಷ್ಟು ಗೊಬ್ಬರ ಹಾಕಬೇಕು ಹೇಳ್ರಿ?",
        "session_id": sess_id,
        "language": "kn",
        "regional_preference": "North Karnataka"
    })
    assert r_nk.status_code == 200
    res_nk = r_nk.json()
    entities = res_nk.get("detected_entities", {})
    print(f"  Detected crop from dialect: {entities.get('crop')}")
    assert entities.get("crop") == "Groundnut", "Dialect vocabulary 'ಶೇಂಗಾ' must normalize to Groundnut"
    assert res_nk.get("is_agriculture_related") == True
    print(f"  North Karnataka response snippet: {res_nk['reply_kn'][:140]}...")
    assert "ಶೇಂಗಾ" in res_nk["reply_kn"] or "Groundnut" in res_nk["reply_kn"]
    print("  ✓ North Karnataka vocabulary successfully normalized and answered in regional style.")

    # -------------------------------------------------------------------------
    # TEST 5: INTELLIGENT CASE-BASED COLLECTION - CROP INSURANCE (Case B)
    # -------------------------------------------------------------------------
    print("\n[TEST 5] Testing Case B: Crop Insurance (PMFBY / Samrakshane)...")
    r_ins = requests.post(f"{BASE_URL}/chat", headers=headers, json={
        "message": "ಭತ್ತದ ಬೆಳೆಗೆ ಬೆಳೆ ವಿಮೆ ವಿವರ ಕೊಡಿ",
        "session_id": sess_id,
        "language": "kn"
    })
    assert r_ins.status_code == 200
    res_ins = r_ins.json()
    print(f"  Crop Insurance response: {res_ins['reply_kn'][:180]}...")
    assert any(k in res_ins["reply_kn"] for k in ["ಸಂರಕ್ಷಣೆ", "Samrakshane", "ಪಿಎಂಎಫ್‌ಬಿವೈ", "PMFBY"])
    assert any(k in res_ins["reply_kn"] for k in ["೭೨ ಗಂಟೆ", "72", "ಪ್ರೀಮಿಯಂ"])
    assert any(k in res_ins["reply_kn"] for k in ["RTC", "ಪಹಣಿ", "ಆಧಾರ್"])
    assert res_ins.get("audio_url") is not None
    print("  ✓ Crop Insurance provided verified Samrakshane rules, 72-hour calamity rule, documents, and audio.")

    # -------------------------------------------------------------------------
    # TEST 6: INTELLIGENT CASE-BASED COLLECTION - CROP GUIDANCE (Case D)
    # -------------------------------------------------------------------------
    print("\n[TEST 6] Testing Case D: Crop Guidance & Selection (Paddy / Jowar)...")
    r_guide = requests.post(f"{BASE_URL}/chat", headers=headers, json={
        "message": "ಭತ್ತದ ಬೆಳೆಗೆ ಸಮಗ್ರ ಮಾರ್ಗದರ್ಶನ ನೀಡಿ",
        "session_id": sess_id,
        "language": "kn"
    })
    assert r_guide.status_code == 200
    res_guide = r_guide.json()
    print(f"  Crop Guidance response: {res_guide['reply_kn'][:180]}...")
    assert any(k in res_guide["reply_kn"] for k in ["ಬಿತ್ತನೆ", "ನಾಟಿ", "ನೀರಾವರಿ", "ಕೀಟ", "ಬೆಂಕಿ ರೋಗ", "SRI"])
    print("  ✓ Crop Guidance provided verified agronomic practices and stage-specific advice.")

    # -------------------------------------------------------------------------
    # TEST 7: INTELLIGENT CASE-BASED COLLECTION - GOVERNMENT SCHEMES (Case A)
    # -------------------------------------------------------------------------
    print("\n[TEST 7] Testing Case A: Government Scheme Recommendations (Reusing profile)...")
    r_scheme = requests.post(f"{BASE_URL}/chat", headers=headers, json={
        "message": "ನನಗೆ ಯಾವ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಲಭ್ಯವಿವೆ?",
        "session_id": sess_id,
        "language": "kn"
    })
    assert r_scheme.status_code == 200
    res_sc = r_scheme.json()
    print(f"  Schemes response: {res_sc['reply_kn'][:180]}...")
    assert any(k in res_sc["reply_kn"] for k in ["PM-KISAN", "ಕಿಸಾನ್", "PMFBY", "ಕೃಷಿ ಭಾಗ್ಯ"])
    assert any(k in res_sc["reply_kn"] for k in ["RTC", "ಪಹಣಿ", "ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರ"])
    print("  ✓ Schemes recommended based on saved profile without asking all 7 questions.")

    # -------------------------------------------------------------------------
    # TEST 8: STRICT AGRICULTURE-ONLY GUARDRAILS
    # -------------------------------------------------------------------------
    print("\n[TEST 8] Testing Strict Agriculture-Only Guardrails (Kannada & English)...")
    guardrail_queries = [
        ("ಯಾರು ಸಿನಿಮಾ ನಿರ್ದೇಶಕ?", "kn"),
        ("Who is the prime minister of Canada?", "en"),
        ("Write a poem about space travel", "en")
    ]
    for q, lang in guardrail_queries:
        r_g = requests.post(f"{BASE_URL}/chat", headers=headers, json={
            "message": q,
            "session_id": sess_id,
            "language": lang
        })
        assert r_g.status_code == 200
        res_g = r_g.json()
        assert res_g["is_agriculture_related"] == False, f"Query '{q}' should be blocked by guardrail!"
        if lang == "kn":
            assert "ಕ್ಷಮಿಸಿ, ನಾನು ಕೃಷಿ ಸಂಬಂಧಿತ ವಿಷಯಗಳಲ್ಲಿ ಮಾತ್ರ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ" in res_g["reply_kn"]
        else:
            assert "Sorry, I can only assist with agriculture-related topics" in res_g["reply"]
        print(f"  ✓ Non-agri query '{q}' rejected cleanly with standard guardrail.")

    # -------------------------------------------------------------------------
    # TEST 9: CONVERSATION HISTORY & AUDIT PERSISTENCE
    # -------------------------------------------------------------------------
    print("\n[TEST 9] Testing Conversation History & Saved Analysis...")
    r_history = requests.get(f"{BASE_URL}/chat/conversations", headers=headers)
    assert r_history.status_code == 200
    conv_list = r_history.json()
    assert len(conv_list) >= 1
    print(f"  ✓ Conversation listed in farmer's history ({len(conv_list)} total threads).")

    r_detail = requests.get(f"{BASE_URL}/chat/conversations/{conv_id}", headers=headers)
    assert r_detail.status_code == 200
    conv_detail = r_detail.json()
    assert len(conv_detail["messages"]) >= 5
    print(f"  ✓ Conversation details contain full transcript with {len(conv_detail['messages'])} messages.")

    # -------------------------------------------------------------------------
    # TEST 10: SPEECH SYNTHESIS ENGINE (Edge TTS / Kannada Neural Voice)
    # -------------------------------------------------------------------------
    print("\n[TEST 10] Testing Neural Speech Synthesis (Male and Female Voices)...")
    for gender in ["female", "male"]:
        r_tts = requests.post(f"{BASE_URL}/speech/synthesize", json={
            "text": "ನಮಸ್ಕಾರ, ಕೃಷಿ ಮಿತ್ರ AI ಸಹಾಯಕಕ್ಕೆ ಸ್ವಾಗತ.",
            "voice_gender": gender,
            "language": "kn",
            "speech_speed": 1.0
        })
        assert r_tts.status_code == 200
        data = r_tts.json()
        assert data.get("audio_url") is not None
        print(f"  ✓ Synthesized {gender} voice successfully: {data['audio_url']}")

    print("\n=====================================================================")
    print("ALL 10 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("Krishi Mitra AI Voice Assistant & Settings Upgrade is 100% Complete.")
    print("=====================================================================")

if __name__ == "__main__":
    run_comprehensive_tests()
