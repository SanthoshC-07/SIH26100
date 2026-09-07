import pytest
from app.documents.requirement_extractors import (
    FinancialEligibilityExtractor,
    SimilarPipelineExtractor,
    TechnicalManpowerExtractor,
    OilGasExperienceExtractor,
    HSESafetyExtractor,
    GSTRegistrationExtractor,
    PANCardExtractor,
    RequirementExtractorRegistry
)
from app.checkers.technical_manpower_checker import TechnicalManpowerChecker
from app.checkers.turnover_checker import TurnoverChecker
from app.checkers.similar_pipeline_checker import SimilarPipelineExperienceChecker
from app.checkers.oil_gas_experience_checker import OilGasExperienceChecker
from app.checkers.tender_specific_checker import TenderSpecificChecker


def test_req_003_extracts_financial_fields():
    text = """
    AUDITED FINANCIAL STATEMENTS & CA CERTIFICATE
    Company: Praveen B S Engineering Services
    PAN: BSZPP1234K
    Turnover FY 2023-24: INR 30.00 Crore
    Turnover FY 2024-25: INR 27.00 Crore
    Turnover FY 2025-26: INR 24.00 Crore
    Average Annual Turnover: INR 27.00 Crore
    Chartered Accountant: M/s Raman & Associates
    UDIN: 24078912AAAAAB1234
    We confirm that the books of accounts have been duly audited.
    """
    res = FinancialEligibilityExtractor.extract_from_text(text, doc_name="03_Audited_Financial_Statements.pdf", doc_id="doc-fin-01")
    assert res["requirement_id"] == "REQ-003"
    assert res["category"] == "FINANCIAL_ELIGIBILITY"
    data = res["data"]
    assert len(data["turnover_values"]) >= 3
    assert data["average_turnover"] == 27.0
    assert data["ca_certificate_present"] is True
    assert data["udin"] == "24078912AAAAAB1234"
    assert data["pan"] == "BSZPP1234K"

    # Check fields schema
    fields = {f["field"]: f for f in res["fields"]}
    assert "average_turnover" in fields
    assert fields["average_turnover"]["value"] == 27.0
    assert fields["average_turnover"]["source"] == "03_Audited_Financial_Statements.pdf"
    assert fields["average_turnover"]["detected"] is True
    assert "udin" in fields
    assert fields["udin"]["value"] == "24078912AAAAAB1234"


def test_req_004_extracts_pipeline_fields():
    text = """
    PROJECT COMPLETION CERTIFICATE
    Client: GAIL (India) Limited
    Contractor: Praveen B S Engineering Services (EPC Contractor)
    Scope: Laying and commissioning of 156.0 KM cross country high pressure natural gas transmission pipeline
    Diameter: 24 Inch OD (API 5L X70)
    Work Order No: WO/GAIL/2021/8871
    Project Value: INR 82.50 Crore
    Date of Commencement: 01-04-2022
    Date of Completion: 15-03-2025
    Certificate: Pipeline has been successfully commissioned and handed over.
    """
    res = SimilarPipelineExtractor.extract_from_text(text, doc_name="04_Similar_Pipeline_Experience.pdf", doc_id="doc-pipe-01")
    assert res["requirement_id"] == "REQ-004"
    assert res["category"] == "SIMILAR_PIPELINE_EXPERIENCE"
    data = res["data"]
    assert data["length_km"] == 156.0
    assert data["diameter_inch"] == 24.0
    assert data["pipeline_type"] == "Natural Gas Transmission"
    assert data["completion_date"] == "15-03-2025"
    assert data["bidder_role"] == "EPC Contractor"
    assert data["completion_certificate_present"] is True

    # Check source metadata
    fields = {f["field"]: f for f in res["fields"]}
    assert fields["length_km"]["value"] == 156.0
    assert fields["length_km"]["source"] == "04_Similar_Pipeline_Experience.pdf"
    assert fields["length_km"]["confidence"] >= 0.90


def test_req_005_extracts_manpower_fields_and_no_pipeline_length():
    text = """
    TECHNICAL MANPOWER AND KEY ENGINEERING PERSONNEL
    1. Rajesh Sharma - Lead Pipeline Engineer - B.Tech Mechanical - 12 Years Experience (Pipeline EPC)
    2. Amit Patel - Senior Welding & NDT Inspector - BE Metallurgy - 9 Years Experience
    3. Sunil Rao - Project Construction Manager - B.Tech Civil - 10 Years Experience
    4. Vikram Sen - Senior QA/QC Pipeline Engineer - B.Tech Mechanical - 11 Years Experience
    5. Deepa Nair - Corrosion & Integrity Engineer - M.Tech Chemical - 8 Years Experience
    All detailed CVs and university degree certificates are attached herewith.
    """
    res = TechnicalManpowerExtractor.extract_from_text(text, doc_name="05_Technical_Manpower_CVs.pdf", doc_id="doc-manpower-01")
    assert res["requirement_id"] == "REQ-005"
    assert res["category"] == "TECHNICAL_MANPOWER"
    data = res["data"]
    assert data["engineer_count"] >= 5
    assert len(data["engineers"]) >= 5
    assert data["cv_present"] is True

    # Verify that NO pipeline length, diameter, or turnover fields exist in REQ-005
    fields = {f["field"]: f for f in res["fields"]}
    assert "length_km" not in fields
    assert "diameter_inch" not in fields
    assert "turnover" not in fields
    assert "gstin" not in fields
    assert "engineer_count" in fields
    assert fields["engineer_count"]["source"] == "05_Technical_Manpower_CVs.pdf"


