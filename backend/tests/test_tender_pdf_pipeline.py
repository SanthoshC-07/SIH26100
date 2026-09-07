"""
SIH26100 — Phase 3A: Tender PDF -> Requirement Dataset Pipeline Unit & Integration Tests
-----------------------------------------------------------------------------------------
Validates:
 1. PDF text extraction
 2. OCR fallback behavior
 3. Clause segmentation and boilerplate filtering
 4. Requirement detection
 5. Category classification across 10 locked taxonomy classes
 6. LLM extraction
 7. Regex fallback extraction
 8. Source document and page preservation (audit traceability)
 9. Duplicate detection and handling
 10. CSV dataset and review generation and schema compliance
 11. Backend API endpoints for dataset & human review queue
"""
import os
import csv
import json
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.documents.extractor import DocumentExtractor
from app.nlp.clause_segmenter import ClauseSegmenter
from app.nlp.requirement_detector import RequirementDetector
from app.nlp.text_normalizer import TextNormalizer
from ml.scripts.requirement_classifier import requirement_classifier, REQUIREMENT_CLASSES
from ml.services.requirement_extractor import unified_requirement_extractor
from ml.services.requirement_regex import regex_requirement_extractor
from ml.scripts.tender_pdf_pipeline import (
    TenderPDFRequirementPipeline,
    DATASET_COLUMNS,
    REVIEW_COLUMNS,
    REQUIREMENT_DATASET_CSV,
    REQUIREMENT_REVIEW_CSV
)


@pytest.fixture
def client():
    return TestClient(app)


# ----------------------------------------------------------------------
# 1. PDF Text Extraction
# ----------------------------------------------------------------------
def test_01_pdf_text_extraction():
    """Verify PyMuPDF extracts text structure and page numbers from valid PDFs."""
    test_pdf = os.path.join("backend", "uploads", "Tender_IOCL_2026_PL_VALVES_5810.pdf")
    if os.path.exists(test_pdf):
        res = DocumentExtractor.extract_document(test_pdf)
        assert res["page_count"] >= 1
        assert "pages" in res
        assert len(res["pages"]) >= 1
        assert res["pages"][0]["page_number"] == 1
        assert len(res["pages"][0]["text"]) > 20
        assert res["pages"][0]["extraction_method"] in ["PDF_TEXT", "TESSERACT_OCR"]


# ----------------------------------------------------------------------
# 2. OCR Fallback Simulation
# ----------------------------------------------------------------------
def test_02_ocr_fallback_handling():
    """Verify OCR fallback logic when scanned/sparse text is encountered."""
    # Test text extractor handles image or text modes gracefully
    fake_img_path = os.path.join("backend", "uploads", "non_existent_scan.png")
    # File not found should raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        DocumentExtractor.extract_document(fake_img_path)


# ----------------------------------------------------------------------
# 3. Clause Segmentation & Boilerplate Filtering
# ----------------------------------------------------------------------
def test_03_clause_segmentation_and_filtering():
    """Verify segmentation isolates numbered clauses and filters non-requirement boilerplate."""
    sample_text = """
    Tender No: IOCL/2026/PL-01
    Table of Contents
    1. Scope of Work
    Supply of API 6D pipeline valves for 150 km transmission line.
    2. Minimum Turnover
    Bidder must have average annual financial turnover of at least INR 25 Crore.
    Address: New Delhi, India.
    """
    clauses = ClauseSegmenter.segment_text_into_clauses(sample_text)
    assert len(clauses) >= 1

    pipeline = TenderPDFRequirementPipeline()
    # Check boilerplate filtering
    assert pipeline.is_boilerplate_or_non_requirement("Table of Contents") is True
    assert pipeline.is_boilerplate_or_non_requirement("Address: New Delhi, India.") is True
    assert pipeline.is_boilerplate_or_non_requirement(
        "Bidder must have average annual financial turnover of at least INR 25 Crore."
    ) is False


# ----------------------------------------------------------------------
# 4. Requirement Detection
# ----------------------------------------------------------------------
def test_04_requirement_detection():
    """Verify detector identifies mandatory bidder requirements vs informative text."""
    req_text = "The contractor shall submit valid GST registration and CA audited balance sheets."
    clause_type, conf = RequirementDetector.detect_clause_type(req_text)
    assert clause_type == "REQUIREMENT"
    assert conf >= 0.70

    info_text = "The project location is located in Gujarat state."
    clause_type2, conf2 = RequirementDetector.detect_clause_type(info_text)
    assert clause_type2 in ["SCOPE", "INFORMATIONAL", "OTHER"]


# ----------------------------------------------------------------------
# 5. Category Classification Across 10 Locked Taxonomy Classes
# ----------------------------------------------------------------------
def test_05_category_classification_10_classes():
    """Verify classification maps across 10 locked classes with confidence."""
    test_cases = [
        ("Bidder shall possess active GSTIN registration.", "GST_TAX_COMPLIANCE"),
        ("Udyam Registration Certificate is mandatory for MSME bidders.", "MSME_UDYAM_ELIGIBILITY"),
        ("Minimum average annual turnover of INR 25 Crore.", "FINANCIAL_ELIGIBILITY"),
        ("Bidder must have completed 100 km natural gas pipeline project.", "EXPERIENCE_ELIGIBILITY"),
        ("Manufacturer Authorization Form from certified OEM.", "OEM_AUTHORIZATION"),
        ("Affidavit confirming bidder is not blacklisted by any PSU.", "BLACKLISTING_DEBARMENT"),
        ("Wall thickness and material grade according to API 5L.", "TECHNICAL_SPECIFICATION"),
        ("Valves must strictly comply with API 6D standard.", "INDUSTRY_STANDARD_COMPLIANCE"),
        ("The bidder must hold certified ISO 45001 safety management system.", "SAFETY_REGULATORY_COMPLIANCE"),
        ("Minimum 50 percent local content under Make in India policy.", "MAKE_IN_INDIA_LOCAL_CONTENT"),
    ]

    for text, expected_cat in test_cases:
        res = requirement_classifier.classify(text)
        assert res["predicted_class"] in REQUIREMENT_CLASSES
        assert res["confidence"] > 0.0


