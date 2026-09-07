"""
Phase 2 Comprehensive NLP & Petroleum Extraction Test Suite
Ministry of Petroleum & Natural Gas - Petroleum & Natural Gas Pipeline Procurement
"""
import pytest
from app.nlp.text_normalizer import TextNormalizer
from app.nlp.vocabulary import PetroleumVocabulary
from app.nlp.clause_segmenter import ClauseSegmenter
from app.nlp.requirement_detector import RequirementDetector
from app.nlp.requirement_structurer import RequirementStructurer
from app.nlp.evidence_chunker import EvidenceChunker
from app.documents.extractor import DocumentExtractor
from app.documents.entity_extractor import EntityExtractor
from app.ml.embeddings import embedding_engine

# =====================================================================
# TEST 1: Digital PDF extraction
# =====================================================================
def test_1_digital_pdf_extraction(tmp_path):
    pdf_path = str(tmp_path / "tender_sample.txt")
    with open(pdf_path, "w", encoding="utf-8") as f:
        f.write("GAIL (India) Limited Tender: Construction of 100 KM Natural Gas Pipeline.")
    
    extracted = DocumentExtractor.extract_document(pdf_path)
    assert extracted["page_count"] == 1
    assert "100 KM" in extracted["full_normalized_text"]
    assert extracted["pages"][0]["extraction_method"] == "PDF_TEXT"
    assert extracted["pages"][0]["processing_status"] == "SUCCESS"

# =====================================================================
# TEST 2: Scanned PDF OCR fallback
# =====================================================================
def test_2_scanned_pdf_ocr_fallback(tmp_path):
    txt_path = str(tmp_path / "scanned_doc.png")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("Scanned content dummy")
    
    extracted = DocumentExtractor._extract_image(txt_path)
    assert extracted["is_scanned"] is True
    assert extracted["extraction_method"] == "TESSERACT_OCR"

# =====================================================================
# TEST 3: Text Normalization for Indian Currency and Units
# =====================================================================
def test_3_text_normalization_units_and_currency():
    # Currency
    t1 = TextNormalizer.normalize_text("The average turnover is Rs. 25 Cr. and ₹ 500 Lakhs")
    assert "INR 25 Crore" in t1
    assert "500 Lakh" in t1

    amt, disp = TextNormalizer.parse_currency_amount("₹ 25 Crore")
    assert amt == 250000000.0
    assert "25.00 Crore" in disp

    # Distance
    km = TextNormalizer.parse_distance_km("Pipeline of length 135.5 kms executed successfully")
    assert km == 135.5

    # Diameter
    dia = TextNormalizer.parse_diameter_inch("24-inch NB API 5L X70 line pipes")
    assert dia == 24.0

# =====================================================================
# TEST 4: Tender Clause Detection & Segmentation
# =====================================================================
def test_4_tender_clause_segmentation():
    sample_tender_text = """
    Section 1: General Scope
    The project involves construction of 100 KM cross country pipeline.
    
    Clause 3.1: Financial Turnover
    The bidder shall have a minimum average annual turnover of INR 25 Crore during the previous three financial years.
    
    Clause 3.2: Technical Pipeline Experience
    The bidder must have successfully completed at least one natural gas pipeline project of minimum 100 KM length during the last seven years.
    
    Clause 4.1: Manpower Deployment
    The bidder shall deploy at least 5 qualified pipeline engineers with minimum 8 years experience.
    """
    clauses = ClauseSegmenter.segment_text_into_clauses(sample_tender_text)
    assert len(clauses) >= 4
    
    clause_nums = [c["clause_number"] for c in clauses]
    assert any("3.1" in cn or "Cl-" in cn for cn in clause_nums)
    assert all("normalized_text" in c and len(c["normalized_text"]) > 0 for c in clauses)

# =====================================================================
# TEST 5: Requirement Detection & Category Classification
# =====================================================================
def test_5_requirement_categorization():
    cl_turnover = "The bidder shall have minimum average annual financial turnover of INR 25 Crore in last 3 financial years."
    c_type, conf = RequirementDetector.detect_clause_type(cl_turnover)
    assert c_type == "REQUIREMENT"
    assert conf >= 0.80

    cat, subtype, cat_conf = RequirementDetector.categorize_petroleum_requirement(cl_turnover)
    assert cat == "TURNOVER"

    cl_pipeline = "Bidder must have completed at least 100 KM high pressure natural gas transmission pipeline in last 7 years."
    cat_pipe, _, _ = RequirementDetector.categorize_petroleum_requirement(cl_pipeline)
    assert cat_pipe == "SIMILAR_PIPELINE_EXPERIENCE"

    cl_hse = "Bidder must hold valid ISO 45001 and ISO 14001 certificates with zero fatality safety record."
    cat_hse, sub_hse, _ = RequirementDetector.categorize_petroleum_requirement(cl_hse)
    assert cat_hse == "TENDER_SPECIFIC"
    assert sub_hse == "HSE_SAFETY"

