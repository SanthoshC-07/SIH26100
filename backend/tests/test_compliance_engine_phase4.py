"""
SIH26100 — Phase 4 Hybrid Petroleum Compliance Engine Test Suite
-----------------------------------------------------------------
Validates all 18 Phase 4 requirements:
1. GST valid format
2. PAN valid format
3. Turnover PASS (30 + 27 + 24 / 3 = 27 Cr >= 25 Cr)
4. Turnover FAIL (18 + 20 + 22 / 3 = 20 Cr < 25 Cr)
5. Oil & Gas experience PASS (9 years >= 7 years)
6. Oil & Gas experience FAIL (4 years < 7 years, or non-O&G generic construction)
7. Pipeline experience PASS (135 KM, 24 Inch, Natural Gas, EPC Contractor)
8. Pipeline length FAIL (60 KM < 100 KM)
9. Pipeline diameter FAIL (18 Inch < 24 Inch)
10. Wrong pipeline type (Water pipeline instead of Natural Gas)
11. Manpower PASS (5 engineers with >= 8 years experience)
12. Manpower insufficient (3 qualifying engineers < 5)
13. Missing evidence handling (INSUFFICIENT)
14. Contradictory documents (REVIEW)
15. Low-confidence semantic evidence (REVIEW)
16. Officer override audit persistence
17. Re-verification flow
18. Full bid compliance summary scorecard
"""
import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.dirname(_THIS_DIR)
_PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

import pytest
from fastapi.testclient import TestClient
from fastapi import Depends
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import Base, engine, get_db
from app.models.models import User, Tender, Requirement, Bidder, Bid, ComplianceCheck, OfficerReview

from app.checkers.gst_checker import GSTChecker
from app.checkers.pan_checker import PANChecker
from app.checkers.turnover_checker import TurnoverChecker
from app.checkers.oil_gas_experience_checker import OilGasExperienceChecker
from app.checkers.similar_pipeline_checker import SimilarPipelineExperienceChecker
from app.checkers.technical_manpower_checker import TechnicalManpowerChecker
from app.checkers.tender_specific_checker import TenderSpecificChecker
from app.scoring.compliance_engine import ComplianceEngine
from app.api.deps import get_current_user, get_current_admin, get_current_officer, get_current_bidder

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_context():
    Base.metadata.create_all(bind=engine)
    
    def get_test_officer(db: Session = Depends(get_db)):
        user = db.query(User).filter(User.username == "officer_phase4").first()
        if not user:
            user = User(
                id="officer-p4-id",
                name="Rajesh Sharma, Senior Procurement Officer",
                username="officer_phase4",
                email="officer_p4@gem.gov.in",
                password_hash="mock_hash",
                role="PROCUREMENT_OFFICER",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    app.dependency_overrides[get_current_user] = get_test_officer
    app.dependency_overrides[get_current_admin] = get_test_officer
    app.dependency_overrides[get_current_officer] = get_test_officer
    app.dependency_overrides[get_current_bidder] = get_test_officer
    yield
    app.dependency_overrides.clear()


# ==============================================================================
# TEST 1: GST Valid Format
# ==============================================================================
def test_01_gst_valid_format():
    checker = GSTChecker()
    req = {"id": "REQ-GST-01", "category": "GST_TAX_COMPLIANCE", "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "GSTIN", "entity_value": "27AABCA1234F1Z5", "context_snippet": "GSTIN: 27AABCA1234F1Z5"}
        ]
    }
    bidder = {"legal_name": "Apex Infotech Solutions Private Limited", "gstin": "27AABCA1234F1Z5"}
    res = checker.verify(req, evidence, bidder)
    
    assert res["status"] == "PASS"
    assert res["confidence"] >= 0.90
    assert len(res["rule_results"]) >= 1
    assert res["rule_results"][0]["passed"] is True
    assert res["risk"] == "LOW"


# ==============================================================================
# TEST 2: PAN Valid Format
# ==============================================================================
def test_02_pan_valid_format():
    checker = PANChecker()
    req = {"id": "REQ-PAN-01", "category": "INCOME_TAX_PAN", "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "PAN", "entity_value": "AABCA1234F", "context_snippet": "PAN: AABCA1234F"}
        ]
    }
    bidder = {"legal_name": "Praveen B S Engineering Services Private Limited", "pan": "AABCA1234F"}
    res = checker.verify(req, evidence, bidder)
    
    assert res["status"] == "PASS"
    assert res["confidence"] >= 0.90
    assert res["rule_results"][0]["passed"] is True


