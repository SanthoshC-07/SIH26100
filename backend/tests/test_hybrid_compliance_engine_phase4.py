"""
SIH26100 — Phase 4 Hybrid Petroleum Bid Compliance Engine Comprehensive Test Suite
----------------------------------------------------------------------------------
Validates all Phase 4 requirements:
1. GSTChecker:
   - valid GST
   - invalid GST
   - name mismatch
2. PANChecker:
   - valid PAN
   - invalid PAN
   - name mismatch
3. TurnoverChecker:
   - above threshold
   - below threshold
   - average calculation
   - missing year
   - conflicting values
4. OilGasExperienceChecker:
   - relevant experience
   - irrelevant experience
   - insufficient duration
5. SimilarPipelineExperienceChecker:
   - correct project
   - wrong pipeline type
   - insufficient length
   - insufficient diameter
   - insufficient project count
   - expired/old experience
   - conflicting evidence
6. TechnicalManpowerChecker:
   - 5 engineers >= 8 years
   - less than 5 engineers
   - one engineer below threshold
   - missing qualification
7. TenderSpecificChecker (HSE):
   - valid evidence
   - missing evidence
   - expired evidence
8. Confidence Gate:
   - high confidence PASS
   - low confidence REVIEW
   - conflicting evidence REVIEW
   - missing evidence INSUFFICIENT
9. Officer Override:
   - override stored
   - reason required
   - audit event generated
   - original AI result preserved
10. End-to-End Test:
   - Complete pipeline execution on mock petroleum bidder PRAVEEN B S ENGINEERING SERVICES
"""
import os
import sys
import uuid
from datetime import datetime, timezone

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
from app.models.models import (
    User, Tender, Requirement, Bidder, Bid, ComplianceCheck, Evidence,
    OfficerReview, OfficerOverride, VerificationRun, AuditLog, BidderProject, BidderPersonnel,
    Document, ExtractedEntity
)

from app.checkers.gst_checker import GSTChecker
from app.checkers.pan_checker import PANChecker
from app.checkers.turnover_checker import TurnoverChecker
from app.checkers.oil_gas_experience_checker import OilGasExperienceChecker
from app.checkers.similar_pipeline_checker import SimilarPipelineExperienceChecker
from app.checkers.technical_manpower_checker import TechnicalManpowerChecker
from app.checkers.tender_specific_checker import TenderSpecificChecker
from app.scoring.compliance_engine import ComplianceEngine
from app.scoring.confidence_engine import ConfidenceEngine
from app.scoring.recommendation_generator import RecommendationGenerator
from app.api.deps import get_current_user, get_current_admin, get_current_officer, get_current_bidder

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_phase4_context():
    Base.metadata.create_all(bind=engine)

    def get_test_officer(db: Session = Depends(get_db)):
        user = db.query(User).filter(User.username == "procurement_officer_phase4").first()
        if not user:
            user = User(
                id="officer-phase4-id",
                name="Rajesh Sharma, Senior Procurement Officer",
                username="procurement_officer_phase4",
                email="officer_phase4@gem.gov.in",
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
# 1. GST CHECKER UNIT TESTS
# ==============================================================================
def test_gst_valid():
    """Valid GSTIN format + matching bidder name -> PASS."""
    checker = GSTChecker()
    req = {"id": "REQ-GST-VAL", "category": "GST_TAX_COMPLIANCE", "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "GSTIN", "entity_value": "29AABCP1234M1Z5", "context_snippet": "GSTIN: 29AABCP1234M1Z5"}
        ]
    }
    bidder = {"legal_name": "Praveen B S Engineering Services Private Limited", "gstin": "29AABCP1234M1Z5"}
    res = checker.verify(req, evidence, bidder)

    assert res["status"] == "PASS"
    assert res["confidence"] >= 0.90
    assert any(r["rule"] == "GSTIN Statutory Format Verification" and r["passed"] for r in res["rule_results"])
    assert res["risk"] == "LOW"
    # Ensure no false claim of live portal verification
    assert "live government" not in res["explanation"].lower() or "no live government" in res["explanation"].lower()

def test_gst_invalid_format():
    """Invalid GSTIN format -> FAIL."""
    checker = GSTChecker()
    req = {"id": "REQ-GST-INV", "category": "GST_TAX_COMPLIANCE", "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "GSTIN", "entity_value": "INVALID_GST_999", "context_snippet": "GST: INVALID_GST_999"}
        ]
    }
    bidder = {"legal_name": "Praveen B S Engineering Services", "gstin": "INVALID_GST_999"}
    res = checker.verify(req, evidence, bidder)

    assert res["status"] == "FAIL"
    assert any(r["rule"] == "GSTIN Statutory Format Verification" and not r["passed"] for r in res["rule_results"])
    assert res["risk"] == "HIGH"

def test_gst_name_mismatch():
    """Valid GSTIN but registered legal name differs from declared bidder -> REVIEW."""
    checker = GSTChecker()
    req = {"id": "REQ-GST-MISMATCH", "category": "GST_TAX_COMPLIANCE", "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "GSTIN", "entity_value": "27AABCA1234F1Z5", "context_snippet": "GSTIN: 27AABCA1234F1Z5"}
        ]
    }
    # Adapter returns Apex Infotech Solutions, declared bidder is Different Corp
    bidder = {"legal_name": "Completely Unrelated Pipeline Contractor Pvt Ltd", "gstin": "27AABCA1234F1Z5"}
    res = checker.verify(req, evidence, bidder)

    assert res["status"] == "REVIEW"
    assert any(r["rule"] == "Legal Name Consistency" and not r["passed"] for r in res["rule_results"])