def test_req_006_extracts_oil_gas_experience():
    text = """
    CORPORATE SECTOR EXPERIENCE SUMMARY
    Company: Praveen B S Engineering Services
    Verified Total Track Record: 9.0 Years in Oil & Gas and Hydrocarbon Sector
    Projects Executed:
    - Cross-Country High Pressure Hydrocarbon Pipeline EPC for GAIL
    - City Gas Distribution (CGD) Steel Network for IOCL
    - Refinery Interconnecting Pipeline for HPCL
    Role: Main EPC Contractor
    """
    res = OilGasExperienceExtractor.extract_from_text(text, doc_name="06_Oil_Gas_Experience_Certificate.pdf", doc_id="doc-oilgas-01")
    assert res["requirement_id"] == "REQ-006"
    assert res["category"] == "OIL_GAS_EXPERIENCE"
    data = res["data"]
    assert data["oil_gas_experience_years"] == 9.0
    assert data["sector"] == "OIL_AND_GAS"

    fields = {f["field"]: f for f in res["fields"]}
    assert fields["oil_gas_experience_years"]["value"] == 9.0
    assert fields["oil_gas_experience_years"]["source"] == "06_Oil_Gas_Experience_Certificate.pdf"


def test_req_007_extracts_hse_safety_fields():
    text = """
    HEALTH, SAFETY & ENVIRONMENTAL (HSE) CERTIFICATE & POLICY
    Company: Praveen B S Engineering Services
    ISO 45001:2018 Occupational Health and Safety Management System (Cert No: ISO-45001-2018-IND)
    ISO 14001:2015 Environmental Management System (Cert No: ISO-14001-2015-IND)
    Issue Date: 10-01-2023 | Valid Until: 09-01-2026
    Corporate Safety Policy: Zero fatality, zero lost time injuries record maintained for past 3 consecutive years.
    """
    res = HSESafetyExtractor.extract_from_text(text, doc_name="07_HSE_and_Safety_Policy.pdf", doc_id="doc-hse-01")
    assert res["requirement_id"] == "REQ-007"
    assert res["category"] == "HSE_SAFETY"
    data = res["data"]
    assert data["iso_45001"] is True
    assert data["iso_14001"] is True
    assert data["hse_policy_present"] is True
    assert data["zero_fatality_statement"] is True
    assert "09-01-2026" in str(data["valid_until"])

    fields = {f["field"]: f for f in res["fields"]}
    assert fields["iso_45001"]["value"] is True
    assert fields["iso_45001"]["source"] == "07_HSE_and_Safety_Policy.pdf"


