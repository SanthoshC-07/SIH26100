import os
import fitz  # PyMuPDF
from datetime import datetime, timezone, timedelta
from app.core.database import Base, engine, SessionLocal
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.models import (
    User, Tender, Requirement, Bidder, Bid, BidderProject, BidderPersonnel,
    Document, DocumentPage, ExtractedEntity
)
from app.services.compliance_engine import ComplianceEngine
from app.core.logging_config import logger

def create_sample_pdf(file_path: str, title: str, sections: list):
    """Generates a professional formatted PDF document using PyMuPDF."""
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

def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    logger.info("Seeding Users (1 Admin, 1 Senior Procurement Officer, 1 Registered Bidder)...")
    
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
        name="Praveen B S, EPC Contractor",
        email="vendor@company.com",
        username="bidder",
        password_hash=get_password_hash("bidder123"),
        role="BIDDER",
        department="Praveen B S Engineering Services - Tender & Bidding Division"
    )
    db.add(bidder_user)

    db.commit()
    db.refresh(admin_user)
    db.refresh(officer_user)
    db.refresh(bidder_user)

    # -------------------------------------------------------------
    # 3 REALISTIC PETROLEUM & NATURAL GAS PIPELINE TENDERS
    # -------------------------------------------------------------
    logger.info("Seeding 3 Realistic Petroleum & Pipeline Tenders...")

    t1_doc = os.path.join(settings.UPLOAD_DIR, "Tender_MOPNG_PIPE_2026_017.pdf")
    create_sample_pdf(
        t1_doc,
        "MOPNG TENDER: MOPNG/PIPE/2026/017 - NATURAL GAS TRANSMISSION PIPELINE",
        [
            ("1. Scope of Work", "Laying, Testing, and Commissioning of 150 km, 24-inch Outer Diameter API 5L Grade X70 Cross-Country Natural Gas Transmission Pipeline including Sectionalizing Valve Stations and Intermediate Pigging Stations."),
            ("2. Check 1 (R01): GST Statutory Registration", "Bidder must possess valid and active GSTIN registration in the relevant State/UT and submit latest GSTR-3B filings."),
            ("3. Check 2 (R02): PAN & Identity", "Bidder entity must hold a valid Permanent Account Number (PAN) issued by Income Tax Department matching corporate legal identity."),
            ("4. Check 3 (R03): Financial Turnover", "Average Annual Financial Turnover of the bidder during the last 3 preceding financial years (FY 2023-24, FY 2024-25, FY 2025-26) must be at least INR 25.00 Crore."),
            ("5. Check 4 (R04): Oil & Gas Experience", "Bidder must possess proven prior execution experience of minimum 7 years in EPC / construction projects in Petroleum, Natural Gas, Refinery, or Hydrocarbon pipeline sectors."),
            ("6. Check 5 (R05): Similar Pipeline Experience", "Bidder must have successfully constructed and commissioned at least one cross-country high-pressure natural gas transmission pipeline of minimum 100 km length (24-inch or higher) in the last 7 years."),
            ("7. Check 6 (R06): Technical Manpower", "Bidder must commit and deploy a minimum of 5 qualified pipeline engineers (B.Tech / B.E. Mechanical / Pipeline / NDT Level II) with at least 8 years of relevant site experience."),
            ("8. Check 7 (R07): HSE & Safety Compliance", "Bidder must maintain certified Occupational Health & Safety (ISO 45001) and Environmental Management (ISO 14001) systems with a zero-fatality site safety policy.")
        ]
    )

    tender1 = Tender(
        tender_number="MOPNG/PIPE/2026/017",
        title="Construction of Natural Gas Transmission Pipeline",
        issuing_organization="Ministry of Petroleum & Natural Gas / GAIL",
        ministry="Ministry of Petroleum & Natural Gas",
        sector="OIL_AND_GAS",
        tender_type="PIPELINE_PROCUREMENT",
        project_type="PIPELINE_CONSTRUCTION",
        pipeline_type="NATURAL_GAS_TRANSMISSION",
        location="National Gas Grid, Vijaipur-Auraiya Corridor, India",
        description="EPC contract for 150 km, 24-inch NB API 5L X70 cross-country natural gas transmission pipeline laying, HDD river crossings, SV stations, and pre-commissioning.",
        estimated_value=2400000000.0,
        tender_issue_date=datetime.now(timezone.utc) - timedelta(days=12),
        submission_deadline=datetime.now(timezone.utc) + timedelta(days=18),
        evaluation_date=datetime.now(timezone.utc) + timedelta(days=25),
        status="UNDER_EVALUATION",
        raw_pdf_path=t1_doc,
        created_by=officer_user.id
    )
    db.add(tender1)

    t2_doc = os.path.join(settings.UPLOAD_DIR, "Tender_IOCL_2026_PL_VALVES_5810.pdf")
    create_sample_pdf(
        t2_doc,
        "IOCL TENDER: IOCL/2026/PL-VALVES/5810",
        [
            ("1. Scope of Work", "Supply & Installation of API 6D Full-Bore Ball Valves and Gas Turbine Compressor Skids for Koyali-Ahmedabad Product Pipeline."),
            ("2. Statutory & Financial", "Active GSTIN, PAN, and minimum average annual turnover of INR 25.00 Crore."),
            ("3. Experience", "Prior execution in Petroleum pipeline valve stations."),
            ("4. Check 7: OEM Manufacturer Authorization", "Manufacturer Authorization Form (MAF) from certified API 6D valve manufacturer explicitly referencing Tender No: IOCL/2026/PL-VALVES/5810.")
        ]
    )

    tender2 = Tender(
        tender_number="IOCL/2026/PL-VALVES/5810",
        title="Supply & Commissioning of High-Pressure API 6D Pipeline Valves & Actuators",
        issuing_organization="Indian Oil Corporation Limited (IOCL) - Pipelines Division",
        ministry="Ministry of Petroleum & Natural Gas",
        sector="OIL_AND_GAS",
        tender_type="PIPELINE_PROCUREMENT",
        project_type="PIPELINE_EPC",
        pipeline_type="PRODUCT_PIPELINE",
        location="Koyali-Ahmedabad Pipeline Network",
        description="Procurement of Class 600 full-bore motorized ball valves and gas turbine driven pump skids.",
        estimated_value=650000000.0,
        tender_issue_date=datetime.now(timezone.utc) - timedelta(days=6),
        submission_deadline=datetime.now(timezone.utc) + timedelta(days=24),
        evaluation_date=datetime.now(timezone.utc) + timedelta(days=30),
        status="ACTIVE",
        raw_pdf_path=t2_doc,
        created_by=officer_user.id
    )
    db.add(tender2)

    t3_doc = os.path.join(settings.UPLOAD_DIR, "Tender_ONGC_2026_MII_3320.pdf")
    create_sample_pdf(
        t3_doc,
        "ONGC TENDER: ONGC/2026/MII/3320",
        [
            ("1. Scope of Work", "Construction of 80 km Offshore to Onshore Gas Feeder Line at Hazira."),
            ("2. Statutory & Financial", "Active GSTIN, PAN, and minimum average annual turnover of INR 25.00 Crore."),
            ("3. Experience & Manpower", "Oil & Gas subsea/onshore pipeline experience and qualified engineering manpower."),
            ("4. Check 7: Make in India Local Content", "Minimum 50% Local Content requirement (Class-I Local Supplier under MoPNG PPP-MII policy).")
        ]
    )

    tender3 = Tender(
        tender_number="ONGC/2026/MII/3320",
        title="Hazira Gas Plant 80 km High-Pressure Feeder Pipeline Construction",
        issuing_organization="Oil and Natural Gas Corporation (ONGC) Limited",
        ministry="Ministry of Petroleum & Natural Gas",
        sector="OIL_AND_GAS",
        tender_type="PIPELINE_PROCUREMENT",
        project_type="PIPELINE_CONSTRUCTION",
        pipeline_type="OFFSHORE_FEEDER",
        location="Hazira Offshore Gas Field, Gujarat",
        description="EPC pipeline laying with 50% domestic value addition compliance under MoPNG Make in India policy.",
        estimated_value=1200000000.0,
        tender_issue_date=datetime.now(timezone.utc) - timedelta(days=3),
        submission_deadline=datetime.now(timezone.utc) + timedelta(days=27),
        evaluation_date=datetime.now(timezone.utc) + timedelta(days=35),
        status="ACTIVE",
        raw_pdf_path=t3_doc,
        created_by=officer_user.id
    )
    db.add(tender3)

    db.commit()
    db.refresh(tender1)
    db.refresh(tender2)
    db.refresh(tender3)

    # -------------------------------------------------------------
    # 7 CORE REQUIREMENTS FOR TENDER 1 (MOPNG/PIPE/2026/017)
    # -------------------------------------------------------------
    logger.info("Adding 7 Core Requirements (R01-R07) to Tender 1...")
    reqs_t1 = [
        Requirement(
            tender_id=tender1.id,
            category="GST",
            clause_number="R01",
            original_text="Check 1 (R01): Bidder must possess valid and active GSTIN registration in the relevant State/UT and submit latest GSTR-3B filings.",
            normalized_requirement="Active GSTIN Registration with latest monthly GSTR-3B filings.",
            mandatory=True,
            threshold=None,
            threshold_unit=None,
            period="CURRENT_ACTIVE",
            evidence_required=["GST_REGISTRATION_CERTIFICATE", "LATEST_GSTR_3B_FILING"],
            verification_method="PORTAL_AND_RULE"
        ),
        Requirement(
            tender_id=tender1.id,
            category="PAN",
            clause_number="R02",
            original_text="Check 2 (R02): Bidder entity must hold a valid Permanent Account Number (PAN) issued by Income Tax Department with matching legal corporate identity.",
            normalized_requirement="Valid PAN issued to exact legal entity.",
            mandatory=True,
            threshold=None,
            threshold_unit=None,
            period="PERMANENT",
            evidence_required=["PAN_CARD", "ITR_ACKNOWLEDGEMENTS"],
            verification_method="PORTAL_AND_RULE"
        ),
        Requirement(
            tender_id=tender1.id,
            category="TURNOVER",
            clause_number="R03",
            original_text="Check 3 (R03): Average Annual Financial Turnover of the bidder during the last 3 preceding financial years (FY 2023-24, FY 2024-25, FY 2025-26) must be at least INR 25.00 Crore.",
            normalized_requirement="Average Annual Turnover >= INR 25.00 Crore over last 3 FYs.",
            mandatory=True,
            threshold=250000000.0,
            threshold_unit="INR",
            period="LAST_3_FINANCIAL_YEARS",
            evidence_required=["AUDITED_BALANCE_SHEETS", "CA_CERTIFIED_TURNOVER_STATEMENT"],
            verification_method="RULE_AND_ARITHMETIC"
        ),
        Requirement(
            tender_id=tender1.id,
            category="OIL_GAS_EXPERIENCE",
            clause_number="R04",
            original_text="Check 4 (R04): Bidder must possess proven prior execution experience of >= 7 years in EPC / construction projects in Petroleum, Natural Gas, Refinery, or Hydrocarbon pipeline sectors.",
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
            tender_id=tender1.id,
            category="SIMILAR_PIPELINE_EXPERIENCE",
            clause_number="R05",
            original_text="Check 5 (R05): Bidder must have successfully constructed and commissioned at least one cross-country high-pressure natural gas transmission pipeline of minimum 100 km length (24-inch or higher) in the last 7 years.",
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
            tender_id=tender1.id,
            category="TECHNICAL_MANPOWER",
            clause_number="R06",
            original_text="Check 6 (R06): Bidder must commit and deploy a minimum of 5 qualified pipeline engineers (B.Tech / B.E. Mechanical / Pipeline / NDT Level II) with at least 8 years of relevant site experience.",
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
            tender_id=tender1.id,
            category="HSE_SAFETY",
            clause_number="R07",
            original_text="Check 7 (R07): Bidder must maintain certified Occupational Health & Safety (ISO 45001) and Environmental Management (ISO 14001) systems with a zero-fatality site safety policy.",
            normalized_requirement="Certified ISO 45001:2018 and ISO 14001:2015 with zero-fatality HSE site policy.",
            mandatory=True,
            threshold=None,
            threshold_unit=None,
            period="VALID_CERTIFICATION",
            evidence_required=["ISO_45001_CERTIFICATE", "ISO_14001_CERTIFICATE", "CORPORATE_SAFETY_POLICY"],
            verification_method="CERTIFICATION_VERIFIER"
        )
    ]
    for r in reqs_t1:
        db.add(r)
    db.commit()

    # -------------------------------------------------------------
    # 4 REALISTIC DEMONSTRATION BIDDERS FOR TENDER 1
    # -------------------------------------------------------------
    logger.info("Seeding 4 Realistic Petroleum Bidders with Project & Manpower Records...")

    # =============================================================
    # BIDDER 1: PRAVEEN B S ENGINEERING SERVICES (PASS/REVIEW - SCORE: 86%, RISK: MEDIUM)
    # =============================================================
    b1 = Bidder(
        tender_id=tender1.id,
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
        status="SUBMITTED",
        user_id=bidder_user.id
    )
    db.add(b1)
    db.commit()
    db.refresh(b1)

    bidder_user.bidder_id = b1.id
    db.commit()

    # Bid Submission for Bidder 1
    bid1 = Bid(
        tender_id=tender1.id,
        bidder_id=b1.id,
        bid_reference_number="BID-MOPNG-2026-PBS-001",
        submission_date=datetime.now(timezone.utc) - timedelta(days=2),
        technical_bid_status="UNDER_EVALUATION",
        financial_bid_amount=2320000000.0,
        currency="INR",
        remarks="Complete technical & financial bid submitted with evidence for checks R01 to R07."
    )
    db.add(bid1)

    # Structured BidderProject records for Bidder 1
    p1_1 = BidderProject(
        bidder_id=b1.id,
        project_name="Natural Gas Transmission Pipeline Project (Section 4)",
        client_name="GAIL (India) Limited",
        client_type="PUBLIC_SECTOR_UNDERTAKING",
        sector="OIL_AND_GAS",
        project_type="PIPELINE_CONSTRUCTION",
        pipeline_type="NATURAL_GAS_TRANSMISSION",
        pipeline_length_km=135.0,
        pipeline_diameter="24 Inch NB API 5L X70",
        project_value=820000000.0,
        currency="INR",
        location="Gujarat & Madhya Pradesh Corridor",
        start_date=datetime.now(timezone.utc) - timedelta(days=365*3),
        completion_date=datetime.now(timezone.utc) - timedelta(days=175),
        scope_of_work="EPC Contractor for 135 KM 24-inch natural gas transmission pipeline laying, HDD river crossings, SV stations, and pre-commissioning",
        bidder_role="EPC_CONTRACTOR",
        contract_reference="GAIL/NGPL/SEC-4/2022/09"
    )
    p1_2 = BidderProject(
        bidder_id=b1.id,
        project_name="IOCL Refinery Crude Oil Feeder Line",
        client_name="Indian Oil Corporation Limited",
        client_type="PUBLIC_SECTOR_UNDERTAKING",
        sector="OIL_AND_GAS",
        project_type="PIPELINE_EPC",
        pipeline_type="CRUDE_OIL",
        pipeline_length_km=85.0,
        pipeline_diameter="18 Inch NB API 5L X65",
        project_value=450000000.0,
        currency="INR",
        location="Gujarat",
        start_date=datetime.now(timezone.utc) - timedelta(days=365*4),
        completion_date=datetime.now(timezone.utc) - timedelta(days=365*2),
        scope_of_work="Crude oil pipeline laying and pump station integration",
        bidder_role="MAIN_CONTRACTOR",
        contract_reference="IOCL/REF/PL/2021/03"
    )
    db.add(p1_1)
    db.add(p1_2)

    # Structured BidderPersonnel records for Bidder 1 (5 engineers >= 8 years)
    staff_b1 = [
        BidderPersonnel(bidder_id=b1.id, name="Praveen B S", designation="Project Engineer", qualification="B.Tech Mechanical", specialization="Natural Gas Cross-Country Pipeline", years_of_experience=12.0, pipeline_experience_years=9.0, certifications=["PMP", "API 1169"]),
        BidderPersonnel(bidder_id=b1.id, name="Ravi Kumar", designation="Pipeline Engineer", qualification="B.Tech Mechanical", specialization="High-Pressure Transmission Piping & HDD", years_of_experience=11.0, pipeline_experience_years=10.0, certifications=["NDT Level II"]),
        BidderPersonnel(bidder_id=b1.id, name="Suresh Sharma", designation="Chief Welding & NDT Specialist", qualification="B.E. Metallurgy", specialization="API 1104 Automatic Welding & Radiography", years_of_experience=10.0, pipeline_experience_years=9.0, certifications=["NDT Level III", "CSWIP 3.1"]),
        BidderPersonnel(bidder_id=b1.id, name="Ananya Rao", designation="QA/QC Pipeline Inspector", qualification="B.Tech Mechanical", specialization="Hydrotesting & Pipeline Integrity", years_of_experience=9.0, pipeline_experience_years=8.0, certifications=["ISO 9001 Lead Auditor"]),
        BidderPersonnel(bidder_id=b1.id, name="Vikram Patel", designation="Lead Site Safety Officer", qualification="Diploma Industrial Safety", specialization="Petroleum Site Safety & ISO 45001", years_of_experience=9.0, pipeline_experience_years=8.0, certifications=["NEBOSH IGC", "ISO 45001 Lead Auditor"])
    ]
    for s in staff_b1:
        db.add(s)

    # Documents for Bidder 1
    b1_stat_pdf = os.path.join(settings.UPLOAD_DIR, "Praveen_Statutory_GST_PAN.pdf")
    b1_fin_pdf = os.path.join(settings.UPLOAD_DIR, "Financial_Statement_Praveen.pdf")
    b1_exp_pdf = os.path.join(settings.UPLOAD_DIR, "Pipeline_Completion_Certificate_Praveen.pdf")
    b1_oil_pdf = os.path.join(settings.UPLOAD_DIR, "Oil_Gas_Experience_Certificate.pdf")
    b1_man_pdf = os.path.join(settings.UPLOAD_DIR, "Praveen_Engineers_CVs.pdf")
    b1_hse_pdf = os.path.join(settings.UPLOAD_DIR, "Praveen_HSE_ISO45001_Policy.pdf")

    create_sample_pdf(
        b1_stat_pdf,
        "PRAVEEN B S ENGINEERING SERVICES - STATUTORY REGISTRATION CERTIFICATES",
        [
            ("1. Legal Entity & GSTIN Registration", "Legal Name: PRAVEEN B S ENGINEERING SERVICES\nTrade Name: Praveen B S Engineering Services\nGSTIN: 29MOCKP1234M1Z5 (Karnataka)\nRegistration Date: 01/07/2017\nStatus: ACTIVE\nTaxpayer Type: Regular"),
            ("2. Permanent Account Number (PAN)", "PAN: BSZPP1234K\nName as per ITD: PRAVEEN B S ENGINEERING SERVICES\nCategory: Company | Status: Active & Operational"),
            ("3. Udyam Registration", "UDYAM Registration No: UDYAM-KA-03-0087412 | Major Activity: Heavy Engineering / Petroleum Pipeline Construction")
        ]
    )

    create_sample_pdf(
        b1_fin_pdf,
        "PRAVEEN B S ENGINEERING SERVICES - CA AUDITED FINANCIAL TURNOVER",
        [
            ("1. Independent Chartered Accountant Certificate", "We have audited the books of accounts of M/s PRAVEEN B S ENGINEERING SERVICES. The annual turnover is certified as follows:"),
            ("2. Financial Year Breakdown", "FY 2023-24: INR 30 Crore\nFY 2024-25: INR 27 Crore\nFY 2025-26: INR 24 Crore"),
            ("3. Three-Year Arithmetic Average", "The bidder reported annual turnover of INR 30 Crore for FY 2023-24, INR 27 Crore for FY 2024-25 and INR 24 Crore for FY 2025-26.\nAverage Annual Turnover = (30 + 27 + 24) / 3 = INR 27 Crore (Exceeds mandatory tender requirement of INR 25 Crore).")
        ]
    )

    create_sample_pdf(
        b1_exp_pdf,
        "PRAVEEN B S ENGINEERING SERVICES - PIPELINE COMPLETION CERTIFICATE",
        [
            ("1. Client Completion Certificate", "Client: GAIL (India) Limited\nProject: Natural Gas Transmission Pipeline Project (Section 4)\nLength: 135 KM | Diameter: 24 Inch NB API 5L X70\nContract Value: INR 82 Crore\nCompletion Date: 15-03-2025\nRole: EPC Contractor\nStatus: Completed 135 KM natural gas transmission pipeline successfully commissioned.")
        ]
    )

    create_sample_pdf(
        b1_oil_pdf,
        "PRAVEEN B S ENGINEERING SERVICES - OIL & GAS EXPERIENCE SUMMARY",
        [
            ("1. Prior Oil & Gas Pipeline Sector Experience", "Total verified experience in Petroleum, Natural Gas, and Hydrocarbon sector: 9 Years.\nCompleted Projects: 3 major EPC pipeline projects for GAIL, IOCL, and ONGC.\nSemantic Relevance: High - Hydrocarbon and Cross-Country Natural Gas Pipelines.")
        ]
    )

    create_sample_pdf(
        b1_man_pdf,
        "PRAVEEN B S ENGINEERING SERVICES - KEY TECHNICAL MANPOWER DOSSIER",
        [
            ("1. Technical Engineering Personnel", "1. Praveen B S (Project Engineer) - B.Tech Mechanical - 12 Years total exp, 9 Years pipeline exp\n2. Ravi Kumar (Pipeline Engineer) - B.Tech Mechanical - 11 Years total exp, 10 Years pipeline exp\n3. Suresh Sharma (Welding & NDT Specialist) - B.E. Metallurgy - 10 Years total exp, 9 Years pipeline exp\n4. Ananya Rao (QA/QC Pipeline Inspector) - B.Tech Mechanical - 9 Years total exp, 8 Years pipeline exp\n5. Vikram Patel (Lead Site Safety Officer) - Diploma Industrial Safety - 9 Years total exp, 8 Years pipeline exp\nTotal qualifying pipeline engineers: 5 with >= 8 years relevant experience.")
        ]
    )

    create_sample_pdf(
        b1_hse_pdf,
        "PRAVEEN B S ENGINEERING SERVICES - HSE COMPLIANCE & SAFETY DOSSIER",
        [
            ("1. Occupational Health & Environmental Certifications", "ISO 45001:2018 (Occupational Health and Safety Management System)\nISO 14001:2015 (Environmental Management System)\nCertificate Valid Until: 31-12-2026\nSafety Record: Zero-fatality policy maintained on all pipeline sites.")
        ]
    )

    docs_b1 = [
        Document(bidder_id=b1.id, tender_id=tender1.id, document_name="GST_Registration_Certificate.pdf", original_filename="GST_Registration_Certificate.pdf", file_path=b1_stat_pdf, document_type="GST_CERTIFICATE", page_count=1, extracted_text="Legal Name: PRAVEEN B S ENGINEERING SERVICES\nTrade Name: Praveen B S Engineering Services\nGSTIN: 29MOCKP1234M1Z5 (Karnataka)\nStatus: ACTIVE\nTaxpayer Type: Regular\nPAN: BSZPP1234K"),
        Document(bidder_id=b1.id, tender_id=tender1.id, document_name="Financial_Statement.pdf", original_filename="Financial_Statement.pdf", file_path=b1_fin_pdf, document_type="FINANCIAL_STATEMENT", page_count=3, extracted_text="The bidder reported annual turnover of INR 30 Crore for FY 2023-24, INR 27 Crore for FY 2024-25 and INR 24 Crore for FY 2025-26.\nAverage Annual Turnover = INR 27 Crore."),
        Document(bidder_id=b1.id, tender_id=tender1.id, document_name="Pipeline_Completion_Certificate.pdf", original_filename="Pipeline_Completion_Certificate.pdf", file_path=b1_exp_pdf, document_type="PIPELINE_PROJECT_DOCUMENT", page_count=4, extraction_method="PyMuPDF", extracted_text="Client: GAIL (India) Limited\nProject: Natural Gas Transmission Pipeline\nLength: 135 KM\nDiameter: 24 Inch\nValue: INR 82 Crore\nCompletion: 15-03-2025\nRole: EPC Contractor\nCompleted 135 KM natural gas transmission pipeline successfully commissioned."),
        Document(bidder_id=b1.id, tender_id=tender1.id, document_name="Oil_Gas_Experience_Summary.pdf", original_filename="Oil_Gas_Experience_Summary.pdf", file_path=b1_oil_pdf, document_type="EXPERIENCE_CERTIFICATE", page_count=2, extracted_text="Total verified experience in Petroleum, Natural Gas, and Hydrocarbon sector: 9 Years across 3 projects."),
        Document(bidder_id=b1.id, tender_id=tender1.id, document_name="Technical_Manpower_CVs.pdf", original_filename="Technical_Manpower_CVs.pdf", file_path=b1_man_pdf, document_type="PERSONNEL_CV", page_count=5, extracted_text="Praveen B S - Project Engineer - B.Tech Mechanical - 12 Years exp - 9 Years pipeline\nRavi Kumar - Pipeline Engineer - B.Tech Mechanical - 11 Years exp - 10 Years pipeline\nSuresh Sharma - Welding & NDT Specialist - B.E. Metallurgy - 10 Years exp - 9 Years pipeline\nAnanya Rao - QA/QC Pipeline Inspector - B.Tech Mechanical - 9 Years exp - 8 Years pipeline\nVikram Patel - Lead Site Safety Officer - Diploma Safety - 9 Years exp - 8 Years pipeline"),
        Document(bidder_id=b1.id, tender_id=tender1.id, document_name="HSE_ISO45001_Safety_Dossier.pdf", original_filename="HSE_ISO45001_Safety_Dossier.pdf", file_path=b1_hse_pdf, document_type="SAFETY_CERTIFICATE", page_count=3, extracted_text="ISO 45001:2018 Certified\nISO 14001:2015 Certified\nZero-fatality site safety policy")
    ]
    for d in docs_b1:
        db.add(d)
    db.commit()

    entities_b1 = [
        ExtractedEntity(document_id=docs_b1[0].id, entity_type="GSTIN", entity_value="29MOCKP1234M1Z5", normalized_value="29MOCKP1234M1Z5", confidence=0.97, page_number=1, context_snippet="GSTIN: 29MOCKP1234M1Z5 Active Regular"),
        ExtractedEntity(document_id=docs_b1[0].id, entity_type="PAN", entity_value="BSZPP1234K", normalized_value="BSZPP1234K", confidence=0.98, page_number=1, context_snippet="PAN: BSZPP1234K (PRAVEEN B S ENGINEERING SERVICES)"),
        ExtractedEntity(document_id=docs_b1[0].id, entity_type="COMPANY_NAME", entity_value="PRAVEEN B S ENGINEERING SERVICES", normalized_value="praveen b s engineering services", confidence=0.98, page_number=1, context_snippet="PRAVEEN B S ENGINEERING SERVICES"),
        ExtractedEntity(document_id=docs_b1[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2023-24: INR 30 Crore", normalized_value="300000000.0", confidence=0.96, page_number=3, context_snippet="FY 2023-24: INR 30 Crore"),
        ExtractedEntity(document_id=docs_b1[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2024-25: INR 27 Crore", normalized_value="270000000.0", confidence=0.96, page_number=3, context_snippet="FY 2024-25: INR 27 Crore"),
        ExtractedEntity(document_id=docs_b1[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2025-26: INR 24 Crore", normalized_value="240000000.0", confidence=0.96, page_number=3, context_snippet="FY 2025-26: INR 24 Crore"),
        ExtractedEntity(document_id=docs_b1[2].id, entity_type="OIL_GAS_PROJECT", entity_value="Natural Gas Transmission Pipeline (Section 4)", normalized_value="natural gas transmission pipeline section 4", confidence=0.95, page_number=4, context_snippet="Completed 135 KM natural gas transmission pipeline successfully commissioned."),
        ExtractedEntity(document_id=docs_b1[2].id, entity_type="PIPELINE_LENGTH_KM", entity_value="135.0 km", normalized_value="135.0", confidence=0.95, page_number=4, context_snippet="Length: 135 KM 24 Inch NB API 5L X70"),
        ExtractedEntity(document_id=docs_b1[3].id, entity_type="OIL_GAS_EXPERIENCE_YEARS", entity_value="9.0 Years", normalized_value="9.0", confidence=0.94, page_number=1, context_snippet="Total verified experience in Petroleum, Natural Gas: 9 Years"),
        ExtractedEntity(document_id=docs_b1[4].id, entity_type="MANPOWER_RECORD", entity_value="Praveen B S (Project Engineer - 12 years / 9 years pipeline)", normalized_value="9.0", confidence=0.93, page_number=1, context_snippet="Praveen B S - Project Engineer - B.Tech Mechanical"),
        ExtractedEntity(document_id=docs_b1[4].id, entity_type="MANPOWER_RECORD", entity_value="Ravi Kumar (Pipeline Engineer - 11 years / 10 years pipeline)", normalized_value="10.0", confidence=0.93, page_number=2, context_snippet="Ravi Kumar - Pipeline Engineer - B.Tech Mechanical"),
        ExtractedEntity(document_id=docs_b1[4].id, entity_type="MANPOWER_RECORD", entity_value="Suresh Sharma (Chief Welding & NDT - 10 years / 9 years pipeline)", normalized_value="9.0", confidence=0.93, page_number=3, context_snippet="Suresh Sharma - Chief Welding Specialist"),
        ExtractedEntity(document_id=docs_b1[4].id, entity_type="MANPOWER_RECORD", entity_value="Ananya Rao (QA/QC Inspector - 9 years / 8 years pipeline)", normalized_value="8.0", confidence=0.93, page_number=4, context_snippet="Ananya Rao - QA/QC Pipeline Inspector"),
        ExtractedEntity(document_id=docs_b1[4].id, entity_type="MANPOWER_RECORD", entity_value="Vikram Patel (Lead Site Safety Officer - 9 years / 8 years pipeline)", normalized_value="8.0", confidence=0.93, page_number=5, context_snippet="Vikram Patel - Lead Site Safety Officer"),
        ExtractedEntity(document_id=docs_b1[5].id, entity_type="HSE_CERTIFICATION", entity_value="ISO 45001:2018 & ISO 14001:2015", normalized_value="ISO_45001_14001", confidence=0.81, page_number=1, context_snippet="ISO 45001:2018 Certified Occupational Health")
    ]
    for ent in entities_b1:
        db.add(ent)
    db.commit()

    # =============================================================
    # BIDDER 2: LARSEN & TOUBRO HYDROCARBON PIPELINE DIVISION (PASS / QUALIFIED - SCORE: 100%, RISK: LOW)
    # =============================================================
    b2 = Bidder(
        tender_id=tender1.id,
        legal_name="LARSEN & TOUBRO HYDROCARBON PIPELINE DIVISION",
        trade_name="L&T Hydrocarbon",
        pan="AAACL0123L",
        gstin="27AAACL0123L1Z6",
        registered_address="L&T House, Ballard Estate, Mumbai, Maharashtra 400001",
        contact_information={"email": "tenders@lthydrocarbon.com", "phone": "+91 22 6752 5656"},
        bidder_type="INDIAN_EPC_CONTRACTOR",
        country="INDIA",
        oil_gas_experience_years=18.0,
        pipeline_experience_years=16.0,
        udyam_number="UDYAM-MH-19-0019284",
        cin="L99999MH1946PLC004768",
        email="tenders@lthydrocarbon.com",
        phone="+91 22 6752 5656",
        contact_person="Sunil R. Deshmukh (Head - Pipeline Procurement)",
        status="QUALIFIED"
    )
    db.add(b2)
    db.commit()
    db.refresh(b2)

    bid2 = Bid(
        tender_id=tender1.id,
        bidder_id=b2.id,
        bid_reference_number="BID-MOPNG-2026-LT-002",
        submission_date=datetime.now(timezone.utc) - timedelta(days=2),
        technical_bid_status="QUALIFIED",
        financial_bid_amount=2380000000.0,
        currency="INR",
        remarks="Tier-1 EPC Contractor with full technical, financial, manpower, and safety compliance."
    )
    db.add(bid2)

    p2_1 = BidderProject(
        bidder_id=b2.id,
        project_name="IOCL Paradip-Haldia-Durgapur LPG & Natural Gas Grid Pipeline",
        client_name="Indian Oil Corporation Limited",
        client_type="PUBLIC_SECTOR_UNDERTAKING",
        sector="OIL_AND_GAS",
        project_type="PIPELINE_CONSTRUCTION",
        pipeline_type="NATURAL_GAS_TRANSMISSION",
        pipeline_length_km=240.0,
        pipeline_diameter="28 Inch NB API 5L X70",
        project_value=1650000000.0,
        currency="INR",
        location="Odisha & West Bengal",
        start_date=datetime.now(timezone.utc) - timedelta(days=365*4),
        completion_date=datetime.now(timezone.utc) - timedelta(days=210),
        scope_of_work="EPC contractor for 240 km 28-inch high pressure natural gas grid with mainline valve stations",
        bidder_role="EPC_CONTRACTOR",
        contract_reference="IOCL/PHDPL/2021/04"
    )
    db.add(p2_1)

    staff_b2 = [
        BidderPersonnel(bidder_id=b2.id, name="Siddharth Mehta", designation="Chief Project Manager", qualification="B.E. Mechanical", specialization="Cross-Country Natural Gas Pipelines", years_of_experience=18.0, pipeline_experience_years=16.0),
        BidderPersonnel(bidder_id=b2.id, name="Manoj Nambiar", designation="Senior Pipeline Engineer", qualification="B.Tech Mechanical", specialization="HDD & River Crossings", years_of_experience=15.0, pipeline_experience_years=13.0),
        BidderPersonnel(bidder_id=b2.id, name="Rajiv Sengupta", designation="QA/QC Lead Specialist", qualification="B.E. Metallurgy", specialization="NDT & API 1104 Welding", years_of_experience=14.0, pipeline_experience_years=12.0),
        BidderPersonnel(bidder_id=b2.id, name="Ashok Kulkarni", designation="Senior Integrity Engineer", qualification="M.Tech Mechanical", specialization="Hydrotesting & SCADA", years_of_experience=12.0, pipeline_experience_years=11.0),
        BidderPersonnel(bidder_id=b2.id, name="Deepak Chauhan", designation="HSE & Safety Director", qualification="Degree Industrial Safety", specialization="ISO 45001 & Petroleum Site Safety", years_of_experience=14.0, pipeline_experience_years=12.0)
    ]
    for s in staff_b2:
        db.add(s)

    b2_stat_pdf = os.path.join(settings.UPLOAD_DIR, "LT_Statutory_GST_PAN.pdf")
    b2_fin_pdf = os.path.join(settings.UPLOAD_DIR, "LT_Turnover_Financials.pdf")
    b2_exp_pdf = os.path.join(settings.UPLOAD_DIR, "LT_240km_Pipeline_Experience.pdf")
    b2_man_pdf = os.path.join(settings.UPLOAD_DIR, "LT_Manpower_CVs.pdf")
    b2_hse_pdf = os.path.join(settings.UPLOAD_DIR, "LT_HSE_ISO45001_Policy.pdf")

    create_sample_pdf(
        b2_stat_pdf,
        "L&T HYDROCARBON - STATUTORY REGISTRATION CERTIFICATES",
        [
            ("1. GST & PAN Registration", "Legal Name: LARSEN & TOUBRO HYDROCARBON PIPELINE DIVISION\nGSTIN: 27AAACL0123L1Z6 (Maharashtra)\nPAN: AAACL0123L\nStatus: ACTIVE\nTaxpayer Type: Regular")
        ]
    )
    create_sample_pdf(
        b2_fin_pdf,
        "L&T HYDROCARBON - AUDITED ANNUAL TURNOVER",
        [
            ("1. 3-Year Audited Turnover Statement", "FY 2023-24: INR 180.00 Crore\nFY 2024-25: INR 165.00 Crore\nFY 2025-26: INR 172.00 Crore\nAverage Annual Turnover = INR 172.33 Crore (Exceeds mandatory threshold of INR 25.00 Crore).\nAudited by M/s Deloitte Haskins & Sells | UDIN: 26012345AAAAAB1234.")
        ]
    )
    create_sample_pdf(
        b2_exp_pdf,
        "L&T HYDROCARBON - PIPELINE COMPLETION CERTIFICATE",
        [
            ("1. Client Completion Certificate", "Client: Indian Oil Corporation Limited (IOCL)\nProject: Paradip-Haldia-Durgapur Gas Grid Pipeline\nLength: 240 KM | Diameter: 28 Inch NB API 5L X70\nCompletion Date: 20-04-2025\nStatus: Completed 240 KM natural gas transmission pipeline successfully.")
        ]
    )
    create_sample_pdf(
        b2_man_pdf,
        "L&T HYDROCARBON - KEY PERSONNEL CVs",
        [
            ("1. Engineering Roster", "1. Siddharth Mehta (Chief Project Manager) - 18 yrs exp\n2. Manoj Nambiar (Senior Pipeline Engineer) - 15 yrs exp\n3. Rajiv Sengupta (QA/QC Specialist) - 14 yrs exp\n4. Ashok Kulkarni (Senior Integrity Engineer) - 12 yrs exp\n5. Deepak Chauhan (HSE Safety Director) - 14 yrs exp\n(All 5 personnel hold B.Tech/M.Tech with > 10 years pipeline experience).")
        ]
    )
    create_sample_pdf(
        b2_hse_pdf,
        "L&T HYDROCARBON - HSE & SAFETY POLICY",
        [
            ("1. Certifications & Policy", "Certified ISO 45001:2018 (Occupational Health & Safety) & ISO 14001:2015 (Environmental Management).\nZero-Fatality Corporate Commitment in place.")
        ]
    )

    docs_b2 = [
        Document(bidder_id=b2.id, tender_id=tender1.id, document_name="01_GST_Registration_LT.pdf", file_path=b2_stat_pdf, document_type="GST_CERTIFICATE", page_count=1, extracted_text="Legal Name: LARSEN & TOUBRO HYDROCARBON PIPELINE DIVISION\nGSTIN: 27AAACL0123L1Z6\nPAN: AAACL0123L\nStatus: ACTIVE"),
        Document(bidder_id=b2.id, tender_id=tender1.id, document_name="03_Financial_Statement_LT.pdf", file_path=b2_fin_pdf, document_type="FINANCIAL_STATEMENT", page_count=1, extracted_text="FY 2023-24: INR 180.00 Crore\nFY 2024-25: INR 165.00 Crore\nFY 2025-26: INR 172.00 Crore\nAverage: INR 172.33 Crore\nUDIN: 26012345AAAAAB1234"),
        Document(bidder_id=b2.id, tender_id=tender1.id, document_name="04_Similar_Pipeline_Experience_LT.pdf", file_path=b2_exp_pdf, document_type="PIPELINE_PROJECT_DOCUMENT", page_count=1, extracted_text="Client: IOCL\nProject: Natural Gas Grid Pipeline\nLength: 240 KM | Diameter: 28 Inch NB API 5L X70\nCompleted: 20-04-2025"),
        Document(bidder_id=b2.id, tender_id=tender1.id, document_name="05_Key_Personnel_CVs_LT.pdf", file_path=b2_man_pdf, document_type="PERSONNEL_CV", page_count=1, extracted_text="Siddharth Mehta (18 yrs) - B.E. Mechanical\nManoj Nambiar (15 yrs) - B.Tech Mechanical\nRajiv Sengupta (14 yrs) - B.E. Metallurgy\nAshok Kulkarni (12 yrs) - M.Tech Mechanical\nDeepak Chauhan (14 yrs) - Safety Director"),
        Document(bidder_id=b2.id, tender_id=tender1.id, document_name="07_HSE_and_Safety_Policy_LT.pdf", file_path=b2_hse_pdf, document_type="HSE_DOCUMENT", page_count=1, extracted_text="ISO 45001:2018 Certified\nISO 14001:2015 Certified\nZero-fatality site safety policy")
    ]
    for d in docs_b2:
        db.add(d)
    db.commit()

    entities_b2 = [
        ExtractedEntity(document_id=docs_b2[0].id, entity_type="GSTIN", entity_value="27AAACL0123L1Z6", normalized_value="27AAACL0123L1Z6", confidence=0.99, page_number=1, context_snippet="GSTIN: 27AAACL0123L1Z6 ACTIVE"),
        ExtractedEntity(document_id=docs_b2[0].id, entity_type="PAN", entity_value="AAACL0123L", normalized_value="AAACL0123L", confidence=0.99, page_number=1, context_snippet="PAN: AAACL0123L (L&T Hydrocarbon)"),
        ExtractedEntity(document_id=docs_b2[0].id, entity_type="COMPANY_NAME", entity_value="LARSEN & TOUBRO HYDROCARBON PIPELINE DIVISION", normalized_value="larsen & toubro hydrocarbon pipeline division", confidence=0.99, page_number=1, context_snippet="LARSEN & TOUBRO HYDROCARBON PIPELINE DIVISION"),
        ExtractedEntity(document_id=docs_b2[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2023-24: INR 180.00 Crore", normalized_value="1800000000.0", confidence=0.98, page_number=1, context_snippet="FY 2023-24: INR 180.00 Crore"),
        ExtractedEntity(document_id=docs_b2[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2024-25: INR 165.00 Crore", normalized_value="1650000000.0", confidence=0.98, page_number=1, context_snippet="FY 2024-25: INR 165.00 Crore"),
        ExtractedEntity(document_id=docs_b2[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2025-26: INR 172.00 Crore", normalized_value="1720000000.0", confidence=0.98, page_number=1, context_snippet="FY 2025-26: INR 172.00 Crore"),
        ExtractedEntity(document_id=docs_b2[2].id, entity_type="PIPELINE_LENGTH_KM", entity_value="240.0 km", normalized_value="240.0", confidence=0.98, page_number=1, context_snippet="Length: 240 KM Diameter: 28 Inch NB API 5L X70"),
        ExtractedEntity(document_id=docs_b2[3].id, entity_type="MANPOWER_RECORD", entity_value="Siddharth Mehta (18 yrs) - Chief Project Manager", normalized_value="18.0", confidence=0.98, page_number=1, context_snippet="Siddharth Mehta (18 yrs) - B.E. Mechanical"),
        ExtractedEntity(document_id=docs_b2[4].id, entity_type="HSE_CERTIFICATION", entity_value="ISO 45001:2018 & ISO 14001:2015", normalized_value="ISO_45001_14001", confidence=0.98, page_number=1, context_snippet="ISO 45001:2018 and ISO 14001:2015 Certified")
    ]
    for ent in entities_b2:
        db.add(ent)
    db.commit()

    # =============================================================
    # BIDDER 3: APEX PIPELINE & INFRA SOLUTIONS (FAIL / DISQUALIFIED - TURNOVER & GSTIN SHORTFALL)
    # =============================================================
    b3 = Bidder(
        tender_id=tender1.id,
        legal_name="APEX PIPELINE & INFRA SOLUTIONS PVT LTD",
        trade_name="Apex Pipeline",
        pan="AAACA4567A",
        gstin="07AAACA4567A1Z1",
        registered_address="Apex Tower, Nehru Place, New Delhi 110019",
        contact_information={"email": "info@apexpipeline.com", "phone": "+91 11 2641 9000"},
        bidder_type="INDIAN_EPC_CONTRACTOR",
        country="INDIA",
        oil_gas_experience_years=5.0,
        pipeline_experience_years=3.0,
        udyam_number="UDYAM-DL-02-0089123",
        cin="U45200DL2018PTC321456",
        email="info@apexpipeline.com",
        phone="+91 11 2641 9000",
        contact_person="Alok K. Gupta (Director)",
        status="DISQUALIFIED"
    )
    db.add(b3)
    db.commit()
    db.refresh(b3)

    bid3 = Bid(
        tender_id=tender1.id,
        bidder_id=b3.id,
        bid_reference_number="BID-MOPNG-2026-APEX-003",
        submission_date=datetime.now(timezone.utc) - timedelta(days=1),
        technical_bid_status="DISQUALIFIED",
        financial_bid_amount=2190000000.0,
        currency="INR",
        remarks="Disqualified: 3-year turnover INR 14.23 Cr is below mandatory INR 25.00 Cr threshold. GSTIN registration cancelled."
    )
    db.add(bid3)

    b3_stat_pdf = os.path.join(settings.UPLOAD_DIR, "Apex_Statutory_GST_PAN.pdf")
    b3_fin_pdf = os.path.join(settings.UPLOAD_DIR, "Apex_Turnover_Financials.pdf")
    b3_exp_pdf = os.path.join(settings.UPLOAD_DIR, "Apex_Pipeline_Experience.pdf")

    create_sample_pdf(
        b3_stat_pdf,
        "APEX PIPELINE - STATUTORY CERTIFICATES",
        [
            ("1. GST & PAN Registration", "Legal Name: APEX PIPELINE & INFRA SOLUTIONS PVT LTD\nGSTIN: 07AAACA4567A1Z1 (Delhi)\nRegistration Status: CANCELLED / INACTIVE\nPAN: AAACA4567A")
        ]
    )
    create_sample_pdf(
        b3_fin_pdf,
        "APEX PIPELINE - AUDITED ANNUAL TURNOVER",
        [
            ("1. 3-Year Turnover Statement", "FY 2023-24: INR 14.50 Crore\nFY 2024-25: INR 12.00 Crore\nFY 2025-26: INR 16.20 Crore\nAverage Annual Turnover = INR 14.23 Crore (Below tender requirement of INR 25.00 Crore, Shortfall: INR 10.77 Crore).")
        ]
    )
    create_sample_pdf(
        b3_exp_pdf,
        "APEX PIPELINE - PAST WORK CERTIFICATE",
        [
            ("1. Small Diameter Spur Pipeline", "Client: State Distribution Grid\nExecuted Length: 45 KM | Diameter: 16 Inch NB\nStatus: 45 KM executed (Shortfall vs 100 KM mandatory / 24-inch minimum).")
        ]
    )

    docs_b3 = [
        Document(bidder_id=b3.id, tender_id=tender1.id, document_name="01_GST_Registration_Apex.pdf", file_path=b3_stat_pdf, document_type="GST_CERTIFICATE", page_count=1, extracted_text="Legal Name: APEX PIPELINE & INFRA SOLUTIONS PVT LTD\nGSTIN: 07AAACA4567A1Z1\nRegistration Status: CANCELLED\nPAN: AAACA4567A"),
        Document(bidder_id=b3.id, tender_id=tender1.id, document_name="03_Financial_Statement_Apex.pdf", file_path=b3_fin_pdf, document_type="FINANCIAL_STATEMENT", page_count=1, extracted_text="FY 2023-24: INR 14.50 Crore\nFY 2024-25: INR 12.00 Crore\nFY 2025-26: INR 16.20 Crore\nAverage Annual Turnover: INR 14.23 Crore (Below ₹25 Cr mandatory)."),
        Document(bidder_id=b3.id, tender_id=tender1.id, document_name="04_Similar_Pipeline_Experience_Apex.pdf", file_path=b3_exp_pdf, document_type="PIPELINE_PROJECT_DOCUMENT", page_count=1, extracted_text="Executed Length: 45 KM | Diameter: 16 Inch NB")
    ]
    for d in docs_b3:
        db.add(d)
    db.commit()

    entities_b3 = [
        ExtractedEntity(document_id=docs_b3[0].id, entity_type="GSTIN", entity_value="07AAACA4567A1Z1", normalized_value="07AAACA4567A1Z1", confidence=0.98, page_number=1, context_snippet="GSTIN: 07AAACA4567A1Z1 CANCELLED"),
        ExtractedEntity(document_id=docs_b3[0].id, entity_type="PAN", entity_value="AAACA4567A", normalized_value="AAACA4567A", confidence=0.98, page_number=1, context_snippet="PAN: AAACA4567A"),
        ExtractedEntity(document_id=docs_b3[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2023-24: INR 14.50 Crore", normalized_value="145000000.0", confidence=0.95, page_number=1, context_snippet="FY 2023-24: INR 14.50 Crore"),
        ExtractedEntity(document_id=docs_b3[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2024-25: INR 12.00 Crore", normalized_value="120000000.0", confidence=0.95, page_number=1, context_snippet="FY 2024-25: INR 12.00 Crore"),
        ExtractedEntity(document_id=docs_b3[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2025-26: INR 16.20 Crore", normalized_value="162000000.0", confidence=0.95, page_number=1, context_snippet="FY 2025-26: INR 16.20 Crore"),
        ExtractedEntity(document_id=docs_b3[2].id, entity_type="PIPELINE_LENGTH_KM", entity_value="45.0 km", normalized_value="45.0", confidence=0.95, page_number=1, context_snippet="Executed Length: 45 KM Diameter: 16 Inch NB")
    ]
    for ent in entities_b3:
        db.add(ent)
    db.commit()

    # =============================================================
    # BIDDER 4: ZENITH ENGINEERING & CONSTRUCTION (FAIL / DISQUALIFIED - NON-HYDROCARBON WORK & NO HSE)
    # =============================================================
    b4 = Bidder(
        tender_id=tender1.id,
        legal_name="ZENITH ENGINEERING & CONSTRUCTION LTD",
        trade_name="Zenith Engineering",
        pan="AAACZ8901Z",
        gstin="03AAACZ8901Z1Z4",
        registered_address="Zenith Complex, Mall Road, Ludhiana, Punjab 141001",
        contact_information={"email": "bids@zenitheng.com", "phone": "+91 161 240 1800"},
        bidder_type="INDIAN_EPC_CONTRACTOR",
        country="INDIA",
        oil_gas_experience_years=2.0,
        pipeline_experience_years=2.0,
        udyam_number="UDYAM-PB-12-0034189",
        cin="U45200PB2012PLC045120",
        email="bids@zenitheng.com",
        phone="+91 161 240 1800",
        contact_person="Harpreet S. Gill (Managing Director)",
        status="DISQUALIFIED"
    )
    db.add(b4)
    db.commit()
    db.refresh(b4)

    bid4 = Bid(
        tender_id=tender1.id,
        bidder_id=b4.id,
        bid_reference_number="BID-MOPNG-2026-ZENITH-004",
        submission_date=datetime.now(timezone.utc) - timedelta(days=1),
        technical_bid_status="DISQUALIFIED",
        financial_bid_amount=2240000000.0,
        currency="INR",
        remarks="Disqualified: Missing mandatory ISO 45001 safety certification and submitted 12-inch water piping experience does not meet 24-inch hydrocarbon pipeline criteria."
    )
    db.add(bid4)

    b4_stat_pdf = os.path.join(settings.UPLOAD_DIR, "Zenith_Statutory_GST_PAN.pdf")
    b4_fin_pdf = os.path.join(settings.UPLOAD_DIR, "Zenith_Turnover_Financials.pdf")
    b4_exp_pdf = os.path.join(settings.UPLOAD_DIR, "Zenith_Water_Pipe_Experience.pdf")

    create_sample_pdf(
        b4_stat_pdf,
        "ZENITH ENGINEERING - STATUTORY CERTIFICATES",
        [
            ("1. GST & PAN Registration", "Legal Name: ZENITH ENGINEERING & CONSTRUCTION LTD\nGSTIN: 03AAACZ8901Z1Z4 (Punjab)\nPAN: AAACZ8901Z\nStatus: ACTIVE")
        ]
    )
    create_sample_pdf(
        b4_fin_pdf,
        "ZENITH ENGINEERING - AUDITED ANNUAL TURNOVER",
        [
            ("1. 3-Year Audited Turnover", "FY 2023-24: INR 28.00 Crore\nFY 2024-25: INR 26.00 Crore\nFY 2025-26: INR 25.00 Crore\nAverage Annual Turnover = INR 26.33 Crore (Meets ₹25.00 Cr turnover requirement).")
        ]
    )
    create_sample_pdf(
        b4_exp_pdf,
        "ZENITH ENGINEERING - PAST PIPELINE WORK",
        [
            ("1. Municipal Water Distribution Line", "Client: Punjab Municipal Water Supply Board\nScope: Laying of 80 km, 12-inch ductile iron municipal water piping.\nNote: No hydrocarbon / natural gas pipeline experience or ISO 45001 safety certificate submitted.")
        ]
    )

    docs_b4 = [
        Document(bidder_id=b4.id, tender_id=tender1.id, document_name="01_GST_Registration_Zenith.pdf", file_path=b4_stat_pdf, document_type="GST_CERTIFICATE", page_count=1, extracted_text="Legal Name: ZENITH ENGINEERING & CONSTRUCTION LTD\nGSTIN: 03AAACZ8901Z1Z4\nPAN: AAACZ8901Z\nStatus: ACTIVE"),
        Document(bidder_id=b4.id, tender_id=tender1.id, document_name="03_Financial_Statement_Zenith.pdf", file_path=b4_fin_pdf, document_type="FINANCIAL_STATEMENT", page_count=1, extracted_text="FY 2023-24: INR 28.00 Crore\nFY 2024-25: INR 26.00 Crore\nFY 2025-26: INR 25.00 Crore\nAverage: INR 26.33 Crore"),
        Document(bidder_id=b4.id, tender_id=tender1.id, document_name="04_Similar_Pipeline_Experience_Zenith.pdf", file_path=b4_exp_pdf, document_type="PIPELINE_PROJECT_DOCUMENT", page_count=1, extracted_text="Municipal Water Distribution Line\nExecuted Length: 80 KM | Diameter: 12 Inch NB Ductile Iron Water Piping\nNo ISO 45001 safety certificate submitted")
    ]
    for d in docs_b4:
        db.add(d)
    db.commit()

    entities_b4 = [
        ExtractedEntity(document_id=docs_b4[0].id, entity_type="GSTIN", entity_value="03AAACZ8901Z1Z4", normalized_value="03AAACZ8901Z1Z4", confidence=0.98, page_number=1, context_snippet="GSTIN: 03AAACZ8901Z1Z4 ACTIVE"),
        ExtractedEntity(document_id=docs_b4[0].id, entity_type="PAN", entity_value="AAACZ8901Z", normalized_value="AAACZ8901Z", confidence=0.98, page_number=1, context_snippet="PAN: AAACZ8901Z"),
        ExtractedEntity(document_id=docs_b4[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2023-24: INR 28.00 Crore", normalized_value="280000000.0", confidence=0.96, page_number=1, context_snippet="FY 2023-24: INR 28.00 Crore"),
        ExtractedEntity(document_id=docs_b4[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2024-25: INR 26.00 Crore", normalized_value="260000000.0", confidence=0.96, page_number=1, context_snippet="FY 2024-25: INR 26.00 Crore"),
        ExtractedEntity(document_id=docs_b4[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2025-26: INR 25.00 Crore", normalized_value="250000000.0", confidence=0.96, page_number=1, context_snippet="FY 2025-26: INR 25.00 Crore"),
        ExtractedEntity(document_id=docs_b4[2].id, entity_type="PIPELINE_LENGTH_KM", entity_value="80.0 km", normalized_value="80.0", confidence=0.94, page_number=1, context_snippet="Municipal Water Piping 80 km 12 Inch")
    ]
    for ent in entities_b4:
        db.add(ent)
    db.commit()

    # =============================================================
    # BIDDER 5: BHARAT PETROLEUM INFRA CONSORTIUM (REVIEW / HOLD - SCORE: 85%, RISK: MEDIUM)
    # =============================================================
    b5 = Bidder(
        tender_id=tender1.id,
        legal_name="BHARAT PETROLEUM INFRA CONSORTIUM",
        trade_name="Bharat Petroleum Infra",
        pan="AABCB9012B",
        gstin="24AABCB9012B1Z9",
        registered_address="Bharat Infra Towers, SG Highway, Ahmedabad, Gujarat 380054",
        contact_information={"email": "tenders@bharatinfra.in", "phone": "+91 79 2685 4900"},
        bidder_type="INDIAN_EPC_CONTRACTOR",
        country="INDIA",
        oil_gas_experience_years=12.0,
        pipeline_experience_years=10.0,
        udyam_number="UDYAM-GJ-01-0089451",
        cin="U45200GJ2015PTC089201",
        email="tenders@bharatinfra.in",
        phone="+91 79 2685 4900",
        contact_person="Ketan B. Patel (Managing Partner)",
        status="UNDER_EVALUATION"
    )
    db.add(b5)
    db.commit()
    db.refresh(b5)

    bid5 = Bid(
        tender_id=tender1.id,
        bidder_id=b5.id,
        bid_reference_number="BID-MOPNG-2026-BHARAT-005",
        submission_date=datetime.now(timezone.utc) - timedelta(days=1),
        technical_bid_status="UNDER_EVALUATION",
        financial_bid_amount=2290000000.0,
        currency="INR",
        remarks="Under Review: Pipeline experience certificate issued in affiliate joint venture name; 1 CV has borderline 7.5 yrs experience requiring officer verification."
    )
    db.add(bid5)

    p5_1 = BidderProject(
        bidder_id=b5.id,
        project_name="Gujarat Gas Transmission & CGD Feeder Grid Laying",
        client_name="Gujarat Gas Limited",
        client_type="PUBLIC_SECTOR_UNDERTAKING",
        sector="OIL_AND_GAS",
        project_type="PIPELINE_CONSTRUCTION",
        pipeline_type="NATURAL_GAS_TRANSMISSION",
        pipeline_length_km=120.0,
        pipeline_diameter="24 Inch NB API 5L X60",
        project_value=980000000.0,
        currency="INR",
        location="Surat & Bharuch",
        start_date=datetime.now(timezone.utc) - timedelta(days=365*3),
        completion_date=datetime.now(timezone.utc) - timedelta(days=190),
        scope_of_work="Laying 120 km 24-inch natural gas transmission line under Bharat-PetroCon JV consortium",
        bidder_role="CONSORTIUM_LEADER",
        contract_reference="GGL/PL/2022/07"
    )
    db.add(p5_1)

    staff_b5 = [
        BidderPersonnel(bidder_id=b5.id, name="Hardik Shah", designation="Project Lead", qualification="B.Tech Mechanical", years_of_experience=11.0, pipeline_experience_years=10.0),
        BidderPersonnel(bidder_id=b5.id, name="Bhavesh Joshi", designation="Senior Mechanical Engineer", qualification="B.E. Mechanical", years_of_experience=9.5, pipeline_experience_years=9.0),
        BidderPersonnel(bidder_id=b5.id, name="Chirag Dave", designation="Welding & QA Inspector", qualification="B.E. Metallurgy", years_of_experience=9.0, pipeline_experience_years=8.5),
        BidderPersonnel(bidder_id=b5.id, name="Manish Vyas", designation="NDT Level II Specialist", qualification="Diploma Mechanical", years_of_experience=8.5, pipeline_experience_years=8.0),
        BidderPersonnel(bidder_id=b5.id, name="Nilesh Parmar", designation="Site Engineer", qualification="B.Tech Mechanical", years_of_experience=7.5, pipeline_experience_years=7.5)
    ]
    for s in staff_b5:
        db.add(s)

    b5_stat_pdf = os.path.join(settings.UPLOAD_DIR, "Bharat_Statutory_GST_PAN.pdf")
    b5_fin_pdf = os.path.join(settings.UPLOAD_DIR, "Bharat_Turnover_Financials.pdf")
    b5_exp_pdf = os.path.join(settings.UPLOAD_DIR, "Bharat_120km_Pipeline_Experience.pdf")
    b5_man_pdf = os.path.join(settings.UPLOAD_DIR, "Bharat_Manpower_CVs.pdf")
    b5_hse_pdf = os.path.join(settings.UPLOAD_DIR, "Bharat_HSE_ISO45001_Policy.pdf")

    create_sample_pdf(
        b5_stat_pdf,
        "BHARAT PETROLEUM INFRA - STATUTORY CERTIFICATES",
        [
            ("1. GST & PAN Registration", "Legal Name: BHARAT PETROLEUM INFRA CONSORTIUM\nGSTIN: 24AABCB9012B1Z9 (Gujarat)\nPAN: AABCB9012B\nStatus: ACTIVE")
        ]
    )
    create_sample_pdf(
        b5_fin_pdf,
        "BHARAT PETROLEUM INFRA - AUDITED FINANCIAL TURNOVER",
        [
            ("1. 3-Year Audited Turnover", "FY 2023-24: INR 35.00 Crore\nFY 2024-25: INR 32.00 Crore\nFY 2025-26: INR 30.00 Crore\nAverage Annual Turnover = INR 32.33 Crore (Exceeds ₹25.00 Cr mandatory threshold).")
        ]
    )
    create_sample_pdf(
        b5_exp_pdf,
        "BHARAT PETROLEUM INFRA - PIPELINE WORK CERTIFICATE",
        [
            ("1. Natural Gas Feeder Grid (Issued to Bharat-PetroCon JV)", "Client: Gujarat Gas Limited\nProject: 120 KM, 24 Inch NB Natural Gas Transmission Line.\nNote: Certificate issued in Consortium JV name; requires Officer Review for JV parent entity pass-through.")
        ]
    )
    create_sample_pdf(
        b5_man_pdf,
        "BHARAT PETROLEUM INFRA - KEY PERSONNEL CVs",
        [
            ("1. Personnel Roster", "1. Hardik Shah (Project Lead) - 11 yrs exp\n2. Bhavesh Joshi (Senior Engineer) - 9.5 yrs exp\n3. Chirag Dave (QA Inspector) - 9.0 yrs exp\n4. Manish Vyas (NDT Level II) - 8.5 yrs exp\n5. Nilesh Parmar (Site Engineer) - 7.5 yrs exp (Borderline vs 8.0 yrs threshold, flagged for review).")
        ]
    )
    create_sample_pdf(
        b5_hse_pdf,
        "BHARAT PETROLEUM INFRA - HSE SAFETY POLICY",
        [
            ("1. Safety Certification", "ISO 45001:2018 Certified & ISO 14001:2015 Certified. Zero-fatality safety commitment.")
        ]
    )

    docs_b5 = [
        Document(bidder_id=b5.id, tender_id=tender1.id, document_name="01_GST_Registration_Bharat.pdf", file_path=b5_stat_pdf, document_type="GST_CERTIFICATE", page_count=1, extracted_text="Legal Name: BHARAT PETROLEUM INFRA CONSORTIUM\nGSTIN: 24AABCB9012B1Z9\nPAN: AABCB9012B\nStatus: ACTIVE"),
        Document(bidder_id=b5.id, tender_id=tender1.id, document_name="03_Financial_Statement_Bharat.pdf", file_path=b5_fin_pdf, document_type="FINANCIAL_STATEMENT", page_count=1, extracted_text="FY 2023-24: INR 35.00 Crore\nFY 2024-25: INR 32.00 Crore\nFY 2025-26: INR 30.00 Crore\nAverage: INR 32.33 Crore"),
        Document(bidder_id=b5.id, tender_id=tender1.id, document_name="04_Similar_Pipeline_Experience_Bharat.pdf", file_path=b5_exp_pdf, document_type="PIPELINE_PROJECT_DOCUMENT", page_count=1, extracted_text="Client: Gujarat Gas Limited\nLength: 120 KM | Diameter: 24 Inch NB\nIssued to Bharat-PetroCon JV consortium. Subject to officer verification."),
        Document(bidder_id=b5.id, tender_id=tender1.id, document_name="05_Key_Personnel_CVs_Bharat.pdf", file_path=b5_man_pdf, document_type="PERSONNEL_CV", page_count=1, extracted_text="Hardik Shah (11 yrs)\nBhavesh Joshi (9.5 yrs)\nChirag Dave (9.0 yrs)\nManish Vyas (8.5 yrs)\nNilesh Parmar (7.5 yrs)"),
        Document(bidder_id=b5.id, tender_id=tender1.id, document_name="07_HSE_and_Safety_Policy_Bharat.pdf", file_path=b5_hse_pdf, document_type="HSE_DOCUMENT", page_count=1, extracted_text="ISO 45001:2018 Certified\nISO 14001:2015 Certified\nZero-fatality policy")
    ]
    for d in docs_b5:
        db.add(d)
    db.commit()

    entities_b5 = [
        ExtractedEntity(document_id=docs_b5[0].id, entity_type="GSTIN", entity_value="24AABCB9012B1Z9", normalized_value="24AABCB9012B1Z9", confidence=0.98, page_number=1, context_snippet="GSTIN: 24AABCB9012B1Z9 ACTIVE"),
        ExtractedEntity(document_id=docs_b5[0].id, entity_type="PAN", entity_value="AABCB9012B", normalized_value="AABCB9012B", confidence=0.98, page_number=1, context_snippet="PAN: AABCB9012B"),
        ExtractedEntity(document_id=docs_b5[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2023-24: INR 35.00 Crore", normalized_value="350000000.0", confidence=0.96, page_number=1, context_snippet="FY 2023-24: INR 35.00 Crore"),
        ExtractedEntity(document_id=docs_b5[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2024-25: INR 32.00 Crore", normalized_value="320000000.0", confidence=0.96, page_number=1, context_snippet="FY 2024-25: INR 32.00 Crore"),
        ExtractedEntity(document_id=docs_b5[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2025-26: INR 30.00 Crore", normalized_value="300000000.0", confidence=0.96, page_number=1, context_snippet="FY 2025-26: INR 30.00 Crore"),
        ExtractedEntity(document_id=docs_b5[2].id, entity_type="PIPELINE_LENGTH_KM", entity_value="120.0 km", normalized_value="120.0", confidence=0.95, page_number=1, context_snippet="120 KM 24 Inch NB Natural Gas Feeder Grid"),
        ExtractedEntity(document_id=docs_b5[3].id, entity_type="MANPOWER_RECORD", entity_value="Hardik Shah (11.0 yrs)", normalized_value="11.0", confidence=0.95, page_number=1, context_snippet="Hardik Shah (Project Lead) - 11 yrs exp"),
        ExtractedEntity(document_id=docs_b5[4].id, entity_type="HSE_CERTIFICATION", entity_value="ISO 45001:2018 & ISO 14001:2015", normalized_value="ISO_45001_14001", confidence=0.95, page_number=1, context_snippet="ISO 45001 & ISO 14001 Certified")
    ]
    for ent in entities_b5:
        db.add(ent)
    db.commit()

    # -------------------------------------------------------------
    # EXECUTE AUTOMATED COMPLIANCE VERIFICATION & GENERATE REPORTS FOR ALL 5 BIDDERS
    # -------------------------------------------------------------
    from app.services.report_generator import ReportGenerator
    from app.models.models import OfficerDecision, Recommendation
    all_5_bidders = [b1, b2, b3, b4, b5]
    logger.info("Executing Automated Compliance Verification & Report Generation for all 5 Bidders...")
    for b in all_5_bidders:
        ComplianceEngine.run_full_verification(db=db, bidder_id=b.id, officer_id=officer_user.id, officer_name=officer_user.name)

    # 1. Bidder 1: PASS / QUALIFIED
    b1.status = "QUALIFIED"
    db.add(OfficerDecision(
        bid_id=b1.id, officer_id=officer_user.id, officer_name=officer_user.name,
        decision_type="FINAL_BID_DECISION", ai_status="PASS", officer_status="QUALIFIED",
        officer_reason="All 7 mandatory statutory, financial, pipeline experience, manpower, and HSE criteria verified 100% compliant."
    ))

    # 2. Bidder 2: PASS / QUALIFIED
    b2.status = "QUALIFIED"
    db.add(OfficerDecision(
        bid_id=b2.id, officer_id=officer_user.id, officer_name=officer_user.name,
        decision_type="FINAL_BID_DECISION", ai_status="PASS", officer_status="QUALIFIED",
        officer_reason="Substantial Tier-1 EPC contractor credentials. 100% compliant across all statutory, financial, and technical criteria."
    ))

    # 3. Bidder 3: FAIL / DISQUALIFIED
    b3.status = "DISQUALIFIED"
    rec3 = db.query(Recommendation).filter(Recommendation.bidder_id == b3.id).first()
    if rec3:
        rec3.ai_recommendation = "Reject"
        rec3.justification = "Failed statutory & financial criteria: GSTIN marked CANCELLED on GST portal, and 3-Year average turnover of ₹14.23 Cr falls below mandatory ₹25.00 Cr threshold."
    db.add(OfficerDecision(
        bid_id=b3.id, officer_id=officer_user.id, officer_name=officer_user.name,
        decision_type="FINAL_BID_DECISION", ai_status="FAIL", officer_status="DISQUALIFIED",
        officer_reason="Disqualified per GFR 2017 & MoPNG Tender Clause 3.2. GSTIN cancelled and annual turnover shortfall."
    ))

    # 4. Bidder 4: FAIL / DISQUALIFIED
    b4.status = "DISQUALIFIED"
    rec4 = db.query(Recommendation).filter(Recommendation.bidder_id == b4.id).first()
    if rec4:
        rec4.ai_recommendation = "Reject"
        rec4.justification = "Failed technical & HSE criteria: Submitted water pipeline (12-inch) does not meet 24-inch natural gas requirement, and mandatory ISO 45001 safety certification is missing."
    db.add(OfficerDecision(
        bid_id=b4.id, officer_id=officer_user.id, officer_name=officer_user.name,
        decision_type="FINAL_BID_DECISION", ai_status="FAIL", officer_status="DISQUALIFIED",
        officer_reason="Disqualified per Tender Clause 4.1 & 7.1. Technical experience and HSE safety standards not met."
    ))

    # 5. Bidder 5: IN REVIEW / UNDER_EVALUATION
    b5.status = "UNDER_REVIEW"
    rec5 = db.query(Recommendation).filter(Recommendation.bidder_id == b5.id).first()
    if rec5:
        rec5.ai_recommendation = "Manual Review Required"
        rec5.justification = "Pipeline completion certificate issued under Bharat-PetroCon JV consortium; officer confirmation required for parent entity qualification pass-through."
    db.add(OfficerDecision(
        bid_id=b5.id, officer_id=officer_user.id, officer_name=officer_user.name,
        decision_type="FINAL_BID_DECISION", ai_status="REVIEW", officer_status="REVIEW / HOLD",
        officer_reason="Pending Joint Venture legal endorsement documentation for parent consortium entity qualification pass-through."
    ))

    db.commit()

    # Generate rich reports for all 5 bidders with their updated statuses
    for b in all_5_bidders:
        rep = ReportGenerator.generate_bid_report(db=db, bid_id=b.id, officer=officer_user)
        logger.info(f"Generated Official Report for '{b.legal_name}' -> Status: {b.status}, Report: {rep.report_number}")

    db.close()
    logger.info("Database seeding successfully completed with 5 distinct scenario bidders: 2 PASS, 2 FAIL, 1 IN REVIEW!")

if __name__ == "__main__":
    seed()
