import pytest
from app.scoring import ComplianceScorer, RiskEngine, RecommendationGenerator

def test_compliance_scoring():
    checks = [
        {"requirement_category": "GST", "status": "PASS"},
        {"requirement_category": "PAN", "status": "PASS"},
        {"requirement_category": "UDYAM", "status": "PASS"},
        {"requirement_category": "TURNOVER", "status": "PASS"},
        {"requirement_category": "LOCAL_CONTENT", "status": "PASS"},
        {"requirement_category": "OEM", "status": "PASS"},
        {"requirement_category": "BLACKLISTING", "status": "PASS"},
    ]
    score = ComplianceScorer.calculate_score(checks)
    assert score["overall_score"] == 100.0
    assert score["statutory_score"] == 100.0
    assert score["financial_score"] == 100.0

def test_risk_classification():
    # Low Risk
    checks_pass = [
        {"requirement_category": "GST", "status": "PASS"},
        {"requirement_category": "TURNOVER", "status": "PASS"},
        {"requirement_category": "BLACKLISTING", "status": "PASS"}
    ]
    risk_low = RiskEngine.assess_risk(checks_pass, 98.0)
    assert risk_low["risk_level"] == "LOW"

    # High Risk on mandatory failure
    checks_fail = [
        {"requirement_category": "GST", "status": "PASS"},
        {"requirement_category": "TURNOVER", "status": "FAIL", "requirement_mandatory": True, "reason": "Shortfall in turnover"},
        {"requirement_category": "BLACKLISTING", "status": "PASS"}
    ]
    risk_high = RiskEngine.assess_risk(checks_fail, 65.0)
    assert risk_high["risk_level"] == "HIGH"

    # Critical Risk on Blacklist
    checks_blacklist = [
        {"requirement_category": "BLACKLISTING", "status": "FAIL", "reason": "Debarred entity"}
    ]
    risk_critical = RiskEngine.assess_risk(checks_blacklist, 40.0)
    assert risk_critical["risk_level"] == "CRITICAL"

def test_ai_recommendation():
    checks_pass = [{"requirement_category": "GST", "status": "PASS"}]
    rec = RecommendationGenerator.generate_recommendation("Apex", checks_pass, 98.0, "LOW")
    assert rec["recommendation_type"] == "RECOMMENDED_FOR_QUALIFICATION"
