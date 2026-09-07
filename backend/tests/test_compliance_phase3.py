import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, Base, engine
from app.models.models import Tender, Requirement, Bidder, Document
from app.checkers import (
    GSTChecker,
    PANChecker,
    TurnoverChecker,
    OilGasExperienceChecker,
    SimilarPipelineExperienceChecker,
    TechnicalManpowerChecker,
    TenderSpecificChecker,
    get_checker_for_category
)
from app.scoring.confidence_engine import ConfidenceEngine
from app.scoring.compliance_engine import ComplianceEngine
from app.rules.cross_document_rule import CrossDocumentConsistencyEngine

def test_1_gst_checker_valid_and_invalid():
    gst_checker = GSTChecker()
    req = {"category": "GST", "mandatory": True, "description": "Valid active GSTIN required"}
    
    # Valid GST
    bidder_valid = {"legal_name": "PRAVEEN B S ENGINEERING SERVICES", "gstin": "29MOCKP1234M1Z5"}
    evidence_valid = {
        "entities": [
            {"entity_type": "GSTIN", "entity_value": "29MOCKP1234M1Z5", "page_number": 1, "document_name": "GST_Certificate.pdf"}
        ]
    }
    res_valid = gst_checker.verify(req, evidence_valid, bidder_valid)
    assert res_valid["status"] == "PASS"
    assert res_valid["confidence"] >= 0.90
    assert "29MOCKP1234M1Z5" in str(res_valid["evidence"]) or "29MOCKP1234M1Z5" in res_valid["explanation"]
    assert res_valid["source_document"] == "GST_Certificate.pdf"
    assert res_valid["page_number"] == 1

    # Missing GST
    res_missing = gst_checker.verify(req, {"entities": []}, {"legal_name": "Unknown Corp", "gstin": ""})
    assert res_missing["status"] == "FAIL"

def test_2_pan_checker_valid_and_invalid():
    pan_checker = PANChecker()
    req = {"category": "PAN", "mandatory": True, "description": "Valid corporate PAN card"}
    
    bidder_valid = {"legal_name": "PRAVEEN B S ENGINEERING SERVICES", "pan": "BSZPP1234K"}
    evidence_valid = {
        "entities": [
            {"entity_type": "PAN", "entity_value": "BSZPP1234K", "page_number": 1, "document_name": "PAN_Card.pdf"}
        ]
    }
    res_valid = pan_checker.verify(req, evidence_valid, bidder_valid)
    assert res_valid["status"] == "PASS"
    assert "BSZPP1234K" in str(res_valid["rule_results"]) or "BSZPP1234K" in res_valid["explanation"]

def test_3_turnover_checker_arithmetic_average_and_breakdown():
    turnover_checker = TurnoverChecker()
    req = {"category": "TURNOVER", "mandatory": True, "threshold": 250000000.0} # 25 Cr
    
    # Pass case: 30, 27, 24 Cr -> average 27 Cr >= 25 Cr
    evidence_pass = {
        "entities": [
            {"entity_type": "FINANCIAL_TURNOVER", "entity_value": "FY 2023-24: ₹30.00 Cr", "normalized_value": 300000000, "page_number": 2, "document_name": "Financial_Statements.pdf"},
            {"entity_type": "FINANCIAL_TURNOVER", "entity_value": "FY 2024-25: ₹27.00 Cr", "normalized_value": 270000000, "page_number": 2, "document_name": "Financial_Statements.pdf"},
            {"entity_type": "FINANCIAL_TURNOVER", "entity_value": "FY 2025-26: ₹24.00 Cr", "normalized_value": 240000000, "page_number": 2, "document_name": "Financial_Statements.pdf"}
        ]
    }
    res_pass = turnover_checker.verify(req, evidence_pass, {"legal_name": "PRAVEEN B S"})
    assert res_pass["status"] == "PASS"
    assert res_pass["rule_results"][0]["passed"] is True
    assert "27" in res_pass["rule_results"][0]["condition"]
    assert res_pass["page_number"] == 2

    # Fail case: 15, 14, 13 Cr -> average 14 Cr < 25 Cr
    evidence_fail = {
        "entities": [
            {"entity_type": "FINANCIAL_TURNOVER", "entity_value": "FY 2023-24: ₹15.00 Cr", "normalized_value": 150000000},
            {"entity_type": "FINANCIAL_TURNOVER", "entity_value": "FY 2024-25: ₹14.00 Cr", "normalized_value": 140000000},
            {"entity_type": "FINANCIAL_TURNOVER", "entity_value": "FY 2025-26: ₹13.00 Cr", "normalized_value": 130000000}
        ]
    }
    res_fail = turnover_checker.verify(req, evidence_fail, {"legal_name": "Underfunded Bidder"})
    assert res_fail["status"] == "FAIL"
    assert res_fail["rule_results"][0]["passed"] is False

