"""
Idempotent Demo Database Seeding Script for SIH26100
Ministry of Petroleum & Natural Gas - GeM Bid Compliance Verification Platform

Resets and seeds:
1. Demo Users (Admin & Procurement Officer)
2. Primary Demo Tender: MOPNG/PIPE/2026/017
3. 7 Normalized Requirements (REQ-001 to REQ-007)
4. 3 Fixed Demo Bidders:
   - Bidder A (Compliant): PRAVEEN B S ENGINEERING SERVICES
   - Bidder B (Review Required): Bharat Hydrocarbon Infra Ltd
   - Bidder C (Non-Compliant): Indus Pipeline Infrastructure Limited
5. Auditable Documents & Extracted NLP Entities
6. Deterministic Phase 3 Compliance Checks, Scores, Risk Assessments, and Recommendations
7. GFR 2017 Immutable Audit Trail
"""

import os
import sys
from datetime import datetime, timezone, timedelta

# Ensure backend modules are on PYTHONPATH
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import fitz  # PyMuPDF
from app.core.database import Base, engine, SessionLocal
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.models import (
    User, Tender, Requirement, Bidder, Bid, BidderProject, BidderPersonnel,
    Document, ExtractedEntity, OfficerReview
)
from app.services.compliance_engine import ComplianceEngine
from app.audit.audit_service import AuditService
from app.core.logging_config import logger

