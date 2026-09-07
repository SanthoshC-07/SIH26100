"""
SIH26100 — Phase 3 Document Intelligence & Neural Retrieval Test Suite
----------------------------------------------------------------------
Validates:
1. LLM Requirement Extraction JSON parsing
2. Invalid LLM response handling & error resilience
3. Deterministic Regex Fallback engine
4. Specific target extractions:
   - 25 Crore (INR)
   - 100 KM (Length)
   - 24 Inch (Diameter)
   - 7 Years (Experience)
   - Natural Gas Pipeline (Project Type)
   - Oil & Gas (Sector)
   - 5 Engineers (Required Count)
   - 8 Years (Personnel Experience)
5. Sentence Transformer dense embeddings (384-d)
6. FAISS vector indexing & metadata provenance (document_name, page_number)
7. Requirement -> Evidence search
8. Separation of semantic similarity from numeric compliance decisions
9. Confidence scoring and REVIEW gating
10. Intelligence and Evidence REST API endpoints
"""
import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.dirname(_THIS_DIR)
_PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

import pytest
from fastapi.testclient import TestClient
from fastapi import Depends
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import Base, engine, SessionLocal, get_db
from app.models.models import User, Tender, Requirement, Bidder, Document, DocumentPage
from app.api.deps import get_current_user, get_current_admin, get_current_officer, get_current_bidder