# ==============================================================================
# TEST 3: Turnover PASS (30 + 27 + 24 / 3 = 27 Cr >= 25 Cr)
# ==============================================================================
def test_03_turnover_pass():
    checker = TurnoverChecker()
    req = {"id": "REQ-TURNOVER-01", "threshold": 250000000.0, "category": "FINANCIAL_ELIGIBILITY", "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "TURNOVER_ANNUAL", "entity_value": "30.0 Crore", "normalized_value": 300000000.0, "context_snippet": "FY 2023-24 turnover INR 30 Crore"},
            {"entity_type": "TURNOVER_ANNUAL", "entity_value": "27.0 Crore", "normalized_value": 270000000.0, "context_snippet": "FY 2024-25 turnover INR 27 Crore"},
            {"entity_type": "TURNOVER_ANNUAL", "entity_value": "24.0 Crore", "normalized_value": 240000000.0, "context_snippet": "FY 2025-26 turnover INR 24 Crore"}
        ]
    }
    bidder = {"legal_name": "Praveen B S Engineering Services Private Limited"}
    res = checker.verify(req, evidence, bidder)
    
    assert res["status"] == "PASS"
    assert res["extracted_requirement"]["minimum_value"] == 25.0
    assert "27" in res["rule_results"][0]["condition"]
    assert res["rule_results"][0]["passed"] is True


# ==============================================================================
# TEST 4: Turnover FAIL (18 + 20 + 22 / 3 = 20 Cr < 25 Cr)
# ==============================================================================
def test_04_turnover_fail():
    checker = TurnoverChecker()
    req = {"id": "REQ-TURNOVER-02", "threshold": 250000000.0, "category": "FINANCIAL_ELIGIBILITY", "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "TURNOVER_ANNUAL", "entity_value": "18.0 Crore", "normalized_value": 180000000.0, "context_snippet": "FY 2023-24 turnover INR 18 Crore"},
            {"entity_type": "TURNOVER_ANNUAL", "entity_value": "20.0 Crore", "normalized_value": 200000000.0, "context_snippet": "FY 2024-25 turnover INR 20 Crore"},
            {"entity_type": "TURNOVER_ANNUAL", "entity_value": "22.0 Crore", "normalized_value": 220000000.0, "context_snippet": "FY 2025-26 turnover INR 22 Crore"}
        ]
    }
    bidder = {"legal_name": "Small Infra EPC Ltd"}
    res = checker.verify(req, evidence, bidder)
    
    assert res["status"] == "FAIL"
    assert res["rule_results"][0]["passed"] is False
    assert res["risk"] == "HIGH"


# ==============================================================================
# TEST 5: Oil & Gas Experience PASS (9 years >= 7 years)
# ==============================================================================
def test_05_oil_gas_experience_pass():
    checker = OilGasExperienceChecker()
    req = {"id": "REQ-OG-01", "threshold": 7.0, "category": "EXPERIENCE_ELIGIBILITY", "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "EXPERIENCE_YEARS", "entity_value": "9 Years", "normalized_value": 9.0, "context_snippet": "9 years prior execution experience in cross-country oil & gas pipeline projects for GAIL and IOCL."}
        ]
    }
    bidder = {"legal_name": "Praveen B S Engineering Services", "oil_gas_experience_years": 9.0}
    res = checker.verify(req, evidence, bidder)
    
    assert res["status"] == "PASS"
    assert res["rule_results"][1]["passed"] is True
    assert res["risk"] == "LOW"


# ==============================================================================
# TEST 6: Oil & Gas Experience FAIL (4 years < 7 years, or non-O&G generic construction)
# ==============================================================================
def test_06_oil_gas_experience_fail():
    checker = OilGasExperienceChecker()
    req = {"id": "REQ-OG-02", "threshold": 7.0, "category": "EXPERIENCE_ELIGIBILITY", "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "EXPERIENCE_YEARS", "entity_value": "4 Years", "normalized_value": 4.0, "context_snippet": "4 years prior execution experience in refinery piping."}
        ]
    }
    bidder = {"legal_name": "Junior Pipeline Contractor", "oil_gas_experience_years": 4.0}
    res = checker.verify(req, evidence, bidder)
    
    assert res["status"] == "FAIL"
    assert res["rule_results"][1]["passed"] is False