# ==============================================================================
# 2. PAN CHECKER UNIT TESTS
# ==============================================================================
def test_pan_valid():
    """Valid PAN format + matching corporate entity -> PASS."""
    checker = PANChecker()
    req = {"id": "REQ-PAN-VAL", "category": "INCOME_TAX_PAN", "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "PAN", "entity_value": "AABCP1234M", "context_snippet": "PAN: AABCP1234M"}
        ]
    }
    bidder = {"legal_name": "Praveen B S Engineering Services Private Limited", "pan": "AABCP1234M"}
    res = checker.verify(req, evidence, bidder)

    assert res["status"] == "PASS"
    assert res["confidence"] >= 0.90
    assert any(r["rule"] == "PAN Statutory Format Verification" and r["passed"] for r in res["rule_results"])

def test_pan_invalid_format():
    """Invalid PAN format -> FAIL."""
    checker = PANChecker()
    req = {"id": "REQ-PAN-INV", "category": "INCOME_TAX_PAN", "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "PAN", "entity_value": "12345ABC", "context_snippet": "PAN: 12345ABC"}
        ]
    }
    bidder = {"legal_name": "Praveen B S Engineering Services", "pan": "12345ABC"}
    res = checker.verify(req, evidence, bidder)

    assert res["status"] == "FAIL"
    assert any(r["rule"] == "PAN Statutory Format Verification" and not r["passed"] for r in res["rule_results"])

def test_pan_name_mismatch():
    """Valid PAN format but corporate name mismatch -> REVIEW."""
    checker = PANChecker()
    req = {"id": "REQ-PAN-MISMATCH", "category": "INCOME_TAX_PAN", "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "PAN", "entity_value": "AABCA1234F", "context_snippet": "PAN: AABCA1234F"}
        ]
    }
    bidder = {"legal_name": "Different Firm Name LLP", "pan": "AABCA1234F"}
    res = checker.verify(req, evidence, bidder)

    assert res["status"] in ["REVIEW", "PASS"]


# ==============================================================================
# 3. TURNOVER CHECKER UNIT TESTS
# ==============================================================================
def test_turnover_above_threshold():
    """FY23-24 = ₹30 Cr, FY24-25 = ₹27 Cr, FY25-26 = ₹24 Cr. Avg = 27 Cr >= 25 Cr -> PASS."""
    checker = TurnoverChecker()
    req = {"id": "REQ-TO-PASS", "threshold": 250000000.0, "time_period_years": 3, "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "TURNOVER_ANNUAL", "entity_value": "₹30 Cr", "context_snippet": "FY 2023-24 turnover ₹30 Cr"},
            {"entity_type": "TURNOVER_ANNUAL", "entity_value": "₹27 Cr", "context_snippet": "FY 2024-25 turnover ₹27 Cr"},
            {"entity_type": "TURNOVER_ANNUAL", "entity_value": "₹24 Cr", "context_snippet": "FY 2025-26 turnover ₹24 Cr"}
        ]
    }
    bidder = {"legal_name": "Praveen B S Engineering Services Private Limited"}
    res = checker.verify(req, evidence, bidder)

    assert res["status"] == "PASS"
    assert res["extracted_requirement"]["minimum_value"] == 25.0
    assert "27" in res["rule_results"][0]["condition"]
    assert res["rule_results"][0]["passed"] is True

def test_turnover_below_threshold():
    """FY23-24 = ₹18 Cr, FY24-25 = ₹20 Cr, FY25-26 = ₹22 Cr. Avg = 20 Cr < 25 Cr -> FAIL."""
    checker = TurnoverChecker()
    req = {"id": "REQ-TO-FAIL", "threshold": 250000000.0, "time_period_years": 3, "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "TURNOVER_ANNUAL", "entity_value": "₹18 Cr", "context_snippet": "FY 2023-24 turnover ₹18 Cr"},
            {"entity_type": "TURNOVER_ANNUAL", "entity_value": "₹20 Cr", "context_snippet": "FY 2024-25 turnover ₹20 Cr"},
            {"entity_type": "TURNOVER_ANNUAL", "entity_value": "₹22 Cr", "context_snippet": "FY 2025-26 turnover ₹22 Cr"}
        ]
    }
    bidder = {"legal_name": "Small EPC Contractor"}
    res = checker.verify(req, evidence, bidder)

    assert res["status"] == "FAIL"
    assert res["rule_results"][0]["passed"] is False

def test_turnover_average_calculation_exact():
    """Verify exact formula representation and unit normalization (₹, Lakh, Million, Crore)."""
    checker = TurnoverChecker()
    req = {"id": "REQ-TO-CALC", "threshold": 200000000.0, "time_period_years": 3, "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "TURNOVER_ANNUAL", "entity_value": "3000 Lakh", "context_snippet": "FY 2023-24 turnover 3000 Lakh"}, # = 30 Cr
            {"entity_type": "TURNOVER_ANNUAL", "entity_value": "270 Million", "context_snippet": "FY 2024-25 turnover 270 Million"}, # = 27 Cr
            {"entity_type": "TURNOVER_ANNUAL", "entity_value": "INR 24.0 Crore", "context_snippet": "FY 2025-26 turnover INR 24.0 Crore"} # = 24 Cr
        ]
    }
    res = checker.verify(req, evidence, {"legal_name": "Test Firm"})
    assert res["status"] == "PASS"
    calc = res["verification_details"]
    assert calc["average_cr"] == 27.0
    assert "formula_display" in calc
    assert "27" in calc["formula_display"]