def test_4_oil_gas_experience_checker_years_and_semantic_relevance():
    oil_gas_checker = OilGasExperienceChecker()
    req = {"category": "OIL_GAS_EXPERIENCE", "mandatory": True, "threshold": 7.0} # 7 years
    
    # Valid Oil & Gas experience (9 years >= 7 years)
    bidder_pass = {
        "legal_name": "PRAVEEN B S ENGINEERING SERVICES",
        "oil_gas_experience_years": 9.0,
        "projects": [
            {"project_name": "GAIL Natural Gas Pipeline", "sector": "OIL_AND_GAS", "project_value": 820000000}
        ]
    }
    evidence_pass = {
        "entities": [
            {"entity_type": "OIL_GAS_PROJECT", "entity_value": "Natural Gas Transmission EPC", "context_snippet": "9 years proven execution in petroleum and natural gas pipeline laying."}
        ]
    }
    res_pass = oil_gas_checker.verify(req, evidence_pass, bidder_pass)
    assert res_pass["status"] == "PASS"
    assert res_pass["rule_results"][0]["passed"] is True or res_pass["rule_results"][1]["passed"] is True

    # Ambiguous industrial construction without petroleum relevance -> REVIEW
    evidence_ambiguous = {
        "entities": [
            {"entity_type": "EXPERIENCE", "entity_value": "Industrial Construction Experience", "context_snippet": "Extensive industrial construction experience and civil building works."}
        ]
    }
    res_ambiguous = oil_gas_checker.verify(req, evidence_ambiguous, {"legal_name": "Civil Contractors Ltd", "oil_gas_experience_years": 0.0})
    assert res_ambiguous["status"] == "REVIEW"
    assert "industrial construction" in res_ambiguous["explanation"].lower()

def test_5_similar_pipeline_checker_sentence_transformers_and_numerical_rule():
    pipeline_checker = SimilarPipelineExperienceChecker()
    req = {
        "category": "SIMILAR_PIPELINE_EXPERIENCE",
        "mandatory": True,
        "threshold": 100.0, # 100 KM
        "description": "Execution of minimum 100 KM natural gas cross-country pipeline (24-inch OD API 5L X70)."
    }
    
    # Pass case: 135 KM Natural gas pipeline
    bidder_pass = {
        "legal_name": "PRAVEEN B S ENGINEERING SERVICES",
        "projects": [
            {
                "project_name": "GAIL Natural Gas Transmission Pipeline",
                "client_name": "GAIL (India) Limited",
                "pipeline_length_km": 135.0,
                "pipeline_diameter": "24-inch NB API 5L X70",
                "bidder_role": "EPC Contractor"
            }
        ]
    }
    evidence_pass = {
        "entities": [
            {"entity_type": "PIPELINE_LENGTH_KM", "entity_value": "135 KM", "normalized_value": 135.0, "page_number": 4, "context_snippet": "Successfully commissioned 135 KM natural gas pipeline."}
        ]
    }
    res_pass = pipeline_checker.verify(req, evidence_pass, bidder_pass)
    assert res_pass["status"] == "PASS"
    assert res_pass["page_number"] == 4
    assert res_pass["semantic_score"] >= 0.70
    assert "135" in str(res_pass["rule_results"])

    # Shortfall case: 60 KM < 100 KM -> FAIL
    bidder_shortfall = {
        "legal_name": "Short Pipeline Bidder",
        "projects": [
            {"project_name": "Short Feeder Spur", "pipeline_length_km": 60.0, "client_name": "IOCL"}
        ]
    }
    evidence_shortfall = {
        "entities": [
            {"entity_type": "PIPELINE_LENGTH_KM", "entity_value": "60 KM", "normalized_value": 60.0, "page_number": 1, "context_snippet": "Completed 60 KM feeder line."}
        ]
    }
    res_shortfall = pipeline_checker.verify(req, evidence_shortfall, bidder_shortfall)
    assert res_shortfall["status"] == "FAIL"