# ==============================================================================
# TEST 7: Pipeline Experience PASS (135 KM, 24 Inch, Natural Gas)
# ==============================================================================
def test_07_pipeline_experience_pass():
    checker = SimilarPipelineExperienceChecker()
    req = {
        "id": "REQ-PIPE-01",
        "threshold": 100.0,
        "required_pipeline_length_km": 100.0,
        "required_diameter_inch": 24.0,
        "category": "SIMILAR_PIPELINE_EXPERIENCE",
        "description": "At least one natural gas pipeline project of minimum 100 KM and 24 Inch diameter within last 7 years.",
        "mandatory": True
    }
    evidence = {"entities": []}
    bidder = {
        "legal_name": "Praveen B S Engineering Services Private Limited",
        "projects": [
            {
                "project_name": "GAIL Auraiya-Jagdishpur Natural Gas Pipeline",
                "client_name": "GAIL (India) Limited",
                "sector": "NATURAL_GAS",
                "pipeline_type": "NATURAL_GAS",
                "pipeline_length_km": 135.0,
                "pipeline_diameter": "24-inch NB",
                "bidder_role": "EPC Contractor",
                "evidence_document_id": "doc-proj-001"
            }
        ]
    }
    res = checker.verify(req, evidence, bidder)
    
    assert res["status"] == "PASS"
    assert res["rule_results"][0]["passed"] is True # Length 135 >= 100
    assert res["rule_results"][1]["passed"] is True # Diameter 24 >= 24
    assert res["rule_results"][2]["passed"] is True # Natural gas type match


# ==============================================================================
# TEST 8: Pipeline Length FAIL (60 KM < 100 KM)
# ==============================================================================
def test_08_pipeline_length_fail():
    checker = SimilarPipelineExperienceChecker()
    req = {
        "id": "REQ-PIPE-02",
        "threshold": 100.0,
        "required_pipeline_length_km": 100.0,
        "required_diameter_inch": 24.0,
        "category": "SIMILAR_PIPELINE_EXPERIENCE",
        "mandatory": True
    }
    bidder = {
        "legal_name": "Indus Gas Grid EPC",
        "projects": [
            {
                "project_name": "State Gas Grid Spur Line",
                "client_name": "Gujarat Gas",
                "sector": "NATURAL_GAS",
                "pipeline_type": "NATURAL_GAS",
                "pipeline_length_km": 60.0,
                "pipeline_diameter": "24-inch",
                "bidder_role": "EPC Contractor"
            }
        ]
    }
    res = checker.verify(req, {}, bidder)
    
    assert res["status"] == "FAIL"
    assert res["rule_results"][0]["passed"] is False # 60 < 100


# ==============================================================================
# TEST 9: Pipeline Diameter FAIL (18 Inch < 24 Inch)
# ==============================================================================
def test_09_pipeline_diameter_fail():
    checker = SimilarPipelineExperienceChecker()
    req = {
        "id": "REQ-PIPE-03",
        "threshold": 100.0,
        "required_pipeline_length_km": 100.0,
        "required_diameter_inch": 24.0,
        "category": "SIMILAR_PIPELINE_EXPERIENCE",
        "mandatory": True
    }
    bidder = {
        "legal_name": "Small Diameter Pipe Laying Co",
        "projects": [
            {
                "project_name": "120 KM Distribution Line",
                "client_name": "IOCL",
                "sector": "NATURAL_GAS",
                "pipeline_type": "NATURAL_GAS",
                "pipeline_length_km": 120.0,
                "pipeline_diameter": "18 Inch",
                "bidder_role": "EPC Contractor"
            }
        ]
    }
    res = checker.verify(req, {}, bidder)
    
    assert res["status"] == "FAIL"
    assert res["rule_results"][1]["passed"] is False # 18 < 24


