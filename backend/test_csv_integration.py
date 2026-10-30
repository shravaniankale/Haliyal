import sys
import os
import json

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_tests():
    print("======================================================================")
    print("   KRISHI MITRA — 5 CSV DATASETS INTEGRATION VERIFICATION TEST SUITE  ")
    print("======================================================================")

    # 0. Health check
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health = res.json()
    print("\n[TEST 0] Health Check:")
    print(f"  ✓ Status: {health['status']}, CSV Integration: {health.get('csv_integration')}")

    # -------------------------------------------------------------------------
    # 1. Dataset 1: government_schemes.csv
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Testing government_schemes.csv Integration:")
    schemes_res = client.get("/api/schemes")
    assert schemes_res.status_code == 200, f"Schemes failed: {schemes_res.text}"
    schemes = schemes_res.json()
    assert len(schemes) >= 5, f"Expected at least 5 schemes, got {len(schemes)}"
    
    verified_schemes = [s for s in schemes if s["verification_status"] == "Verified"]
    demo_schemes = [s for s in schemes if s["verification_status"] == "Synthetic Demo"]
    
    print(f"  ✓ Loaded Schemes: {len(schemes)} total")
    print(f"  ✓ Official Verified Programs: {len(verified_schemes)} (e.g. {[s['scheme_name'] for s in verified_schemes]})")
    print(f"  ✓ Synthetic Demo Benchmarks: {len(demo_schemes)} (e.g. {[s['scheme_name'] for s in demo_schemes]})")
    
    # Check deduplication & dual lookup (SCM001 / PM-KISAN)
    pmkisan_by_code = client.get("/api/schemes/SCM001")
    pmkisan_by_id = client.get("/api/schemes/PM-KISAN")
    assert pmkisan_by_code.status_code == 200, "Lookup by CSV scheme_code SCM001 failed"
    assert pmkisan_by_id.status_code == 200, "Lookup by scheme_id PM-KISAN failed"
    print(f"  ✓ Scheme Lookup by both 'SCM001' and 'PM-KISAN' verified successfully!")

    # Check deterministic rule eligibility
    elig_res = client.post("/api/schemes/eligibility", json={
        "district": "Belagavi",
        "crop": "Paddy",
        "land_acres": 3.0,
        "land_ownership": "Own",
        "season": "Kharif",
        "irrigation_type": "Rainfed",
        "farmer_category": "Small & Marginal"
    })
    assert elig_res.status_code == 200, "Eligibility check failed"
    elig_data = elig_res.json()
    print(f"  ✓ Deterministic Rule Evaluator: {elig_data['eligible_count']}/{elig_data['total_evaluated']} schemes eligible for 3.0 acres Paddy farmer.")

    # -------------------------------------------------------------------------
    # 2. Dataset 2: regional_kannada_vocabulary.csv
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Testing regional_kannada_vocabulary.csv Integration:")
    vocab_res = client.get("/api/vocabulary")
    assert vocab_res.status_code == 200, f"Vocabulary failed: {vocab_res.text}"
    vocab_list = vocab_res.json()
    assert len(vocab_list) >= 10, f"Expected >= 10 vocabulary terms, got {len(vocab_list)}"
    print(f"  ✓ Loaded Regional Vocabulary Terms: {len(vocab_list)}")
    
    # Test normalization endpoint
    norm_res = client.post("/api/vocabulary/normalize", json={
        "text": "ನನ್ನ ಹೊಲದಾಗ ಶೇಂಗಾ ಬೆಳಿಲಿಕತ್ತೇನಿ, ಮೂರು ಎಕರೆ ಖುಷ್ಕಿ ಭೂಮಿ ಐತಿ"
    })
    assert norm_res.status_code == 200, "Normalize endpoint failed"
    norm_data = norm_res.json()
    print(f"  ✓ Normalization Input:  '{norm_data['original_text']}'")
    print(f"  ✓ Normalization Output: '{norm_data['normalized_text']}'")
    print(f"  ✓ Detected Terms: {[t['original_term'] + ' -> ' + t['standard_term'] for t in norm_data['detected_local_terms']]}")
    print(f"  ✓ Concepts Mapped: {norm_data['applied_concepts']}")
    assert "CROP_GROUNDNUT" in norm_data["applied_concepts"], "Expected CROP_GROUNDNUT concept mapped"
    assert "LAND_RAINFED" in norm_data["applied_concepts"], "Expected LAND_RAINFED concept mapped"

    # -------------------------------------------------------------------------
    # 3. Dataset 3: kannada_speech_metadata.csv
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Testing kannada_speech_metadata.csv Integration:")
    meta_res = client.get("/api/speech/metadata")
    assert meta_res.status_code == 200, f"Speech metadata failed: {meta_res.text}"
    meta_list = meta_res.json()
    assert len(meta_list) == 5, f"Expected 5 speech metadata records, got {len(meta_list)}"
    print(f"  ✓ Speech Metadata Records Loaded: {len(meta_list)}")
    for m in meta_list[:2]:
        print(f"    - [{m['audio_id']}] ({m['district_or_region']}): '{m['transcript_verbatim'][:40]}...' (Consent: {m['consent_status']})")

    # Speech dataset stats
    stats_res = client.get("/api/speech/metadata/stats")
    assert stats_res.status_code == 200, "Speech stats failed"
    stats_data = stats_res.json()
    print(f"  ✓ Consent Rate: {stats_data['consent_rate_pct']}%, Total Consented Duration: {stats_data['total_duration_seconds']}s")
    print(f"  ✓ Districts in Metadata: {list(stats_data['regions'].keys())}")

    # Speech evaluation (WER / CER)
    eval_res = client.post("/api/speech/evaluate", json={
        "audio_id": "AUD_KN_001",
        "hypothesis_transcript": "ನನ್ನ ಹೊಲದಲ್ಲಿ ಶೇಂಗಾ ಬೆಳೆಯುತ್ತಿದ್ದೇನೆ ಸಾಲ ಸಿಗುತ್ತದೆಯೇ"
    })
    assert eval_res.status_code == 200, "Speech evaluation failed"
    eval_data = eval_res.json()
    print(f"  ✓ Transcription Evaluation on AUD_KN_001:")
    print(f"    WER: {eval_data['word_error_rate']}, CER: {eval_data['character_error_rate']}, Accuracy: {eval_data['accuracy_percentage']}%, Acceptable: {eval_data['is_acceptable']}")

    # Benchmark test split
    bm_res = client.get("/api/speech/benchmark")
    assert bm_res.status_code == 200, "Speech benchmark failed"
    bm_data = bm_res.json()
    print(f"  ✓ Benchmark Test Suite Evaluated: {bm_data['evaluated_count']} records, Average Alignment Accuracy: {bm_data['average_accuracy']}%")

    # -------------------------------------------------------------------------
    # 4. Dataset 4: farmer_session_profile.csv
    # -------------------------------------------------------------------------
    print("\n[TEST 4] Testing farmer_session_profile.csv Integration:")
    sess_res = client.get("/api/farmer/sessions")
    assert sess_res.status_code == 200, f"Farmer sessions failed: {sess_res.text}"
    sessions = sess_res.json()
    assert len(sessions) >= 3, f"Expected >= 3 pre-seeded sessions, got {len(sessions)}"
    print(f"  ✓ Total Farmer Sessions in DB: {len(sessions)}")
    
    # Check SESSION_DEMO_002 (confirmed profile)
    s2 = client.get("/api/farmer/sessions/SESSION_DEMO_002").json()
    print(f"  ✓ Session 2 (Dharwad): Crops='{s2['crops_grown']}', Confirmed='{s2['confirmed_fields']}', State='{s2['conversation_state']}'")
    
    # Check SESSION_DEMO_003 (missing field profile)
    s3 = client.get("/api/farmer/sessions/SESSION_DEMO_003").json()
    print(f"  ✓ Session 3 (Mandya): Missing='{s3['missing_fields']}', State='{s3['conversation_state']}'")

    # -------------------------------------------------------------------------
    # 5. Dataset 5: dataset_data_dictionary.csv
    # -------------------------------------------------------------------------
    print("\n[TEST 5] Testing dataset_data_dictionary.csv Integration:")
    dict_res = client.get("/api/datasets/dictionary")
    assert dict_res.status_code == 200, f"Dictionary failed: {dict_res.text}"
    dict_list = dict_res.json()
    assert len(dict_list) == 4, f"Expected 4 dataset dictionary records, got {len(dict_list)}"
    print(f"  ✓ Documentation Records in Dictionary: {len(dict_list)}")
    for d in dict_list:
        print(f"    - {d['file_name']}: {d['purpose'][:60]}...")

    # Multi-dataset integration summary
    summary_res = client.get("/api/datasets/summary")
    assert summary_res.status_code == 200, "Summary failed"
    summary_data = summary_res.json()
    print(f"\n  ✓ Integrated Datasets Summary: {summary_data['datasets_integrated']} datasets active ({summary_data['status']})")

    # -------------------------------------------------------------------------
    # 6. End-to-end Chat with Dialect Normalization & Session Tracking
    # -------------------------------------------------------------------------
    print("\n[TEST 6] Testing End-to-End Chat with Dialect Normalization & Session Tracking:")
    chat_res = client.post("/api/chat", json={
        "message": "ನನ್ನ ಹೊಲದಾಗ ಶೇಂಗಾ ಬೆಳಿಲಿಕತ್ತೇನಿ, ಧಾರವಾಡ ಜಿಲ್ಲೆ, ಮೂರು ಎಕರೆ ಸ್ವಂತ ಜಮೀನು ಐತಿ.",
        "session_id": "test_e2e_session_kannada_01",
        "language": "kn",
        "regional_preference": "North Karnataka"
    })
    assert chat_res.status_code == 200, f"Chat failed: {chat_res.text}"
    chat_data = chat_res.json()
    print(f"  ✓ User Query (North Karnataka): 'ನನ್ನ ಹೊಲದಾಗ ಶೇಂಗಾ ಬೆಳಿಲಿಕತ್ತೇನಿ, ಧಾರವಾಡ ಜಿಲ್ಲೆ, ಮೂರು ಎಕರೆ ಸ್ವಂತ ಜಮೀನು ಐತಿ.'")
    print(f"  ✓ Detected Entities: {chat_data['detected_entities']}")
    print(f"  ✓ Recommended Schemes: {[s['scheme_id'] for s in chat_data['recommended_schemes']]}")
    print(f"  ✓ AI Response (Kannada): {chat_data['reply_kn'][:80]}...")
    print(f"  ✓ Generated Audio Stream: {chat_data['audio_url']}")
    assert chat_data["detected_entities"].get("crop") == "Groundnut", "Expected crop to be resolved to Groundnut via ಶೇಂಗಾ vocabulary"

    # Verify session profile was dynamically synced
    synced_sess = client.get("/api/farmer/sessions/test_e2e_session_kannada_01")
    assert synced_sess.status_code == 200, "Synced session lookup failed"
    sess_info = synced_sess.json()
    print(f"  ✓ Auto-Persisted Farmer Session Profile:")
    print(f"    - Session ID: {sess_info['farmer_session_id']}")
    print(f"    - District: {sess_info['district']}")
    print(f"    - Crops: {sess_info['crops_grown']}")
    print(f"    - Land: {sess_info['land_area']} {sess_info['land_area_unit']}")
    print(f"    - Ownership: {sess_info['land_ownership']}")
    print(f"    - Confirmed Fields: {sess_info['confirmed_fields']}")
    print(f"    - Missing Fields: {sess_info['missing_fields']}")
    print(f"    - State: {sess_info['conversation_state']}")

    print("\n======================================================================")
    print("   ALL CSV INTEGRATION TESTS COMPLETED AND VERIFIED SUCCESSFULLY!    ")
    print("======================================================================")

if __name__ == "__main__":
    run_tests()