def test_6_technical_manpower_checker_engineer_count():
    manpower_checker = TechnicalManpowerChecker()
    req = {"category": "TECHNICAL_MANPOWER", "mandatory": True, "threshold": 5, "required_years": 8.0}
    
    # Pass: 5 engineers with >= 8 years
    bidder_pass = {
        "personnel": [
            {"name": "Praveen B S", "designation": "Project Engineer", "years_of_experience": 12.0},
            {"name": "Ravi Kumar", "designation": "Pipeline Engineer", "years_of_experience": 11.0},
            {"name": "Suresh Sharma", "designation": "Welding Specialist", "years_of_experience": 10.0},
            {"name": "Ananya Rao", "designation": "QA/QC Inspector", "years_of_experience": 9.0},
            {"name": "Vikram Patel", "designation": "Safety Officer", "years_of_experience": 9.0}
        ]
    }
    res_pass = manpower_checker.verify(req, {}, bidder_pass)
    assert res_pass["status"] == "PASS"
    assert res_pass["rule_results"][0]["passed"] is True

    # Fail: only 3 engineers with >= 8 years
    bidder_fail = {
        "personnel": [
            {"name": "Eng 1", "years_of_experience": 10.0},
            {"name": "Eng 2", "years_of_experience": 9.0},
            {"name": "Eng 3", "years_of_experience": 8.0},
            {"name": "Junior Eng 4", "years_of_experience": 3.0}
        ]
    }
    res_fail = manpower_checker.verify(req, {}, bidder_fail)
    assert res_fail["status"] == "FAIL"
    assert res_fail["rule_results"][0]["passed"] is False

def test_7_hse_safety_checker():
    hse_checker = TenderSpecificChecker()
    req = {"category": "HSE_SAFETY", "mandatory": True}
    
    evidence_pass = {
        "entities": [
            {"entity_type": "CERTIFICATION", "entity_value": "ISO 45001:2018", "context_snippet": "Certified ISO 45001 and ISO 14001 with zero-fatality site safety policy."}
        ]
    }
    res_pass = hse_checker.verify(req, evidence_pass, {"legal_name": "PRAVEEN B S"})
    assert res_pass["status"] == "PASS"

def test_8_oem_authorization_checker():
    oem_checker = TenderSpecificChecker()
    req = {"category": "OEM_AUTHORIZATION", "mandatory": True}
    
    evidence_pass = {
        "entities": [
            {"entity_type": "OEM_AUTHORIZATION", "entity_value": "Welspun Corp Limited", "context_snippet": "Authorized supplier of API 5L line pipes."}
        ]
    }
    res_pass = oem_checker.verify(req, evidence_pass, {"legal_name": "PRAVEEN B S"})
    assert res_pass["status"] == "PASS"

def test_9_local_content_percentage_checker():
    local_checker = TenderSpecificChecker()
    req = {"category": "LOCAL_CONTENT", "mandatory": True, "threshold": 50.0}
    
    evidence_pass = {
        "entities": [
            {"entity_type": "LOCAL_CONTENT_DECLARATION", "entity_value": "65%", "normalized_value": 65.0, "context_snippet": "Class-I Local Supplier declaring 65% domestic local content."}
        ]
    }
    res_pass = local_checker.verify(req, evidence_pass, {"legal_name": "PRAVEEN B S"})
    assert res_pass["status"] == "PASS"
    assert "65% >= 50%" in str(res_pass["rule_results"]) or "65" in str(res_pass["rule_results"])