# ==============================================================================
# TEST 10: Wrong Pipeline Type (Water pipeline instead of Natural Gas)
# ==============================================================================
def test_10_wrong_pipeline_type_fail():
    checker = SimilarPipelineExperienceChecker()
    req = {
        "id": "REQ-PIPE-04",
        "threshold": 100.0,
        "required_pipeline_length_km": 100.0,
        "required_diameter_inch": 24.0,
        "category": "SIMILAR_PIPELINE_EXPERIENCE",
        "mandatory": True
    }
    bidder = {
        "legal_name": "Civil Water Infra Works",
        "projects": [
            {
                "project_name": "Municipal Potable Water Supply Pipeline",
                "client_name": "Jal Nigam",
                "sector": "WATER_SUPPLY",
                "pipeline_type": "WATER_PIPELINE",
                "pipeline_length_km": 150.0,
                "pipeline_diameter": "36 Inch",
                "bidder_role": "EPC Contractor"
            }
        ]
    }
    res = checker.verify(req, {}, bidder)
    
    assert res["status"] == "FAIL"
    assert res["rule_results"][2]["passed"] is False # Type mismatch


# ==============================================================================
# TEST 11: Manpower PASS (5 engineers with >= 8 years experience)
# ==============================================================================
def test_11_manpower_pass():
    checker = TechnicalManpowerChecker()
    req = {"id": "REQ-MAN-01", "threshold": 5, "required_manpower_count": 5, "required_years": 8.0, "category": "TECHNICAL_MANPOWER", "mandatory": True}
    bidder = {
        "legal_name": "Praveen B S Engineering Services",
        "personnel": [
            {"name": "Suresh Kumar", "designation": "Lead Pipeline Engineer", "years_of_experience": 10.0},
            {"name": "Amitabh Sen", "designation": "Sr. Welding Inspector", "years_of_experience": 9.0},
            {"name": "Rajesh Nair", "designation": "QA/QC Manager", "years_of_experience": 8.5},
            {"name": "Manoj Tiwari", "designation": "NDT Level III Engineer", "years_of_experience": 11.0},
            {"name": "Karthik Raja", "designation": "Safety Lead", "years_of_experience": 8.0}
        ]
    }
    res = checker.verify(req, {}, bidder)
    
    assert res["status"] == "PASS"
    assert res["rule_results"][0]["passed"] is True
    assert res["cross_document_consistency"]["unique_engineers_evaluated"] == 5


# ==============================================================================
# TEST 12: Manpower Insufficient (3 qualifying engineers < 5)
# ==============================================================================
def test_12_manpower_insufficient_fail():
    checker = TechnicalManpowerChecker()
    req = {"id": "REQ-MAN-02", "threshold": 5, "required_manpower_count": 5, "required_years": 8.0, "category": "TECHNICAL_MANPOWER", "mandatory": True}
    bidder = {
        "legal_name": "Small Tech Team Ltd",
        "personnel": [
            {"name": "Engineer 1", "designation": "Engineer", "years_of_experience": 10.0},
            {"name": "Engineer 2", "designation": "Engineer", "years_of_experience": 9.0},
            {"name": "Engineer 3", "designation": "Junior Engineer", "years_of_experience": 3.0}
        ]
    }
    res = checker.verify(req, {}, bidder)
    
    assert res["status"] == "FAIL"
    assert res["rule_results"][0]["passed"] is False


# ==============================================================================
# TEST 13: Missing Evidence Handling (INSUFFICIENT)
# ==============================================================================
def test_13_missing_evidence_handling():
    req = {
        "id": "REQ-MISSING-01",
        "category": "SAFETY_REGULATORY_COMPLIANCE",
        "description": "Valid OISD-141 Emergency Preparedness Standard Audit Certification.",
        "mandatory": True
    }
    bidder = {"legal_name": "Empty Documentation Corp", "extracted_entities": []}
    
    res = ComplianceEngine.verify_requirement(req, {}, bidder)
    assert res["status"] in ["REVIEW", "INSUFFICIENT", "FAIL"]
    assert res["risk"] in ["HIGH", "MEDIUM"]


