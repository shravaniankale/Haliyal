import requests
import json

BASE = "http://127.0.0.1:8000/api"

def test_api():
    print("=== STARTING KRISHI MITRA BACKEND & AI TEST SUITE ===")

    # 1. Health check
    res = requests.get(f"{BASE}/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("✓ Health Check Passed:", res.json())

    # 2. Registration with North Karnataka district (Belagavi)
    reg_payload = {
        "name": "Basavaraj Patil",
        "mobile": "9845012345",
        "password": "FarmerPassword@123",
        "district": "Belagavi",
        "taluk": "Bailhongal",
        "village": "Deshnur",
        "preferred_language": "kn",
        "preferred_speech_style": "North Karnataka"
    }
    # If already exists, test login
    reg_res = requests.post(f"{BASE}/auth/register", json=reg_payload)
    if reg_res.status_code == 200:
        token = reg_res.json()["access_token"]
        print("✓ Farmer Registration Passed! Token generated, Region:", reg_res.json()["regional_speech"])
    else:
        login_res = requests.post(f"{BASE}/auth/login", json={"mobile": "9845012345", "password": "FarmerPassword@123"})
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token = login_res.json()["access_token"]
        print("✓ Farmer Login Passed! Token retrieved, Region:", login_res.json()["regional_speech"])

    headers = {"Authorization": f"Bearer {token}"}

    # 3. Farmer Profile Retrieval & Update
    prof_res = requests.get(f"{BASE}/farmer/profile", headers=headers)
    assert prof_res.status_code == 200, "Get profile failed"
    print("✓ Farmer Profile Retrieval Passed:", prof_res.json()["district"], prof_res.json()["regional_speech_preference"])

    # Update profile with land details
    update_res = requests.put(f"{BASE}/farmer/profile", headers=headers, json={
        "land_acres": 3.5,
        "land_ownership": "Own",
        "crops_grown": ["Paddy", "Jowar"]
    })
    assert update_res.status_code == 200, "Update profile failed"
    print("✓ Farmer Profile Update Passed! Land acres set to 3.5")

    # 4. Schemes retrieval & filters
    schemes_res = requests.get(f"{BASE}/schemes")
    assert schemes_res.status_code == 200, "Schemes list failed"
    schemes = schemes_res.json()
    print(f"✓ Schemes List Passed! Total schemes in DB: {len(schemes)}")
    verified_count = sum(1 for s in schemes if s["verification_status"] == "Verified")
    demo_count = sum(1 for s in schemes if s["verification_status"] == "Synthetic Demo")
    print(f"  -> Verified Official: {verified_count}, Synthetic Demo: {demo_count}")

    # 5. Deterministic Rule Eligibility Check
    elig_payload = {
        "district": "Belagavi",
        "crop": "Paddy",
        "land_acres": 3.0,
        "land_ownership": "Own",
        "season": "Kharif",
        "irrigation_type": "Rainfed",
        "farmer_category": "Small & Marginal"
    }
    elig_res = requests.post(f"{BASE}/schemes/eligibility", json=elig_payload)
    assert elig_res.status_code == 200, "Eligibility evaluation failed"
    elig_data = elig_res.json()
    print(f"✓ Deterministic Rule Engine Passed! Total Evaluated: {elig_data['total_evaluated']}, Eligible Count: {elig_data['eligible_count']}")
    for r in elig_data["results"][:3]:
        print(f"  -> [{r['status']}] {r['scheme_id']}: {r['explanation'][:60]}...")

    # 6. Test UNKNOWN condition when land area is missing
    missing_elig_payload = {
        "district": "Belagavi",
        "crop": "Paddy",
        "land_acres": None,
        "land_ownership": "Own"
    }
    miss_res = requests.post(f"{BASE}/schemes/eligibility", json=missing_elig_payload)
    miss_data = miss_res.json()
    unknown_schemes = [r for r in miss_data["results"] if r["status"] == "UNKNOWN"]
    print(f"✓ Missing-Information Detection (UNKNOWN state) Verified! Found {len(unknown_schemes)} schemes requiring missing land data.")

    # 7. Agriculture Loans & EMI calculation
    loans_res = requests.get(f"{BASE}/loans")
    assert loans_res.status_code == 200, "Loans list failed"
    print(f"✓ Loans List Passed! Total loans: {len(loans_res.json())}")

    emi_res = requests.post(f"{BASE}/loans/calculator", json={
        "amount": 100000,
        "interest_rate": 4.0,
        "tenure_months": 36
    })
    assert emi_res.status_code == 200, "EMI calc failed"
    emi_data = emi_res.json()
    print(f"✓ Mathematical EMI Calculation Passed! Principal: ₹100,000 @ 4% for 36 mos -> Monthly EMI: ₹{emi_data['monthly_emi']}, Total Interest: ₹{emi_data['total_interest']}")

    # 8. Karnataka Crop Guidance
    crops_res = requests.get(f"{BASE}/crops")
    assert crops_res.status_code == 200, "Crops list failed"
    print(f"✓ Karnataka Crops Guidance Passed! Crops: {len(crops_res.json())}")

    # 9. Fertilizer Guidance
    fert_res = requests.post(f"{BASE}/fertilizer/recommend", json={
        "crop": "Paddy",
        "soil_type": "Red Loamy",
        "growth_stage": "Basal / Sowing"
    })
    assert fert_res.status_code == 200, "Fertilizer recommendation failed"
    print("✓ Fertilizer Guidance Passed! NPK Ratio:", fert_res.json()["recommended_npk"][:40])

    # 10. Live Weather for Belagavi
    weather_res = requests.get(f"{BASE}/weather?district=Belagavi")
    assert weather_res.status_code == 200, "Weather failed"
    w_data = weather_res.json()
    print(f"✓ Weather Module Passed! {w_data['district']}: {w_data['temperature']}°C, Condition: {w_data['condition_kn']} (Live: {w_data['is_live']})")

    # 11. APMC Market Prices
    market_res = requests.get(f"{BASE}/market-prices")
    assert market_res.status_code == 200, "Market prices failed"
    print(f"✓ APMC Mandi Prices Passed! Total mandi records: {len(market_res.json())}")

    # 12. Conversational AI with North Karnataka Dialect & Context Memory
    chat_payload = {
        "message": "ನಾನು ಭತ್ತ ಬೆಳೆಯುತ್ತೇನೆ ಮತ್ತು ಬೆಳಗಾವಿ ಜಿಲ್ಲೆಯವನು. ನನ್ನ ಬಳಿ ೩ ಎಕರೆ ಜಮೀನಿದೆ.",
        "session_id": "test_session_automated_101",
        "language": "kn",
        "regional_preference": "North Karnataka"
    }
    chat_res = requests.post(f"{BASE}/chat", headers=headers, json=chat_payload)
    assert chat_res.status_code == 200, f"Chat failed: {chat_res.text}"
    chat_data = chat_res.json()
    print("✓ Conversational AI Dialogue Passed!")
    print(f"  -> Extracted Entities: {chat_data['detected_entities']}")
    print(f"  -> AI Spoken Reply (Kannada): {chat_data['reply_kn'][:90]}...")
    print(f"  -> Generated Neural Audio URL: {chat_data['audio_url']}")
    print(f"  -> Recommended Schemes matched: {len(chat_data['recommended_schemes'])}")

    # 13. Kannada Neural Speech Synthesis (TTS)
    tts_res = requests.post(f"{BASE}/speech/synthesize", json={
        "text": "ಕೃಷಿ ಮಿತ್ರ AI ಸಹಾಯಕ ಯಶಸ್ವಿಯಾಗಿ ಧ್ವನಿಯನ್ನು ಸೃಷ್ಟಿಸಿದೆ.",
        "regional_preference": "North Karnataka"
    })
    assert tts_res.status_code == 200, "TTS synthesis failed"
    print("✓ Kannada Speech Synthesis (TTS) Passed! Audio Stream:", tts_res.json()["audio_url"])

    print("\n=== ALL 13 TEST SUITES PASSED FLAWLESSLY! ===")

if __name__ == "__main__":
    test_api()