def test_10_cross_document_consistency_matcher():
    # Consistent tokens
    res_pass = CrossDocumentConsistencyEngine.evaluate(
        bidder_name="PRAVEEN B S ENGINEERING SERVICES",
        claimed_gstin="29MOCKP1234M1Z5",
        claimed_pan="BSZPP1234K",
        extracted_entities=[
            {"entity_type": "GSTIN", "entity_value": "29MOCKP1234M1Z5"},
            {"entity_type": "PAN", "entity_value": "BSZPP1234K"},
            {"entity_type": "COMPANY_NAME", "entity_value": "PRAVEEN B S ENGINEERING SERVICES"}
        ]
    )
    assert res_pass["status"] == "PASS"

    # Mismatch in PAN embedded in GSTIN
    res_mismatch = CrossDocumentConsistencyEngine.evaluate(
        bidder_name="PRAVEEN B S ENGINEERING SERVICES",
        claimed_gstin="29MOCKP1234M1Z5",
        claimed_pan="DIFFERENT99K",
        extracted_entities=[
            {"entity_type": "PAN", "entity_value": "DIFFERENT99K"}
        ]
    )
    assert res_mismatch["status"] == "REVIEW"

def test_11_confidence_engine_and_gating():
    conf_data = ConfidenceEngine.calculate_confidence(
        rule_confidence=0.98,
        semantic_confidence=0.94,
        evidence_confidence=0.92,
        consistency_confidence=0.98
    )
    assert conf_data["overall_confidence"] >= 0.90
    assert conf_data["confidence_gate"] == "HIGH"

    # Gating check for missing evidence
    gated = ConfidenceEngine.apply_confidence_policy(
        provisional_status="PASS",
        overall_confidence=0.90,
        has_missing_evidence=True
    )
    assert gated["status"] == "INSUFFICIENT"

def test_12_mandatory_failure_not_masked_by_average_score():
    # Tender with 7 requirements, where 6 pass and 1 mandatory fails
    requirements = [
        {"id": "R01", "category": "GST", "mandatory": True},
        {"id": "R02", "category": "PAN", "mandatory": True},
        {"id": "R03", "category": "TURNOVER", "mandatory": True, "threshold": 250000000.0},
        {"id": "R04", "category": "OIL_GAS_EXPERIENCE", "mandatory": True, "threshold": 7.0},
        {"id": "R05", "category": "SIMILAR_PIPELINE_EXPERIENCE", "mandatory": True, "threshold": 100.0},
        {"id": "R06", "category": "TECHNICAL_MANPOWER", "mandatory": True, "threshold": 5},
        {"id": "R07", "category": "HSE_SAFETY", "mandatory": True}
    ]
    
    # Bidder with deficient pipeline length (60 km vs 100 km)
    bidder = {
        "id": "bidder-failing-mandatory",
        "legal_name": "Deficient Bidder Ltd",
        "gstin": "29MOCKP1234M1Z5",
        "pan": "BSZPP1234K",
        "oil_gas_experience_years": 9.0,
        "projects": [
            {"project_name": "Short pipeline", "pipeline_length_km": 60.0, "client_name": "IOCL"}
        ],
        "personnel": [
            {"name": f"Engineer {i}", "years_of_experience": 10.0} for i in range(5)
        ]
    }
    
    evidence_by_req = {
        "GST": {"entities": [{"entity_type": "GSTIN", "entity_value": "29MOCKP1234M1Z5"}]},
        "PAN": {"entities": [{"entity_type": "PAN", "entity_value": "BSZPP1234K"}]},
        "TURNOVER": {"entities": [{"entity_type": "FINANCIAL_TURNOVER", "entity_value": "FY 2023-24: ₹30 Cr", "normalized_value": 300000000}]},
        "OIL_GAS_EXPERIENCE": {"entities": [{"entity_type": "OIL_GAS_PROJECT", "entity_value": "Oil & Gas EPC", "context_snippet": "9 years petroleum experience"}]},
        "SIMILAR_PIPELINE_EXPERIENCE": {"entities": [{"entity_type": "PIPELINE_LENGTH_KM", "entity_value": "60 KM", "normalized_value": 60.0}]},
        "TECHNICAL_MANPOWER": {},
        "HSE_SAFETY": {"entities": [{"entity_type": "CERTIFICATION", "entity_value": "ISO 45001"}]}
    }
    
    eval_res = ComplianceEngine.evaluate_bidder(
        tender={"id": "t1", "tender_number": "MOPNG/PIPE/2026/017"},
        bidder=bidder,
        requirements=requirements,
        evidence_by_req=evidence_by_req
    )
    
    # Overall status MUST be NON_COMPLIANT despite high numerical subscores
    assert eval_res["overall_status"] == "NON_COMPLIANT"
    assert eval_res["mandatory_compliance"] is False
    assert any(c["status"] == "FAIL" for c in eval_res["requirements"])