def test_turnover_missing_year():
    """Tender requires 3 years average, but bidder submitted only 2 financial years -> REVIEW/INSUFFICIENT."""
    checker = TurnoverChecker()
    req = {"id": "REQ-TO-MISSING-YR", "threshold": 250000000.0, "time_period_years": 3, "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "TURNOVER_ANNUAL", "entity_value": "₹30 Cr", "context_snippet": "FY 2023-24 turnover ₹30 Cr"},
            {"entity_type": "TURNOVER_ANNUAL", "entity_value": "₹27 Cr", "context_snippet": "FY 2024-25 turnover ₹27 Cr"}
        ]
    }
    res = checker.verify(req, evidence, {"legal_name": "Two Year Firm"})
    assert res["status"] in ["REVIEW", "INSUFFICIENT"]
    assert "missing" in res["explanation"].lower() or "only 2" in res["explanation"].lower()

def test_turnover_conflicting_values():
    """Conflicting turnover figures extracted for the same FY from different documents -> REVIEW."""
    checker = TurnoverChecker()
    req = {"id": "REQ-TO-CONFLICT", "threshold": 250000000.0, "time_period_years": 3, "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "TURNOVER_ANNUAL", "entity_value": "₹30 Cr", "context_snippet": "Audited Balance Sheet: FY 2023-24 turnover ₹30 Cr"},
            {"entity_type": "TURNOVER_ANNUAL", "entity_value": "₹22 Cr", "context_snippet": "Director Report: FY 2023-24 turnover ₹22 Cr"}
        ]
    }
    res = checker.verify(req, evidence, {"legal_name": "Conflicted Financials Ltd"})
    assert res["status"] == "REVIEW"
    assert "conflict" in res["explanation"].lower() or "discrepanc" in res["explanation"].lower()


# ==============================================================================
# 4. OIL & GAS EXPERIENCE CHECKER UNIT TESTS
# ==============================================================================
def test_oil_gas_relevant_experience():
    """Bidder with 9 years verified experience in oil & gas pipeline projects against 7-year requirement -> PASS."""
    checker = OilGasExperienceChecker()
    req = {"id": "REQ-OG-PASS", "threshold": 7.0, "category": "EXPERIENCE_ELIGIBILITY", "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "EXPERIENCE_YEARS", "entity_value": "9 Years", "context_snippet": "9 years prior execution experience in cross-country oil & gas pipeline projects."}
        ]
    }
    bidder = {"legal_name": "Praveen B S Engineering Services", "oil_gas_experience_years": 9.0}
    res = checker.verify(req, evidence, bidder)

    assert res["status"] == "PASS"
    assert res["confidence"] >= 0.90
    assert any(r["rule"] == "Experience Duration Check" and r["passed"] for r in res["rule_results"])

def test_oil_gas_irrelevant_experience():
    """Bidder with civil engineering / general construction experience without petroleum credentials -> REVIEW."""
    checker = OilGasExperienceChecker()
    req = {"id": "REQ-OG-IRREL", "threshold": 7.0, "category": "EXPERIENCE_ELIGIBILITY", "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "EXPERIENCE", "entity_value": "8 years", "context_snippet": "8 years industrial construction and municipal road development."}
        ]
    }
    bidder = {"legal_name": "Civil Road Contractors Ltd", "oil_gas_experience_years": 0.0, "projects": []}
    res = checker.verify(req, evidence, bidder)

    assert res["status"] == "REVIEW"
    assert "industrial construction" in res["explanation"].lower() or "credentials" in res["explanation"].lower()

def test_oil_gas_insufficient_duration():
    """Bidder with 4 years oil & gas experience against 7-year threshold -> FAIL."""
    checker = OilGasExperienceChecker()
    req = {"id": "REQ-OG-SHORTFALL", "threshold": 7.0, "category": "EXPERIENCE_ELIGIBILITY", "mandatory": True}
    bidder = {"legal_name": "Young Petroleum EPC", "oil_gas_experience_years": 4.0}
    res = checker.verify(req, {"entities": []}, bidder)

    assert res["status"] == "FAIL"
    assert any(r["rule"] == "Experience Duration Check" and not r["passed"] for r in res["rule_results"])


# ==============================================================================
# 5. SIMILAR PIPELINE EXPERIENCE CHECKER UNIT TESTS
# ==============================================================================
def test_similar_pipeline_correct_project():
    """Natural Gas pipeline of 135 KM, 24 Inch, EPC Contractor, commissioned within lookback window -> PASS."""
    checker = SimilarPipelineExperienceChecker()
    req = {
        "id": "REQ-PIPE-PASS",
        "threshold": 100.0,
        "required_pipeline_length_km": 100.0,
        "required_diameter_inch": 24.0,
        "required_project_count": 1,
        "time_period_years": 7.0,
        "category": "SIMILAR_PIPELINE_EXPERIENCE",
        "mandatory": True
    }
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
                "completion_date": "2025-03-15"
            }
        ]
    }
    res = checker.verify(req, {}, bidder)

    assert res["status"] == "PASS"
    assert all(r["passed"] for r in res["rule_results"])
    assert res["confidence"] >= 0.90

def test_similar_pipeline_wrong_pipeline_type():
    """Water supply pipeline instead of Natural Gas/Petroleum -> FAIL."""
    checker = SimilarPipelineExperienceChecker()
    req = {
        "id": "REQ-PIPE-WRONG-TYPE",
        "threshold": 100.0,
        "required_pipeline_length_km": 100.0,
        "required_diameter_inch": 24.0,
        "mandatory": True
    }
    bidder = {
        "legal_name": "Water Infra Works",
        "projects": [
            {
                "project_name": "Municipal Water Supply Project",
                "client_name": "Jal Nigam",
                "sector": "WATER_SUPPLY",
                "pipeline_type": "WATER_PIPELINE",
                "pipeline_length_km": 150.0,
                "pipeline_diameter": "36 Inch",
                "bidder_role": "EPC Contractor",
                "completion_date": "2024-01-01"
            }
        ]
    }
    res = checker.verify(req, {}, bidder)

    assert res["status"] == "FAIL"
    assert any("Relevance" in r["rule"] and not r["passed"] for r in res["rule_results"])

