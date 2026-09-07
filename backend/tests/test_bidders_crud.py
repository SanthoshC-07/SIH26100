import io
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal
from app.models.models import Tender, Bidder, Document, User
from app.api.deps import get_current_user, get_current_admin, get_current_officer, get_current_bidder

client = TestClient(app)

from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    bidder_user = db.query(User).filter(User.username == "bidder_test_crud").first()
    if not bidder_user:
        bidder_user = User(
            id="bidder-test-crud-id",
            name="Bidder User",
            username="bidder_test_crud",
            email="bidder_test_crud@gem.gov.in",
            password_hash="dummy_hash_for_test",
            role="BIDDER",
            is_active=True
        )
        db.add(bidder_user)
        db.commit()

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

    def get_test_bidder(db: Session = Depends(get_db)):
        return db.query(User).filter(User.username == "bidder_test_crud").first()

    app.dependency_overrides[get_current_user] = get_test_bidder
    app.dependency_overrides[get_current_bidder] = get_test_bidder
    yield
    app.dependency_overrides.clear()

def create_test_tender():
    t_num = f"MOPNG/2026/TEST/{uuid.uuid4().hex[:10]}"
    def get_test_officer(db: Session = Depends(get_db)):
        return db.query(User).filter(User.username == "officer_test").first()
    
    app.dependency_overrides[get_current_user] = get_test_officer
    res = client.post("/api/tenders", json={
        "tender_number": t_num,
        "title": "120 km Natural Gas Transmission Pipeline Tender",
        "issuing_organization": "GAIL (India) Limited",
        "estimated_value": 1500000000.0,
        "status": "ACTIVE"
    })
    
    def get_test_bidder(db: Session = Depends(get_db)):
        return db.query(User).filter(User.username == "bidder_test_crud").first()
    app.dependency_overrides[get_current_user] = get_test_bidder
    app.dependency_overrides[get_current_bidder] = get_test_bidder

    assert res.status_code == 201
    return res.json()["id"]

# =====================================================================
# TEST 1: Valid bidder + valid PDF -> Bidder created successfully
# =====================================================================
def test_1_valid_bidder_with_pdf():
    tender_id = create_test_tender()
    
    pdf_content = b"%PDF-1.4 Mock petroleum compliance dossier evidence for Praveen BS"
    files = [
        ("documents", ("Praveen_BS_Mock_Petroleum_Compliance_Evidence_Pack.pdf", pdf_content, "application/pdf"))
    ]
    data = {
        "tender_id": tender_id,
        "legal_name": "PRAVEEN B S ENGINEERING SERVICES",
        "pan": "BSZPP1234K",
        "gstin": "29MOCKP1234M1Z5"
    }
    
    res = client.post("/api/bidders/with-documents", data=data, files=files)
    assert res.status_code == 200
    bidder = res.json()
    assert bidder["legal_name"] == "PRAVEEN B S ENGINEERING SERVICES"
    assert bidder["pan"] == "BSZPP1234K"
    assert bidder["gstin"] == "29MOCKP1234M1Z5"
    assert bidder["documents_count"] == 1

# =====================================================================
# TEST 2: Invalid PAN -> Clear PAN validation error
# =====================================================================
def test_2_invalid_pan_format():
    tender_id = create_test_tender()
    
    res = client.post("/api/bidders", json={
        "tender_id": tender_id,
        "legal_name": "Praveen Pipeline Infra Ltd",
        "pan": "INVALID_PAN_123"
    })
    assert res.status_code == 422
    data = res.json()
    error_text = str(data["detail"]).lower()
    assert "pan" in error_text

# =====================================================================
# TEST 3: Invalid GSTIN format -> Clear GSTIN validation error
# =====================================================================
def test_3_invalid_gstin_format():
    tender_id = create_test_tender()
    
    res = client.post("/api/bidders", json={
        "tender_id": tender_id,
        "legal_name": "Praveen Pipeline Infra Ltd",
        "pan": "BSZPP1234K",
        "gstin": "123_INVALID_GSTIN"
    })
    assert res.status_code == 422
    data = res.json()
    error_text = str(data["detail"]).lower()
    assert "gstin" in error_text