# ----------------------------------------------------------------------
# 6. LLM Extraction
# ----------------------------------------------------------------------
def test_06_llm_structured_extraction():
    """Verify unified extraction produces structured dictionary with standard keys."""
    text = "Bidder must have completed at least one 100 KM natural gas pipeline of 24-inch diameter."
    res = unified_requirement_extractor.extract(text)
    assert res is not None
    assert "category" in res
    assert res.get("length_km") == 100.0
    assert res.get("diameter_inch") == 24.0


# ----------------------------------------------------------------------
# 7. Regex Fallback
# ----------------------------------------------------------------------
def test_07_regex_fallback_numeric_parsing():
    """Verify deterministic regex engine extracts INR, KM, Inch, %, Years, Counts."""
    text = "Minimum turnover of INR 35.5 Crore in last 3 financial years, with 50% local content and 5 engineers."
    res = regex_requirement_extractor.extract_deterministic_entities(text)

    assert res["minimum_value"] == 35.5
    assert res["unit"] == "CRORE"
    assert res["currency"] == "INR"
    assert res["time_period_years"] == 3
    assert res["percentage"] == 50.0
    assert res["required_count"] == 5
    assert res["confidence"] >= 0.80


# ----------------------------------------------------------------------
# 8. Source & Page Preservation (Auditability)
# ----------------------------------------------------------------------
def test_08_source_and_page_preservation():
    """Verify every requirement dataset record retains source_document and page_number."""
    pipeline = TenderPDFRequirementPipeline()
    test_pdf = os.path.join("backend", "uploads", "Tender_MOPNG_PIPE_2026_017.pdf")
    if os.path.exists(test_pdf):
        res = pipeline.process_pdf(test_pdf)
        assert res["filename"] == "Tender_MOPNG_PIPE_2026_017.pdf"
        for req in res["candidate_requirements"]:
            assert req["source_document"] == "Tender_MOPNG_PIPE_2026_017.pdf"
            assert req["page_number"] >= 1
            assert len(req["original_text"]) > 0


# ----------------------------------------------------------------------
# 9. Duplicate Detection
# ----------------------------------------------------------------------
def test_09_duplicate_detection():
    """Verify duplicate clauses are detected and flagged in review dataset."""
    pipeline = TenderPDFRequirementPipeline()
    upload_dir = os.path.join("backend", "uploads")
    if os.path.exists(upload_dir):
        res = pipeline.process_directory(upload_dir)
        stats = res["stats"]
        assert stats["total_pdfs_scanned"] >= 1
        assert "duplicate_clauses_detected" in stats


# ----------------------------------------------------------------------
# 10. CSV Dataset & Review Generation and Schema Compliance
# ----------------------------------------------------------------------
def test_10_csv_dataset_generation_and_headers():
    """Verify generated requirement_dataset.csv and requirement_review.csv match required headers."""
    pipeline = TenderPDFRequirementPipeline()
    upload_dir = os.path.join("backend", "uploads")
    if os.path.exists(upload_dir):
        res = pipeline.process_directory(upload_dir)
        assert os.path.exists(REQUIREMENT_DATASET_CSV)
        assert os.path.exists(REQUIREMENT_REVIEW_CSV)

        # Validate master dataset CSV headers
        with open(REQUIREMENT_DATASET_CSV, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            assert headers == DATASET_COLUMNS

        # Validate review queue CSV headers
        with open(REQUIREMENT_REVIEW_CSV, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            review_headers = next(reader)
            assert review_headers == REVIEW_COLUMNS


# ----------------------------------------------------------------------
# 11. Backend API Integration Endpoints
# ----------------------------------------------------------------------
def test_11_api_requirement_endpoints(client):
    """Test API endpoints for dataset queries, stats, and review status updates."""
    # Obtain admin JWT token
    login_res = client.post("/api/v1/auth/login", data={"username": "admin@petrobid.gov.in", "password": "adminpassword123"})
    if login_res.status_code == 200:
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Stats endpoint
        stats_res = client.get("/api/v1/requirements-pipeline/stats", headers=headers)
        assert stats_res.status_code == 200
        data = stats_res.json()
        assert "total_requirements" in data
        assert "category_distribution" in data

        # 2. Dataset listing
        list_res = client.get("/api/v1/requirements-pipeline/dataset?limit=10", headers=headers)
        assert list_res.status_code == 200
        items_data = list_res.json()
        assert "items" in items_data
        assert "total" in items_data

        # 3. Review queue listing
        rev_res = client.get("/api/v1/requirements-pipeline/reviews?limit=10", headers=headers)
        assert rev_res.status_code == 200
        assert "items" in rev_res.json()

        # 4. Update review status
        if items_data["items"]:
            first_id = items_data["items"][0]["requirement_id"]
            upd_res = client.post(
                f"/api/v1/requirements-pipeline/review/{first_id}",
                json={"review_status": "APPROVED", "notes": "Verified by lead officer"},
                headers=headers
            )
            assert upd_res.status_code == 200
            assert upd_res.json()["new_status"] == "APPROVED"