def create_sample_pdf(file_path: str, title: str, sections: list):
    """Generates a professional formatted PDF document using PyMuPDF."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    
    # Header Banner
    header_rect = fitz.Rect(40, 40, 555, 90)
    page.draw_rect(header_rect, color=(0.1, 0.2, 0.45), fill=(0.93, 0.95, 0.98))
    page.insert_text(fitz.Point(55, 65), title, fontsize=12, color=(0.08, 0.18, 0.38))
    page.insert_text(fitz.Point(55, 80), "MINISTRY OF PETROLEUM & NATURAL GAS - PIPELINE TENDER DOSSIER", fontsize=8, color=(0.4, 0.45, 0.5))
    
    y = 120
    for heading, text_body in sections:
        page.insert_text(fitz.Point(40, y), heading.upper(), fontsize=10.0, color=(0.12, 0.23, 0.45))
        y += 16
        
        words = text_body.split()
        line = []
        for word in words:
            line.append(word)
            if len(" ".join(line)) > 75 or "\n" in word:
                page.insert_text(fitz.Point(40, y), " ".join(line).replace("\n", ""), fontsize=9, color=(0.2, 0.2, 0.2))
                y += 13
                line = []
        if line:
            page.insert_text(fitz.Point(40, y), " ".join(line), fontsize=9, color=(0.2, 0.2, 0.2))
            y += 13
            
        y += 12
        page.draw_line(fitz.Point(40, y), fitz.Point(555, y), color=(0.88, 0.88, 0.88))
        y += 18

    page.insert_text(fitz.Point(40, 810), f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} | MoPNG Official Stamp", fontsize=7.5, color=(0.5, 0.5, 0.5))
    doc.save(file_path)
    doc.close()


def seed_demo():
    logger.info("Initializing clean database state for presentation mode...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. USERS
    logger.info("Seeding Demo Users...")
    admin_user = User(
        name="Sunil Verma, Chief Procurement Officer",
        email="admin@gem.gov.in",
        username="admin",
        password_hash=get_password_hash("admin123"),
        role="ADMIN",
        department="Ministry of Petroleum & Natural Gas - Policy Division, New Delhi"
    )
    db.add(admin_user)

    officer_user = User(
        name="Rajesh Sharma, Senior Procurement Officer",
        email="officer@gem.gov.in",
        username="procurement_officer",
        password_hash=get_password_hash("officer123"),
        role="PROCUREMENT_OFFICER",
        department="GAIL / MoPNG Pipeline Tender Evaluation Cell, New Delhi"
    )
    db.add(officer_user)

    bidder_user = User(
        name="Praveen B S, Authorized Signatory",
        email="vendor@company.com",
        username="bidder",
        password_hash=get_password_hash("bidder123"),
        role="BIDDER",
        department="PRAVEEN B S ENGINEERING SERVICES, Bidder Desk"
    )
    db.add(bidder_user)

    db.commit()
    db.refresh(admin_user)
    db.refresh(officer_user)
    db.refresh(bidder_user)

    # 2. PRIMARY DEMO TENDER: MOPNG/PIPE/2026/017
    logger.info("Seeding Primary Demo Tender (MOPNG/PIPE/2026/017)...")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    t1_doc = os.path.join(settings.UPLOAD_DIR, "Tender_MOPNG_PIPE_2026_017.pdf")
    create_sample_pdf(
        t1_doc,
        "MOPNG TENDER: MOPNG/PIPE/2026/017 - NATURAL GAS TRANSMISSION PIPELINE",
        [
            ("1. Scope of Work", "Laying, Testing, and Commissioning of 150 km, 24-inch Outer Diameter API 5L Grade X70 Cross-Country Natural Gas Transmission Pipeline including Sectionalizing Valve Stations and Intermediate Pigging Stations."),
            ("2. REQ-001: GST Statutory Registration", "Bidder must possess valid and active GSTIN registration in the relevant State/UT and submit latest GSTR-3B filings."),
            ("3. REQ-002: PAN & Identity", "Bidder entity must hold a valid Permanent Account Number (PAN) issued by Income Tax Department matching corporate legal identity."),
            ("4. REQ-003: Financial Turnover", "Average Annual Financial Turnover of the bidder during the last 3 preceding financial years (FY 2023-24, FY 2024-25, FY 2025-26) must be at least INR 25.00 Crore."),
            ("5. REQ-004: Similar Pipeline Experience", "Bidder must have successfully constructed and commissioned at least one cross-country high-pressure natural gas transmission pipeline of minimum 100 km length (24-inch or higher) in the last 7 years."),
            ("6. REQ-005: Technical Manpower", "Bidder must commit and deploy a minimum of 5 qualified pipeline engineers (B.Tech / B.E. Mechanical / Pipeline / NDT Level II) with at least 8 years of relevant site experience."),
            ("7. REQ-006: Oil & Gas Experience", "Bidder must possess proven prior execution experience of minimum 7 years in EPC / construction projects in Petroleum, Natural Gas, Refinery, or Hydrocarbon pipeline sectors."),
            ("8. REQ-007: HSE & Safety Compliance", "Bidder must maintain certified Occupational Health & Safety (ISO 45001) and Environmental Management (ISO 14001) systems with a zero-fatality site safety policy.")
        ]
    )

    primary_tender = Tender(
        tender_number="MOPNG/PIPE/2026/017",
        title="Natural Gas Transmission Pipeline Procurement",
        issuing_organization="Ministry of Petroleum & Natural Gas / GAIL",
        ministry="Ministry of Petroleum & Natural Gas",
        sector="OIL_AND_GAS",
        tender_type="PIPELINE_PROCUREMENT",
        project_type="PIPELINE_CONSTRUCTION",
        pipeline_type="NATURAL_GAS_TRANSMISSION",
        location="National Gas Grid, Vijaipur-Auraiya Corridor, India",
        description="EPC contract for 150 km, 24-inch NB API 5L Grade X70 cross-country high-pressure natural gas transmission pipeline laying, HDD river crossings, SV stations, and pre-commissioning.",
        estimated_value=2400000000.0,
        tender_issue_date=datetime.now(timezone.utc) - timedelta(days=12),
        submission_deadline=datetime.now(timezone.utc) + timedelta(days=18),
        evaluation_date=datetime.now(timezone.utc) + timedelta(days=25),
        status="ACTIVE",
        raw_pdf_path=t1_doc,
        created_by=officer_user.id
    )
    db.add(primary_tender)
    db.commit()
    db.refresh(primary_tender)

    # 3. 7 NORMALIZED REQUIREMENTS (REQ-001 TO REQ-007)
    logger.info("Seeding 7 Normalized Requirements for MOPNG/PIPE/2026/017...")
    reqs = [
        Requirement(
            tender_id=primary_tender.id,
            category="GST",
            clause_number="REQ-001",
            original_text="Check 1 (REQ-001): Bidder must possess valid and active GSTIN registration in the relevant State/UT and submit latest GSTR-3B filings.",
            normalized_requirement="Active GSTIN Registration with latest monthly GSTR-3B filings.",
            mandatory=True,
            threshold=None,
            threshold_unit=None,
            period="CURRENT_ACTIVE",
            evidence_required=["GST_REGISTRATION_CERTIFICATE", "LATEST_GSTR_3B_FILING"],
            verification_method="PORTAL_AND_RULE"
        ),
        Requirement(
            tender_id=primary_tender.id,
            category="PAN",
            clause_number="REQ-002",
            original_text="Check 2 (REQ-002): Bidder entity must hold a valid Permanent Account Number (PAN) issued by Income Tax Department matching corporate legal identity.",
            normalized_requirement="Valid PAN issued to exact corporate legal entity.",
            mandatory=True,
            threshold=None,
            threshold_unit=None,
            period="PERMANENT",
            evidence_required=["PAN_CARD", "ITR_ACKNOWLEDGEMENTS"],
            verification_method="PORTAL_AND_RULE"
        ),
        Requirement(
            tender_id=primary_tender.id,
            category="TURNOVER",
            clause_number="REQ-003",
            original_text="Check 3 (REQ-003): Average Annual Financial Turnover of the bidder during the last 3 preceding financial years (FY 2023-24, FY 2024-25, FY 2025-26) must be at least INR 25.00 Crore.",
            normalized_requirement="Average Annual Turnover >= INR 25.00 Crore over last 3 FYs.",
            mandatory=True,
            threshold=250000000.0,
            threshold_unit="INR",
            period="LAST_3_FINANCIAL_YEARS",
            evidence_required=["AUDITED_BALANCE_SHEETS", "CA_CERTIFIED_TURNOVER_STATEMENT"],
            verification_method="RULE_AND_ARITHMETIC"
        ),
        Requirement(
            tender_id=primary_tender.id,
            category="SIMILAR_PIPELINE_EXPERIENCE",
            clause_number="REQ-004",
            original_text="Check 4 (REQ-004): Bidder must have successfully constructed and commissioned at least one cross-country high-pressure natural gas transmission pipeline of minimum 100 km length (24-inch or higher) in the last 7 years.",
            normalized_requirement="Execution of >= 100 km cross-country natural gas transmission pipeline (>= 24-inch OD).",
            mandatory=True,
            threshold=100.0,
            threshold_unit="KM",
            required_pipeline_length_km=100.0,
            period="LAST_7_YEARS",
            evidence_required=["PIPELINE_COMPLETION_CERTIFICATE", "CLIENT_TAKING_OVER_CERTIFICATE"],
            verification_method="RULE_AND_SEMANTIC"
        ),
        Requirement(
            tender_id=primary_tender.id,
            category="TECHNICAL_MANPOWER",
            clause_number="REQ-005",
            original_text="Check 5 (REQ-005): Bidder must commit and deploy a minimum of 5 qualified pipeline engineers (B.Tech / B.E. Mechanical / Pipeline / NDT Level II) with at least 8 years of relevant site experience.",
            normalized_requirement="Minimum 5 qualified pipeline engineers with >= 8 years relevant site experience.",
            mandatory=True,
            threshold=5.0,
            threshold_unit="PERSONNEL_COUNT",
            required_manpower_count=5,
            required_years=8.0,
            period="PROJECT_DEPLOYMENT",
            evidence_required=["KEY_PERSONNEL_CVS", "DEGREE_CERTIFICATES", "EXPERIENCE_AFFIDAVITS"],
            verification_method="DETERMINISTIC_COUNT_AND_NLP"
        ),
        Requirement(
            tender_id=primary_tender.id,
            category="OIL_GAS_EXPERIENCE",
            clause_number="REQ-006",
            original_text="Check 6 (REQ-006): Bidder must possess proven prior execution experience of >= 7 years in EPC / construction projects in Petroleum, Natural Gas, Refinery, or Hydrocarbon pipeline sectors.",
            normalized_requirement="Prior EPC/construction experience >= 7 years in Petroleum / Natural Gas / Hydrocarbon sector.",
            mandatory=True,
            threshold=7.0,
            threshold_unit="YEARS",
            required_years=7.0,
            required_sector="OIL_AND_GAS",
            period="LAST_7_YEARS",
            evidence_required=["EXPERIENCE_CERTIFICATE", "CLIENT_COMPLETION_REPORT"],
            verification_method="SEMANTIC_NLP_CLASSIFIER"
        ),
        Requirement(
            tender_id=primary_tender.id,
            category="HSE_SAFETY",
            clause_number="REQ-007",
            original_text="Check 7 (REQ-007): Bidder must maintain certified Occupational Health & Safety (ISO 45001) and Environmental Management (ISO 14001) systems with a zero-fatality site safety policy.",
            normalized_requirement="Certified ISO 45001:2018 and ISO 14001:2015 with zero-fatality HSE site policy.",
            mandatory=True,
            threshold=None,
            threshold_unit=None,
            period="VALID_CERTIFICATION",
            evidence_required=["ISO_45001_CERTIFICATE", "ISO_14001_CERTIFICATE", "CORPORATE_SAFETY_POLICY"],
            verification_method="CERTIFICATION_VERIFIER"
        )
    ]
    for r in reqs:
        db.add(r)
    db.commit()

    # 4. THREE FIXED DEMO BIDDERS
    # =============================================================
    # BIDDER A — COMPLIANT: PRAVEEN B S ENGINEERING SERVICES
    # =============================================================
    logger.info("Seeding Bidder A: PRAVEEN B S ENGINEERING SERVICES (Compliant)...")
    b1 = Bidder(
        tender_id=primary_tender.id,
        legal_name="PRAVEEN B S ENGINEERING SERVICES",
        trade_name="Praveen B S Engineering Services",
        pan="BSZPP1234K",
        gstin="29MOCKP1234M1Z5",
        registered_address="#42, Pipeline Corridor Industrial Estate, Peenya, Bengaluru, Karnataka 560058",
        contact_information={"email": "contact@praveen-engineering.com", "phone": "+91 80 2839 4410"},
        bidder_type="INDIAN_EPC_CONTRACTOR",
        country="INDIA",
        oil_gas_experience_years=9.0,
        pipeline_experience_years=9.0,
        udyam_number="UDYAM-KA-03-0087412",
        cin="U45200KA2015PTC081290",
        email="contact@praveen-engineering.com",
        phone="+91 80 2839 4410",
        contact_person="Praveen B S (Managing Director & Chief Pipeline Engineer)",
        status="VERIFIED"
    )
    db.add(b1)
    db.commit()
    db.refresh(b1)

    bid1 = Bid(
        tender_id=primary_tender.id,
        bidder_id=b1.id,
        bid_reference_number="BID-MOPNG-2026-PBS-001",
        submission_date=datetime.now(timezone.utc) - timedelta(days=2),
        technical_bid_status="QUALIFIED",
        financial_bid_amount=2320000000.0,
        currency="INR",
        remarks="Fully compliant technical & financial bid submitted with verified evidence for REQ-001 through REQ-007."
    )
    db.add(bid1)

    p1_1 = BidderProject(
        bidder_id=b1.id,
        project_name="Natural Gas Transmission Pipeline Project (Section 4)",
        client_name="GAIL (India) Limited",
        client_type="PUBLIC_SECTOR_UNDERTAKING",
        sector="OIL_AND_GAS",
        project_type="PIPELINE_CONSTRUCTION",
        pipeline_type="NATURAL_GAS_TRANSMISSION",
        pipeline_length_km=135.0,
        pipeline_diameter="24 inch NB API 5L Grade X70",
        project_value=825000000.0,
        currency="INR",
        location="Madhya Pradesh & Uttar Pradesh",
        start_date=datetime.now(timezone.utc) - timedelta(days=365*2),
        completion_date=datetime.now(timezone.utc) - timedelta(days=90),
        scope_of_work="EPC Construction of 135 KM 24-inch natural gas transmission pipeline, SV stations, HDD river crossings, and pigging facilities.",
        bidder_role="MAIN_CONTRACTOR",
        contract_reference="GAIL/ND/C&P/PROJECTS/2023/14"
    )
    db.add(p1_1)

    staff_b1 = [
        BidderPersonnel(bidder_id=b1.id, name="Praveen B S", designation="Project Director", qualification="B.Tech Mechanical", years_of_experience=12.0, pipeline_experience_years=9.0),
        BidderPersonnel(bidder_id=b1.id, name="Ravi Kumar", designation="Lead Pipeline Engineer", qualification="B.Tech Mechanical", years_of_experience=11.0, pipeline_experience_years=10.0),
        BidderPersonnel(bidder_id=b1.id, name="Suresh Sharma", designation="Chief Welding & NDT Specialist", qualification="B.E. Metallurgy", years_of_experience=10.0, pipeline_experience_years=9.0),
        BidderPersonnel(bidder_id=b1.id, name="Ananya Rao", designation="QA/QC Pipeline Inspector", qualification="B.Tech Mechanical", years_of_experience=9.0, pipeline_experience_years=8.0),
        BidderPersonnel(bidder_id=b1.id, name="Vikram Patel", designation="Lead Site Safety Officer", qualification="Diploma Industrial Safety", years_of_experience=9.0, pipeline_experience_years=8.0)
    ]
    for s in staff_b1:
        db.add(s)

    b1_stat_pdf = os.path.join(settings.UPLOAD_DIR, "Praveen_Statutory_GST_PAN.pdf")
    b1_fin_pdf = os.path.join(settings.UPLOAD_DIR, "Audited_Financial_Statement_FY24-26.pdf")
    b1_exp_pdf = os.path.join(settings.UPLOAD_DIR, "Experience_Certificate.pdf")
    b1_oil_pdf = os.path.join(settings.UPLOAD_DIR, "Oil_Gas_Experience_Summary.pdf")
    b1_man_pdf = os.path.join(settings.UPLOAD_DIR, "Technical_Manpower_CVs.pdf")
    b1_hse_pdf = os.path.join(settings.UPLOAD_DIR, "HSE_Policy_ISO45001.pdf")

    create_sample_pdf(b1_stat_pdf, "PRAVEEN B S ENGINEERING SERVICES - STATUTORY GST & PAN", [
        ("1. GSTIN Certificate", "Entity: PRAVEEN B S ENGINEERING SERVICES\nGSTIN: 29MOCKP1234M1Z5 (Karnataka)\nStatus: ACTIVE Regular\nPAN: BSZPP1234K")
    ])
    create_sample_pdf(b1_fin_pdf, "PRAVEEN B S ENGINEERING SERVICES - AUDITED FINANCIAL STATEMENTS", [
        ("1. Three-Year Turnover Summary", "FY 2023-24: INR 30.00 Crore\nFY 2024-25: INR 27.00 Crore\nFY 2025-26: INR 24.00 Crore\nThree-Year Average Annual Turnover = (30 + 27 + 24) / 3 = INR 27.00 Crore (Exceeds mandatory INR 25.00 Crore).")
    ])
    create_sample_pdf(b1_exp_pdf, "EXPERIENCE CERTIFICATE - GAIL (INDIA) LIMITED", [
        ("1. Work Completion Certification", "Client: GAIL (India) Limited\nContractor: PRAVEEN B S ENGINEERING SERVICES\nProject: Natural Gas Transmission Pipeline Project (Section 4)\nScope: Engineering, Procurement and Construction of 135 KM Natural Gas Transmission Pipeline (24-inch OD API 5L Grade X70).\nExecuted Length: 135 KM\nDiameter: 24 Inch\nProject Value: INR 82.50 Crore\nRole: EPC Contractor\nCompletion Date: 15-03-2025\nPerformance: Successfully commissioned with zero defects.")
    ])
    create_sample_pdf(b1_oil_pdf, "CORPORATE OIL & GAS EXPERIENCE SUMMARY", [
        ("1. Cumulative Experience Dossier", "PRAVEEN B S ENGINEERING SERVICES has executed cross-country pipeline and station projects in Petroleum, Natural Gas, and Hydrocarbon sectors continuously from 2017 to 2026 (9.0 Total Years).")
    ])
    create_sample_pdf(b1_man_pdf, "TECHNICAL PERSONNEL DEPLOYMENT PLAN & CVs", [
        ("1. Key Qualified Engineers", "1. Praveen B S - Project Director (B.Tech Mechanical, 12 yrs exp, 9 yrs pipeline)\n2. Ravi Kumar - Lead Pipeline Engineer (B.Tech Mechanical, 11 yrs exp, 10 yrs pipeline)\n3. Suresh Sharma - Welding & NDT Specialist (B.E. Metallurgy, 10 yrs exp, 9 yrs pipeline)\n4. Ananya Rao - QA/QC Pipeline Inspector (B.Tech Mechanical, 9 yrs exp, 8 yrs pipeline)\n5. Vikram Patel - Lead Site Safety Officer (Diploma Safety, 9 yrs exp, 8 yrs pipeline)\nTotal Qualifying Engineers: 5 (All >= 8 years relevant experience).")
    ])
    create_sample_pdf(b1_hse_pdf, "HSE & OCCUPATIONAL HEALTH SAFETY CERTIFICATE", [
        ("1. Certifications", "ISO 45001:2018 (Occupational Health & Safety)\nISO 14001:2015 (Environmental Management)\nValid Through: 31-December-2026\nSite Policy: Zero-fatality site safety policy endorsed by executive management.")
    ])

    docs_b1 = [
        Document(bidder_id=b1.id, tender_id=primary_tender.id, document_name="GST_Registration_Certificate.pdf", file_path=b1_stat_pdf, document_type="GST_CERTIFICATE", page_count=1, extracted_text="Legal Name: PRAVEEN B S ENGINEERING SERVICES\nGSTIN: 29MOCKP1234M1Z5\nPAN: BSZPP1234K\nStatus: ACTIVE"),
        Document(bidder_id=b1.id, tender_id=primary_tender.id, document_name="Audited_Financial_Statement_FY24-26.pdf", file_path=b1_fin_pdf, document_type="FINANCIAL_STATEMENT", page_count=3, extracted_text="FY 2023-24: INR 30.00 Crore\nFY 2024-25: INR 27.00 Crore\nFY 2025-26: INR 24.00 Crore\nAverage Annual Turnover = INR 27.00 Crore."),
        Document(bidder_id=b1.id, tender_id=primary_tender.id, document_name="Experience_Certificate.pdf", file_path=b1_exp_pdf, document_type="PIPELINE_PROJECT_DOCUMENT", page_count=4, extraction_method="TESSERACT_OCR", extracted_text="Client: GAIL (India) Limited\nProject: Natural Gas Transmission Pipeline\nPipeline Type: Natural Gas\nLength: 135 KM\nDiameter: 24 Inch\nProject Value: INR 82.50 Crore\nRole: EPC Contractor\nCompletion Date: 15-03-2025\nExecuted Length: 135 KM (24 Inch OD)."),
        Document(bidder_id=b1.id, tender_id=primary_tender.id, document_name="Oil_Gas_Experience_Summary.pdf", file_path=b1_oil_pdf, document_type="EXPERIENCE_CERTIFICATE", page_count=2, extracted_text="Verified Oil and Gas corporate execution: 9.0 Years in Petroleum and Natural Gas pipeline projects."),
        Document(bidder_id=b1.id, tender_id=primary_tender.id, document_name="Technical_Manpower_CVs.pdf", file_path=b1_man_pdf, document_type="PERSONNEL_CV", page_count=5, extracted_text="Praveen B S (12 yrs / 9 yrs pipeline)\nRavi Kumar (11 yrs / 10 yrs pipeline)\nSuresh Sharma (10 yrs / 9 yrs pipeline)\nAnanya Rao (9 yrs / 8 yrs pipeline)\nVikram Patel (9 yrs / 8 yrs pipeline)\nTotal 5 qualifying pipeline engineers."),
        Document(bidder_id=b1.id, tender_id=primary_tender.id, document_name="HSE_Policy_ISO45001.pdf", file_path=b1_hse_pdf, document_type="SAFETY_CERTIFICATE", page_count=1, extracted_text="ISO 45001:2018 Certified\nISO 14001:2015 Certified\nZero-fatality site safety policy valid through 31-December-2026.")
    ]
    for d in docs_b1:
        db.add(d)
    db.commit()

    entities_b1 = [
        ExtractedEntity(document_id=docs_b1[0].id, entity_type="GSTIN", entity_value="29MOCKP1234M1Z5", normalized_value="29MOCKP1234M1Z5", confidence=0.98, page_number=1, context_snippet="GSTIN: 29MOCKP1234M1Z5 Active Regular"),
        ExtractedEntity(document_id=docs_b1[0].id, entity_type="PAN", entity_value="BSZPP1234K", normalized_value="BSZPP1234K", confidence=0.99, page_number=1, context_snippet="PAN: BSZPP1234K matching corporate identity"),
        ExtractedEntity(document_id=docs_b1[0].id, entity_type="COMPANY_NAME", entity_value="PRAVEEN B S ENGINEERING SERVICES", normalized_value="praveen b s engineering services", confidence=0.99, page_number=1, context_snippet="PRAVEEN B S ENGINEERING SERVICES"),
        ExtractedEntity(document_id=docs_b1[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2023-24: INR 30.00 Crore", normalized_value="300000000.0", confidence=0.96, page_number=3, context_snippet="FY 2023-24: INR 30.00 Crore"),
        ExtractedEntity(document_id=docs_b1[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2024-25: INR 27.00 Crore", normalized_value="270000000.0", confidence=0.96, page_number=3, context_snippet="FY 2024-25: INR 27.00 Crore"),
        ExtractedEntity(document_id=docs_b1[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2025-26: INR 24.00 Crore", normalized_value="240000000.0", confidence=0.96, page_number=3, context_snippet="FY 2025-26: INR 24.00 Crore"),
        ExtractedEntity(document_id=docs_b1[2].id, entity_type="OIL_GAS_PROJECT", entity_value="Natural Gas Transmission Pipeline Project (Section 4)", normalized_value="natural gas transmission pipeline", confidence=0.95, page_number=4, context_snippet="EPC of 135 KM Natural Gas Transmission Pipeline (24-inch OD)."),
        ExtractedEntity(document_id=docs_b1[2].id, entity_type="PIPELINE_LENGTH_KM", entity_value="135.0 km", normalized_value="135.0", confidence=0.96, page_number=4, context_snippet="Executed Length: 135 KM 24 Inch NB API 5L Grade X70"),
        ExtractedEntity(document_id=docs_b1[3].id, entity_type="OIL_GAS_EXPERIENCE_YEARS", entity_value="9.0 Years", normalized_value="9.0", confidence=0.95, page_number=1, context_snippet="Verified experience in Petroleum, Natural Gas: 9.0 Years"),
        ExtractedEntity(document_id=docs_b1[4].id, entity_type="MANPOWER_RECORD", entity_value="Praveen B S (12 yrs / 9 yrs pipeline)", normalized_value="9.0", confidence=0.93, page_number=1, context_snippet="Praveen B S - Project Director - B.Tech Mechanical"),
        ExtractedEntity(document_id=docs_b1[4].id, entity_type="MANPOWER_RECORD", entity_value="Ravi Kumar (11 yrs / 10 yrs pipeline)", normalized_value="10.0", confidence=0.93, page_number=2, context_snippet="Ravi Kumar - Lead Pipeline Engineer - B.Tech Mechanical"),
        ExtractedEntity(document_id=docs_b1[4].id, entity_type="MANPOWER_RECORD", entity_value="Suresh Sharma (10 yrs / 9 yrs pipeline)", normalized_value="9.0", confidence=0.93, page_number=3, context_snippet="Suresh Sharma - Chief Welding Specialist"),
        ExtractedEntity(document_id=docs_b1[4].id, entity_type="MANPOWER_RECORD", entity_value="Ananya Rao (9 yrs / 8 yrs pipeline)", normalized_value="8.0", confidence=0.93, page_number=4, context_snippet="Ananya Rao - QA/QC Pipeline Inspector"),
        ExtractedEntity(document_id=docs_b1[4].id, entity_type="MANPOWER_RECORD", entity_value="Vikram Patel (9 yrs / 8 yrs pipeline)", normalized_value="8.0", confidence=0.93, page_number=5, context_snippet="Vikram Patel - Lead Site Safety Officer"),
        ExtractedEntity(document_id=docs_b1[5].id, entity_type="HSE_CERTIFICATION", entity_value="ISO 45001:2018 & ISO 14001:2015", normalized_value="ISO_45001_14001", confidence=0.95, page_number=1, context_snippet="ISO 45001:2018 Certified Occupational Health")
    ]
    for ent in entities_b1:
        db.add(ent)
    db.commit()


    # =============================================================
    # BIDDER B — REVIEW REQUIRED: Bharat Hydrocarbon Infra Ltd
    # =============================================================
    logger.info("Seeding Bidder B: Bharat Hydrocarbon Infra Ltd (Review Required)...")
    b2 = Bidder(
        tender_id=primary_tender.id,
        legal_name="Bharat Hydrocarbon Infra Ltd",
        trade_name="Bharat Hydrocarbon",
        pan="AABCB7890K",
        gstin="27AABCB7890K1Z4",
        registered_address="Bharat Energy Tower, Bandra Kurla Complex, Mumbai, Maharashtra 400051",
        contact_information={"email": "tenders@bharathydrocarbon.in", "phone": "+91 22 6120 4500"},
        bidder_type="PUBLIC_LIMITED_EPC",
        country="INDIA",
        oil_gas_experience_years=8.5,
        pipeline_experience_years=8.0,
        udyam_number="UDYAM-MH-01-0045231",
        cin="L45200MH2012PLC231890",
        email="tenders@bharathydrocarbon.in",
        phone="+91 22 6120 4500",
        contact_person="Rajan Mehta (Vice President - Cross-Country Pipelines)",
        status="UNDER_REVIEW"
    )
    db.add(b2)
    db.commit()
    db.refresh(b2)

    bid2 = Bid(
        tender_id=primary_tender.id,
        bidder_id=b2.id,
        bid_reference_number="BID-MOPNG-2026-BHI-002",
        submission_date=datetime.now(timezone.utc) - timedelta(days=1),
        technical_bid_status="UNDER_REVIEW",
        financial_bid_amount=2360000000.0,
        currency="INR",
        remarks="Technical bid submitted with HSE certification clarification requested by evaluation committee."
    )
    db.add(bid2)

    p2_1 = BidderProject(
        bidder_id=b2.id,
        project_name="Western Gas Grid 115 KM Pipeline Laying",
        client_name="GAIL / Gujarat State Petronet Limited",
        client_type="PUBLIC_SECTOR_UNDERTAKING",
        sector="OIL_AND_GAS",
        project_type="PIPELINE_CONSTRUCTION",
        pipeline_type="NATURAL_GAS_TRANSMISSION",
        pipeline_length_km=115.0,
        pipeline_diameter="24 inch NB API 5L X70",
        project_value=760000000.0,
        currency="INR",
        location="Gujarat",
        start_date=datetime.now(timezone.utc) - timedelta(days=365*3),
        completion_date=datetime.now(timezone.utc) - timedelta(days=120),
        scope_of_work="EPC execution of 115 km 24-inch natural gas transmission pipeline.",
        bidder_role="MAIN_CONTRACTOR",
        contract_reference="GSPL/WGG/2022/09"
    )
    db.add(p2_1)

    staff_b2 = [
        BidderPersonnel(bidder_id=b2.id, name="Amitabh Sen", designation="Senior Project Manager", qualification="B.Tech Mechanical", years_of_experience=11.0, pipeline_experience_years=9.0),
        BidderPersonnel(bidder_id=b2.id, name="Nitin Gadgil", designation="Pipeline Construction Engineer", qualification="B.E. Mechanical", years_of_experience=10.0, pipeline_experience_years=8.5),
        BidderPersonnel(bidder_id=b2.id, name="Kiran Joshi", designation="Chief Welding Inspector", qualification="B.E. Metallurgy", years_of_experience=9.5, pipeline_experience_years=8.5),
        BidderPersonnel(bidder_id=b2.id, name="Gaurav Deshmukh", designation="NDT Level II Specialist", qualification="Diploma Mechanical", years_of_experience=9.0, pipeline_experience_years=8.0),
        BidderPersonnel(bidder_id=b2.id, name="Pooja Kulkarni", designation="QA/QC Engineer", qualification="B.Tech Mechanical", years_of_experience=8.5, pipeline_experience_years=8.0)
    ]
    for s in staff_b2:
        db.add(s)

    b2_stat_pdf = os.path.join(settings.UPLOAD_DIR, "Bharat_Hydrocarbon_Statutory_GST_PAN.pdf")
    b2_fin_pdf = os.path.join(settings.UPLOAD_DIR, "Bharat_Hydrocarbon_Turnover_Audited.pdf")
    b2_exp_pdf = os.path.join(settings.UPLOAD_DIR, "Bharat_Hydrocarbon_115km_Pipeline.pdf")
    b2_oil_pdf = os.path.join(settings.UPLOAD_DIR, "Bharat_Hydrocarbon_Oil_Gas_Exp.pdf")
    b2_man_pdf = os.path.join(settings.UPLOAD_DIR, "Bharat_Hydrocarbon_Manpower.pdf")
    b2_hse_pdf = os.path.join(settings.UPLOAD_DIR, "Bharat_Hydrocarbon_HSE_Scanned.pdf")

    create_sample_pdf(b2_stat_pdf, "BHARAT HYDROCARBON INFRA - STATUTORY CERTIFICATES", [
        ("1. GST & PAN Registration", "Entity: Bharat Hydrocarbon Infra Ltd\nGSTIN: 27AABCB7890K1Z4 (Maharashtra)\nPAN: AABCB7890K\nStatus: ACTIVE Regular")
    ])
    create_sample_pdf(b2_fin_pdf, "BHARAT HYDROCARBON INFRA - FINANCIAL AUDIT", [
        ("1. Three-Year Turnover", "FY 2023-24: INR 29.00 Crore\nFY 2024-25: INR 28.50 Crore\nFY 2025-26: INR 28.00 Crore\nThree-Year Average: INR 28.50 Crore (Exceeds mandatory threshold of INR 25.00 Crore).")
    ])
    create_sample_pdf(b2_exp_pdf, "BHARAT HYDROCARBON INFRA - PIPELINE COMPLETION", [
        ("1. Western Gas Grid Project", "Client: GSPL\nScope: 115 KM Natural Gas Transmission Pipeline (24-inch OD).\nCompletion: Successfully executed 115 km length.")
    ])
    create_sample_pdf(b2_oil_pdf, "BHARAT HYDROCARBON INFRA - HYDROCARBON EXPERIENCE", [
        ("1. Sector Experience", "Total verified experience in Petroleum and Natural Gas sectors: 8.5 Years.")
    ])
    create_sample_pdf(b2_man_pdf, "BHARAT HYDROCARBON INFRA - TECHNICAL STAFF", [
        ("1. Manpower List", "5 qualifying pipeline engineers deployed with 8.5 to 11 years experience.")
    ])
    create_sample_pdf(b2_hse_pdf, "BHARAT HYDROCARBON INFRA - HSE COMPLIANCE (PROVISIONAL)", [
        ("1. Safety Certificate", "Provisional safety management plan. ISO 45001 accreditation endorsement certificate requires verification of renewal seal by procurement officer.")
    ])

    docs_b2 = [
        Document(bidder_id=b2.id, tender_id=primary_tender.id, document_name="Bharat_Statutory_GST_PAN.pdf", file_path=b2_stat_pdf, document_type="GST_CERTIFICATE", page_count=1, extracted_text="Bharat Hydrocarbon Infra Ltd\nGSTIN: 27AABCB7890K1Z4\nPAN: AABCB7890K"),
        Document(bidder_id=b2.id, tender_id=primary_tender.id, document_name="Bharat_Turnover_Audited.pdf", file_path=b2_fin_pdf, document_type="FINANCIAL_STATEMENT", page_count=2, extracted_text="FY 2023-24: 29.00 Cr\nFY 2024-25: 28.50 Cr\nFY 2025-26: 28.00 Cr\nAverage Turnover: 28.50 Crore."),
        Document(bidder_id=b2.id, tender_id=primary_tender.id, document_name="Bharat_115km_Pipeline.pdf", file_path=b2_exp_pdf, document_type="PIPELINE_PROJECT_DOCUMENT", page_count=3, extracted_text="Western Gas Grid 115 KM Natural Gas Pipeline (24-inch OD). Executed length: 115 KM."),
        Document(bidder_id=b2.id, tender_id=primary_tender.id, document_name="Bharat_Oil_Gas_Exp.pdf", file_path=b2_oil_pdf, document_type="EXPERIENCE_CERTIFICATE", page_count=1, extracted_text="Verified Oil & Gas experience: 8.5 Years."),
        Document(bidder_id=b2.id, tender_id=primary_tender.id, document_name="Bharat_Manpower.pdf", file_path=b2_man_pdf, document_type="PERSONNEL_CV", page_count=3, extracted_text="5 qualified pipeline engineers with >= 8 years experience."),
        Document(bidder_id=b2.id, tender_id=primary_tender.id, document_name="Bharat_HSE_Scanned.pdf", file_path=b2_hse_pdf, document_type="SAFETY_CERTIFICATE", page_count=1, extraction_method="TESSERACT_OCR", extracted_text="Provisional safety plan. Clarification required on ISO 45001 renewal stamp.")
    ]
    for d in docs_b2:
        db.add(d)
    db.commit()

    entities_b2 = [
        ExtractedEntity(document_id=docs_b2[0].id, entity_type="GSTIN", entity_value="27AABCB7890K1Z4", normalized_value="27AABCB7890K1Z4", confidence=0.98, page_number=1, context_snippet="GSTIN: 27AABCB7890K1Z4 Active"),
        ExtractedEntity(document_id=docs_b2[0].id, entity_type="PAN", entity_value="AABCB7890K", normalized_value="AABCB7890K", confidence=0.98, page_number=1, context_snippet="PAN: AABCB7890K"),
        ExtractedEntity(document_id=docs_b2[0].id, entity_type="COMPANY_NAME", entity_value="Bharat Hydrocarbon Infra Ltd", normalized_value="bharat hydrocarbon infra ltd", confidence=0.98, page_number=1, context_snippet="Bharat Hydrocarbon Infra Ltd"),
        ExtractedEntity(document_id=docs_b2[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2023-24: ₹29.00 Cr", normalized_value="290000000.0", confidence=0.96, page_number=1, context_snippet="FY 2023-24: INR 29.00 Crore"),
        ExtractedEntity(document_id=docs_b2[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2024-25: ₹28.50 Cr", normalized_value="285000000.0", confidence=0.96, page_number=1, context_snippet="FY 2024-25: INR 28.50 Crore"),
        ExtractedEntity(document_id=docs_b2[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2025-26: ₹28.00 Cr", normalized_value="280000000.0", confidence=0.96, page_number=1, context_snippet="FY 2025-26: INR 28.00 Crore"),
        ExtractedEntity(document_id=docs_b2[2].id, entity_type="OIL_GAS_PROJECT", entity_value="Western Gas Grid Pipeline", normalized_value="western gas grid pipeline", confidence=0.95, page_number=1, context_snippet="EPC execution of 115 km 24-inch natural gas transmission pipeline."),
        ExtractedEntity(document_id=docs_b2[2].id, entity_type="PIPELINE_LENGTH_KM", entity_value="115.0 km", normalized_value="115.0", confidence=0.95, page_number=1, context_snippet="Executed length: 115 KM"),
        ExtractedEntity(document_id=docs_b2[3].id, entity_type="OIL_GAS_EXPERIENCE_YEARS", entity_value="8.5 Years", normalized_value="8.5", confidence=0.95, page_number=1, context_snippet="Verified Oil & Gas experience: 8.5 Years"),
        ExtractedEntity(document_id=docs_b2[4].id, entity_type="MANPOWER_RECORD", entity_value="Amitabh Sen (11 yrs / 9 yrs pipeline)", normalized_value="9.0", confidence=0.93, page_number=1, context_snippet="Amitabh Sen - Senior Project Manager"),
        ExtractedEntity(document_id=docs_b2[4].id, entity_type="MANPOWER_RECORD", entity_value="Nitin Gadgil (10 yrs / 8.5 yrs pipeline)", normalized_value="8.5", confidence=0.93, page_number=2, context_snippet="Nitin Gadgil - Pipeline Construction Engineer"),
        ExtractedEntity(document_id=docs_b2[4].id, entity_type="MANPOWER_RECORD", entity_value="Kiran Joshi (9.5 yrs / 8.5 yrs pipeline)", normalized_value="8.5", confidence=0.93, page_number=3, context_snippet="Kiran Joshi - Chief Welding Inspector"),
        ExtractedEntity(document_id=docs_b2[4].id, entity_type="MANPOWER_RECORD", entity_value="Gaurav Deshmukh (9 yrs / 8 yrs pipeline)", normalized_value="8.0", confidence=0.93, page_number=4, context_snippet="Gaurav Deshmukh - NDT Level II Specialist"),
        ExtractedEntity(document_id=docs_b2[4].id, entity_type="MANPOWER_RECORD", entity_value="Pooja Kulkarni (8.5 yrs / 8 yrs pipeline)", normalized_value="8.0", confidence=0.93, page_number=5, context_snippet="Pooja Kulkarni - QA/QC Engineer"),
        ExtractedEntity(document_id=docs_b2[5].id, entity_type="HSE_CERTIFICATION", entity_value="Provisional ISO 45001:2018 (Renewal Verification Required)", normalized_value="PROVISIONAL_HSE", confidence=0.72, page_number=1, context_snippet="Provisional safety plan. Clarification required on ISO 45001 renewal stamp.")
    ]
    for ent in entities_b2:
        db.add(ent)
    db.commit()


    # =============================================================
    # BIDDER C — NON-COMPLIANT: Indus Pipeline Infrastructure Limited
    # =============================================================
    logger.info("Seeding Bidder C: Indus Pipeline Infrastructure Limited (Non-Compliant)...")
    b3 = Bidder(
        tender_id=primary_tender.id,
        legal_name="Indus Pipeline Infrastructure Limited",
        trade_name="Indus Pipeline",
        pan="AABCI5678K",
        gstin="07AABCI5678K1Z2",
        registered_address="Indus House, Barakhamba Road, Connaught Place, New Delhi 110001",
        contact_information={"email": "contracts@induspipeline.in", "phone": "+91 11 4120 7800"},
        bidder_type="INDIAN_EPC_CONTRACTOR",
        country="INDIA",
        oil_gas_experience_years=12.0,
        pipeline_experience_years=5.0,
        udyam_number="UDYAM-DL-04-0012948",
        cin="U45200DL2014PLC264819",
        email="contracts@induspipeline.in",
        phone="+91 11 4120 7800",
        contact_person="Ramesh K. Jindal (Director - Projects)",
        status="DISQUALIFIED"
    )
    db.add(b3)
    db.commit()
    db.refresh(b3)

    bid3 = Bid(
        tender_id=primary_tender.id,
        bidder_id=b3.id,
        bid_reference_number="BID-MOPNG-2026-INDUS-003",
        submission_date=datetime.now(timezone.utc) - timedelta(days=1),
        technical_bid_status="DISQUALIFIED",
        financial_bid_amount=2150000000.0,
        currency="INR",
        remarks="Disqualification: Executed pipeline length of 60 km fails mandatory tender threshold of 100 km."
    )
    db.add(bid3)

    p3_1 = BidderProject(
        bidder_id=b3.id,
        project_name="IOCL Mathura-Tundla Spur Pipeline Construction",
        client_name="Indian Oil Corporation Limited",
        client_type="PUBLIC_SECTOR_UNDERTAKING",
        sector="PETROLEUM",
        project_type="PIPELINE_CONSTRUCTION",
        pipeline_type="PRODUCT_PIPELINE",
        pipeline_length_km=60.0,
        pipeline_diameter="18 inch NB API 5L X60",
        project_value=480000000.0,
        currency="INR",
        location="Uttar Pradesh",
        start_date=datetime.now(timezone.utc) - timedelta(days=365*3),
        completion_date=datetime.now(timezone.utc) - timedelta(days=365*2),
        scope_of_work="Pipeline construction of 60 km petroleum spur line.",
        bidder_role="MAIN_CONTRACTOR",
        contract_reference="IOCL/MT/2019/08"
    )
    db.add(p3_1)

    staff_b3 = [
        BidderPersonnel(bidder_id=b3.id, name="Pankaj Verma", designation="Pipeline Engineer", qualification="B.E. Mechanical", years_of_experience=8.5, pipeline_experience_years=8.5),
        BidderPersonnel(bidder_id=b3.id, name="Sunil Kumar", designation="Mechanical Engineer", qualification="B.Tech Mechanical", years_of_experience=9.0, pipeline_experience_years=9.0),
        BidderPersonnel(bidder_id=b3.id, name="Ankit Mishra", designation="Safety Officer", qualification="Diploma Safety", years_of_experience=8.0, pipeline_experience_years=8.0)
    ]
    for s in staff_b3:
        db.add(s)

    b3_stat_pdf = os.path.join(settings.UPLOAD_DIR, "Indus_Statutory_GST_PAN.pdf")
    b3_fin_pdf = os.path.join(settings.UPLOAD_DIR, "Indus_Turnover_Statement.pdf")
    b3_exp_pdf = os.path.join(settings.UPLOAD_DIR, "Indus_60km_Pipeline_Certificate.pdf")
    b3_man_pdf = os.path.join(settings.UPLOAD_DIR, "Indus_Manpower_List.pdf")

    create_sample_pdf(b3_stat_pdf, "INDUS PIPELINE - STATUTORY REGISTRATION", [
        ("1. GSTIN & PAN", "Indus Pipeline Infrastructure Limited\nGSTIN: 07AABCI5678K1Z2 (Delhi)\nPAN: AABCI5678K\nStatus: ACTIVE")
    ])
    create_sample_pdf(b3_fin_pdf, "INDUS PIPELINE - FINANCIAL TURNOVER", [
        ("1. Three-Year Turnover", "FY 2023-24: INR 16.50 Crore\nFY 2024-25: INR 18.20 Crore\nFY 2025-26: INR 19.30 Crore\nThree-Year Average: INR 18.00 Crore (Below tender threshold of INR 25.00 Crore, Shortfall: INR 7.00 Crore).")
    ])
    create_sample_pdf(b3_exp_pdf, "INDUS PIPELINE - PIPELINE COMPLETION CERTIFICATE", [
        ("1. IOCL Spur Pipeline", "Client: Indian Oil Corporation Limited\nScope: Construction of 60 km, 18-inch OD spur pipeline.\nCompleted Length: 60 KM (Fails mandatory tender threshold of 100 KM).")
    ])
    create_sample_pdf(b3_man_pdf, "INDUS PIPELINE - TECHNICAL STAFF", [
        ("1. Manpower List", "Total qualifying technical personnel: 3 engineers (Fails mandatory threshold of 5 engineers).")
    ])

    docs_b3 = [
        Document(bidder_id=b3.id, tender_id=primary_tender.id, document_name="Indus_Statutory_GST_PAN.pdf", file_path=b3_stat_pdf, document_type="GST_CERTIFICATE", page_count=1, extracted_text="Indus Pipeline Infrastructure Limited\nGSTIN: 07AABCI5678K1Z2\nPAN: AABCI5678K"),
        Document(bidder_id=b3.id, tender_id=primary_tender.id, document_name="Indus_Turnover_Statement.pdf", file_path=b3_fin_pdf, document_type="FINANCIAL_STATEMENT", page_count=1, extracted_text="FY 2023-24: 16.50 Crore\nFY 2024-25: 18.20 Crore\nFY 2025-26: 19.30 Crore\nAverage Turnover: 18.00 Crore (Shortfall: 7.00 Crore)."),
        Document(bidder_id=b3.id, tender_id=primary_tender.id, document_name="Indus_60km_Pipeline_Certificate.pdf", file_path=b3_exp_pdf, document_type="PIPELINE_PROJECT_DOCUMENT", page_count=1, extracted_text="Construction of 60 km spur pipeline for IOCL. Successfully completed 60 km length (18-inch OD)."),
        Document(bidder_id=b3.id, tender_id=primary_tender.id, document_name="Indus_Manpower_List.pdf", file_path=b3_man_pdf, document_type="PERSONNEL_CV", page_count=1, extracted_text="Pankaj Verma (Pipeline Engineer) - 8.5 years\nSunil Kumar (Mechanical Engineer) - 9.0 years\nAnkit Mishra (Safety Officer) - 8.0 years\nTotal: 3 engineers.")
    ]
    for d in docs_b3:
        db.add(d)
    db.commit()

    entities_b3 = [
        ExtractedEntity(document_id=docs_b3[0].id, entity_type="GSTIN", entity_value="07AABCI5678K1Z2", normalized_value="07AABCI5678K1Z2", confidence=0.98, page_number=1, context_snippet="GSTIN: 07AABCI5678K1Z2 Active"),
        ExtractedEntity(document_id=docs_b3[0].id, entity_type="PAN", entity_value="AABCI5678K", normalized_value="AABCI5678K", confidence=0.98, page_number=1, context_snippet="PAN: AABCI5678K (Indus Pipeline)"),
        ExtractedEntity(document_id=docs_b3[0].id, entity_type="COMPANY_NAME", entity_value="Indus Pipeline Infrastructure Limited", normalized_value="indus pipeline infrastructure ltd", confidence=0.98, page_number=1, context_snippet="Indus Pipeline Infrastructure Limited"),
        ExtractedEntity(document_id=docs_b3[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2023-24: ₹16.50 Cr", normalized_value="165000000.0", confidence=0.95, page_number=1, context_snippet="FY 2023-24: INR 16.50 Crore"),
        ExtractedEntity(document_id=docs_b3[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2024-25: ₹18.20 Cr", normalized_value="182000000.0", confidence=0.95, page_number=1, context_snippet="FY 2024-25: INR 18.20 Crore"),
        ExtractedEntity(document_id=docs_b3[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2025-26: ₹19.30 Cr", normalized_value="193000000.0", confidence=0.95, page_number=1, context_snippet="FY 2025-26: INR 19.30 Crore"),
        ExtractedEntity(document_id=docs_b3[2].id, entity_type="OIL_GAS_PROJECT", entity_value="IOCL Mathura-Tundla Spur Pipeline", normalized_value="iocl mathura tundla spur pipeline", confidence=0.94, page_number=1, context_snippet="Construction of 60 km spur pipeline for IOCL."),
        ExtractedEntity(document_id=docs_b3[2].id, entity_type="PIPELINE_LENGTH_KM", entity_value="60.0 km", normalized_value="60.0", confidence=0.96, page_number=1, context_snippet="Construction of 60 km spur pipeline for IOCL (Fails 100 KM threshold)"),
        ExtractedEntity(document_id=docs_b3[3].id, entity_type="MANPOWER_RECORD", entity_value="Pankaj Verma (Pipeline Engineer - 8.5 years)", normalized_value="8.5", confidence=0.95, page_number=1, context_snippet="Pankaj Verma (Pipeline Engineer) - 8.5 years"),
        ExtractedEntity(document_id=docs_b3[3].id, entity_type="MANPOWER_RECORD", entity_value="Sunil Kumar (Mechanical Engineer - 9.0 years)", normalized_value="9.0", confidence=0.95, page_number=1, context_snippet="Sunil Kumar (Mechanical Engineer) - 9.0 years"),
        ExtractedEntity(document_id=docs_b3[3].id, entity_type="MANPOWER_RECORD", entity_value="Ankit Mishra (Safety Officer - 8.0 years)", normalized_value="8.0", confidence=0.95, page_number=1, context_snippet="Ankit Mishra (Safety Officer) - 8.0 years")
    ]
    for ent in entities_b3:
        db.add(ent)
    db.commit()

    # 5. EXECUTE VERIFICATION ON THE THREE BIDDERS
    logger.info("Executing Phase 3 Compliance Engine on all 3 Bidders...")
    for b in [b1, b2, b3]:
        res = ComplianceEngine.run_full_verification(
            db=db,
            bidder_id=b.id,
            officer_id=officer_user.id,
            officer_name=officer_user.name
        )
        logger.info(f"Verified Bidder '{b.legal_name}': Score={res.get('compliance_score')}%, Risk={res.get('risk_level')}, Status={res.get('status')}")

    # Set appropriate final officer decisions and statuses matching specification
    # Bidder A: Qualified
    b1.status = "VERIFIED"
    rev1 = OfficerReview(
        bidder_id=b1.id,
        officer_id=officer_user.id,
        officer_name=officer_user.name,
        previous_status="UNDER_REVIEW",
        new_status="PASSED",
        action_type="APPROVE",
        remarks="All statutory, financial, technical pipeline (135 KM), and HSE requirements fully substantiated with auditable evidence. Bidder qualified for financial opening.",
        reviewed_at=datetime.now(timezone.utc) - timedelta(hours=2)
    )
    db.add(rev1)

    # Bidder B: Under Review
    b2.status = "UNDER_REVIEW"
    rev2 = OfficerReview(
        bidder_id=b2.id,
        officer_id=officer_user.id,
        officer_name=officer_user.name,
        previous_status="UNDER_REVIEW",
        new_status="UNDER_REVIEW",
        action_type="REVIEW",
        remarks="HSE certification requires submission of renewed ISO 45001 endorsement letter. Clarification notice issued to bidder with 48-hour response window.",
        reviewed_at=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    db.add(rev2)

    # Bidder C: Disqualified
    b3.status = "DISQUALIFIED"
    rev3 = OfficerReview(
        bidder_id=b3.id,
        officer_id=officer_user.id,
        officer_name=officer_user.name,
        previous_status="UNDER_REVIEW",
        new_status="REJECTED",
        action_type="REJECT",
        remarks="Non-Compliant: Executed pipeline length of 60 km falls 40 km short of the mandatory 100 km threshold. Technical bid disqualified under GFR Rule 173(v).",
        reviewed_at=datetime.now(timezone.utc) - timedelta(minutes=30)
    )
    db.add(rev3)
    db.commit()

    # Log initial GFR 2017 Audit entries
    AuditService.log_action(
        db=db,
        action="TENDER_PUBLISHED",
        entity_type="TENDER",
        entity_id=primary_tender.id,
        user_id=officer_user.id,
        user_name=officer_user.name,
        tender_id=primary_tender.id,
        reason="Official publication of MOPNG/PIPE/2026/017 on GeM Portal with 7 GFR 2017 compliance clauses."
    )

    AuditService.log_action(
        db=db,
        action="OFFICER_DETERMINATION",
        entity_type="BIDDER",
        entity_id=b1.id,
        user_id=officer_user.id,
        user_name=officer_user.name,
        tender_id=primary_tender.id,
        bidder_id=b1.id,
        new_state={"decision": "Qualified", "score": 100.0, "risk": "LOW"},
        reason="Procurement Officer determination: PRAVEEN B S ENGINEERING SERVICES Qualified for Financial Opening."
    )

    db.close()
    logger.info("Demo database seeding successfully completed! (1 Tender, 7 Requirements, 3 Bidders, 100% Consistent)")

if __name__ == "__main__":
    seed_demo()