# =====================================================================
# TEST 4: Duplicate PAN in same tender -> Clear duplicate bidder error
# =====================================================================
def test_4_duplicate_pan_rejection():
    tender_id = create_test_tender()
    
    # First creation
    res1 = client.post("/api/bidders", json={
        "tender_id": tender_id,
        "legal_name": "Praveen Hydrocarbon EPC Ltd",
        "pan": "BSZPP1234K"
    })
    assert res1.status_code == 200

    # Second creation with identical PAN in same tender
    res2 = client.post("/api/bidders", json={
        "tender_id": tender_id,
        "legal_name": "Praveen Infra Alternate Name Ltd",
        "pan": "BSZPP1234K"
    })
    assert res2.status_code == 409
    data = res2.json()
    assert data["detail"]["code"] == "BIDDER_ALREADY_EXISTS"
    assert "BSZPP1234K" in data["detail"]["message"]

# =====================================================================
# TEST 5: No company name -> Clear required-field error
# =====================================================================
def test_5_missing_company_name():
    tender_id = create_test_tender()
    
    res = client.post("/api/bidders", json={
        "tender_id": tender_id,
        "legal_name": "",
        "pan": "BSZPP1234K"
    })
    assert res.status_code == 422
    error_text = str(res.json()["detail"]).lower()
    assert "name" in error_text

# =====================================================================
# TEST 6: No document -> Bidder creation succeeds
# =====================================================================
def test_6_valid_bidder_no_documents():
    tender_id = create_test_tender()
    
    res = client.post("/api/bidders", json={
        "tender_id": tender_id,
        "legal_name": "Praveen Pure Consultancy Ltd",
        "pan": "BSZPP1234K",
        "gstin": "29MOCKP1234M1Z5"
    })
    assert res.status_code == 200
    bidder = res.json()
    assert bidder["legal_name"] == "Praveen Pure Consultancy Ltd"
    assert bidder["documents_count"] == 0

# =====================================================================
# TEST 7: Multiple PDF documents -> All files stored and associated
# =====================================================================
def test_7_multiple_pdf_documents_upload():
    tender_id = create_test_tender()
    
    files = [
        ("documents", ("Doc1_Statutory_GST_PAN.pdf", b"%PDF-1.4 GST and PAN statutory sheet", "application/pdf")),
        ("documents", ("Doc2_Financial_Turnover.pdf", b"%PDF-1.4 Audited CA Turnover Statement", "application/pdf")),
        ("documents", ("Doc3_Pipeline_Experience.pdf", b"%PDF-1.4 120km pipeline completion report", "application/pdf"))
    ]
    data = {
        "tender_id": tender_id,
        "legal_name": "PRAVEEN B S ENGINEERING SERVICES",
        "pan": "BSZPP1234K",
        "gstin": "29MOCKP1234M1Z5"
    }
    
    res = client.post("/api/bidders/with-documents", data=data, files=files)
    assert res.status_code == 200
    bidder = res.json()
    assert bidder["documents_count"] == 3

    # Verify detail returns all 3 documents
    detail_res = client.get(f"/api/bidders/{bidder['id']}")
    assert detail_res.status_code == 200
    assert len(detail_res.json()["documents"]) == 3

# =====================================================================
# TEST 8: Text extraction / OCR failure resilience
# =====================================================================
def test_8_ocr_extraction_failure_resilience():
    tender_id = create_test_tender()
    
    # Send a non-standard PDF buffer that might fail standard stream parsing
    corrupt_pdf = b"%PDF-1.4 [corrupted stream data]"
    files = [
        ("documents", ("Praveen_Complex_Scan.pdf", corrupt_pdf, "application/pdf"))
    ]
    data = {
        "tender_id": tender_id,
        "legal_name": "Praveen Robust Pipeline Solutions",
        "pan": "BSZPP1234K"
    }
    
    # Creation must NOT fail; document must be preserved
    res = client.post("/api/bidders/with-documents", data=data, files=files)
    assert res.status_code == 200
    bidder = res.json()
    assert bidder["legal_name"] == "Praveen Robust Pipeline Solutions"
    assert bidder["documents_count"] == 1