def test_req_005_never_receives_pipeline_length_from_req_004():
    """Test requirement isolation: Manpower checker with pipeline text does not leak pipeline length."""
    manpower_doc_text = """
    KEY PERSONNEL CVs
    Rajesh Sharma - 10 Years Experience - Pipeline Engineer
    Amit Patel - 8 Years Experience - Mechanical Engineer
    Sunil Rao - 9 Years Experience - QA/QC Engineer
    Vikram Sen - 8 Years Experience - NDT Inspector
    Deepa Nair - 8 Years Experience - Safety Officer
    """
    # Simulate mixed entity payload that contains pipeline length from another document
    entities = [
        {"entity_type": "PIPELINE_LENGTH", "entity_value": "156.0 KM", "page_number": 2, "document_name": "Pipeline_Cert.pdf"},
        {"entity_type": "PIPELINE_DIAMETER", "entity_value": "24 Inch", "page_number": 2, "document_name": "Pipeline_Cert.pdf"},
        {"entity_type": "MANPOWER_RECORD", "entity_value": "Rajesh Sharma", "context_snippet": "Rajesh Sharma - 10 Years Experience", "page_number": 1, "document_name": "CVs.pdf"},
        {"entity_type": "MANPOWER_RECORD", "entity_value": "Amit Patel", "context_snippet": "Amit Patel - 8 Years Experience", "page_number": 1, "document_name": "CVs.pdf"},
        {"entity_type": "MANPOWER_RECORD", "entity_value": "Sunil Rao", "context_snippet": "Sunil Rao - 9 Years Experience", "page_number": 1, "document_name": "CVs.pdf"},
        {"entity_type": "MANPOWER_RECORD", "entity_value": "Vikram Sen", "context_snippet": "Vikram Sen - 8 Years Experience", "page_number": 1, "document_name": "CVs.pdf"},
        {"entity_type": "MANPOWER_RECORD", "entity_value": "Deepa Nair", "context_snippet": "Deepa Nair - 8 Years Experience", "page_number": 1, "document_name": "CVs.pdf"}
    ]
    
    checker = TechnicalManpowerChecker()
    req = {"id": "REQ-005", "clause_number": "REQ-005", "category": "TECHNICAL_MANPOWER", "threshold": 5, "required_years": 8.0, "mandatory": True}
    evidence = {"entities": entities, "doc_chunks": [{"document_name": "Key_Personnel_CVs.pdf", "text": manpower_doc_text, "page_number": 1}]}
    bidder = {"legal_name": "Praveen B S Engineering Services", "personnel": []}

    res = checker.verify(req, evidence, bidder)
    verif = res.get("verification_details", {})
    fields = verif.get("fields", [])
    field_names = [f["field"] for f in fields]
    
    # Must contain manpower fields
    assert "engineer_count" in field_names or "required_engineer_count" in field_names
    # MUST NOT contain pipeline length or diameter
    assert "length_km" not in field_names
    assert "pipeline_length" not in field_names
    assert "diameter_inch" not in field_names
    assert "156.0 KM" not in str(verif.get("summary", ""))


def test_missing_fields_return_null_and_not_detected():
    empty_text = "This document contains generic unformatted text without any figures."
    res = SimilarPipelineExtractor.extract_from_text(empty_text, doc_name="Empty_Doc.pdf", doc_id="doc-empty")
    data = res["data"]
    assert data["length_km"] is None
    assert data["diameter_inch"] is None
    assert data["project_value"] is None

    for f in res["fields"]:
        if f["value"] is None or f["value"] is False:
            assert f["detected"] is False
            assert f["display_value"] == "Not detected"


def test_every_extracted_field_has_traceability_metadata():
    text = "Successful execution of 110.0 KM pipeline with 24 Inch diameter for HPCL completed on 15-03-2025."
    res = SimilarPipelineExtractor.extract_from_text(text, doc_name="HPCL_Cert.pdf", doc_id="hpcl-01")
    for f in res["fields"]:
        assert "field" in f
        assert "label" in f
        assert "source" in f
        assert "page" in f
        assert "method" in f
        assert "confidence" in f
        assert "detected" in f
        assert f["source"] == "HPCL_Cert.pdf"
        assert f["page"] >= 1
        assert f["method"] in ["PDF_TEXT", "TESSERACT_OCR"]


def test_same_document_supporting_multiple_requirements_is_isolated():
    """When a single document supports multiple requirements, each extractor extracts ONLY its schema."""
    multi_purpose_text = """
    COMPREHENSIVE EPC WORK COMPLETION CERTIFICATE
    Company: Praveen B S Engineering Services
    PAN: BSZPP1234K | GSTIN: 29MOCKP1234M1Z5
    Scope: 156.0 KM Natural Gas Pipeline (24 Inch)
    Turnover generated from project: INR 82.50 Crore
    Key Staff: 5 Qualified Engineers deployed (Rajesh Sharma, Lead Engineer, 12 Yrs Exp)
    HSE: ISO 45001 & ISO 14001 Compliant
    """
    # 1. Extract for REQ-003 (Financial)
    fin_res = FinancialEligibilityExtractor.extract_from_text(multi_purpose_text, "Master_Certificate.pdf", "doc-m1")
    assert fin_res["category"] == "FINANCIAL_ELIGIBILITY"
    assert "average_turnover" in [f["field"] for f in fin_res["fields"]]
    assert "length_km" not in [f["field"] for f in fin_res["fields"]]

    # 2. Extract for REQ-004 (Pipeline)
    pipe_res = SimilarPipelineExtractor.extract_from_text(multi_purpose_text, "Master_Certificate.pdf", "doc-m1")
    assert pipe_res["data"]["length_km"] == 156.0
    assert "engineer_count" not in [f["field"] for f in pipe_res["fields"]]

    # 3. Extract for REQ-005 (Manpower)
    manpower_res = TechnicalManpowerExtractor.extract_from_text(multi_purpose_text, "Master_Certificate.pdf", "doc-m1")
    assert "engineer_count" in [f["field"] for f in manpower_res["fields"]]
    assert "length_km" not in [f["field"] for f in manpower_res["fields"]]