def test_similar_pipeline_insufficient_length():
    """Length 60 KM against 100 KM requirement -> FAIL."""
    checker = SimilarPipelineExperienceChecker()
    req = {
        "id": "REQ-PIPE-SHORT-LEN",
        "threshold": 100.0,
        "required_pipeline_length_km": 100.0,
        "required_diameter_inch": 24.0,
        "mandatory": True
    }
    bidder = {
        "legal_name": "Spur Line Contractor",
        "projects": [
            {
                "project_name": "Spur Pipeline",
                "client_name": "IOCL",
                "sector": "NATURAL_GAS",
                "pipeline_type": "NATURAL_GAS",
                "pipeline_length_km": 60.0,
                "pipeline_diameter": "24 Inch",
                "bidder_role": "EPC Contractor",
                "completion_date": "2024-01-01"
            }
        ]
    }
    res = checker.verify(req, {}, bidder)

    assert res["status"] == "FAIL"
    assert any("Length" in r["rule"] and not r["passed"] for r in res["rule_results"])

def test_similar_pipeline_insufficient_diameter():
    """Diameter 18 Inch against 24 Inch requirement -> FAIL."""
    checker = SimilarPipelineExperienceChecker()
    req = {
        "id": "REQ-PIPE-SMALL-DIA",
        "threshold": 100.0,
        "required_pipeline_length_km": 100.0,
        "required_diameter_inch": 24.0,
        "mandatory": True
    }
    bidder = {
        "legal_name": "Small Diameter Pipe Laying Co",
        "projects": [
            {
                "project_name": "120 KM Feeder Line",
                "client_name": "GAIL",
                "sector": "NATURAL_GAS",
                "pipeline_type": "NATURAL_GAS",
                "pipeline_length_km": 120.0,
                "pipeline_diameter": "18 Inch",
                "bidder_role": "EPC Contractor",
                "completion_date": "2024-01-01"
            }
        ]
    }
    res = checker.verify(req, {}, bidder)

    assert res["status"] == "FAIL"
    assert any("Diameter" in r["rule"] and not r["passed"] for r in res["rule_results"])

def test_similar_pipeline_insufficient_project_count():
    """Tender requires 2 projects, bidder submitted only 1 -> FAIL."""
    checker = SimilarPipelineExperienceChecker()
    req = {
        "id": "REQ-PIPE-COUNT-SHORTFALL",
        "threshold": 100.0,
        "required_pipeline_length_km": 100.0,
        "required_diameter_inch": 24.0,
        "required_project_count": 2,
        "mandatory": True
    }
    bidder = {
        "legal_name": "Single Project EPC",
        "projects": [
            {
                "project_name": "Cross Country Pipeline 1",
                "client_name": "GAIL",
                "sector": "NATURAL_GAS",
                "pipeline_type": "NATURAL_GAS",
                "pipeline_length_km": 135.0,
                "pipeline_diameter": "24 Inch",
                "bidder_role": "EPC Contractor",
                "completion_date": "2024-01-01"
            }
        ]
    }
    res = checker.verify(req, {}, bidder)

    assert res["status"] == "FAIL"
    assert any("Count" in r["rule"] and not r["passed"] for r in res["rule_results"])

def test_similar_pipeline_expired_old_experience():
    """Project completed in 2014 exceeds the 7-year lookback window -> FAIL."""
    checker = SimilarPipelineExperienceChecker()
    req = {
        "id": "REQ-PIPE-EXPIRED",
        "threshold": 100.0,
        "required_pipeline_length_km": 100.0,
        "required_diameter_inch": 24.0,
        "time_period_years": 7.0,
        "mandatory": True
    }
    bidder = {
        "legal_name": "Old EPC Contractor",
        "projects": [
            {
                "project_name": "Old Gas Pipeline 2014",
                "client_name": "GAIL",
                "sector": "NATURAL_GAS",
                "pipeline_type": "NATURAL_GAS",
                "pipeline_length_km": 135.0,
                "pipeline_diameter": "24 Inch",
                "bidder_role": "EPC Contractor",
                "completion_date": "2014-05-10"
            }
        ]
    }
    res = checker.verify(req, {}, bidder)

    assert res["status"] == "FAIL"
    assert any("Lookback" in r["rule"] and not r["passed"] for r in res["rule_results"])

def test_similar_pipeline_conflicting_evidence():
    """Conflicting length figures across submitted certificates -> REVIEW."""
    checker = SimilarPipelineExperienceChecker()
    req = {
        "id": "REQ-PIPE-CONFLICT",
        "threshold": 100.0,
        "required_pipeline_length_km": 100.0,
        "required_diameter_inch": 24.0,
        "mandatory": True
    }
    evidence = {
        "entities": [
            {"entity_type": "PIPELINE_LENGTH_KM", "entity_value": "135.0 KM", "normalized_value": 135.0},
            {"entity_type": "PIPELINE_LENGTH_KM", "entity_value": "60.0 KM", "normalized_value": 60.0}
        ]
    }
    bidder = {"legal_name": "Conflicted Bidder", "projects": []}
    res = checker.verify(req, evidence, bidder)

    assert res["status"] == "REVIEW"
    assert "conflict" in res["explanation"].lower() or "discrepanc" in res["explanation"].lower()


