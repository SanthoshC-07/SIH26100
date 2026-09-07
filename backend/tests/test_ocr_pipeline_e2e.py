"""
Comprehensive End-to-End Test Suite for Document OCR & Entity Extraction Pipeline
Ministry of Petroleum & Natural Gas - Petroleum Pipeline Procurement (SIH26100)
"""
import os
import io
import pytest
import pymupdf
from PIL import Image, ImageDraw, ImageFont
from fastapi.testclient import TestClient

from app.main import app
from app.documents.extractor import DocumentExtractor
from app.documents.entity_extractor import EntityExtractor
from app.models.models import User, Bidder, Document, ExtractedEntity
from app.api.deps import get_current_user, get_current_admin, get_current_officer, get_current_bidder
from app.core.database import SessionLocal, engine, Base

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_auth():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    officer_user = db.query(User).filter(User.username == "officer_test").first()
    if not officer_user:
        officer_user = User(
            id="officer-test-id",
            name="Officer User",
            username="officer_test",
            email="officer_test@gem.gov.in",
            password_hash="dummy_hash_for_test",
            role="PROCUREMENT_OFFICER",
            is_active=True
        )
        db.add(officer_user)
        db.commit()
    db.close()

    def _get_test_user():
        d = SessionLocal()
        u = d.query(User).filter(User.username == "officer_test").first()
        d.close()
        return u

    app.dependency_overrides[get_current_user] = _get_test_user
    app.dependency_overrides[get_current_admin] = _get_test_user
    app.dependency_overrides[get_current_officer] = _get_test_user
    app.dependency_overrides[get_current_bidder] = _get_test_user
    yield
    app.dependency_overrides.clear()


