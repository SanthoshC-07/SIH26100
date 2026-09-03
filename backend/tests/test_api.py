import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal
from app.models.models import User, Tender, Requirement, Bidder

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

# 1. Health Endpoint Test
def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "SIH26100" in data["service"]

# 2. User Registration & Login Test
def test_user_registration_and_login():
    unique_email = f"officer_test_{id(setup_db)}@gem.gov.in"
    unique_user = f"officer_test_{id(setup_db)}"
    
    # Register
    reg_res = client.post("/api/auth/register", json={
        "name": "Test Officer",
        "email": unique_email,
        "username": unique_user,
        "password": "secure_password_123",
        "role": "PROCUREMENT_OFFICER",
        "department": "National Informatics Centre"
    })
    assert reg_res.status_code == 200
    user_data = reg_res.json()
    assert user_data["username"] == unique_user
    assert user_data["role"] == "PROCUREMENT_OFFICER"

    # Duplicate registration rejection
    dup_res = client.post("/api/auth/register", json={
        "name": "Test Officer Dup",
        "email": unique_email,
        "username": unique_user,
        "password": "secure_password_123"
    })
    assert dup_res.status_code == 400

    # Login
    login_res = client.post("/api/auth/login", json={
        "username_or_email": unique_user,
        "password": "secure_password_123"
    })
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    token = token_data["access_token"]
    
    # Get Current User (/api/auth/me)
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == unique_email