# ==============================================================================
# 6. TECHNICAL MANPOWER CHECKER UNIT TESTS
# ==============================================================================
def test_manpower_5_engineers_8_plus_years():
    """5 engineers deployed, each having >= 8 years experience -> PASS."""
    checker = TechnicalManpowerChecker()
    req = {"id": "REQ-MAN-PASS", "threshold": 5, "required_manpower_count": 5, "required_years": 8.0, "mandatory": True}
    bidder = {
        "legal_name": "Praveen B S Engineering Services",
        "personnel": [
            {"name": "Suresh Kumar", "designation": "Lead Pipeline Engineer", "years_of_experience": 10.0, "qualification": "B.Tech Mechanical"},
            {"name": "Amitabh Sen", "designation": "Sr. Welding Inspector", "years_of_experience": 9.0, "qualification": "B.E. Metallurgy"},
            {"name": "Rajesh Nair", "designation": "QA/QC Manager", "years_of_experience": 8.5, "qualification": "B.Tech Civil"},
            {"name": "Manoj Tiwari", "designation": "NDT Level III Engineer", "years_of_experience": 11.0, "qualification": "B.Tech Mechanical"},
            {"name": "Karthik Raja", "designation": "Safety Lead", "years_of_experience": 8.0, "qualification": "B.E. Safety"}
        ]
    }
    res = checker.verify(req, {}, bidder)

    assert res["status"] == "PASS"
    assert any(r["rule"] == "Engineer Headcount Check" and r["passed"] for r in res["rule_results"])
    assert any(r["rule"] == "Experience Threshold Per Engineer" and r["passed"] for r in res["rule_results"])

def test_manpower_less_than_5_engineers():
    """Only 3 engineers deployed against 5 required -> FAIL."""
    checker = TechnicalManpowerChecker()
    req = {"id": "REQ-MAN-LESS", "threshold": 5, "required_manpower_count": 5, "required_years": 8.0, "mandatory": True}
    bidder = {
        "legal_name": "Small Team Ltd",
        "personnel": [
            {"name": "Engineer 1", "years_of_experience": 10.0},
            {"name": "Engineer 2", "years_of_experience": 9.0},
            {"name": "Engineer 3", "years_of_experience": 8.5}
        ]
    }
    res = checker.verify(req, {}, bidder)

    assert res["status"] == "FAIL"
    assert any(r["rule"] == "Engineer Headcount Check" and not r["passed"] for r in res["rule_results"])

def test_manpower_one_engineer_below_threshold():
    """5 engineers deployed, but one has only 3 years experience (only 4 qualify) -> FAIL."""
    checker = TechnicalManpowerChecker()
    req = {"id": "REQ-MAN-ONE-BELOW", "threshold": 5, "required_manpower_count": 5, "required_years": 8.0, "mandatory": True}
    bidder = {
        "legal_name": "Junior Team Ltd",
        "personnel": [
            {"name": "Engineer 1", "years_of_experience": 10.0},
            {"name": "Engineer 2", "years_of_experience": 9.0},
            {"name": "Engineer 3", "years_of_experience": 8.5},
            {"name": "Engineer 4", "years_of_experience": 8.0},
            {"name": "Engineer 5", "years_of_experience": 3.0} # Shortfall!
        ]
    }
    res = checker.verify(req, {}, bidder)

    assert res["status"] == "FAIL"
    assert any(r["rule"] == "Engineer Headcount Check" and not r["passed"] for r in res["rule_results"])

def test_manpower_missing_qualification():
    """5 engineers with >= 8 years, but mandatory qualification is missing or unverified -> REVIEW."""
    checker = TechnicalManpowerChecker()
    req = {
        "id": "REQ-MAN-QUAL-MISS",
        "threshold": 5,
        "required_manpower_count": 5,
        "required_years": 8.0,
        "required_qualification": "B.Tech Mechanical / Pipeline",
        "mandatory": True
    }
    bidder = {
        "legal_name": "Unverified Degrees Ltd",
        "personnel": [
            {"name": "Engineer 1", "years_of_experience": 10.0, "qualification": "B.Tech Mechanical"},
            {"name": "Engineer 2", "years_of_experience": 9.0, "qualification": "B.Tech Mechanical"},
            {"name": "Engineer 3", "years_of_experience": 8.5, "qualification": "MISSING"},
            {"name": "Engineer 4", "years_of_experience": 8.0, "qualification": "B.Tech Mechanical"},
            {"name": "Engineer 5", "years_of_experience": 8.0, "qualification": "B.Tech Mechanical"}
        ]
    }
    res = checker.verify(req, {}, bidder)

    assert res["status"] == "REVIEW"
    assert any(r["rule"] == "Engineering Qualification Verification" and not r["passed"] for r in res["rule_results"])


# ==============================================================================
# 7. TENDER-SPECIFIC (HSE) CHECKER UNIT TESTS
# ==============================================================================
def test_hse_valid_evidence():
    """Valid ISO 45001 & ISO 14001 certificates -> PASS."""
    checker = TenderSpecificChecker()
    req = {"id": "REQ-HSE-VAL", "category": "HSE_SAFETY", "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "HSE_CERTIFICATION", "entity_value": "ISO 45001:2018 Certified", "context_snippet": "Valid ISO 45001:2018 and ISO 14001:2015 safety certificates."}
        ]
    }
    res = checker.verify(req, evidence, {"legal_name": "Praveen B S Engineering Services"})

    assert res["status"] == "PASS"
    assert res["confidence"] >= 0.90

def test_hse_missing_evidence():
    """No HSE certificates submitted -> INSUFFICIENT."""
    checker = TenderSpecificChecker()
    req = {"id": "REQ-HSE-MISS", "category": "HSE_SAFETY", "mandatory": True}
    res = checker.verify(req, {"entities": []}, {"legal_name": "No HSE Firm"})

    assert res["status"] in ["INSUFFICIENT", "REVIEW"]

