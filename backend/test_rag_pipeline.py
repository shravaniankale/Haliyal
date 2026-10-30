import sys
import os
import io

# Ensure root and backend directory in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
for p in [BASE_DIR, PARENT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.services.rag_engine import RAGEngine
from app.services.vector_store import VectorStoreService

# Set stdout to utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def run_tests():
    print("==================================================")
    print("KRISHI MITRA RAG PIPELINE VERIFICATION TEST SUITE")
    print("==================================================")

    # 1. Check Vector Store Status
    status = VectorStoreService.get_status()
    print(f"\n[1] Vector Store Status:")
    print(f"    - Collection Name: {status['collection_name']}")
    print(f"    - Total Chunks: {status['total_chunks']}")
    print(f"    - Documents: {status['documents']}")
    print(f"    - Embedding Model: {status['embedding_model']}")
    print(f"    - Gemini API Configured: {status['gemini_api_configured']}")

    assert status["total_chunks"] > 0, "No chunks found in vector store!"
    assert len(status["documents"]) == 4, "Expected 4 PDF documents indexed!"

    # 2. Test Queries
    test_cases = [
        {
            "query": "How much financial assistance is given under PM-KISAN per year?",
            "lang": "en",
            "expected_doc": "PM_KISAN_Operational_Guidelines.pdf",
            "expected_page": 1,
            "must_contain": "6,000"
        },
        {
            "query": "ಪಿಎಂ ಕಿಸಾನ್ ಯೋಜನೆಯಲ್ಲಿ ರೈತರಿಗೆ ಎಷ್ಟು ಹಣ ಸಿಗುತ್ತದೆ?",
            "lang": "kn",
            "expected_doc": "PM_KISAN_Operational_Guidelines.pdf",
            "expected_page": 1,
            "must_contain": "6,000"
        },
        {
            "query": "Who is excluded from PM-KISAN benefits?",
            "lang": "en",
            "expected_doc": "PM_KISAN_Operational_Guidelines.pdf",
            "expected_page": 2,
            "must_contain": "excluded"
        },
        {
            "query": "ಬೆಳೆ ಹಾನಿಯಾದರೆ ಎಷ್ಟು ಗಂಟೆಯೊಳಗೆ ಸಂರಕ್ಷಣೆ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ತಿಳಿಸಬೇಕು?",
            "lang": "kn",
            "expected_doc": "PMFBY_Karnataka_Samrakshane_Crop_Insurance.pdf",
            "expected_page": 3,
            "must_contain": "72"
        },
        {
            "query": "What is the subsidy percentage for SC/ST farmers in Krishi Bhagya farm pond?",
            "lang": "en",
            "expected_doc": "Karnataka_Krishi_Bhagya_Scheme_Dryland_Manual.pdf",
            "expected_page": 2,
            "must_contain": "90%"
        },
        {
            "query": "ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ ಅಡಿಯಲ್ಲಿ ಬಡ್ಡಿದರ ಎಷ್ಟು?",
            "lang": "kn",
            "expected_doc": "Kisan_Credit_Card_KCC_Crop_Loans_Handbook.pdf",
            "expected_page": 2,
            "must_contain": "4%"
        },
        {
            "query": "How to apply for driving license and passport online?",
            "lang": "en",
            "expected_available": False,
            "must_contain": "not available"
        }
    ]

    all_passed = True
    for idx, tc in enumerate(test_cases, 1):
        q = tc["query"]
        lang = tc["lang"]
        print(f"\n[Test Case {idx}] Query: {q} (Language: {lang})")
        res = RAGEngine.answer_query(q, preferred_language=lang)

        print(f"    - Available: {res['available']}")
        print(f"    - Confidence Score: {res['confidence']}")
        print(f"    - Generation Mode: {res['generation_mode']}")

        if tc.get("expected_available") is False:
            if res["available"] is False and tc["must_contain"] in res["answer_en"]:
                print(f"    [PASSED] Strict refusal triggered correctly: No hallucinated data.")
            else:
                print(f"    [FAILED] Expected refusal for irrelevant query, but got available={res['available']}")
                all_passed = False
            continue

        assert res["available"] is True, f"Query '{q}' should be available!"
        citations = res["citations"]
        print(f"    - Citations Count: {len(citations)}")
        if citations:
            top_cit = citations[0]
            print(f"    - Top Citation: {top_cit['doc_name']} (Page {top_cit['page_number']})")
            print(f"    - Excerpt: {top_cit['excerpt'][:90]}...")

            if tc.get("expected_doc") and top_cit["doc_name"] != tc["expected_doc"]:
                print(f"    [WARNING] Expected doc {tc['expected_doc']}, got {top_cit['doc_name']}")

        print(f"    - English Answer: {res['answer_en'][:130]}...")
        print(f"    - Kannada Answer: {res['answer_kn'][:130]}...")

        # Verify key factual term is present
        if tc.get("must_contain"):
            found = (tc["must_contain"].lower() in res["answer_en"].lower() or
                     tc["must_contain"].lower() in res["answer_kn"].lower())
            if found:
                print(f"    [PASSED] Answer correctly grounded with facts ('{tc['must_contain']}').")
            else:
                print(f"    [FAILED] Answer missing expected factual string '{tc['must_contain']}'")
                all_passed = False

    print("\n" + "="*50)
    if all_passed:
        print("ALL RAG RETRIEVAL & GROUNDING TESTS PASSED!")
    else:
        print("SOME TESTS HAD WARNINGS OR FAILURES - REVIEW ABOVE")
    print("="*50)

if __name__ == "__main__":
    run_tests()
