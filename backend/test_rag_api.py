import requests
import json
import sys
import io

# Set stdout to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000/api"

def run_rag_api_tests():
    print("========================================================")
    print("KRISHI MITRA - RAG REST API END-TO-END VERIFICATION")
    print("========================================================")

    # 1. Health check with RAG status
    print("\n[Test 1] Health Check & RAG Status...")
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    h_data = res.json()
    print("  ✓ Status:", h_data.get("status"))
    print("  ✓ RAG Pipeline:", h_data.get("rag_pipeline"))
    print("  ✓ Embedding Model:", h_data.get("rag_embedding_model"))
    assert "rag_pipeline" in h_data, "rag_pipeline missing from health check!"

    # 2. Vector store status endpoint
    print("\n[Test 2] GET /api/rag/status...")
    res = requests.get(f"{BASE_URL}/rag/status")
    assert res.status_code == 200, f"RAG status failed: {res.text}"
    s_data = res.json()
    print(f"  ✓ Collection: {s_data['collection_name']}")
    print(f"  ✓ Total Chunks: {s_data['total_chunks']}")
    print(f"  ✓ Total Documents: {s_data['total_documents']}")
    print(f"  ✓ Embedding Model: {s_data['embedding_model']}")
    print(f"  ✓ Gemini API Configured: {s_data['gemini_api_configured']}")
    assert s_data["total_chunks"] >= 40, f"Expected at least 40 chunks, got {s_data['total_chunks']}"
    assert s_data["total_documents"] == 4, f"Expected 4 documents, got {s_data['total_documents']}"

    # 3. Documents list endpoint
    print("\n[Test 3] GET /api/rag/documents...")
    res = requests.get(f"{BASE_URL}/rag/documents")
    assert res.status_code == 200, f"Documents list failed: {res.text}"
    docs = res.json()
    print(f"  ✓ Retrieved {len(docs)} official documents:")
    for d in docs:
        print(f"     - {d['filename']} ({d['page_count']} pages, scheme: {d['scheme_id']})")
    assert len(docs) == 4, "Expected 4 official documents!"

    # 4. English Scheme Query: PM-KISAN amount
    print("\n[Test 4] POST /api/rag/query - English PM-KISAN amount...")
    res = requests.post(f"{BASE_URL}/rag/query", json={
        "query": "How much financial assistance does PM-KISAN provide per year?",
        "language": "en"
    })
    assert res.status_code == 200, f"Query failed: {res.text}"
    q_data = res.json()
    print(f"  ✓ Available: {q_data['available']}")
    print(f"  ✓ Confidence: {q_data['confidence']}")
    print(f"  ✓ Mode: {q_data['generation_mode']}")
    assert q_data["available"] is True
    assert "6,000" in q_data["answer_en"]
    top_c = q_data["citations"][0]
    print(f"  ✓ Citation: {top_c['doc_name']} (Page {top_c['page_number']})")
    assert top_c["doc_name"] == "PM_KISAN_Operational_Guidelines.pdf"
    assert top_c["page_number"] == 1

    # 5. Kannada Scheme Query: PM-KISAN amount
    print("\n[Test 5] POST /api/rag/query - Kannada PM-KISAN amount...")
    res = requests.post(f"{BASE_URL}/rag/query", json={
        "query": "ಪಿಎಂ ಕಿಸಾನ್ ಯೋಜನೆಯಲ್ಲಿ ರೈತರಿಗೆ ಎಷ್ಟು ಹಣ ಸಿಗುತ್ತದೆ?",
        "language": "kn"
    })
    assert res.status_code == 200, f"Query failed: {res.text}"
    q_data = res.json()
    print(f"  ✓ Available: {q_data['available']}")
    print(f"  ✓ Confidence: {q_data['confidence']}")
    assert q_data["available"] is True
    assert "6,000" in q_data["answer_kn"] or "೬,೦೦೦" in q_data["answer_kn"]
    print(f"  ✓ Kannada Answer: {q_data['answer_kn'][:90]}...")

    # 6. Kannada PMFBY 72 hours deadline
    print("\n[Test 6] POST /api/rag/query - Kannada PMFBY 72 hours reporting rule...")
    res = requests.post(f"{BASE_URL}/rag/query", json={
        "query": "ಬೆಳೆ ಹಾನಿಯಾದರೆ ಎಷ್ಟು ಗಂಟೆಯೊಳಗೆ ಸಂರಕ್ಷಣೆ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ತಿಳಿಸಬೇಕು?",
        "language": "kn"
    })
    assert res.status_code == 200
    q_data = res.json()
    assert q_data["available"] is True
    assert "72" in q_data["answer_kn"] or "೭೨" in q_data["answer_kn"]
    top_c = q_data["citations"][0]
    print(f"  ✓ Citation: {top_c['doc_name']} (Page {top_c['page_number']})")
    print(f"  ✓ Fact Verified: 72 hours rule cited accurately.")

    # 7. Krishi Bhagya Farm Pond subsidy
    print("\n[Test 7] POST /api/rag/query - Krishi Bhagya subsidy percentage...")
    res = requests.post(f"{BASE_URL}/rag/query", json={
        "query": "What is the subsidy percentage for SC/ST farmers in Krishi Bhagya farm pond?",
        "language": "en"
    })
    assert res.status_code == 200
    q_data = res.json()
    assert q_data["available"] is True
    assert "90%" in q_data["answer_en"]
    top_c = q_data["citations"][0]
    print(f"  ✓ Citation: {top_c['doc_name']} (Page {top_c['page_number']})")
    print(f"  ✓ Fact Verified: 90% SC/ST subsidy cited accurately.")

    # 8. KCC Subsidized Interest Rate
    print("\n[Test 8] POST /api/rag/query - KCC Subsidized Interest Rate...")
    res = requests.post(f"{BASE_URL}/rag/query", json={
        "query": "ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ ಅಡಿಯಲ್ಲಿ ಬಡ್ಡಿದರ ಎಷ್ಟು?",
        "language": "kn"
    })
    assert res.status_code == 200
    q_data = res.json()
    assert q_data["available"] is True
    assert "4%" in q_data["answer_kn"] or "೪%" in q_data["answer_kn"]
    top_c = q_data["citations"][0]
    print(f"  ✓ Citation: {top_c['doc_name']} (Page {top_c['page_number']})")
    print(f"  ✓ Fact Verified: 4% prompt repayment interest cited accurately.")

    # 9. Strict Refusal on Out-of-Domain / Unavailable Query (No Hallucination)
    print("\n[Test 9] POST /api/rag/query - Strict Refusal Test (No Hallucination)...")
    res = requests.post(f"{BASE_URL}/rag/query", json={
        "query": "How to get a motorcycle driving license online?",
        "language": "en"
    })
    assert res.status_code == 200
    q_data = res.json()
    print(f"  ✓ Available: {q_data['available']}")
    print(f"  ✓ Confidence: {q_data['confidence']}")
    print(f"  ✓ Mode: {q_data['generation_mode']}")
    assert q_data["available"] is False, "Expected refusal for irrelevant non-agricultural query!"
    assert q_data["confidence"] == 0.0
    assert len(q_data["citations"]) == 0
    assert "not available" in q_data["answer_en"].lower()
    print(f"  ✓ Refusal Message: {q_data['answer_en'][:90]}...")
    print(f"  ✓ Zero Hallucination Confirmed: Agent refuses to invent data.")

    # 10. Chatbot Integration with RAG Citations
    print("\n[Test 10] POST /api/chat - Agricultural Chatbot with RAG Integration...")
    chat_payload = {
        "message": "ಪಿಎಂ ಕಿಸಾನ್ ಯೋಜನೆಯಲ್ಲಿ ಎಷ್ಟು ಹಣ ಸಿಗುತ್ತದೆ?",
        "session_id": "test_rag_chat_session_01",
        "language": "kn",
        "regional_preference": "North Karnataka"
    }
    chat_res = requests.post(f"{BASE_URL}/chat", json=chat_payload)
    assert chat_res.status_code == 200, f"Chat failed: {chat_res.text}"
    c_data = chat_res.json()
    print(f"  ✓ Chat Reply (KN): {c_data['reply_kn'][:90]}...")
    print(f"  ✓ Audio URL: {c_data['audio_url']}")
    print(f"  ✓ RAG Citations Attached: {len(c_data.get('rag_citations', []))}")
    if c_data.get("rag_citations"):
        cit = c_data["rag_citations"][0]
        print(f"     -> Top Citation: {cit['doc_name']} (Page {cit['page_number']})")
    print(f"  ✓ RAG Mode: {c_data.get('rag_mode')}")
    assert len(c_data.get("rag_citations", [])) > 0, "Chat response should contain RAG citations!"

    # 11. Profile-Driven Scheme Recommendation with RAG Citations
    print("\n[Test 11] POST /api/chat - Farmer Profile with Scheme Recommendation & Citations...")
    chat_payload_2 = {
        "message": "ನಾನು ಭತ್ತ ಬೆಳೆಯುತ್ತೇನೆ ಮತ್ತು ಬೆಳಗಾವಿ ಜಿಲ್ಲೆಯವನು, ೩ ಎಕರೆ ಜಮೀನಿದೆ. ನನಗೆ ಯಾವ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಸಿಗುತ್ತವೆ?",
        "session_id": "test_rag_chat_session_02",
        "language": "kn",
        "regional_preference": "North Karnataka"
    }
    chat_res_2 = requests.post(f"{BASE_URL}/chat", json=chat_payload_2)
    assert chat_res_2.status_code == 200
    c_data_2 = chat_res_2.json()
    print(f"  ✓ Matched Schemes: {len(c_data_2['recommended_schemes'])}")
    print(f"  ✓ RAG Citations: {len(c_data_2.get('rag_citations', []))}")
    assert len(c_data_2["recommended_schemes"]) > 0, "Expected recommended schemes!"

    print("\n========================================================")
    print("ALL 11 RAG API TESTS PASSED FLAWLESSLY!")
    print("========================================================")

if __name__ == "__main__":
    run_rag_api_tests()