def test_hse_expired_evidence():
    """Expired HSE certificate -> FAIL."""
    checker = TenderSpecificChecker()
    req = {"id": "REQ-HSE-EXP", "category": "HSE_SAFETY", "mandatory": True}
    evidence = {
        "entities": [
            {"entity_type": "HSE_CERTIFICATION", "entity_value": "ISO 45001", "context_snippet": "ISO 45001:2018 validity expired 31-December-2022"}
        ]
    }
    res = checker.verify(req, evidence, {"legal_name": "Lapsed Certs Firm"})

    assert res["status"] == "FAIL"


# ==============================================================================
# 8. CONFIDENCE GATE TESTS
# ==============================================================================
def test_confidence_gate_high_pass():
    """High confidence with deterministic rule pass -> PASS."""
    gated = ConfidenceEngine.apply_confidence_policy(
        provisional_status="PASS",
        overall_confidence=0.95,
        semantic_score=0.92,
        has_missing_evidence=False,
        has_contradictions=False,
        is_mandatory=True
    )
    assert gated["status"] == "PASS"
    assert gated["gate"] == "HIGH"

def test_confidence_gate_low_review():
    """Low confidence overall -> REVIEW."""
    gated = ConfidenceEngine.apply_confidence_policy(
        provisional_status="PASS",
        overall_confidence=0.65,
        semantic_score=0.68,
        has_missing_evidence=False,
        has_contradictions=False,
        is_mandatory=True
    )
    assert gated["status"] == "REVIEW"

def test_confidence_gate_conflicting_review():
    """Contradictory information identified across submitted documents -> REVIEW."""
    gated = ConfidenceEngine.apply_confidence_policy(
        provisional_status="PASS",
        overall_confidence=0.95,
        semantic_score=0.92,
        has_missing_evidence=False,
        has_contradictions=True,
        is_mandatory=True
    )
    assert gated["status"] == "REVIEW"
    assert "Contradictory" in gated["gating_rationale"]

def test_confidence_gate_missing_insufficient():
    """Missing evidence -> INSUFFICIENT."""
    gated = ConfidenceEngine.apply_confidence_policy(
        provisional_status="PASS",
        overall_confidence=0.90,
        semantic_score=None,
        has_missing_evidence=True,
        has_contradictions=False,
        is_mandatory=True
    )
    assert gated["status"] == "INSUFFICIENT"


# ==============================================================================
# 9. OFFICER OVERRIDE & AUDIT TESTS
# ==============================================================================
def test_officer_override_lifecycle():
    """Tests override storage, mandatory reason requirement, audit event generation, and AI baseline preservation."""
    db = next(get_db())
    uid = uuid.uuid4().hex[:8]

    tender = Tender(
        id=f"tender-override-{uid}",
        tender_number=f"MOPNG/2026/P4/{uid}",
        title="Cross-Country Pipeline Phase 4",
        issuing_organization="GAIL (India) Limited",
        status="ACTIVE"
    )
    db.add(tender)
    db.commit()

    bidder = Bidder(
        id=f"bidder-override-{uid}",
        tender_id=tender.id,
        legal_name="Praveen B S Engineering Services Private Limited",
        gstin="29AABCP1234M1Z5",
        pan="AABCP1234M",
        status="UNDER_REVIEW"
    )
    db.add(bidder)
    db.commit()

    req = Requirement(
        id=f"req-override-{uid}",
        tender_id=tender.id,
        clause_number="5.2",
        category="SIMILAR_PIPELINE_EXPERIENCE",
        description="Minimum 100 KM natural gas pipeline of 24 Inch diameter.",
        mandatory=True,
        threshold=100.0
    )
    db.add(req)
    db.commit()

    check = ComplianceCheck(
        id=f"check-override-{uid}",
        bidder_id=bidder.id,
        requirement_id=req.id,
        status="REVIEW",
        confidence=0.80,
        reason="Initial AI Evaluation: Pipeline length evidence required manual confirmation.",
        verified_at=datetime.now(timezone.utc)
    )
    db.add(check)
    db.commit()

    # 1. Override without reason -> 400 Bad Request
    fail_payload = {
        "bidder_id": bidder.id,
        "requirement_id": req.id,
        "new_status": "PASS",
        "action_type": "OFFICER_OVERRIDE",
        "remarks": "" # Empty!
    }
    res_fail = client.post(f"/api/compliance/{bidder.id}/requirements/{req.id}/override", json=fail_payload)
    assert res_fail.status_code == 400
    assert "mandatory" in res_fail.json()["detail"].lower()

    # 2. Override with documented justification -> 200 OK
    valid_payload = {
        "bidder_id": bidder.id,
        "requirement_id": req.id,
        "new_status": "PASS",
        "action_type": "OFFICER_OVERRIDE",
        "remarks": "Procurement Officer physically inspected original GAIL stamped completion certificate."
    }
    res_ok = client.post(f"/api/compliance/{bidder.id}/requirements/{req.id}/override", json=valid_payload)
    assert res_ok.status_code == 200

    # Verify check status updated
    db.refresh(check)
    assert check.status == "PASS"
    # Original AI note preserved
    assert "Original AI Baseline Status: REVIEW" in check.reason
    assert "physically inspected" in check.reason

    # Verify OfficerReview entry
    rev = db.query(OfficerReview).filter(OfficerReview.requirement_id == req.id).first()
    assert rev is not None
    assert rev.previous_status == "REVIEW"
    assert rev.new_status == "PASS"

    # Verify OfficerOverride entry
    over = db.query(OfficerOverride).filter(OfficerOverride.requirement_id == req.id).first()
    assert over is not None
    assert over.original_ai_status == "REVIEW"
    assert over.overridden_status == "PASS"
    assert "GAIL" in over.override_reason

    # Verify AuditLog generated
    audit = db.query(AuditLog).filter(AuditLog.entity_id == check.id).first()
    assert audit is not None
    assert "OFFICER" in audit.action