# 3. Tender CRUD Lifecycle Tests
def test_tender_crud_lifecycle():
    tender_num = f"GeM/2026/TEST/{id(setup_db)}"
    
    # 3a. Create Tender
    create_res = client.post("/api/tenders", json={
        "tender_number": tender_num,
        "title": "Procurement of High-Capacity Flash Storage",
        "organization": "Centre for Development of Advanced Computing (C-DAC)",
        "category": "Data Storage",
        "estimated_value": 45000000.0,
        "status": "ACTIVE"
    })
    assert create_res.status_code == 201
    tender = create_res.json()
    tender_id = tender["id"]
    assert tender["tender_number"] == tender_num
    assert tender["status"] == "ACTIVE"

    # 3b. Duplicate tender number rejection
    dup_res = client.post("/api/tenders", json={
        "tender_number": tender_num,
        "title": "Duplicate",
        "organization": "Test",
        "estimated_value": 100.0
    })
    assert dup_res.status_code == 400

    # 3c. Get Tender Detail
    get_res = client.get(f"/api/tenders/{tender_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Procurement of High-Capacity Flash Storage"

    # 3d. Update Tender
    update_res = client.put(f"/api/tenders/{tender_id}", json={
        "title": "Procurement of High-Capacity NVMe Flash Storage Arrays",
        "status": "UNDER_REVIEW"
    })
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Procurement of High-Capacity NVMe Flash Storage Arrays"
    assert update_res.json()["status"] == "UNDER_REVIEW"

    # 3e. List Tenders with search & filter
    list_res = client.get("/api/tenders", params={"search": tender_num})
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 3f. Delete Tender
    del_res = client.delete(f"/api/tenders/{tender_id}")
    assert del_res.status_code == 200

    # 3g. Verify Deleted
    get_after_del = client.get(f"/api/tenders/{tender_id}")
    assert get_after_del.status_code == 404

# 4. Document Upload Validation Tests
def test_document_upload_validation():
    # Create tender first
    tender_num = f"GeM/2026/DOC/{id(setup_db)}"
    t_res = client.post("/api/tenders", json={
        "tender_number": tender_num,
        "title": "Doc Validation Tender",
        "organization": "MeitY",
        "estimated_value": 1000000.0
    })
    tender_id = t_res.json()["id"]

    # Invalid extension test (e.g. .exe or .sh)
    invalid_file = ("bad_script.exe", b"malicious binary content", "application/octet-stream")
    bad_upload = client.post(
        f"/api/tenders/{tender_id}/documents",
        files={"file": invalid_file}
    )
    assert bad_upload.status_code == 400
    assert "Invalid file extension" in bad_upload.json()["detail"]

    # Valid PDF upload
    valid_pdf_content = b"%PDF-1.4 sample pdf content for testing validation"
    valid_upload = client.post(
        f"/api/tenders/{tender_id}/documents",
        files={"file": ("specification.pdf", valid_pdf_content, "application/pdf")}
    )
    assert valid_upload.status_code == 200
    doc_data = valid_upload.json()
    assert doc_data["tender_id"] == tender_id
    assert doc_data["mime_type"] == "application/pdf"

# 5. Bidder Projects & Personnel Endpoints Test
def test_bidder_projects_and_personnel_api():
    # 5a. Create Tender & Bidder
    t_num = f"GAIL/2026/PROJ/{id(setup_db)}"
    t_res = client.post("/api/tenders", json={
        "tender_number": t_num,
        "title": "Pipeline Laying Tender",
        "issuing_organization": "GAIL",
        "estimated_value": 150000000.0
    })
    tender_id = t_res.json()["id"]

    b_res = client.post("/api/bidders", json={
        "tender_id": tender_id,
        "legal_name": "Apex Hydrocarbon Infra Ltd",
        "gstin": "27AAACA9999F1Z5",
        "pan": "AAACA9999F"
    })
    bidder_id = b_res.json()["id"]

    # 5b. Add Project Experience
    p_res = client.post(f"/api/bidders/{bidder_id}/projects", json={
        "project_name": "ONGC Hazira Gas Pipeline",
        "client_name": "ONGC",
        "sector": "OIL_AND_GAS",
        "pipeline_length_km": 140.0,
        "pipeline_diameter": "24 inch API 5L X70",
        "project_value": 1800000000.0
    })
    assert p_res.status_code == 200
    p_data = p_res.json()
    assert p_data["project_name"] == "ONGC Hazira Gas Pipeline"
    assert p_data["pipeline_length_km"] == 140.0

    # 5c. List Projects
    p_list = client.get(f"/api/bidders/{bidder_id}/projects")
    assert p_list.status_code == 200
    assert len(p_list.json()) >= 1

    # 5d. Add Personnel
    pers_res = client.post(f"/api/bidders/{bidder_id}/personnel", json={
        "name": "Suresh Patel",
        "designation": "Lead Pipeline Engineer",
        "qualification": "B.Tech Mechanical",
        "years_of_experience": 12.0,
        "pipeline_experience_years": 12.0
    })
    assert pers_res.status_code == 200
    pers_data = pers_res.json()
    assert pers_data["name"] == "Suresh Patel"
    assert pers_data["years_of_experience"] == 12.0

    # 5e. List Personnel
    pers_list = client.get(f"/api/bidders/{bidder_id}/personnel")
    assert pers_list.status_code == 200
    assert len(pers_list.json()) >= 1

# 6. Bids API Endpoints Test
def test_bids_api():
    t_num = f"IOCL/2026/BID/{id(setup_db)}"
    t_res = client.post("/api/tenders", json={
        "tender_number": t_num,
        "title": "IOCL Pipeline Procurement",
        "estimated_value": 50000000.0
    })
    tender_id = t_res.json()["id"]

    b_res = client.post("/api/bidders", json={
        "tender_id": tender_id,
        "legal_name": "Bharat Pipeline EPC Pvt Ltd"
    })
    bidder_id = b_res.json()["id"]

    bid_res = client.post("/api/bids", json={
        "tender_id": tender_id,
        "bidder_id": bidder_id,
        "bid_reference_number": f"BID-REF-{id(setup_db)}",
        "financial_bid_amount": 48000000.0
    })
    assert bid_res.status_code == 200
    bid_data = bid_res.json()
    assert bid_data["financial_bid_amount"] == 48000000.0

    list_bids = client.get(f"/api/bids?tender_id={tender_id}")
    assert list_bids.status_code == 200
    assert len(list_bids.json()) >= 1

# 7. Verifications & Evidence API Test
def test_verifications_and_evidence_api():
    verif_res = client.get("/api/verifications")
    assert verif_res.status_code == 200
    assert isinstance(verif_res.json(), list)

    ev_res = client.get("/api/evidence")
    assert ev_res.status_code == 200
    assert isinstance(ev_res.json(), list)

