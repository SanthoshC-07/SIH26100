import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.models import User, Bidder
from app.api.deps import (
    get_current_user, get_current_admin, get_current_officer,
    get_current_officer_only, get_current_bidder
)

from app.core.database import SessionLocal, engine, Base

client = TestClient(app)

from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

@pytest.fixture(autouse=True)
def setup_auth():
    from seed_data import seed
    seed()

    db = SessionLocal()
    officer_user = db.query(User).filter(User.role == "PROCUREMENT_OFFICER").first()
    if not officer_user:
        officer_user = User(
            id="officer-test-id",
            name="Rajesh Sharma, Senior Procurement Officer",
            username="procurement_officer",
            email="officer@gem.gov.in",
            password_hash="dummy_hash_for_test",
            role="PROCUREMENT_OFFICER",
            is_active=True
        )
        db.add(officer_user)
        db.commit()
    db.close()

    def _get_test_officer(db_session: Session = Depends(get_db)):
        return db_session.query(User).filter(User.role == "PROCUREMENT_OFFICER").first()

    app.dependency_overrides[get_current_user] = _get_test_officer
    app.dependency_overrides[get_current_admin] = _get_test_officer
    app.dependency_overrides[get_current_officer] = _get_test_officer
    app.dependency_overrides[get_current_officer_only] = _get_test_officer
    app.dependency_overrides[get_current_bidder] = _get_test_officer
    yield
    app.dependency_overrides.clear()

def test_e2e_five_petroleum_pipeline_bidders_evaluation():
    # 1. Fetch bidders
    res = client.get("/api/bidders")
    assert res.status_code == 200
    bidders = res.json()
    assert len(bidders) >= 5

    b1 = next((b for b in bidders if "PRAVEEN" in b.get("legal_name", "").upper()), None)
    b2 = next((b for b in bidders if "LARSEN" in b.get("legal_name", "").upper()), None)
    b3 = next((b for b in bidders if "APEX" in b.get("legal_name", "").upper()), None)
    b4 = next((b for b in bidders if "ZENITH" in b.get("legal_name", "").upper()), None)
    b5 = next((b for b in bidders if "BHARAT" in b.get("legal_name", "").upper()), None)

    assert b1 is not None
    assert b2 is not None
    assert b3 is not None
    assert b4 is not None
    assert b5 is not None

    # Bidder 1: PASS / QUALIFIED (Score >= 80)
    detail1 = client.get(f"/api/bidders/{b1['id']}").json()
    score1 = detail1.get("compliance_score") or (detail1.get("compliance_score_detail") or {}).get("overall_score", 0.0)
    risk1 = detail1.get("risk_level") or (detail1.get("risk_assessment_detail") or {}).get("risk_level")
    assert score1 >= 80.0
    assert risk1 in ["LOW", "MEDIUM"]

    # Bidder 2: PASS / QUALIFIED (Score >= 80)
    detail2 = client.get(f"/api/bidders/{b2['id']}").json()
    score2 = detail2.get("compliance_score") or (detail2.get("compliance_score_detail") or {}).get("overall_score", 0.0)
    risk2 = detail2.get("risk_level") or (detail2.get("risk_assessment_detail") or {}).get("risk_level")
    assert score2 >= 80.0
    assert risk2 in ["LOW", "MEDIUM"]

    # Bidder 3: FAIL / DISQUALIFIED (Apex - Turnover Shortfall & Cancelled GSTIN)
    detail3 = client.get(f"/api/bidders/{b3['id']}").json()
    assert detail3["status"] == "DISQUALIFIED"
    turnover_check = next((c for c in detail3["compliance_checks"] if c["requirement_category"] == "TURNOVER"), None)
    assert turnover_check is not None
    assert turnover_check["status"] == "FAIL"

    # Bidder 4: FAIL / DISQUALIFIED (Zenith - ISO 45001 & Non-Gas Pipe)
    detail4 = client.get(f"/api/bidders/{b4['id']}").json()
    assert detail4["status"] == "DISQUALIFIED"

    # Bidder 5: IN REVIEW / UNDER_EVALUATION (Bharat - JV Review)
    detail5 = client.get(f"/api/bidders/{b5['id']}").json()
    assert detail5["status"] == "UNDER_REVIEW"

def test_officer_review_override_commit():
    res = client.get("/api/bidders")
    assert res.status_code == 200
    bidders = res.json()
    b = bidders[0]
    detail = client.get(f"/api/bidders/{b['id']}").json()
    checks = detail.get("compliance_checks", [])
    assert len(checks) > 0
    check = checks[0]

    # Submit Officer Override
    review_payload = {
        "bidder_id": b["id"],
        "requirement_id": check.get("requirement_id"),
        "action_type": "OFFICER_OVERRIDE",
        "new_status": "PASS",
        "remarks": "Officer verified via physical audited statement per Section 4 GFR 2017."
    }
    rev_res = client.post(f"/api/compliance/{check['id']}/review", json=review_payload)
    assert rev_res.status_code == 200, f"Error: {rev_res.text}"
    data = rev_res.json()
    assert data["new_status"] == "PASS"
    assert "OFFICER_OVERRIDE" in data["action_type"]
    assert "Officer verified" in data["remarks"]