def test_13_praveen_bs_full_compliance_evaluation():
    # Praveen B S meets all MoPNG Natural Gas Pipeline criteria
    requirements = [
        {"id": "R01", "category": "GST", "mandatory": True},
        {"id": "R02", "category": "PAN", "mandatory": True},
        {"id": "R03", "category": "TURNOVER", "mandatory": True, "threshold": 250000000.0},
        {"id": "R04", "category": "OIL_GAS_EXPERIENCE", "mandatory": True, "threshold": 7.0},
        {"id": "R05", "category": "SIMILAR_PIPELINE_EXPERIENCE", "mandatory": True, "threshold": 100.0},
        {"id": "R06", "category": "TECHNICAL_MANPOWER", "mandatory": True, "threshold": 5},
        {"id": "R07", "category": "HSE_SAFETY", "mandatory": True}
    ]
    
    bidder_praveen = {
        "id": "bidder-praveen-bs",
        "legal_name": "PRAVEEN B S ENGINEERING SERVICES",
        "gstin": "29MOCKP1234M1Z5",
        "pan": "BSZPP1234K",
        "oil_gas_experience_years": 9.0,
        "pipeline_experience_years": 9.0,
        "projects": [
            {
                "project_name": "GAIL Natural Gas Transmission Pipeline",
                "client_name": "GAIL (India) Limited",
                "pipeline_length_km": 135.0,
                "pipeline_diameter": "24-inch NB API 5L X70",
                "project_value": 820000000,
                "bidder_role": "EPC Contractor"
            }
        ],
        "personnel": [
            {"name": "Praveen B S", "designation": "Project Engineer", "years_of_experience": 12.0},
            {"name": "Ravi Kumar", "designation": "Pipeline Engineer", "years_of_experience": 11.0},
            {"name": "Suresh Sharma", "designation": "Welding Specialist", "years_of_experience": 10.0},
            {"name": "Ananya Rao", "designation": "QA/QC Inspector", "years_of_experience": 9.0},
            {"name": "Vikram Patel", "designation": "Safety Officer", "years_of_experience": 9.0}
        ]
    }
    
    evidence_by_req = {
        "GST": {"entities": [{"entity_type": "GSTIN", "entity_value": "29MOCKP1234M1Z5", "page_number": 1, "document_name": "GST_Certificate.pdf"}]},
        "PAN": {"entities": [{"entity_type": "PAN", "entity_value": "BSZPP1234K", "page_number": 1, "document_name": "PAN_Card.pdf"}]},
        "TURNOVER": {"entities": [
            {"entity_type": "FINANCIAL_TURNOVER", "entity_value": "FY 2023-24: ₹30.00 Cr", "normalized_value": 300000000, "page_number": 2, "document_name": "Financial_Statement.pdf"},
            {"entity_type": "FINANCIAL_TURNOVER", "entity_value": "FY 2024-25: ₹27.00 Cr", "normalized_value": 270000000, "page_number": 2, "document_name": "Financial_Statement.pdf"},
            {"entity_type": "FINANCIAL_TURNOVER", "entity_value": "FY 2025-26: ₹24.00 Cr", "normalized_value": 240000000, "page_number": 2, "document_name": "Financial_Statement.pdf"}
        ]},
        "OIL_GAS_EXPERIENCE": {"entities": [{"entity_type": "OIL_GAS_PROJECT", "entity_value": "Natural Gas Transmission", "context_snippet": "9 years proven petroleum EPC execution", "page_number": 3, "document_name": "Experience_Cert.pdf"}]},
        "SIMILAR_PIPELINE_EXPERIENCE": {"entities": [{"entity_type": "PIPELINE_LENGTH_KM", "entity_value": "135 KM", "normalized_value": 135.0, "page_number": 4, "document_name": "Pipeline_Completion_Cert.pdf"}]},
        "TECHNICAL_MANPOWER": {},
        "HSE_SAFETY": {"entities": [{"entity_type": "CERTIFICATION", "entity_value": "ISO 45001:2018", "context_snippet": "ISO 45001 & ISO 14001 zero fatality", "page_number": 5, "document_name": "HSE_Policy.pdf"}]}
    }
    
    eval_res = ComplianceEngine.evaluate_bidder(
        tender={"id": "t1", "tender_number": "MOPNG/PIPE/2026/017"},
        bidder=bidder_praveen,
        requirements=requirements,
        evidence_by_req=evidence_by_req
    )
    
    assert eval_res["overall_status"] == "COMPLIANT"
    assert eval_res["mandatory_compliance"] is True
    assert eval_res["compliance_score"] >= 85.0
    assert eval_res["summary_counts"]["pass"] == 7
    assert eval_res["summary_counts"]["fail"] == 0

