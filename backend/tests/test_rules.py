import pytest
from app.rules import (
    TurnoverRuleEngine, LocalContentRuleEngine, OEMRuleEngine,
    BlacklistRuleEngine, CrossDocumentConsistencyEngine,
    OilGasExperienceRuleEngine, SimilarPipelineRuleEngine,
    TechnicalManpowerRuleEngine, HSESafetyRuleEngine
)

def test_turnover_rule_pass():
    entities = [
        {"entity_type": "FINANCIAL_TURNOVER", "entity_value": "FY 2022-23: ₹18.50 Cr", "normalized_value": "185000000"},
        {"entity_type": "FINANCIAL_TURNOVER", "entity_value": "FY 2023-24: ₹22.00 Cr", "normalized_value": "220000000"},
        {"entity_type": "FINANCIAL_TURNOVER", "entity_value": "FY 2024-25: ₹24.50 Cr", "normalized_value": "245000000"},
    ]
    res = TurnoverRuleEngine.evaluate(100000000.0, entities)  # Req: 10 Cr
    assert res["status"] == "PASS"
    assert res["confidence"] >= 0.95
    assert res["calculation_breakdown"]["average_cr"] == 21.67
    assert res["calculation_breakdown"]["passed"] is True

def test_turnover_rule_fail():
    entities = [
        {"entity_type": "FINANCIAL_TURNOVER", "entity_value": "FY 2022-23: ₹6.50 Cr", "normalized_value": "65000000"},
        {"entity_type": "FINANCIAL_TURNOVER", "entity_value": "FY 2023-24: ₹7.20 Cr", "normalized_value": "72000000"},
        {"entity_type": "FINANCIAL_TURNOVER", "entity_value": "FY 2024-25: ₹6.80 Cr", "normalized_value": "68000000"},
    ]
    res = TurnoverRuleEngine.evaluate(100000000.0, entities)  # Req: 10 Cr
    assert res["status"] == "FAIL"
    assert res["calculation_breakdown"]["average_cr"] == 6.83
    assert res["calculation_breakdown"]["passed"] is False

def test_oil_gas_experience_rule():
    entities = [
        {
            "entity_type": "OIL_GAS_PROJECT",
            "entity_value": "GAIL Natural Gas Transmission Pipeline",
            "context_snippet": "EPC construction of cross-country natural gas pipeline for GAIL refinery sector."
        }
    ]
    res = OilGasExperienceRuleEngine.evaluate("L&T Hydrocarbon", entities)
    assert res["status"] == "PASS"
    assert res["calculation_breakdown"]["requirement_met"] is True

def test_similar_pipeline_rule_pass_and_fail():
    # Pass: 165 km >= 100 km
    entities_pass = [
        {"entity_type": "PIPELINE_LENGTH_KM", "entity_value": "165 km", "context_snippet": "165 km 24-inch natural gas pipeline"}
    ]
    res_pass = SimilarPipelineRuleEngine.evaluate(100.0, None, entities_pass)
    assert res_pass["status"] == "PASS"
    assert res_pass["calculation_breakdown"]["max_completed_length_km"] == 165.0

    # Fail: 60 km < 100 km
    entities_fail = [
        {"entity_type": "PIPELINE_LENGTH_KM", "entity_value": "60 km", "context_snippet": "60 km spur pipeline"}
    ]
    res_fail = SimilarPipelineRuleEngine.evaluate(100.0, None, entities_fail)
    assert res_fail["status"] == "FAIL"
    assert res_fail["calculation_breakdown"]["length_shortfall_km"] == 40.0

def test_technical_manpower_rule():
    # 6 engineers with 9-14 years exp >= 5 required (min 8 yrs) -> PASS
    entities_pass = [
        {"entity_type": "MANPOWER_RECORD", "entity_value": "Rajesh Sharma (14 years)", "context_snippet": "Rajesh Sharma - 14 years experience"},
        {"entity_type": "MANPOWER_RECORD", "entity_value": "Vikram Mehta (12 years)", "context_snippet": "Vikram Mehta - 12 years experience"},
        {"entity_type": "MANPOWER_RECORD", "entity_value": "Amit Patel (10 years)", "context_snippet": "Amit Patel - 10 years experience"},
        {"entity_type": "MANPOWER_RECORD", "entity_value": "Sanjay Gupta (11 years)", "context_snippet": "Sanjay Gupta - 11 years experience"},
        {"entity_type": "MANPOWER_RECORD", "entity_value": "Dharmendra Rao (9 years)", "context_snippet": "Dharmendra Rao - 9 years experience"},
        {"entity_type": "MANPOWER_RECORD", "entity_value": "Nitin Deshmukh (10 years)", "context_snippet": "Nitin Deshmukh - 10 years experience"}
    ]
    res = TechnicalManpowerRuleEngine.evaluate(5, 8.0, entities_pass)
    assert res["status"] == "PASS"
    assert res["calculation_breakdown"]["qualifying_personnel_count"] == 6

    # 3 engineers < 5 required -> FAIL
    entities_fail = entities_pass[:3]
    res_fail = TechnicalManpowerRuleEngine.evaluate(5, 8.0, entities_fail)
    assert res_fail["status"] == "FAIL"
    assert res_fail["calculation_breakdown"]["shortfall_count"] == 2

def test_hse_safety_rule():
    entities = [
        {"entity_type": "HSE_CERTIFICATION", "entity_value": "ISO 45001", "context_snippet": "Certified ISO 45001:2018 Safety Management"},
        {"entity_type": "HSE_CERTIFICATION", "entity_value": "ISO 14001", "context_snippet": "Certified ISO 14001:2015 Environmental System"}
    ]
    res = HSESafetyRuleEngine.evaluate("L&T Hydrocarbon", entities)
    assert res["status"] == "PASS"
    assert res["calculation_breakdown"]["requirement_met"] is True

def test_local_content_rule():
    entities_pass = [{"entity_type": "LOCAL_CONTENT_PERCENT", "normalized_value": "65"}]
    res_pass = LocalContentRuleEngine.evaluate(50.0, entities_pass)
    assert res_pass["status"] == "PASS"

    entities_fail = [{"entity_type": "LOCAL_CONTENT_PERCENT", "normalized_value": "35"}]
    res_fail = LocalContentRuleEngine.evaluate(50.0, entities_fail)
    assert res_fail["status"] == "FAIL"

def test_oem_rule_name_match_and_mismatch():
    entities_match = [{
        "entity_type": "OEM_AUTHORIZATION",
        "normalized_value": "Larsen & Toubro Hydrocarbon Engineering Limited",
        "context_snippet": "Cisco authorizes Larsen & Toubro Hydrocarbon for GAIL/2026/PL-NC/4182"
    }]
    res_match = OEMRuleEngine.evaluate("Larsen & Toubro Hydrocarbon Engineering Limited", "GAIL/2026/PL-NC/4182", entities_match)
    assert res_match["status"] == "PASS"