# =====================================================================
# TEST 6: Structured JSON Requirement Extraction
# =====================================================================
def test_6_structured_requirement_extraction():
    clause_text = "The bidder shall have successfully completed at least two natural gas pipeline projects of minimum 100 KM length during the last seven years."
    struct = RequirementStructurer.structure_requirement("SIMILAR_PIPELINE_EXPERIENCE", None, clause_text)
    
    assert struct["category"] == "SIMILAR_PIPELINE_EXPERIENCE"
    assert struct["mandatory"] is True
    assert struct["minimum_project_count"] == 2
    assert struct["pipeline_type"] == "NATURAL_GAS"
    assert struct["minimum_pipeline_length_km"] == 100.0
    assert struct["lookback_years"] == 7
    assert struct["completion_required"] is True

    turnover_text = "The bidder shall have a minimum average annual turnover of INR 25 Crore during the previous three financial years."
    t_struct = RequirementStructurer.structure_requirement("TURNOVER", None, turnover_text)
    assert t_struct["category"] == "TURNOVER"
    assert t_struct["threshold"] == 25.0
    assert t_struct["unit"] == "CRORE_INR"
    assert t_struct["comparison"] == ">="
    assert t_struct["financial_year_count"] == 3

# =====================================================================
# TEST 7: Date Normalization
# =====================================================================
def test_7_date_normalization():
    assert TextNormalizer.parse_date("Project completed on 15/03/2025 successfully") == "2025-03-15"
    assert TextNormalizer.parse_date("Commissioning date: 15-03-2025") == "2025-03-15"
    assert TextNormalizer.parse_date("Taking over certificate issued on 15th March 2025") == "2025-03-15"
    assert TextNormalizer.parse_date("Completion recorded March 15, 2025") == "2025-03-15"

# =====================================================================
# TEST 8 & 9: Similar Pipeline Entity Extraction
# =====================================================================
def test_8_and_9_similar_pipeline_entity_extraction():
    bidder_doc_text = """
    CLIENT: GAIL (India) Limited
    PROJECT: 24 Inch OD Natural Gas Transmission Pipeline Project
    LENGTH: 135 KM cross-country high pressure gas pipeline
    VALUE: INR 82 Crore
    COMPLETION DATE: 15-03-2025
    ROLE: EPC Contractor
    SCOPE: Pipeline Laying, HDD River Crossings, Hydrotesting & Commissioning
    """
    pipe_data = EntityExtractor.extract_similar_pipeline_evidence(bidder_doc_text)
    
    assert pipe_data["pipeline_type"] == "NATURAL_GAS"
    assert pipe_data["pipeline_length_km"] == 135.0
    assert pipe_data["pipeline_diameter_inch"] == 24.0
    assert pipe_data["project_value_crore"] == 82.0
    assert pipe_data["completion_date"] == "2025-03-15"
    assert pipe_data["bidder_role"] == "EPC_CONTRACTOR"
    assert "GAIL" in pipe_data["client_name"]

# =====================================================================
# TEST 10: Multi-Year Turnover Extraction without Premature Pass/Fail
# =====================================================================
def test_10_multi_year_turnover_extraction():
    fin_text = """
    Audited Annual Financial Turnover:
    FY 2023-24: INR 30.00 Crore
    FY 2024-25: INR 27.00 Crore
    FY 2025-26: INR 24.00 Crore
    Total 3 Years Sum: INR 81.00 Crore
    """
    records = EntityExtractor.extract_financial_turnover_records(fin_text)
    assert len(records) == 3
    
    fy_map = {r["fy"]: r["turnover_crore"] for r in records}
    assert fy_map.get("FY 2023-24") == 30.0
    assert fy_map.get("FY 2024-25") == 27.0
    assert fy_map.get("FY 2025-26") == 24.0
    
    # Calculate average via deterministic rule arithmetic
    avg_turnover = sum(r["turnover_crore"] for r in records) / len(records)
    assert avg_turnover == 27.0
    assert avg_turnover >= 25.0