def test_14_compliance_api_endpoints():
    client = TestClient(app)
    db = SessionLocal()
    
    # Ensure a test tender and bidder exist
    tender = db.query(Tender).first()
    if not tender:
        tender = Tender(
            id="test-tender-mopng",
            tender_number="MOPNG/TEST/2026/01",
            title="Test Pipeline Procurement",
            status="ACTIVE"
        )
        db.add(tender)
        db.commit()

    # Ensure a requirement exists
    req = db.query(Requirement).filter(Requirement.tender_id == tender.id).first()
    if not req:
        req = Requirement(
            id="test-req-turnover",
            tender_id=tender.id,
            clause_number="R03",
            category="TURNOVER",
            description="Minimum average annual turnover of INR 25 Crore",
            mandatory=True,
            threshold=250000000.0,
            threshold_unit="INR"
        )
        db.add(req)
        db.commit()

    bidder = db.query(Bidder).filter(Bidder.tender_id == tender.id).first()
    if not bidder:
        bidder = Bidder(
            id="test-bidder-api",
            tender_id=tender.id,
            legal_name="PRAVEEN B S ENGINEERING SERVICES",
            bidder_name="Praveen B S",
            gstin="29MOCKP1234M1Z5",
            pan="BSZPP1234K",
            status="SUBMITTED"
        )
        db.add(bidder)
        db.commit()

    bidder_id = bidder.id
    
    from app.models.models import User
    from app.core.security import create_access_token
    officer_user = db.query(User).filter(User.role == "PROCUREMENT_OFFICER").first()
    if not officer_user:
        officer_user = User(
            id="test-officer-compliance",
            username="test_officer_comp",
            email="officer_comp@oilgas.gov.in",
            hashed_password="mock",
            role="PROCUREMENT_OFFICER",
            is_active=True
        )
        db.add(officer_user)
        db.commit()
    token = create_access_token(data={"sub": officer_user.username, "role": officer_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    db.close()
    
    # 1. POST /api/compliance/run/{bid_id}
    res_run = client.post(f"/api/compliance/run/{bidder_id}", headers=headers)
    assert res_run.status_code == 200
    data_run = res_run.json()
    assert data_run["bidder_id"] == bidder_id
    assert "overall_status" in data_run
    assert len(data_run["requirements"]) >= 1

    # 2. GET /api/compliance/{bid_id}
    res_get = client.get(f"/api/compliance/{bidder_id}", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["bidder_id"] == bidder_id

    # 3. GET /api/compliance/{bid_id}/requirements
    res_reqs = client.get(f"/api/compliance/{bidder_id}/requirements", headers=headers)
    assert res_reqs.status_code == 200
    assert isinstance(res_reqs.json(), list)

    # 4. GET /api/compliance/{bid_id}/summary
    res_summary = client.get(f"/api/compliance/{bidder_id}/summary", headers=headers)
    assert res_summary.status_code == 200
    assert "overall_status" in res_summary.json()
    assert "summary_counts" in res_summary.json()


