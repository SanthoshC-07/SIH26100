"""
SIH26100 — Complete Role-Based Access Control (RBAC) & IDOR Security Test Suite
Phase 5A: Exhaustive Verification of Permission Matrix and Object-Level Authorization
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.models import User, Tender, Bidder, Bid, Document, ComplianceCheck, ComplianceReport, AuditLog
from app.core.security import get_password_hash, create_access_token

# In-memory SQLite database
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # 1. Seed Users
    admin_user = User(
        id="admin-user-id",
        name="Sunil Verma",
        email="admin@mopng.gov.in",
        username="admin_user",
        password_hash=get_password_hash("admin123"),
        role="ADMIN",
        is_active=True
    )
    officer_user = User(
        id="officer-user-id",
        name="Rajesh Sharma",
        email="officer@mopng.gov.in",
        username="officer_user",
        password_hash=get_password_hash("officer123"),
        role="PROCUREMENT_OFFICER",
        is_active=True
    )
    bidder_a_user = User(
        id="bidder-a-user-id",
        name="Alpha Contractor",
        email="alpha@contractor.com",
        username="bidder_a",
        password_hash=get_password_hash("bidder123"),
        role="BIDDER",
        bidder_id="bidder-a-id",
        is_active=True
    )
    bidder_b_user = User(
        id="bidder-b-user-id",
        name="Beta Contractor",
        email="beta@contractor.com",
        username="bidder_b",
        password_hash=get_password_hash("bidder123"),
        role="BIDDER",
        bidder_id="bidder-b-id",
        is_active=True
    )
    db.add_all([admin_user, officer_user, bidder_a_user, bidder_b_user])
    db.commit()

    # 2. Seed Tenders (1 Draft, 1 Active)
    draft_tender = Tender(
        id="tender-draft-id",
        tender_number="MOPNG/DRAFT/001",
        title="Draft Pipeline Expansion",
        status="DRAFT",
        created_by=officer_user.id
    )
    active_tender = Tender(
        id="tender-active-id",
        tender_number="MOPNG/ACTIVE/002",
        title="Active Cross-Country Pipeline",
        status="ACTIVE",
        created_by=officer_user.id
    )
    db.add_all([draft_tender, active_tender])
    db.commit()

    # 3. Seed Bidder entities
    bidder_a = Bidder(
        id="bidder-a-id",
        tender_id="tender-active-id",
        user_id=bidder_a_user.id,
        legal_name="Alpha Pipelines Pvt Ltd",
        pan="ABCDE1234F",
        gstin="27ABCDE1234F1Z5",
        status="REGISTERED"
    )
    bidder_b = Bidder(
        id="bidder-b-id",
        tender_id="tender-active-id",
        user_id=bidder_b_user.id,
        legal_name="Beta Gas Infrastructure Ltd",
        pan="BCDEF2345G",
        gstin="27BCDEF2345G1Z6",
        status="REGISTERED"
    )
    db.add_all([bidder_a, bidder_b])
    db.commit()

    # 4. Seed Bids
    bid_a = Bid(
        id="bid-a-id",
        tender_id="tender-active-id",
        bidder_id="bidder-a-id",
        bid_reference_number="BID-ALPHA-001",
        technical_bid_status="SUBMITTED"
    )
    bid_b = Bid(
        id="bid-b-id",
        tender_id="tender-active-id",
        bidder_id="bidder-b-id",
        bid_reference_number="BID-BETA-002",
        technical_bid_status="SUBMITTED"
    )
    db.add_all([bid_a, bid_b])
    db.commit()

    # 5. Seed Documents
    doc_a = Document(
        id="doc-a-id",
        document_name="Alpha_Financials.pdf",
        original_filename="Alpha_Financials.pdf",
        file_path="/uploads/alpha.pdf",
        bidder_id="bidder-a-id",
        document_type="FINANCIAL"
    )
    doc_b = Document(
        id="doc-b-id",
        document_name="Beta_Financials.pdf",
        original_filename="Beta_Financials.pdf",
        file_path="/uploads/beta.pdf",
        bidder_id="bidder-b-id",
        document_type="FINANCIAL"
    )
    db.add_all([doc_a, doc_b])
    db.commit()

    # 6. Seed Report
    report_b = ComplianceReport(
        id="report-b-id",
        bid_id="bidder-b-id",
        tender_id="tender-active-id",
        report_number="REP-MOPNG-B-001",
        title="Technical Compliance Report - Beta",
        generated_by_id=officer_user.id
    )
    db.add(report_b)
    db.commit()

    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def auth_header(user: User):
    token = create_access_token(data={"sub": user.username, "role": user.role, "uid": user.id})
    return {"Authorization": f"Bearer {token}"}


# ==============================================================================
# 1. Unauthenticated & Tampering Security Tests
# ==============================================================================

def test_unauthenticated_requests_return_401(client):
    endpoints = [
        ("GET", "/api/users"),
        ("GET", "/api/audit/logs"),
        ("GET", "/api/settings"),
        ("POST", "/api/tenders"),
        ("POST", "/api/bids"),
        ("POST", "/api/compliance/run/bid-a-id"),
        ("POST", "/api/officer-review/bid-a-id/final-decision"),
    ]
    for method, path in endpoints:
        if method == "GET":
            res = client.get(path)
        else:
            res = client.post(path, json={})
        assert res.status_code == 401, f"{path} expected 401 but got {res.status_code}"


def test_public_registration_privilege_escalation_blocked(client, db_session):
    """
    Public registration attempting to pass role='ADMIN' must be demoted to BIDDER.
    """
    payload = {
        "name": "Malicious User",
        "email": "attacker@evil.com",
        "username": "attacker",
        "password": "password123",
        "role": "ADMIN"  # Attempt privilege escalation
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 200
    created = res.json()
    assert created["role"] == "BIDDER", "Privilege escalation allowed! Role was not forced to BIDDER"


# ==============================================================================
# 2. ADMIN Role Tests
# ==============================================================================

def test_admin_positive_permissions(client, db_session):
    admin = db_session.query(User).filter_by(username="admin_user").first()
    headers = auth_header(admin)

    # 1. User Management (CRUD)
    res = client.get("/api/users", headers=headers)
    assert res.status_code == 200

    new_user_payload = {
        "name": "Temporary User",
        "email": "temp@mopng.gov.in",
        "username": "temp_user",
        "password": "password123",
        "role": "PROCUREMENT_OFFICER"
    }
    create_res = client.post("/api/users", json=new_user_payload, headers=headers)
    assert create_res.status_code == 201
    temp_uid = create_res.json()["id"]

    patch_res = client.patch(f"/api/users/{temp_uid}", json={"is_active": False}, headers=headers)
    assert patch_res.status_code == 200
    assert patch_res.json()["is_active"] is False

    del_res = client.delete(f"/api/users/{temp_uid}", headers=headers)
    assert del_res.status_code == 200

    # 2. View all tenders, bids, bidders, audit, settings
    assert client.get("/api/tenders", headers=headers).status_code == 200
    assert client.get("/api/bidders", headers=headers).status_code == 200
    assert client.get("/api/bids", headers=headers).status_code == 200
    assert client.get("/api/audit/logs", headers=headers).status_code == 200
    assert client.get("/api/reports/bid-a-id", headers=headers).status_code == 200
    assert client.get("/api/settings", headers=headers).status_code == 200

    # Settings update
    settings_payload = {
        "scoring_weights": {"GST": 0.2, "PAN": 0.2, "TURNOVER": 0.2, "EXPERIENCE": 0.4},
        "confidence_high": 0.85,
        "confidence_medium": 0.65
    }
    settings_res = client.post("/api/settings", json=settings_payload, headers=headers)
    assert settings_res.status_code == 200


def test_admin_negative_permissions(client, db_session):
    admin = db_session.query(User).filter_by(username="admin_user").first()
    headers = auth_header(admin)

    # Admin CANNOT create tenders (Section 1: Procurement Officer creates/manages tenders; Admin cannot modify tenders)
    res_tender = client.post("/api/tenders", json={"title": "Admin Tender"}, headers=headers)
    assert res_tender.status_code == 403

    # Admin CANNOT submit bids (Admin cannot submit bids)
    res_bid = client.post("/api/bids", json={"tender_id": "tender-active-id", "bidder_id": "bidder-a-id", "bid_reference_number": "BID-ADMIN-REF"}, headers=headers)
    assert res_bid.status_code == 403

    # Admin CANNOT evaluate bids (Admin cannot evaluate bids / approve compliance)
    res_comp = client.post("/api/compliance/run/bid-a-id", headers=headers)
    assert res_comp.status_code == 403

    # Admin CANNOT submit officer review decisions (Admin cannot override AI / officer decision)
    res_dec = client.post("/api/officer-review/bid-a-id/final-decision", json={"decision": "QUALIFIED", "remarks": "Admin override attempt", "confirmed": True}, headers=headers)
    assert res_dec.status_code == 403


# ==============================================================================
# 3. PROCUREMENT_OFFICER Role Tests
# ==============================================================================

def test_officer_positive_permissions(client, db_session):
    officer = db_session.query(User).filter_by(username="officer_user").first()
    headers = auth_header(officer)

    # 1. Tender creation & publish
    tender_payload = {
        "tender_number": "MOPNG/OFFICER/001",
        "title": "Officer Created Pipeline Tender",
        "organization": "IOCL",
        "estimated_value": 45000000.0,
        "status": "DRAFT"
    }
    t_res = client.post("/api/tenders", json=tender_payload, headers=headers)
    assert t_res.status_code == 201
    new_t_id = t_res.json()["id"]

    pub_res = client.post(f"/api/tenders/{new_t_id}/publish", headers=headers)
    assert pub_res.status_code == 200

    # 2. Officer workspace, risk analysis, audit logs
    assert client.get("/api/officer-review/bid-a-id", headers=headers).status_code == 200
    assert client.get("/api/risk/bid-a-id", headers=headers).status_code == 200
    assert client.get("/api/audit/logs", headers=headers).status_code == 200

    # 3. Officer Review Decision
    dec_payload = {
        "decision": "QUALIFIED",
        "remarks": "Officer verified technical compliance according to tender specs.",
        "confirmed": True
    }
    dec_res = client.post("/api/officer-review/bid-a-id/final-decision", json=dec_payload, headers=headers)
    assert dec_res.status_code == 200

    # 4. Generate report
    rep_res = client.post("/api/reports/bid-a-id/generate", headers=headers)
    assert rep_res.status_code == 200


def test_officer_negative_permissions(client, db_session):
    officer = db_session.query(User).filter_by(username="officer_user").first()
    headers = auth_header(officer)

    # Officer CANNOT access User Management
    assert client.get("/api/users", headers=headers).status_code == 403
    assert client.post("/api/users", json={}, headers=headers).status_code == 403

    # Officer CANNOT submit bids
    res_bid = client.post("/api/bids", json={"tender_id": "tender-active-id", "bidder_id": "bidder-a-id", "bid_reference_number": "BID-OFFICER-REF"}, headers=headers)
    assert res_bid.status_code == 403

    # Officer CANNOT modify system settings
    assert client.get("/api/settings", headers=headers).status_code == 403
    assert client.post("/api/settings", json={}, headers=headers).status_code == 403


# ==============================================================================
# 4. BIDDER Role Tests
# ==============================================================================

def test_bidder_positive_permissions(client, db_session):
    bidder_a = db_session.query(User).filter_by(username="bidder_a").first()
    headers = auth_header(bidder_a)

    # 1. View active tenders
    res = client.get("/api/tenders", headers=headers)
    assert res.status_code == 200
    tenders = res.json()
    assert all(t["status"] != "DRAFT" for t in tenders), "Bidder was returned DRAFT tenders in tender catalog!"

    # 2. View own profile
    res_prof = client.get("/api/bidders/bidder-a-id", headers=headers)
    assert res_prof.status_code == 200

    # 3. Update own profile
    res_upd = client.put("/api/bidders/bidder-a-id", json={"legal_name": "Alpha Pipelines Updated Ltd"}, headers=headers)
    assert res_upd.status_code == 200

    # 4. View own bids
    res_bids = client.get("/api/bids", headers=headers)
    assert res_bids.status_code == 200
    bids = res_bids.json()
    assert all(b["bidder_id"] == "bidder-a-id" for b in bids)

    # 5. Submit bid for own company
    new_bid_payload = {
        "tender_id": "tender-active-id",
        "bidder_id": "bidder-a-id",
        "bid_reference_number": "BID-ALPHA-NEW-REF"
    }
    sub_res = client.post("/api/bids", json=new_bid_payload, headers=headers)
    assert sub_res.status_code == 201


def test_bidder_negative_permissions(client, db_session):
    bidder_a = db_session.query(User).filter_by(username="bidder_a").first()
    headers = auth_header(bidder_a)

    # Bidder CANNOT access user management
    assert client.get("/api/users", headers=headers).status_code == 403

    # Bidder CANNOT create tenders
    assert client.post("/api/tenders", json={"title": "Bidder Tender"}, headers=headers).status_code == 403

    # Bidder CANNOT view draft tenders
    assert client.get("/api/tenders/tender-draft-id", headers=headers).status_code == 403

    # Bidder CANNOT view tender bidders list
    assert client.get("/api/tenders/tender-active-id/bidders", headers=headers).status_code == 403

    # Bidder CANNOT run compliance engine
    assert client.post("/api/compliance/run/bid-a-id", headers=headers).status_code == 403

    # Bidder CANNOT access officer review workspace
    assert client.get("/api/officer-review/bid-a-id", headers=headers).status_code == 403

    # Bidder CANNOT submit officer review decisions
    assert client.post("/api/officer-review/bid-a-id/final-decision", json={"decision": "QUALIFIED", "remarks": "Bidder attempt", "confirmed": True}, headers=headers).status_code == 403

    # Bidder CANNOT view risk analysis
    assert client.get("/api/risk/bid-a-id", headers=headers).status_code == 403

    # Bidder CANNOT view audit logs
    assert client.get("/api/audit/logs", headers=headers).status_code == 403

    # Bidder CANNOT access platform settings
    assert client.get("/api/settings", headers=headers).status_code == 403

    # Bidder CANNOT access requirement dataset
    assert client.get("/api/requirements-pipeline/dataset", headers=headers).status_code == 403


# ==============================================================================
# 5. Object-Level IDOR Protection Tests (Bidder A accessing Bidder B)
# ==============================================================================

def test_bidder_cross_tenant_idor_forbidden(client, db_session):
    bidder_a = db_session.query(User).filter_by(username="bidder_a").first()
    headers = auth_header(bidder_a)

    # 1. Bidder A attempts to view Bidder B's profile
    res1 = client.get("/api/bidders/bidder-b-id", headers=headers)
    assert res1.status_code == 403
    assert res1.json()["detail"] == "Access denied."

    # 2. Bidder A attempts to edit Bidder B's profile
    res2 = client.put("/api/bidders/bidder-b-id", json={"legal_name": "Tampered Name"}, headers=headers)
    assert res2.status_code == 403
    assert res2.json()["detail"] == "Access denied."

    # 3. Bidder A attempts to view Bidder B's bid
    res3 = client.get("/api/bids/bid-b-id", headers=headers)
    assert res3.status_code == 403
    assert res3.json()["detail"] == "Access denied."

    # 4. Bidder A attempts to submit a bid pretending to be Bidder B
    res4 = client.post("/api/bids", json={"tender_id": "tender-active-id", "bidder_id": "bidder-b-id", "bid_reference_number": "BID-IDOR-REF"}, headers=headers)
    assert res4.status_code == 403
    assert res4.json()["detail"] == "Access denied."

    # 5. Bidder A attempts to view Bidder B's document chunks
    res5 = client.get("/api/documents/doc-b-id/chunks", headers=headers)
    assert res5.status_code == 403
    assert res5.json()["detail"] == "Access denied."

    # 6. Bidder A attempts to view Bidder B's compliance summary
    res6 = client.get("/api/compliance/bid-b-id/summary", headers=headers)
    assert res6.status_code == 403
    assert res6.json()["detail"] == "Access denied."

    # 7. Bidder A attempts to download/view Bidder B's report
    res7 = client.get("/api/reports/bid-b-id", headers=headers)
    assert res7.status_code == 403
    assert res7.json()["detail"] == "Access denied."