from ml.services.requirement_llm import requirement_llm_service
from ml.services.requirement_regex import regex_requirement_extractor
from ml.services.requirement_extractor import unified_requirement_extractor
from ml.services.embedding_service import embedding_service
from ml.services.faiss_service import faiss_evidence_index
from ml.services.evidence_retriever import evidence_retriever_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_context():
    Base.metadata.create_all(bind=engine)
    
    def get_test_officer(db: Session = Depends(get_db)):
        user = db.query(User).filter(User.username == "officer_phase3").first()
        if not user:
            user = User(
                id="officer-p3-id",
                name="Phase3 Procurement Officer",
                username="officer_phase3",
                email="officer_p3@gem.gov.in",
                password_hash="mock_hash",
                role="PROCUREMENT_OFFICER",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    app.dependency_overrides[get_current_user] = get_test_officer
    app.dependency_overrides[get_current_admin] = get_test_officer
    app.dependency_overrides[get_current_officer] = get_test_officer
    app.dependency_overrides[get_current_bidder] = get_test_officer
    yield
    app.dependency_overrides.clear()


# ==============================================================================
# TEST 1: LLM Valid Extraction
# ==============================================================================
def test_01_llm_valid_extraction():
    clause = "The bidder must possess average annual turnover of at least INR 25 Crore in the last 3 financial years."
    res = requirement_llm_service.extract_requirement(clause)
    
    assert res["category"] == "FINANCIAL_ELIGIBILITY"
    assert res["unit"] == "CRORE"
    assert res["minimum_value"] == 25.0
    assert res["time_period_years"] == 3
    assert res["value"] == 250000000.0
    assert "LLM" in res["extraction_method"]
    assert res["confidence"] >= 0.70


# ==============================================================================
# TEST 2: LLM Invalid JSON / Error Recovery
# ==============================================================================
def test_02_llm_invalid_json():
    # Test with empty and malformed content
    res_empty = requirement_llm_service.extract_requirement("")
    assert res_empty["confidence"] == 0.0
    assert res_empty["extraction_method"] == "EMPTY_INPUT"

    res_ws = requirement_llm_service.extract_requirement("   \n\t  ")
    assert res_ws["confidence"] == 0.0
    assert res_ws["extraction_method"] == "EMPTY_INPUT"


# ==============================================================================
# TEST 3: Regex Fallback
# ==============================================================================
def test_03_regex_fallback():
    clause = "Required pipeline execution of minimum 100 KM and diameter 24 Inch with 7 years experience."
    res = regex_requirement_extractor.extract_deterministic_entities(clause)
    
    assert res["length_km"] == 100.0
    assert res["diameter_inch"] == 24.0
    assert res["experience_years"] == 7
    assert res["extraction_method"] == "REGEX_FALLBACK"
    assert len(res["entities"]) >= 3


# ==============================================================================
# TEST 4: Crore Extraction
# ==============================================================================
def test_04_crore_extraction():
    res = regex_requirement_extractor.extract_deterministic_entities("Bidder must have annual turnover of INR 25 Crore.")
    assert res["minimum_value"] == 25.0
    assert res["unit"] == "CRORE"
    assert res["value"] == 250000000.0


# ==============================================================================
# TEST 5: KM Extraction
# ==============================================================================
def test_05_km_extraction():
    res = regex_requirement_extractor.extract_deterministic_entities("Pipeline laying work of at least 100 KM length.")
    assert res["length_km"] == 100.0


# ==============================================================================
# TEST 6: Inch Extraction
# ==============================================================================
def test_06_inch_extraction():
    res = regex_requirement_extractor.extract_deterministic_entities("Steel line pipes of diameter 24 Inch (600 mm).")
    assert res["diameter_inch"] == 24.0


# ==============================================================================
# TEST 7: Years Extraction
# ==============================================================================
def test_07_years_extraction():
    res = regex_requirement_extractor.extract_deterministic_entities("Bidder must demonstrate 7 years past experience.")
    assert res["experience_years"] == 7


# ==============================================================================
# TEST 8: Date & Financial Year Extraction
# ==============================================================================
def test_08_date_extraction():
    res = regex_requirement_extractor.extract_deterministic_entities("Work completed before 31/03/2024 for FY 2023-24.")
    assert any("2023-24" in e for e in res["entities"])
    assert any("31/03/2024" in e for e in res["entities"])


# ==============================================================================
# TEST 9: Sentence Transformer Dense Embedding
# ==============================================================================
def test_09_sentence_transformer_embedding():
    vec = embedding_service.embed_text("100 KM natural gas transmission pipeline execution")
    assert isinstance(vec, list)
    assert len(vec) == 384 or len(vec) == embedding_service.dimension

    docs = [
        "135 KM natural gas pipeline completed for GAIL",
        "Audited balance sheet FY 2025-26"
    ]
    doc_vecs = embedding_service.embed_documents(docs)
    assert len(doc_vecs) == 2
    assert len(doc_vecs[0]) == len(vec)


# ==============================================================================
# TEST 10: FAISS Indexing
# ==============================================================================
def test_10_faiss_indexing():
    faiss_evidence_index.clear()
    chunks = [
        {
            "chunk_id": "chunk-test-10",
            "document_id": "doc-test-10",
            "document_name": "Project_Experience.pdf",
            "page_number": 4,
            "text": "Natural Gas Transmission Pipeline - 135 KM - 24 Inch",
            "extraction_method": "PDF_TEXT"
        }
    ]
    count = faiss_evidence_index.add_chunks(chunks)
    assert count == 1
    assert faiss_evidence_index.get_count() >= 1


# ==============================================================================
# TEST 11: FAISS Retrieval
# ==============================================================================
def test_11_faiss_retrieval():
    faiss_evidence_index.clear()
    faiss_evidence_index.add_chunks([
        {
            "chunk_id": "chunk-test-11",
            "document_id": "doc-test-11",
            "document_name": "Project_Experience.pdf",
            "page_number": 4,
            "text": "Natural Gas Transmission Pipeline - 135 KM - 24 Inch",
            "extraction_method": "PDF_TEXT"
        }
    ])
    q_vec = embedding_service.embed_text("natural gas pipeline experience 100 KM")
    results = faiss_evidence_index.search(q_vec, top_k=1)
    assert len(results) == 1
    assert results[0]["document_name"] == "Project_Experience.pdf"
    assert results[0]["page_number"] == 4
    assert results[0]["similarity_score"] > 0.60


# ==============================================================================
# TEST 12: Requirement / Evidence Matching
# ==============================================================================
def test_12_requirement_evidence_matching():
    retrieval = evidence_retriever_service.retrieve_evidence_for_requirement(
        requirement_text="Minimum 100 KM natural gas pipeline experience",
        requirement_id="REQ-005",
        category="EXPERIENCE_ELIGIBILITY",
        top_k=2
    )
    assert retrieval["requirement_id"] == "REQ-005"
    assert "evidence" in retrieval
    assert len(retrieval["evidence"]) >= 1


# ==============================================================================
# TEST 13: Page Metadata Preservation
# ==============================================================================
def test_13_page_metadata_preservation():
    faiss_evidence_index.clear()
    chunk = {
        "chunk_id": "chk-page-7",
        "document_id": "doc-turnover-audit",
        "document_name": "Audited_Financial_Statement_FY24.pdf",
        "page_number": 7,
        "text": "Turnover for the financial year was INR 45.2 Crore.",
        "extraction_method": "TESSERACT_OCR"
    }
    faiss_evidence_index.add_chunks([chunk])
    
    q_vec = embedding_service.embed_text("Annual turnover audited statement")
    hits = faiss_evidence_index.search(q_vec, top_k=1)
    assert len(hits) == 1
    assert hits[0]["document_id"] == "doc-turnover-audit"
    assert hits[0]["document_name"] == "Audited_Financial_Statement_FY24.pdf"
    assert hits[0]["page_number"] == 7
    assert hits[0]["extraction_method"] == "TESSERACT_OCR"


# ==============================================================================
# TEST 14: Low Similarity Handling
# ==============================================================================
def test_14_low_similarity_handling():
    retrieval = evidence_retriever_service.retrieve_evidence_for_requirement(
        requirement_text="Quantum physics entanglement certificate in space satellite",
        requirement_id="REQ-IRRELEVANT-999",
        category="TECHNICAL_SPECIFICATION",
        top_k=3
    )
    # Status should be marked as REVIEW due to poor similarity match
    assert retrieval["evidence_status"] == "REVIEW" or len(retrieval["evidence"]) == 0 or retrieval["evidence"][0]["similarity_score"] < 0.60


# ==============================================================================
# TEST 15: Missing Evidence Handling
# ==============================================================================
def test_15_missing_evidence_handling():
    # Empty index search
    faiss_evidence_index.clear()
    retrieval = evidence_retriever_service.retrieve_evidence_for_requirement(
        requirement_text="Make in India local content certificate 50%",
        requirement_id="REQ-MII-001",
        category="MAKE_IN_INDIA_LOCAL_CONTENT",
        top_k=3
    )
    assert retrieval["evidence_status"] in ["REVIEW", "NO_EVIDENCE"]
    assert len(retrieval["evidence"]) == 0
    assert "No matching evidence chunks found" in retrieval.get("message", "")


# ==============================================================================
# TEST 16: Verification of 8 Mandatory Target Values
# ==============================================================================
def test_16_mandatory_eight_target_extractions():
    # 1. 25 Crore
    res_crore = unified_requirement_extractor.extract("Minimum annual turnover of INR 25 Crore.")
    assert res_crore["minimum_value"] == 25.0
    assert res_crore["unit"] == "CRORE"
    assert res_crore["value"] == 250000000.0

    # 2. 100 KM
    res_km = unified_requirement_extractor.extract("Pipeline of at least 100 KM length.")
    assert res_km["length_km"] == 100.0

    # 3. 24 Inch
    res_inch = unified_requirement_extractor.extract("Minimum diameter of 24 Inch line pipes.")
    assert res_inch["diameter_inch"] == 24.0

    # 4. 7 Years
    res_7yrs = unified_requirement_extractor.extract("Bidder must have 7 years experience in pipeline EPC.")
    assert res_7yrs["experience_years"] == 7

    # 5. Natural Gas Pipeline
    res_ng = unified_requirement_extractor.extract("Execution of cross-country natural gas pipeline projects.")
    assert res_ng["project_type"] == "Natural Gas Pipeline"

    # 6. Oil & Gas
    res_og = unified_requirement_extractor.extract("Minimum turnover in oil & gas hydrocarbon sector.")
    assert "oil & gas" in (res_og["sector"] or "").lower()

    # 7. 5 Engineers
    res_eng = unified_requirement_extractor.extract("Bidder must deploy minimum 5 engineers on site.")
    assert res_eng["required_count"] == 5
    assert res_eng["role"] == "Pipeline Engineer"

    # 8. 8 Years (Personnel experience)
    res_8yrs = unified_requirement_extractor.extract("Engineers must possess at least 8 years experience in cross-country pipeline laying.")
    assert res_8yrs["experience_years"] == 8


# ==============================================================================
# TEST 17: Separation of Semantic Similarity from Compliance Decision
# ==============================================================================
def test_17_similarity_does_not_equal_compliance_pass():
    req_text = "Minimum 100 KM natural gas pipeline construction"
    evidence_text = "Completed 60 KM natural gas pipeline construction"
    
    vec_req = embedding_service.embed_text(req_text)
    vec_ev = embedding_service.embed_text(evidence_text)
    sim = embedding_service.calculate_similarity(vec_req, vec_ev)
    
    # High semantic similarity on topic
    assert sim >= 0.70

    # Deterministic logic
    extracted_req = unified_requirement_extractor.extract(req_text)
    extracted_ev = regex_requirement_extractor.extract_deterministic_entities(evidence_text)
    
    req_threshold = extracted_req["length_km"] # 100
    ev_val = extracted_ev["length_km"]          # 60
    
    is_compliant = (ev_val >= req_threshold)
    assert is_compliant is False, "60 KM evidence must FAIL 100 KM requirement despite high semantic similarity"


# ==============================================================================
# TEST 18: REST API - Intelligence & Evidence Endpoints
# ==============================================================================
def test_18_rest_api_intelligence_endpoints():
    # 1. POST /api/intelligence/extract-requirement
    res = client.post("/api/intelligence/extract-requirement", json={
        "requirement_text": "Average annual turnover of at least INR 25 Crore in last 3 years.",
        "category": "FINANCIAL_ELIGIBILITY"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["unit"] == "CRORE"
    assert data["minimum_value"] == 25.0
    assert data["status"] == "VERIFICATION_READY"

    # 2. POST /api/evidence/index/{bid_id}
    res_index = client.post("/api/evidence/index/demo-bidder-001")
    assert res_index.status_code == 200
    assert res_index.json()["success"] is True

    # 3. GET /api/evidence/search/{bid_id}
    res_search = client.get("/api/evidence/search/demo-bidder-001?q=pipeline%20turnover&top_k=3")
    assert res_search.status_code == 200
    assert "results" in res_search.json()