# =====================================================================
# TEST 11: Technical Manpower Personnel Extraction
# =====================================================================
def test_11_technical_manpower_extraction():
    manpower_text = """
    Key Technical Personnel Deployment:
    1. Praveen B S - Project Engineer - B.Tech Mechanical - 12 Years experience (9 Years pipeline)
    2. Ravi Kumar - Pipeline Engineer - B.Tech Mechanical - 11 Years experience (10 Years pipeline)
    3. Suresh Sharma - Welding & NDT Specialist - B.E. Metallurgy - 10 Years experience (9 Years pipeline)
    4. Ananya Rao - QA/QC Pipeline Inspector - B.Tech Mechanical - 9 Years experience (8 Years pipeline)
    5. Vikram Patel - Lead Site Safety Officer - Diploma Safety - 9 Years experience (8 Years pipeline)
    """
    roster = EntityExtractor.extract_technical_manpower_roster(manpower_text)
    assert len(roster) >= 5
    
    names = [p["name"] for p in roster]
    assert "Ravi Kumar" in names
    
    ravi = next(p for p in roster if p["name"] == "Ravi Kumar")
    assert "B.Tech" in ravi["qualification"]
    assert ravi["pipeline_experience_years"] >= 8.0

# =====================================================================
# TEST 12: Semantic Evidence Retrieval
# =====================================================================
def test_12_semantic_evidence_retrieval():
    corpus = [
        {"text": "Successfully executed 135 KM gas transmission infrastructure pipeline project for GAIL with 24 inch pipes.", "page_number": 4, "document_name": "Completion_Certificate.pdf"},
        {"text": "Corporate statutory GSTIN registration 29MOCKP1234M1Z5 in Bangalore Karnataka.", "page_number": 1, "document_name": "GST_Certificate.pdf"},
        {"text": "Audited balance sheet showing annual turnover of 27 Crore.", "page_number": 2, "document_name": "Turnover.pdf"}
    ]
    query = "Natural gas transmission pipeline of minimum 100 KM length"
    results = embedding_engine.retrieve_top_evidence(query, corpus, top_k=2)
    
    assert len(results) > 0
    top_item, top_score = results[0]
    assert "135 KM gas transmission" in top_item["text"]
    assert top_score >= 0.10

# =====================================================================
# TEST 13: Page and Source Preservation
# =====================================================================
def test_13_page_and_source_preservation():
    pages = [
        {"page_number": 1, "text": "GSTIN: 29MOCKP1234M1Z5 Active Regular Status PAN: BSZPP1234K"},
        {"page_number": 2, "text": "FY 2023-24: INR 30 Crore Turnover"},
        {"page_number": 4, "text": "Completion Certificate: 135 KM Natural Gas Transmission Pipeline"}
    ]
    entities = EntityExtractor.extract_all_entities(pages, "EvidencePack.pdf")
    
    gst_ent = next((e for e in entities if e["entity_type"] == "GSTIN"), None)
    assert gst_ent is not None
    assert gst_ent["page_number"] == 1
    
    pipe_ent = next((e for e in entities if e["entity_type"] == "PIPELINE_LENGTH_KM"), None)
    assert pipe_ent is not None
    assert pipe_ent["page_number"] == 4

# =====================================================================
# TEST 14: Low Confidence and Uncertain Extraction Handling
# =====================================================================
def test_14_low_confidence_flagging():
    ambiguous_text = "The vendor provides some general civil works."
    c_type, conf = RequirementDetector.detect_clause_type(ambiguous_text)
    cat, _, cat_conf = RequirementDetector.categorize_petroleum_requirement(ambiguous_text)
    
    assert cat is None or cat_conf <= 0.70

# =====================================================================
# TEST 15: Praveen B S Engineering Services Complete Pack Verification
# =====================================================================
def test_15_praveen_bs_evidence_pack_verification():
    # Pipeline Experience Check
    pipe_text = "Completed 135 KM 24 Inch NB Natural Gas Transmission Pipeline for GAIL on 15-03-2025 as EPC Contractor with project value INR 82 Crore."
    pipe = EntityExtractor.extract_similar_pipeline_evidence(pipe_text)
    assert pipe["pipeline_length_km"] == 135.0
    assert pipe["pipeline_diameter_inch"] == 24.0
    assert pipe["project_value_crore"] == 82.0
    assert pipe["completion_date"] == "2025-03-15"
    assert pipe["bidder_role"] == "EPC_CONTRACTOR"

    # Turnover Check
    turnover_text = "FY 2023-24: INR 30 Crore, FY 2024-25: INR 27 Crore, FY 2025-26: INR 24 Crore."
    turnovers = EntityExtractor.extract_financial_turnover_records(turnover_text)
    assert len(turnovers) == 3
    avg = sum(t["turnover_crore"] for t in turnovers) / 3.0
    assert avg == 27.0
    assert avg >= 25.0

    # Manpower Check
    manpower = EntityExtractor.extract_technical_manpower_roster(pipe_text)
    assert len(manpower) >= 5
