import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import Base, get_db
from app.models.models import User, Tender, Bidder
from app.core.security import get_password_hash, create_access_token

# Use in-memory SQLite with StaticPool for testing RBAC
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    # Create 3 users
    admin = User(
        name="Admin User",
        email="admin@test.gov.in",
        username="admin_test",
        password_hash=get_password_hash("pass"),
        role="ADMIN"
    )
    officer = User(
        name="Officer User",
        email="officer@test.gov.in",
        username="officer_test",
        password_hash=get_password_hash("pass"),
        role="PROCUREMENT_OFFICER"
    )
    bidder = User(
        name="Bidder User",
        email="bidder@test.com",
        username="bidder_test",
        password_hash=get_password_hash("pass"),
        role="BIDDER"
    )
    session.add_all([admin, officer, bidder])
    session.commit()
    session.refresh(admin)
    session.refresh(officer)
    session.refresh(bidder)
    
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def get_auth_header(username: str, role: str, uid: str = "test-uid"):
    token = create_access_token(data={"sub": username, "role": role, "uid": uid})
    return {"Authorization": f"Bearer {token}"}

def test_officer_can_create_tender(client, db):
    officer_headers = get_auth_header("officer_test", "PROCUREMENT_OFFICER")
    payload = {
        "tender_number": "MOPNG/TEST/2026/001",
        "title": "Test Pipeline Tender Construction",
        "estimated_value": 50000000.0,
        "status": "ACTIVE"
    }
    res = client.post("/api/tenders", json=payload, headers=officer_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["tender_number"] == "MOPNG/TEST/2026/001"

def test_admin_and_bidder_cannot_create_tender(client, db):
    admin_headers = get_auth_header("admin_test", "ADMIN")
    bidder_headers = get_auth_header("bidder_test", "BIDDER")
    
    payload = {
        "tender_number": "MOPNG/TEST/2026/002",
        "title": "Unauthorized Tender Creation Attempt",
        "status": "ACTIVE"
    }
    res_admin = client.post("/api/tenders", json=payload, headers=admin_headers)
    assert res_admin.status_code == 403

    res_bidder = client.post("/api/tenders", json=payload, headers=bidder_headers)
    assert res_bidder.status_code == 403

def test_bidder_can_view_live_tenders_and_apply(client, db):
    bidder_headers = get_auth_header("bidder_test", "BIDDER")
    
    # 1. Bidder can list live tenders
    tenders_res = client.get("/api/tenders", headers=bidder_headers)
    assert tenders_res.status_code == 200
    tenders = tenders_res.json()
    assert len(tenders) >= 1
    tender_id = tenders[0]["id"]
    
    # 2. Bidder can apply
    bidder_payload = {
        "tender_id": tender_id,
        "legal_name": "Test Pipeline EPC Contractor Ltd",
        "pan": "ABCDE1234F",
        "gstin": "29ABCDE1234F1Z5",
        "status": "SUBMITTED"
    }
    app_res = client.post("/api/bidders", json=bidder_payload, headers=bidder_headers)
    assert app_res.status_code == 200
    bidder_data = app_res.json()
    assert bidder_data["legal_name"] == "Test Pipeline EPC Contractor Ltd"
    assert "id" in bidder_data

def test_officer_cannot_apply_as_bidder(client, db):
    officer_headers = get_auth_header("officer_test", "PROCUREMENT_OFFICER")
    tenders_res = client.get("/api/tenders", headers=officer_headers)
    tender_id = tenders_res.json()[0]["id"]
    
    bidder_payload = {
        "tender_id": tender_id,
        "legal_name": "Officer Trying to Bid",
        "pan": "XYZPA9999K",
        "gstin": "29XYZPA9999K1Z5"
    }
    res = client.post("/api/bidders", json=bidder_payload, headers=officer_headers)
    assert res.status_code == 403

def test_officer_has_selecting_authority(client, db):
    officer_headers = get_auth_header("officer_test", "PROCUREMENT_OFFICER")
    bidder = db.query(Bidder).first()
    assert bidder is not None
    
    selecting_payload = {
        "decision": "ELIGIBLE",
        "remarks": "Bidder satisfies all technical criteria and minimum turnover requirement.",
        "statutory_rule": "GFR 2017 Rule 173",
        "technical_score": 95.0,
        "financial_cleared": True
    }
    res = client.post(f"/api/bidders/{bidder.id}/selecting-authority", json=selecting_payload, headers=officer_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["decision"] == "ELIGIBLE"
    assert data["status"] == "ELIGIBLE"

def test_bidder_cannot_exercise_selecting_authority(client, db):
    bidder_headers = get_auth_header("bidder_test", "BIDDER")
    bidder = db.query(Bidder).first()
    assert bidder is not None
    
    selecting_payload = {
        "decision": "QUALIFIED",
        "remarks": "Bidder attempting self-qualification"
    }
    res = client.post(f"/api/bidders/{bidder.id}/selecting-authority", json=selecting_payload, headers=bidder_headers)
    assert res.status_code == 403