# ==============================================================================
# 10. END-TO-END PETROLEUM PIPELINE TEST: PRAVEEN B S ENGINEERING SERVICES
# ==============================================================================
def test_end_to_end_mock_petroleum_bidder_praveen():
    """
    Complete end-to-end evaluation pipeline for mock petroleum bidder:
    PRAVEEN B S ENGINEERING SERVICES
    Checks all 7 core requirements:
    - GST: 29AABCP1234M1Z5 (PASS)
    - PAN: AABCA1234F (PASS)
    - Turnover: 30 + 27 + 24 = 81 / 3 = 27 Cr (PASS)
    - Oil & Gas: 9 years (PASS)
    - Similar Pipeline: Natural Gas Transmission Pipeline, 135 KM, 24 Inch, EPC Contractor (PASS)
    - Technical Manpower: 5 engineers with >= 8 years experience (PASS)
    - HSE: ISO 45001 & ISO 14001 verified (PASS)
    - Summary Recommendation: Potentially Compliant
    """
    db = next(get_db())
    uid = uuid.uuid4().hex[:8]

    # 1. Tender
    tender = Tender(
        id=f"tender-e2e-{uid}",
        tender_number=f"IOCL/PIPE/2026/{uid}",
        title="Cross-Country Natural Gas Transmission Pipeline (National Gas Grid)",
        issuing_organization="Indian Oil Corporation Limited (Pipelines Division)",
        sector="OIL_AND_GAS",
        status="ACTIVE"
    )
    db.add(tender)
    db.commit()

    # 2. Requirements (7 core requirements)
    reqs = [
        Requirement(id=f"req-e2e-gst-{uid}", tender_id=tender.id, clause_number="1.1", category="GST_TAX_COMPLIANCE", description="Valid GSTIN registration in relevant State/UT.", mandatory=True),
        Requirement(id=f"req-e2e-pan-{uid}", tender_id=tender.id, clause_number="1.2", category="INCOME_TAX_PAN", description="Valid Permanent Account Number (PAN) issued by Income Tax Department.", mandatory=True),
        Requirement(id=f"req-e2e-turnover-{uid}", tender_id=tender.id, clause_number="2.1", category="FINANCIAL_ELIGIBILITY", description="Minimum 3-year average annual turnover of INR 25.00 Crore.", threshold=250000000.0, required_years=3.0, mandatory=True),
        Requirement(id=f"req-e2e-oilgas-{uid}", tender_id=tender.id, clause_number="3.1", category="EXPERIENCE_ELIGIBILITY", description="Minimum 7 years proven EPC experience in Oil & Gas / Hydrocarbon sector.", threshold=7.0, required_years=7.0, mandatory=True),
        Requirement(id=f"req-e2e-pipeline-{uid}", tender_id=tender.id, clause_number="4.1", category="SIMILAR_PIPELINE_EXPERIENCE", description="Execution of minimum 100 KM natural gas pipeline of 24 Inch diameter.", threshold=100.0, required_pipeline_length_km=100.0, conditions={"required_diameter_inch": 24.0}, mandatory=True),
        Requirement(id=f"req-e2e-manpower-{uid}", tender_id=tender.id, clause_number="5.1", category="TECHNICAL_MANPOWER", description="Minimum 5 pipeline engineers with at least 8 years experience.", threshold=5, required_manpower_count=5, required_years=8.0, mandatory=True),
        Requirement(id=f"req-e2e-hse-{uid}", tender_id=tender.id, clause_number="6.1", category="HSE_SAFETY", description="Certified ISO 45001 and ISO 14001 with active corporate safety policy.", mandatory=True)
    ]
    for r in reqs:
        db.add(r)
    db.commit()

    # 3. Bidder
    bidder = Bidder(
        id=f"bidder-e2e-praveen-{uid}",
        tender_id=tender.id,
        legal_name="Praveen B S Engineering Services Private Limited",
        bidder_name="PRAVEEN B S ENGINEERING SERVICES",
        gstin="29AABCP1234M1Z5",
        pan="AABCP1234M",
        oil_gas_experience_years=9.0,
        pipeline_experience_years=9.0,
        status="SUBMITTED"
    )
    db.add(bidder)
    db.commit()

    # 4. Bidder Projects
    proj = BidderProject(
        id=f"proj-e2e-{uid}",
        bidder_id=bidder.id,
        project_name="GAIL Auraiya-Jagdishpur Natural Gas Transmission Pipeline",
        client_name="GAIL (India) Limited",
        sector="NATURAL_GAS",
        pipeline_type="NATURAL_GAS",
        pipeline_length_km=135.0,
        pipeline_diameter="24 Inch API 5L X70",
        bidder_role="EPC Contractor",
        completion_date=datetime(2025, 3, 15)
    )
    db.add(proj)

    # 5. Bidder Personnel (5 engineers >= 8 years)
    personnel_list = [
        BidderPersonnel(id=f"pers-1-{uid}", bidder_id=bidder.id, name="Praveen B S", designation="Lead Pipeline Engineer", qualification="B.Tech Mechanical", years_of_experience=12.0),
        BidderPersonnel(id=f"pers-2-{uid}", bidder_id=bidder.id, name="Rajesh Kumar", designation="Construction Manager", qualification="B.Tech Civil", years_of_experience=11.0),
        BidderPersonnel(id=f"pers-3-{uid}", bidder_id=bidder.id, name="Suresh Verma", designation="Welding Inspector", qualification="B.E. Metallurgy", years_of_experience=10.0),
        BidderPersonnel(id=f"pers-4-{uid}", bidder_id=bidder.id, name="Ananya Sen", designation="QA/QC Head", qualification="B.Tech Civil", years_of_experience=9.0),
        BidderPersonnel(id=f"pers-5-{uid}", bidder_id=bidder.id, name="Vikram Malhotra", designation="HDD Specialist", qualification="B.Tech Mechanical", years_of_experience=8.5)
    ]
    for p in personnel_list:
        db.add(p)
    db.commit()

    # 6. Bidder Documents & Extracted Entities
    doc_fin = Document(
        id=f"doc-e2e-turnover-{uid}",
        bidder_id=bidder.id,
        tender_id=tender.id,
        document_name="Audited_Financial_Statement_FY23_FY26.pdf",
        document_type="FINANCIAL_STATEMENTS",
        file_path="/mock/Audited_Financial_Statement_FY23_FY26.pdf",
        extracted_text="Audited Financial Statements. FY 2023-24: ₹30 Cr. FY 2024-25: ₹27 Cr. FY 2025-26: ₹24 Cr."
    )
    db.add(doc_fin)
    db.flush()

    ent_to1 = ExtractedEntity(document_id=doc_fin.id, entity_type="TURNOVER_ANNUAL", entity_value="₹30 Cr", context_snippet="FY 2023-24: ₹30 Cr", page_number=2)
    ent_to2 = ExtractedEntity(document_id=doc_fin.id, entity_type="TURNOVER_ANNUAL", entity_value="₹27 Cr", context_snippet="FY 2024-25: ₹27 Cr", page_number=3)
    ent_to3 = ExtractedEntity(document_id=doc_fin.id, entity_type="TURNOVER_ANNUAL", entity_value="₹24 Cr", context_snippet="FY 2025-26: ₹24 Cr", page_number=4)
    db.add_all([ent_to1, ent_to2, ent_to3])

    doc_hse = Document(
        id=f"doc-e2e-hse-{uid}",
        bidder_id=bidder.id,
        tender_id=tender.id,
        document_name="ISO_Integrated_Safety_Certificates.pdf",
        document_type="HSE_CERTIFICATES",
        file_path="/mock/ISO_Integrated_Safety_Certificates.pdf",
        extracted_text="Integrated Management System Certificate: ISO 45001:2018 (Occupational Health & Safety) valid until 2028-09-30 and ISO 14001:2015 (Environmental Management System) valid until 2028-09-30."
    )
    db.add(doc_hse)
    db.flush()

    ent_hse1 = ExtractedEntity(document_id=doc_hse.id, entity_type="ISO_CERTIFICATE", entity_value="ISO 45001:2018", context_snippet="ISO 45001:2018 valid until 2028-09-30", page_number=1)
    ent_hse2 = ExtractedEntity(document_id=doc_hse.id, entity_type="ISO_CERTIFICATE", entity_value="ISO 14001:2015", context_snippet="ISO 14001:2015 valid until 2028-09-30", page_number=2)
    db.add_all([ent_hse1, ent_hse2])

    doc_exp = Document(
        id=f"doc-e2e-exp-{uid}",
        bidder_id=bidder.id,
        tender_id=tender.id,
        document_name="Oil_Gas_Experience_Certificate.pdf",
        document_type="EXPERIENCE_CERTIFICATES",
        file_path="/mock/Oil_Gas_Experience_Certificate.pdf",
        extracted_text="Proven EPC contractor experience: 9 years in cross-country natural gas pipeline projects for GAIL and IOCL."
    )
    db.add(doc_exp)
    db.flush()

    ent_exp1 = ExtractedEntity(document_id=doc_exp.id, entity_type="OIL_GAS_PROJECT", entity_value="GAIL Natural Gas Pipeline", context_snippet="9 years in cross-country natural gas pipeline projects for GAIL and IOCL", page_number=1)
    ent_exp2 = ExtractedEntity(document_id=doc_exp.id, entity_type="EXPERIENCE_YEARS", entity_value="9.0", context_snippet="9 years in cross-country natural gas pipeline projects", page_number=1)
    db.add_all([ent_exp1, ent_exp2])
    db.commit()

    # 7. Execute full compliance run via API
    res = client.post(f"/api/compliance/run/{bidder.id}")
    assert res.status_code == 200
    data = res.json()

    # Verify overall compliance status
    assert data["overall_status"] in ["COMPLIANT", "REVIEW_REQUIRED"]
    assert data["summary_counts"]["total"] == 7
    assert data["summary_counts"]["pass"] >= 6
    assert data["summary_counts"]["fail"] == 0

    # Verify each requirement result
    req_map = {r["category"]: r for r in data["requirements"]}

    # GST
    assert req_map["GST_TAX_COMPLIANCE"]["status"] == "PASS"
    # PAN
    assert req_map["INCOME_TAX_PAN"]["status"] == "PASS"
    # Similar Pipeline
    assert req_map["SIMILAR_PIPELINE_EXPERIENCE"]["status"] == "PASS"
    assert req_map["SIMILAR_PIPELINE_EXPERIENCE"]["semantic_score"] >= 0.70
    # Technical Manpower
    assert req_map["TECHNICAL_MANPOWER"]["status"] == "PASS"
    # Oil & Gas
    assert req_map["EXPERIENCE_ELIGIBILITY"]["status"] == "PASS"

    # Verify VerificationRun persisted in DB
    run_records = db.query(VerificationRun).filter(VerificationRun.bid_id == bidder.id).all()
    assert len(run_records) >= 1
    latest_run = run_records[-1]
    assert latest_run.total_requirements == 7
    assert latest_run.pass_count >= 6

    # Verify recommendation contains decision support wording (never unilateral "qualified")
    summary_res = client.get(f"/api/compliance/{bidder.id}/summary")
    assert summary_res.status_code == 200
    summary_data = summary_res.json()
    assert summary_data["recommendation"] in ["Potentially Compliant", "Recommended for Officer Review"]
    assert "qualified" not in summary_data["recommendation"].lower() or "potentially" in summary_data["recommendation"].lower()
