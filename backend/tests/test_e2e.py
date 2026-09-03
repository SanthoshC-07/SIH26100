import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_e2e_four_petroleum_pipeline_bidders_evaluation():
    # 1. Fetch bidders
    res = client.get("/api/bidders")
    assert res.status_code == 200
    bidders = res.json()
    assert len(bidders) >= 4

    b1 = next((b for b in bidders if "Larsen" in b["bidder_name"]), None)
    b2 = next((b for b in bidders if "Indus" in b["bidder_name"]), None)
    b3 = next((b for b in bidders if "PetroCon" in b["bidder_name"]), None)
    b4 = next((b for b in bidders if "Vanguard" in b["bidder_name"]), None)

    assert b1 is not None
    assert b2 is not None
    assert b3 is not None
    assert b4 is not None

    # Bidder 1: Fully Compliant (LOW RISK, Score >= 95)
    detail1 = client.get(f"/api/bidders/{b1['id']}").json()
    assert detail1["compliance_score_detail"]["overall_score"] >= 95.0
    assert detail1["risk_assessment_detail"]["risk_level"] == "LOW"
    assert detail1["recommendation_detail"]["recommendation_type"] == "RECOMMENDED_FOR_QUALIFICATION"

    # Bidder 2: Pipeline Length and Turnover Shortfall (HIGH/CRITICAL RISK)
    detail2 = client.get(f"/api/bidders/{b2['id']}").json()
    assert detail2["risk_assessment_detail"]["risk_level"] in ["HIGH", "CRITICAL"]
    turnover_check = next((c for c in detail2["compliance_checks"] if c["requirement_category"] == "TURNOVER"), None)
    assert turnover_check is not None
    assert turnover_check["status"] == "FAIL"
    pipeline_check = next((c for c in detail2["compliance_checks"] if "PIPELINE" in c["requirement_category"]), None)
    assert pipeline_check is not None
    assert pipeline_check["status"] == "FAIL"

    # Bidder 3: Medium Risk / Review (PetroCon - 95 km CGD / affiliate)
    detail3 = client.get(f"/api/bidders/{b3['id']}").json()
    assert detail3["compliance_score_detail"]["overall_score"] >= 75.0

    # Bidder 4: Critical Risk (Vanguard - Debarment / Identity Mismatch)
    detail4 = client.get(f"/api/bidders/{b4['id']}").json()
    assert detail4["risk_assessment_detail"]["risk_level"] == "CRITICAL"