# ==============================================================================
# TEST 14: Contradictory Documents (REVIEW)
# ==============================================================================
def test_14_contradictory_documents_review():
    checker = SimilarPipelineExperienceChecker()
    req = {"id": "REQ-PIPE-AMB", "threshold": 100.0, "category": "SIMILAR_PIPELINE_EXPERIENCE", "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "SCOPE", "entity_value": "City gas infrastructure", "context_snippet": "City gas infrastructure execution work."}
        ]
    }
    bidder = {"legal_name": "Ambiguous Gas Works", "projects": []}
    res = checker.verify(req, evidence, bidder)
    
    assert res["status"] == "REVIEW"
    assert res["risk"] == "MEDIUM"


# ==============================================================================
# TEST 15: Low-Confidence Semantic Evidence (REVIEW)
# ==============================================================================
def test_15_low_confidence_semantic_evidence():
    checker = OilGasExperienceChecker()
    req = {"id": "REQ-OG-AMB", "threshold": 7.0, "category": "EXPERIENCE_ELIGIBILITY", "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "EXPERIENCE", "entity_value": "5 years", "context_snippet": "5 years civil engineering and general industrial construction."}
        ]
    }
    bidder = {"legal_name": "Civil Contractor", "oil_gas_experience_years": 0.0}
    res = checker.verify(req, evidence, bidder)
    
    assert res["status"] == "REVIEW"
    assert "industrial construction" in res["explanation"].lower() or "credentials" in res["explanation"].lower()


# ==============================================================================
# TEST 16: Officer Override Audit Persistence
# ==============================================================================
def test_16_officer_override_audit():
    # Setup test bidder and requirement in database
    db = next(get_db())
    tender = db.query(Tender).first()
    if not tender:
        tender = Tender(
            id="tender-p4-test",
            tender_number="GAIL/P4/2026/001",
            title="Cross-Country Natural Gas Pipeline",
            client_authority="GAIL (India) Limited",
            status="PUBLISHED"
        )
        db.add(tender)
        db.commit()

    bidder = db.query(Bidder).filter(Bidder.tender_id == tender.id).first()
    if not bidder:
        bidder = Bidder(
            id="bidder-p4-praveen",
            tender_id=tender.id,
            legal_name="Praveen B S Engineering Services Private Limited",
            bidder_name="Praveen B S Engineering Services",
            gstin="27AABCA1234F1Z5",
            pan="AABCA1234F",
            status="UNDER_REVIEW"
        )
        db.add(bidder)
        db.commit()

    req = db.query(Requirement).filter(Requirement.tender_id == tender.id).first()
    if not req:
        req = Requirement(
            id="req-p4-pipeline",
            tender_id=tender.id,
            clause_number="4.1.1",
            category="SIMILAR_PIPELINE_EXPERIENCE",
            description="Minimum 100 KM natural gas pipeline of 24 Inch diameter.",
            mandatory=True,
            threshold=100.0,
            threshold_unit="KM"
        )
        db.add(req)
        db.commit()

    # Call override endpoint
    payload = {
        "bidder_id": bidder.id,
        "requirement_id": req.id,
        "new_status": "PASS",
        "action_type": "OFFICER_OVERRIDE",
        "remarks": "Procurement Officer verified original stamped completion certificate from GAIL."
    }
    res = client.post(f"/api/compliance/{bidder.id}/requirements/{req.id}/override", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["new_status"] == "PASS"
    assert "GAIL" in data["remarks"]


# ==============================================================================
# TEST 17: Re-verification Flow
# ==============================================================================
def test_17_reverification_flow():
    db = next(get_db())
    bidder = db.query(Bidder).first()
    req = db.query(Requirement).first()
    assert bidder is not None
    assert req is not None

    res = client.post(f"/api/compliance/{bidder.id}/requirements/{req.id}/reverify")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "confidence" in data
    assert "rule_results" in data


# ==============================================================================
# TEST 18: Full Bid Compliance Summary Scorecard
# ==============================================================================
def test_18_full_bid_compliance_summary_scorecard():
    db = next(get_db())
    bidder = db.query(Bidder).first()
    assert bidder is not None

    res = client.get(f"/api/compliance/{bidder.id}/summary")
    assert res.status_code == 200
    data = res.json()
    
    assert "compliance_score" in data
    assert "summary_counts" in data
    assert "risk_level" in data
    assert "cross_document_consistency" in data
    assert data["summary_counts"]["total"] >= 1