def create_sample_gst_image_bytes() -> bytes:
    """Generates synthetic GST registration certificate image."""
    img = Image.new("RGB", (900, 350), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    text = (
        "GOVERNMENT OF INDIA - GST REGISTRATION CERTIFICATE\n"
        "Registration Number: 29MOCKP1234M1Z5\n"
        "Legal Name: PRAVEEN B S ENGINEERING SERVICES\n"
        "Trade Name: PRAVEEN ENGINEERING\n"
        "PAN: BSZPP1234K\n"
        "Constitution of Business: Proprietorship\n"
        "Date of Validity: 01/04/2021 to Perpetual\n"
        "Taxpayer Type: Regular Active"
    )
    draw.text((25, 25), text, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def create_sample_pan_image_bytes() -> bytes:
    """Generates synthetic PAN card image."""
    img = Image.new("RGB", (800, 250), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    text = (
        "INCOME TAX DEPARTMENT - GOVT OF INDIA\n"
        "Permanent Account Number: BSZPP1234K\n"
        "Name: PRAVEEN B S\n"
        "Father's Name: B SHIVARAM\n"
        "Date of Birth: 15/06/1984"
    )
    draw.text((25, 25), text, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def create_scanned_pdf_bytes() -> bytes:
    """Generates a scanned PDF (image rendered into PDF pages without native text stream)."""
    img_bytes = create_sample_gst_image_bytes()
    img_doc = pymupdf.open("png", img_bytes)
    pdf_bytes = img_doc.convert_to_pdf()
    img_doc.close()
    return pdf_bytes


# ==============================================================================
# TEST 1: Image OCR on PNG and JPEG (No Placeholder Text)
# ==============================================================================
def test_image_ocr_extracts_real_text(tmp_path):
    png_path = str(tmp_path / "gst_registration.png")
    with open(png_path, "wb") as f:
        f.write(create_sample_gst_image_bytes())

    res = DocumentExtractor.extract_document(png_path)

    # 1. Assert Engine and Scanned Flag
    assert res["extraction_method"] == "TESSERACT_OCR"
    assert res["is_scanned"] is True
    assert res["page_count"] == 1

    # 2. Assert Actual Text is Extracted (NEVER Placeholder String)
    full_text = res["full_text"]
    assert len(full_text.strip()) > 0
    assert "[Scanned Image Content:" not in full_text
    assert "[Scanned Image Document:" not in full_text
    assert "29MOCKP1234M1Z5" in full_text or "PRAVEEN" in full_text.upper()

    # 3. Assert Entity Extraction from OCR Text
    entities = EntityExtractor.extract_all_entities(res["pages"], "gst_registration.png")
    assert len(entities) > 0
    entity_types = [e["entity_type"] for e in entities]
    assert "GSTIN" in entity_types or "PAN" in entity_types or "COMPANY_NAME" in entity_types


# ==============================================================================
# TEST 2: Scanned PDF OCR (300 DPI Rendering and Text Extraction)
# ==============================================================================
def test_scanned_pdf_ocr_pipeline(tmp_path):
    pdf_path = str(tmp_path / "scanned_gst_cert.pdf")
    with open(pdf_path, "wb") as f:
        f.write(create_scanned_pdf_bytes())

    res = DocumentExtractor.extract_document(pdf_path)

    assert res["extraction_method"] == "TESSERACT_OCR"
    assert res["is_scanned"] is True
    assert len(res["full_text"].strip()) > 0
    assert "[Scanned Page" not in res["full_text"]
    assert "29MOCKP1234M1Z5" in res["full_text"] or "PRAVEEN" in res["full_text"].upper()


# ==============================================================================
# TEST 3: Digital PDF Native Stream Extraction
# ==============================================================================
def test_digital_pdf_native_extraction(tmp_path):
    pdf_path = str(tmp_path / "digital_contract.pdf")
    doc = pymupdf.open()
    page = doc.new_page(width=600, height=800)
    page.insert_textbox(pymupdf.Rect(50, 50, 550, 400), "Completed 135 KM 24 Inch NB Natural Gas Pipeline for GAIL on 15-03-2025.\nAnnual Turnover: FY 2023-24 INR 30 Crore.")
    doc.save(pdf_path)
    doc.close()

    res = DocumentExtractor.extract_document(pdf_path)
    assert res["extraction_method"] == "PDF_TEXT"
    assert res["is_scanned"] is False
    assert "135 KM" in res["full_text"]
    assert "30 Crore" in res["full_text"]


# ==============================================================================
# TEST 4: Placeholder Rejection Validation
# ==============================================================================
def test_placeholder_validation():
    assert DocumentExtractor.is_placeholder_text("[Scanned Image Content: inspect_abc.png]") is True
    assert DocumentExtractor.is_placeholder_text("[Scanned Image Document: file.png]") is True
    assert DocumentExtractor.is_placeholder_text("[OCR FAILED]") is True
    assert DocumentExtractor.is_placeholder_text("") is True
    assert DocumentExtractor.is_placeholder_text(None) is True
    assert DocumentExtractor.is_placeholder_text("GSTIN: 29MOCKP1234M1Z5 Active Regular Status") is False


# ==============================================================================
# TEST 5: Real-Time Inspect Document API (/api/bidders/inspect-document)
# ==============================================================================
def test_inspect_document_api_with_image():
    img_bytes = create_sample_gst_image_bytes()
    files = {
        "file": ("gst_certificate.png", img_bytes, "image/png")
    }

    res = client.post("/api/bidders/inspect-document", files=files)
    assert res.status_code == 200
    data = res.json()

    assert data["success"] is True
    assert data["status"] == "SUCCESS"
    assert data["extraction_engine"] == "TESSERACT_OCR"
    assert data["is_scanned"] is True
    assert "[Scanned Image Content:" not in data["extracted_text"]
    assert "[Scanned Image Content:" not in data["extracted_snippet"]
    assert len(data["extracted_text"]) > 0
    assert len(data["entities"]) > 0


# ==============================================================================
# TEST 6: Entity Extraction Across All Domain Categories from Real Text
# ==============================================================================
def test_entity_extraction_full_domain():
    full_text = """
    M/S PRAVEEN B S ENGINEERING SERVICES
    GSTIN: 29MOCKP1234M1Z5
    PAN: BSZPP1234K
    UDYAM: UDYAM-KR-03-0012345
    CIN: U11100KA2020PTC123456
    
    FINANCIAL TURNOVER:
    FY 2023-24: INR 30.00 Crore
    FY 2024-25: INR 27.00 Crore
    FY 2025-26: INR 24.00 Crore
    Average Turnover: INR 27.00 Crore
    
    SIMILAR PIPELINE EXPERIENCE:
    Successfully executed 135 KM 24-inch natural gas transmission pipeline for GAIL completed on 15-03-2025.
    Total contract value INR 82.50 Crore.
    
    HSE CERTIFICATION:
    Certified under ISO 45001:2018 and ISO 14001:2015. Zero fatality track record.
    """

    pages = [{"page_number": 1, "text": full_text, "raw_text": full_text}]
    entities = EntityExtractor.extract_all_entities(pages, "FullEvidence.pdf")

    ent_dict = {}
    for e in entities:
        ent_dict.setdefault(e["entity_type"], []).append(e["entity_value"])

    assert "GSTIN" in ent_dict
    assert "PAN" in ent_dict
    assert "UDYAM_NUMBER" in ent_dict
    assert "CIN" in ent_dict
    assert "FINANCIAL_TURNOVER_RECORD" in ent_dict
    assert "PIPELINE_LENGTH_KM" in ent_dict
    assert "HSE_CERTIFICATE" in ent_dict


# ==============================================================================
# TEST 7: Extract Name & Cardholder along with PAN Number from PAN Card
# ==============================================================================
def test_pan_card_name_and_number_extraction():
    # 1. Labeled PAN format
    pan_labeled = """
    INCOME TAX DEPARTMENT - GOVT OF INDIA
    PERMANENT ACCOUNT NUMBER CARD
    PAN: BSZPP1234K
    Name as per ITD: PRAVEEN B S ENGINEERING SERVICES
    Category: Company | Status: Active & Operational
    """
    entities_labeled = EntityExtractor.extract_all_entities([{"page_number": 1, "text": pan_labeled}])
    pan_ent = [e["entity_value"] for e in entities_labeled if e["entity_type"] == "PAN"]
    name_ent = [e["entity_value"] for e in entities_labeled if e["entity_type"] in ["COMPANY_NAME", "LEGAL_NAME"]]

    assert "BSZPP1234K" in pan_ent
    assert any("PRAVEEN B S ENGINEERING SERVICES" in n for n in name_ent)

    # 2. Structural Indian PAN card format (No explicit "Name:" prefix)
    pan_structural = """
    INCOME TAX DEPARTMENT
    GOVT. OF INDIA
    PRAVEEN B S ENGINEERING SERVICES
    SHIVANNA B S
    04/08/1988
    Permanent Account Number
    BSZPP1234K
    """
    entities_structural = EntityExtractor.extract_all_entities([{"page_number": 1, "text": pan_structural}])
    pan_s = [e["entity_value"] for e in entities_structural if e["entity_type"] == "PAN"]
    name_s = [e["entity_value"] for e in entities_structural if e["entity_type"] in ["COMPANY_NAME", "LEGAL_NAME"]]

    assert "BSZPP1234K" in pan_s
    assert any("PRAVEEN B S ENGINEERING SERVICES" in n for n in name_s)

