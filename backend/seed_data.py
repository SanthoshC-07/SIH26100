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

    logger.info("Seeding Users (1 Admin, 1 Senior Procurement Officer)...")
    
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
        password_hash=get_password_hash("password123"),
        role="PROCUREMENT_OFFICER",
        department="GAIL / MoPNG Pipeline Tender Evaluation Cell, New Delhi"
    )
    db.add(officer_user)
    db.commit()
    db.refresh(admin_user)
    db.refresh(officer_user)

    # -------------------------------------------------------------
    # 3 REALISTIC PETROLEUM & NATURAL GAS PIPELINE TENDERS
    # -------------------------------------------------------------
    logger.info("Seeding 3 Realistic Petroleum & Pipeline Tenders...")

    t1_doc = os.path.join(settings.UPLOAD_DIR, "Tender_GAIL_2026_PL_NC_4182.pdf")
    create_sample_pdf(
        t1_doc,
        "GAIL TENDER: GAIL/2026/PL-NC/4182 - NATURAL GAS PIPELINE EPC",
        [
            ("1. Scope of Work", "Laying, Testing, and Commissioning of 150 km, 24-inch Outer Diameter API 5L Grade X70 Cross-Country Natural Gas Transmission Pipeline including Sectionalizing Valve Stations and Intermediate Pigging Stations."),
            ("2. Check 1: GST Statutory Registration", "Bidder must possess valid and active GSTIN registration in the relevant State/UT and submit latest GSTR-3B filings."),
            ("3. Check 2: PAN & Identity", "Bidder entity must hold a valid Permanent Account Number (PAN) issued by Income Tax Department matching corporate legal identity."),
            ("4. Check 3: Financial Turnover", "Average Annual Financial Turnover of the bidder during the last 3 preceding financial years must be at least INR 10.00 Crore."),
            ("5. Check 4: Oil & Gas Experience", "Bidder must possess proven prior execution experience in EPC / construction projects in Petroleum, Natural Gas, Refinery, or Hydrocarbon pipeline sectors."),
            ("6. Check 5: Similar Pipeline Experience", "Bidder must have successfully constructed and commissioned at least one cross-country high-pressure natural gas transmission pipeline of minimum 100 km length (24-inch or higher) in the last 7 years."),
            ("7. Check 6: Technical Manpower", "Bidder must commit and deploy a minimum of 5 qualified pipeline engineers (B.Tech / B.E. Mechanical / Pipeline / NDT Level II) with at least 8 years of relevant site experience."),
            ("8. Check 7: HSE & Safety Compliance", "Bidder must maintain certified Occupational Health & Safety (ISO 45001) and Environmental Management (ISO 14001) systems with a zero-fatality site safety policy.")
        ]
    )

    tender1 = Tender(
        tender_number="GAIL/2026/PL-NC/4182",
        title="Construction of 150 km 24-inch Cross-Country Natural Gas Transmission Pipeline",
        issuing_organization="GAIL (India) Limited",
        ministry="Ministry of Petroleum & Natural Gas",
        sector="OIL_AND_GAS",
        tender_type="PIPELINE_PROCUREMENT",
        project_type="PIPELINE_CONSTRUCTION",
        pipeline_type="CROSS_COUNTRY_PIPELINE",
        location="Vijaipur-Auraiya Section, National Gas Grid",
        description="EPC contract for 150 km, 24-inch NB API 5L X70 cross-country natural gas pipeline laying, HDD river crossings, SV stations, and pre-commissioning.",
        estimated_value=2400000000.0,
        tender_issue_date=datetime.now(timezone.utc) - timedelta(days=12),
        submission_deadline=datetime.now(timezone.utc) + timedelta(days=18),
        evaluation_date=datetime.now(timezone.utc) + timedelta(days=25),
        status="ACTIVE",
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
            ("2. Statutory & Financial", "Active GSTIN, PAN, and minimum average annual turnover of INR 10.00 Crore."),
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
            ("2. Statutory & Financial", "Active GSTIN, PAN, and minimum average annual turnover of INR 10.00 Crore."),
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
    # 7 CORE REQUIREMENTS FOR TENDER 1 (GAIL PIPELINE)
    # -------------------------------------------------------------
    logger.info("Adding 7 Core Requirements to Tender 1...")
    reqs_t1 = [
        Requirement(
            tender_id=tender1.id,
            category="GST",
            clause_number="Cl-1.1",
            original_text="Check 1: Bidder must possess valid and active GSTIN registration in the relevant State/UT and submit latest GSTR-3B filings.",
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
            clause_number="Cl-1.2",
            original_text="Check 2: Bidder entity must hold a valid Permanent Account Number (PAN) issued by Income Tax Department with matching legal corporate identity.",
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
            clause_number="Cl-2.1",
            original_text="Check 3: Average Annual Financial Turnover of the bidder during the last 3 preceding financial years (FY 2022-23, FY 2023-24, FY 2024-25) must be at least INR 10.00 Crore.",
            normalized_requirement="Average Annual Turnover >= INR 10.00 Crore over last 3 FYs.",
            mandatory=True,
            threshold=100000000.0,
            threshold_unit="INR",
            period="LAST_3_FINANCIAL_YEARS",
            evidence_required=["AUDITED_BALANCE_SHEETS", "CA_CERTIFIED_TURNOVER_STATEMENT"],
            verification_method="RULE_AND_ARITHMETIC"
        ),
        Requirement(
            tender_id=tender1.id,
            category="OIL_GAS_EXPERIENCE",
            clause_number="Cl-3.1",
            original_text="Check 4: Bidder must possess proven prior execution experience in EPC / construction projects in Petroleum, Natural Gas, Refinery, or Hydrocarbon pipeline sectors.",
            normalized_requirement="Prior EPC/construction experience in Petroleum / Natural Gas / Hydrocarbon sector.",
            mandatory=True,
            threshold=None,
            threshold_unit=None,
            required_sector="OIL_AND_GAS",
            period="LAST_7_YEARS",
            evidence_required=["EXPERIENCE_CERTIFICATE", "CLIENT_COMPLETION_REPORT"],
            verification_method="SEMANTIC_NLP_CLASSIFIER"
        ),
        Requirement(
            tender_id=tender1.id,
            category="SIMILAR_PIPELINE_EXPERIENCE",
            clause_number="Cl-3.2",
            original_text="Check 5: Bidder must have successfully constructed and commissioned at least one cross-country high-pressure natural gas transmission pipeline of minimum 100 km length (24-inch or higher) in the last 7 years.",
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
            clause_number="Cl-4.1",
            original_text="Check 6: Bidder must commit and deploy a minimum of 5 qualified pipeline engineers (B.Tech / B.E. Mechanical / Pipeline / NDT Level II) with at least 8 years of relevant site experience.",
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
            clause_number="Cl-5.1",
            original_text="Check 7 (Configurable): Bidder must maintain certified Occupational Health & Safety (ISO 45001) and Environmental Management (ISO 14001) systems with a zero-fatality site safety policy.",
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
    # BIDDER 1: LARSEN & TOUBRO HYDROCARBON (PASS - LOW RISK, SCORE: 100%)
    # =============================================================
    b1 = Bidder(
        tender_id=tender1.id,
        legal_name="Larsen & Toubro Hydrocarbon Engineering Limited",
        trade_name="L&T Hydrocarbon",
        pan="AAACL1234F",
        gstin="27AAACL1234F1Z5",
        registered_address="L&T House, Ballard Estate, Mumbai, Maharashtra 400001",
        contact_information={"email": "tenders.hydrocarbon@larsentoubro.com", "phone": "+91 22 6752 5656"},
        bidder_type="INDIAN_EPC_CONTRACTOR",
        country="INDIA",
        oil_gas_experience_years=35.0,
        pipeline_experience_years=28.0,
        udyam_number="UDYAM-MH-12-0098412",
        cin="L29100MH1946PLC004768",
        email="tenders.hydrocarbon@larsentoubro.com",
        phone="+91 22 6752 5656",
        contact_person="Alok K. Sengupta (Executive VP - Pipeline Projects)",
        status="SUBMITTED"
    )
    db.add(b1)
    db.commit()
    db.refresh(b1)

    # Bid Submission for Bidder 1
    bid1 = Bid(
        tender_id=tender1.id,
        bidder_id=b1.id,
        bid_reference_number="BID-GAIL-2026-LT-001",
        submission_date=datetime.now(timezone.utc) - timedelta(days=2),
        technical_bid_status="QUALIFIED",
        financial_bid_amount=2320000000.0,
        currency="INR",
        remarks="Complete technical & financial bid submitted with all 7 compliance certificates."
    )
    db.add(bid1)

    # Structured BidderProject records for Bidder 1
    p1_1 = BidderProject(
        bidder_id=b1.id,
        project_name="GAIL Jagdishpur-Haldia-Bokaro-Dhamra Gas Pipeline Phase-II (Section 3)",
        client_name="GAIL (India) Limited",
        client_type="PUBLIC_SECTOR_UNDERTAKING",
        sector="NATURAL_GAS",
        project_type="PIPELINE_CONSTRUCTION",
        pipeline_type="CROSS_COUNTRY_PIPELINE",
        pipeline_length_km=165.0,
        pipeline_diameter="24 inch NB API 5L X70",
        project_value=2850000000.0,
        currency="INR",
        location="Bihar & West Bengal",
        start_date=datetime.now(timezone.utc) - timedelta(days=365*3),
        completion_date=datetime.now(timezone.utc) - timedelta(days=365),
        scope_of_work="EPC Laying, HDD River Crossings, SV Stations, Hydrotesting, and Commissioning",
        bidder_role="EPC_CONTRACTOR",
        contract_reference="GAIL/JHBDPL/SEC-3/2021/04"
    )
    p1_2 = BidderProject(
        bidder_id=b1.id,
        project_name="IOCL Koyali Refinery Crude & Gas Pipeline Interconnection",
        client_name="Indian Oil Corporation Limited",
        client_type="PUBLIC_SECTOR_UNDERTAKING",
        sector="PETROLEUM",
        project_type="PIPELINE_EPC",
        pipeline_type="CRUDE_OIL",
        pipeline_length_km=120.0,
        pipeline_diameter="28 inch NB API 5L X65",
        project_value=1950000000.0,
        currency="INR",
        location="Gujarat",
        start_date=datetime.now(timezone.utc) - timedelta(days=365*4),
        completion_date=datetime.now(timezone.utc) - timedelta(days=365*2),
        scope_of_work="Pipeline construction and pump station integration",
        bidder_role="MAIN_CONTRACTOR",
        contract_reference="IOCL/KOY/PL/2020/12"
    )
    db.add(p1_1)
    db.add(p1_2)

    # Structured BidderPersonnel records for Bidder 1
    staff_b1 = [
        BidderPersonnel(bidder_id=b1.id, name="Rajesh Sharma", designation="Lead Pipeline Project Manager", qualification="B.Tech Mechanical", specialization="Cross-Country Gas Transmission", years_of_experience=14.0, pipeline_experience_years=14.0, certifications=["PMP", "API 1169"]),
        BidderPersonnel(bidder_id=b1.id, name="Vikram Mehta", designation="Chief Welding & NDT Specialist", qualification="B.E. Metallurgy", specialization="Automatic Welding & Radiography", years_of_experience=12.0, pipeline_experience_years=12.0, certifications=["NDT Level III", "CSWIP 3.1"]),
        BidderPersonnel(bidder_id=b1.id, name="Amit Patel", designation="Senior Pipeline Engineer", qualification="B.Tech Mechanical", specialization="HDD River Crossings & Trenching", years_of_experience=10.0, pipeline_experience_years=10.0, certifications=["NDT Level II"]),
        BidderPersonnel(bidder_id=b1.id, name="Sanjay Gupta", designation="Senior QA/QC Pipeline Inspector", qualification="B.E. Mechanical", specialization="Hydrotesting & Pipeline Integrity", years_of_experience=11.0, pipeline_experience_years=11.0, certifications=["ISO 9001 Lead Auditor"]),
        BidderPersonnel(bidder_id=b1.id, name="Dharmendra Rao", designation="Senior Commissioning Engineer", qualification="B.Tech Chemical", specialization="Gas Pipeline Pigging & Drying", years_of_experience=9.0, pipeline_experience_years=9.0, certifications=["Safety in Hydrocarbons"]),
        BidderPersonnel(bidder_id=b1.id, name="Nitin Deshmukh", designation="Lead Site Safety Officer", qualification="Diploma Industrial Safety", specialization="Petroleum Site HSE & ISO 45001", years_of_experience=10.0, pipeline_experience_years=10.0, certifications=["NEBOSH IGC", "ISO 45001 Lead Auditor"])
    ]
    for s in staff_b1:
        db.add(s)

    # Documents for Bidder 1
    b1_stat_pdf = os.path.join(settings.UPLOAD_DIR, "LT_Hydrocarbon_Statutory_GST_PAN.pdf")
    b1_fin_pdf = os.path.join(settings.UPLOAD_DIR, "LT_Hydrocarbon_Audited_Turnover_Financials.pdf")
    b1_exp_pdf = os.path.join(settings.UPLOAD_DIR, "LT_Hydrocarbon_165km_Pipeline_Experience.pdf")
    b1_man_pdf = os.path.join(settings.UPLOAD_DIR, "LT_Hydrocarbon_Key_Engineers_CVs.pdf")
    b1_hse_pdf = os.path.join(settings.UPLOAD_DIR, "LT_Hydrocarbon_HSE_ISO45001_Policy.pdf")

    create_sample_pdf(
        b1_stat_pdf,
        "LARSEN & TOUBRO HYDROCARBON - STATUTORY REGISTRATION CERTIFICATES",
        [
            ("1. Legal Entity & GSTIN Registration", "Legal Name: Larsen & Toubro Hydrocarbon Engineering Limited\nTrade Name: L&T Hydrocarbon\nGSTIN: 27AAACL1234F1Z5 (Maharashtra)\nRegistration Date: 01/07/2017\nStatus: ACTIVE\nTaxpayer Type: Regular"),
            ("2. Permanent Account Number (PAN)", "PAN: AAACL1234F\nName as per ITD: LARSEN & TOUBRO HYDROCARBON ENGINEERING LIMITED\nCategory: Company | Status: Active & Operational"),
            ("3. Udyam Registration", "UDYAM Registration No: UDYAM-MH-12-0098412 | Major Activity: Heavy Engineering / Energy Infrastructure")
        ]
    )

    create_sample_pdf(
        b1_fin_pdf,
        "LARSEN & TOUBRO HYDROCARBON - CA AUDITED FINANCIAL TURNOVER",
        [
            ("1. Independent Chartered Accountant Certificate", "We have audited the books of accounts of M/s Larsen & Toubro Hydrocarbon Engineering Limited. The annual turnover is certified as follows:"),
            ("2. Financial Year Breakdown", "FY 2022-23: INR 18.50 Crore\nFY 2023-24: INR 22.00 Crore\nFY 2024-25: INR 24.50 Crore"),
            ("3. Three-Year Arithmetic Average", "Average Annual Turnover = (18.50 + 22.00 + 24.50) / 3 = INR 21.67 Crore (Surplus: INR 11.67 Crore above requirement).")
        ]
    )

    create_sample_pdf(
        b1_exp_pdf,
        "LARSEN & TOUBRO HYDROCARBON - PIPELINE & HYDROCARBON COMPLETION CERTIFICATE",
        [
            ("1. GAIL Jagdishpur-Haldia Gas Pipeline Phase-II", "Client: GAIL (India) Limited | Scope: EPC Laying of 165 km, 24-inch Outer Diameter API 5L X70 cross-country natural gas transmission pipeline, HDD crossings, and 4 Sectionalizing Valve stations.\nCompletion Date: November 2023 | Project Value: INR 285.00 Crore | Status: Successfully Commissioned and under commercial gas flow."),
            ("2. IOCL Koyali Refinery Hydrocarbon Line", "Client: Indian Oil Corporation Limited | Execution of high-pressure petroleum refinery feeder pipelines and gas metering terminals.")
        ]
    )

    create_sample_pdf(
        b1_man_pdf,
        "LARSEN & TOUBRO HYDROCARBON - TECHNICAL MANPOWER & CVs",
        [
            ("1. Key Senior Engineering Personnel", "1. Rajesh Sharma (Lead Pipeline Project Manager) - 14 years experience in cross-country gas pipelines.\n2. Vikram Mehta (Chief Welding & NDT Specialist - Level III) - 12 years experience.\n3. Amit Patel (Senior Pipeline Engineer - B.Tech Mechanical) - 10 years experience.\n4. Sanjay Gupta (Senior QA/QC Pipeline Inspector) - 11 years experience.\n5. Dharmendra Rao (Senior Commissioning Engineer) - 9 years experience.\n6. Nitin Deshmukh (Lead Safety Officer - NEBOSH / ISO 45001) - 10 years experience.")
        ]
    )

    create_sample_pdf(
        b1_hse_pdf,
        "LARSEN & TOUBRO HYDROCARBON - HSE & SAFETY CERTIFICATION",
        [
            ("1. Occupational Health & Safety System", "Certified ISO 45001:2018 (Certificate No: TUV-IND-45001-89214, Valid through Dec 2027)."),
            ("2. Environmental Management System", "Certified ISO 14001:2015 (Certificate No: TUV-IND-14001-44102, Valid through Nov 2027)."),
            ("3. Site Safety Declaration", "Zero Lost Time Injury (LTI) track record across 10 million safe man-hours on gas transmission pipeline projects.")
        ]
    )

    docs_b1 = [
        Document(bidder_id=b1.id, tender_id=tender1.id, document_name="Statutory_Registration_Certificates.pdf", file_path=b1_stat_pdf, document_type="GST_CERTIFICATE", page_count=1, extracted_text="Larsen & Toubro Hydrocarbon Engineering Limited\nGSTIN: 27AAACL1234F1Z5\nPAN: AAACL1234F\nUDYAM: UDYAM-MH-12-0098412"),
        Document(bidder_id=b1.id, tender_id=tender1.id, document_name="Audited_Turnover_Financials.pdf", file_path=b1_fin_pdf, document_type="FINANCIAL_STATEMENT", page_count=1, extracted_text="FY 2022-23: 18.50 Crore\nFY 2023-24: 22.00 Crore\nFY 2024-25: 24.50 Crore\nAverage: 21.67 Cr"),
        Document(bidder_id=b1.id, tender_id=tender1.id, document_name="165km_Pipeline_Experience_Certificate.pdf", file_path=b1_exp_pdf, document_type="PIPELINE_PROJECT_DOCUMENT", page_count=1, extracted_text="Laying of 165 km, 24-inch natural gas transmission pipeline for GAIL (India) Limited. Successfully completed and commissioned.\nIOCL Koyali refinery oil and gas project experience."),
        Document(bidder_id=b1.id, tender_id=tender1.id, document_name="Key_Technical_Engineers_CVs.pdf", file_path=b1_man_pdf, document_type="PERSONNEL_CV", page_count=1, extracted_text="Rajesh Sharma (Lead Pipeline Manager) - 14 years experience\nVikram Mehta (Chief Welding Specialist) - 12 years experience\nAmit Patel (Senior Pipeline Engineer) - 10 years experience\nSanjay Gupta (Senior Pipeline Inspector) - 11 years experience\nDharmendra Rao (Senior Commissioning Engineer) - 9 years experience\nNitin Deshmukh (Lead Safety Officer) - 10 years experience"),
        Document(bidder_id=b1.id, tender_id=tender1.id, document_name="HSE_Safety_Compliance_Manual.pdf", file_path=b1_hse_pdf, document_type="HSE_DOCUMENT", page_count=1, extracted_text="Certified ISO 45001:2018 and ISO 14001:2015 for petroleum pipeline construction.\nCorporate HSE Policy Manual.")
    ]
    for d in docs_b1:
        db.add(d)
    db.commit()

    entities_b1 = [
        ExtractedEntity(document_id=docs_b1[0].id, entity_type="GSTIN", entity_value="27AAACL1234F1Z5", normalized_value="27AAACL1234F1Z5", confidence=0.98, page_number=1, context_snippet="GSTIN: 27AAACL1234F1Z5 (Maharashtra) Active"),
        ExtractedEntity(document_id=docs_b1[0].id, entity_type="PAN", entity_value="AAACL1234F", normalized_value="AAACL1234F", confidence=0.98, page_number=1, context_snippet="PAN: AAACL1234F (Larsen & Toubro Hydrocarbon)"),
        ExtractedEntity(document_id=docs_b1[0].id, entity_type="COMPANY_NAME", entity_value="Larsen & Toubro Hydrocarbon Engineering Limited", normalized_value="larsen toubro hydrocarbon engineering ltd", confidence=0.98, page_number=1, context_snippet="Larsen & Toubro Hydrocarbon Engineering Limited"),
        ExtractedEntity(document_id=docs_b1[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2022-23: ₹18.50 Cr", normalized_value="185000000.0", confidence=0.96, page_number=1, context_snippet="FY 2022-23: INR 18.50 Crore"),
        ExtractedEntity(document_id=docs_b1[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2023-24: ₹22.00 Cr", normalized_value="220000000.0", confidence=0.96, page_number=1, context_snippet="FY 2023-24: INR 22.00 Crore"),
        ExtractedEntity(document_id=docs_b1[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2024-25: ₹24.50 Cr", normalized_value="245000000.0", confidence=0.96, page_number=1, context_snippet="FY 2024-25: INR 24.50 Crore"),
        ExtractedEntity(document_id=docs_b1[2].id, entity_type="OIL_GAS_PROJECT", entity_value="GAIL Jagdishpur-Haldia Gas Pipeline & IOCL Refinery", normalized_value="gail jagdishpur haldia gas pipeline", confidence=0.96, page_number=1, context_snippet="EPC Laying of 165 km, 24-inch Outer Diameter API 5L X70 cross-country natural gas transmission pipeline for GAIL."),
        ExtractedEntity(document_id=docs_b1[2].id, entity_type="PIPELINE_LENGTH_KM", entity_value="165.0 km", normalized_value="165.0", confidence=0.98, page_number=1, context_snippet="Laying of 165 km, 24-inch Outer Diameter API 5L X70 cross-country natural gas transmission pipeline"),
        ExtractedEntity(document_id=docs_b1[2].id, entity_type="PIPELINE_DIAMETER_INCH", entity_value="24.0 inch", normalized_value="24.0", confidence=0.98, page_number=1, context_snippet="24-inch Outer Diameter API 5L X70"),
        ExtractedEntity(document_id=docs_b1[3].id, entity_type="MANPOWER_RECORD", entity_value="Rajesh Sharma (Lead Pipeline Manager - 14 years)", normalized_value="14.0", confidence=0.96, page_number=1, context_snippet="Rajesh Sharma (Lead Pipeline Project Manager) - 14 years experience"),
        ExtractedEntity(document_id=docs_b1[3].id, entity_type="MANPOWER_RECORD", entity_value="Vikram Mehta (Chief Welding Specialist - 12 years)", normalized_value="12.0", confidence=0.96, page_number=1, context_snippet="Vikram Mehta (Chief Welding & NDT Specialist) - 12 years experience"),
        ExtractedEntity(document_id=docs_b1[3].id, entity_type="MANPOWER_RECORD", entity_value="Amit Patel (Senior Pipeline Engineer - 10 years)", normalized_value="10.0", confidence=0.96, page_number=1, context_snippet="Amit Patel (Senior Pipeline Engineer) - 10 years experience"),
        ExtractedEntity(document_id=docs_b1[3].id, entity_type="MANPOWER_RECORD", entity_value="Sanjay Gupta (Senior Pipeline Inspector - 11 years)", normalized_value="11.0", confidence=0.96, page_number=1, context_snippet="Sanjay Gupta (Senior QA/QC Pipeline Inspector) - 11 years experience"),
        ExtractedEntity(document_id=docs_b1[3].id, entity_type="MANPOWER_RECORD", entity_value="Dharmendra Rao (Senior Commissioning Engineer - 9 years)", normalized_value="9.0", confidence=0.96, page_number=1, context_snippet="Dharmendra Rao (Senior Commissioning Engineer) - 9 years experience"),
        ExtractedEntity(document_id=docs_b1[3].id, entity_type="MANPOWER_RECORD", entity_value="Nitin Deshmukh (Lead Safety Officer - 10 years)", normalized_value="10.0", confidence=0.96, page_number=1, context_snippet="Nitin Deshmukh (Lead Safety Officer) - 10 years experience"),
        ExtractedEntity(document_id=docs_b1[4].id, entity_type="HSE_CERTIFICATION", entity_value="ISO 45001", normalized_value="ISO 45001", confidence=0.98, page_number=1, context_snippet="Certified ISO 45001:2018 Occupational Health & Safety Management System"),
        ExtractedEntity(document_id=docs_b1[4].id, entity_type="HSE_CERTIFICATION", entity_value="ISO 14001", normalized_value="ISO 14001", confidence=0.98, page_number=1, context_snippet="Certified ISO 14001:2015 Environmental Management System")
    ]
    for ent in entities_b1:
        db.add(ent)
    db.commit()


    # =============================================================
    # BIDDER 2: INDUS PIPELINE INFRASTRUCTURE (FAIL - HIGH RISK, SCORE: 60%)
    # Shortfall in Pipeline Length (60 km vs 100 km), Turnover Shortfall (₹6.83 Cr vs ₹10.0 Cr),
    # Only 3 Technical Personnel, Missing HSE Document
    # =============================================================
    b2 = Bidder(
        tender_id=tender1.id,
        legal_name="Indus Pipeline Infrastructure Limited",
        trade_name="Indus Pipeline",
        pan="AABCI5678K",
        gstin="07AABCI5678K1Z2",
        registered_address="Indus House, Barakhamba Road, Connaught Place, New Delhi 110001",
        contact_information={"email": "contracts@induspipeline.in", "phone": "+91 11 4120 7800"},
        bidder_type="INDIAN_EPC_CONTRACTOR",
        country="INDIA",
        oil_gas_experience_years=12.0,
        pipeline_experience_years=9.0,
        udyam_number="UDYAM-DL-04-0012948",
        cin="U45200DL2014PLC264819",
        email="contracts@induspipeline.in",
        phone="+91 11 4120 7800",
        contact_person="Ramesh K. Jindal (Director - Projects)",
        status="SUBMITTED"
    )
    db.add(b2)
    db.commit()
    db.refresh(b2)

    bid2 = Bid(
        tender_id=tender1.id,
        bidder_id=b2.id,
        bid_reference_number="BID-GAIL-2026-INDUS-002",
        submission_date=datetime.now(timezone.utc) - timedelta(days=1),
        technical_bid_status="UNDER_EVALUATION",
        financial_bid_amount=2150000000.0,
        currency="INR",
        remarks="Bid submitted with technical qualification shortfalls."
    )
    db.add(bid2)

    p2_1 = BidderProject(
        bidder_id=b2.id,
        project_name="IOCL Mathura-Tundla Spur Pipeline Construction",
        client_name="Indian Oil Corporation Limited",
        client_type="PUBLIC_SECTOR_UNDERTAKING",
        sector="PETROLEUM",
        project_type="PIPELINE_CONSTRUCTION",
        pipeline_type="PRODUCT_PIPELINE",
        pipeline_length_km=60.0,
        pipeline_diameter="18 inch NB API 5L X60",
        project_value=680000000.0,
        currency="INR",
        location="Uttar Pradesh",
        start_date=datetime.now(timezone.utc) - timedelta(days=365*3),
        completion_date=datetime.now(timezone.utc) - timedelta(days=365*2),
        scope_of_work="Pipeline laying and spur terminal connection",
        bidder_role="MAIN_CONTRACTOR",
        contract_reference="IOCL/MT/2019/08"
    )
    db.add(p2_1)

    staff_b2 = [
        BidderPersonnel(bidder_id=b2.id, name="Pankaj Verma", designation="Pipeline Engineer", qualification="B.E. Mechanical", years_of_experience=8.5, pipeline_experience_years=8.5),
        BidderPersonnel(bidder_id=b2.id, name="Sunil Kumar", designation="Mechanical Engineer", qualification="B.Tech Mechanical", years_of_experience=9.0, pipeline_experience_years=9.0),
        BidderPersonnel(bidder_id=b2.id, name="Ankit Mishra", designation="Safety Officer", qualification="Diploma Safety", years_of_experience=8.0, pipeline_experience_years=8.0)
    ]
    for s in staff_b2:
        db.add(s)

    b2_stat_pdf = os.path.join(settings.UPLOAD_DIR, "Indus_Pipeline_Statutory_GST_PAN.pdf")
    b2_fin_pdf = os.path.join(settings.UPLOAD_DIR, "Indus_Pipeline_Turnover_Financials.pdf")
    b2_exp_pdf = os.path.join(settings.UPLOAD_DIR, "Indus_Pipeline_60km_Experience.pdf")
    b2_man_pdf = os.path.join(settings.UPLOAD_DIR, "Indus_Pipeline_Manpower_CVs.pdf")

    create_sample_pdf(
        b2_stat_pdf,
        "INDUS PIPELINE INFRASTRUCTURE - STATUTORY CERTIFICATES",
        [
            ("1. GST & PAN Registration", "Entity: Indus Pipeline Infrastructure Limited\nGSTIN: 07AABCI5678K1Z2 (Delhi)\nPAN: AABCI5678K\nStatus: ACTIVE")
        ]
    )

    create_sample_pdf(
        b2_fin_pdf,
        "INDUS PIPELINE INFRASTRUCTURE - AUDITED ANNUAL TURNOVER",
        [
            ("1. Three-Year Turnover Statement", "FY 2022-23: INR 6.50 Crore\nFY 2023-24: INR 7.20 Crore\nFY 2024-25: INR 6.80 Crore\nAverage Annual Turnover: INR 6.83 Crore (Below tender threshold of INR 10.00 Crore, Shortfall: INR 3.17 Crore).")
        ]
    )

    create_sample_pdf(
        b2_exp_pdf,
        "INDUS PIPELINE INFRASTRUCTURE - PIPELINE COMPLETION CERTIFICATE",
        [
            ("1. IOCL Mathura-Tundla Spur Pipeline", "Client: Indian Oil Corporation Limited\nScope: Construction of 60 km, 18-inch OD petroleum spur pipeline.\nCompleted: March 2022 | Executed Length: 60 km (Below mandatory 100 km threshold).")
        ]
    )

    create_sample_pdf(
        b2_man_pdf,
        "INDUS PIPELINE INFRASTRUCTURE - TECHNICAL PERSONNEL",
        [
            ("1. Staff List", "1. Pankaj Verma (Pipeline Engineer) - 8.5 years experience\n2. Sunil Kumar (Mechanical Engineer) - 9.0 years experience\n3. Ankit Mishra (Safety Officer) - 8.0 years experience\n(Total qualifying personnel: 3 engineers vs 5 mandatory).")
        ]
    )

    docs_b2 = [
        Document(bidder_id=b2.id, tender_id=tender1.id, document_name="Indus_Statutory_GST_PAN.pdf", file_path=b2_stat_pdf, document_type="GST_CERTIFICATE", page_count=1, extracted_text="Indus Pipeline Infrastructure Limited\nGSTIN: 07AABCI5678K1Z2\nPAN: AABCI5678K"),
        Document(bidder_id=b2.id, tender_id=tender1.id, document_name="Indus_Turnover_Statement.pdf", file_path=b2_fin_pdf, document_type="FINANCIAL_STATEMENT", page_count=1, extracted_text="FY 2022-23: 6.50 Crore\nFY 2023-24: 7.20 Crore\nFY 2024-25: 6.80 Crore\nAverage: 6.83 Cr"),
        Document(bidder_id=b2.id, tender_id=tender1.id, document_name="Indus_60km_Pipeline_Certificate.pdf", file_path=b2_exp_pdf, document_type="PIPELINE_PROJECT_DOCUMENT", page_count=1, extracted_text="Construction of 60 km spur pipeline for IOCL. Successfully completed 60 km length.\nPetroleum sector experience."),
        Document(bidder_id=b2.id, tender_id=tender1.id, document_name="Indus_Manpower_List.pdf", file_path=b2_man_pdf, document_type="PERSONNEL_CV", page_count=1, extracted_text="Pankaj Verma (Pipeline Engineer) - 8.5 years\nSunil Kumar (Mechanical Engineer) - 9.0 years\nAnkit Mishra (Safety Officer) - 8.0 years")
    ]
    for d in docs_b2:
        db.add(d)
    db.commit()

    entities_b2 = [
        ExtractedEntity(document_id=docs_b2[0].id, entity_type="GSTIN", entity_value="07AABCI5678K1Z2", normalized_value="07AABCI5678K1Z2", confidence=0.98, page_number=1, context_snippet="GSTIN: 07AABCI5678K1Z2 Active"),
        ExtractedEntity(document_id=docs_b2[0].id, entity_type="PAN", entity_value="AABCI5678K", normalized_value="AABCI5678K", confidence=0.98, page_number=1, context_snippet="PAN: AABCI5678K (Indus Pipeline)"),
        ExtractedEntity(document_id=docs_b2[0].id, entity_type="COMPANY_NAME", entity_value="Indus Pipeline Infrastructure Limited", normalized_value="indus pipeline infrastructure ltd", confidence=0.98, page_number=1, context_snippet="Indus Pipeline Infrastructure Limited"),
        ExtractedEntity(document_id=docs_b2[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2022-23: ₹6.50 Cr", normalized_value="65000000.0", confidence=0.95, page_number=1, context_snippet="FY 2022-23: INR 6.50 Crore"),
        ExtractedEntity(document_id=docs_b2[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2023-24: ₹7.20 Cr", normalized_value="72000000.0", confidence=0.95, page_number=1, context_snippet="FY 2023-24: INR 7.20 Crore"),
        ExtractedEntity(document_id=docs_b2[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2024-25: ₹6.80 Cr", normalized_value="68000000.0", confidence=0.95, page_number=1, context_snippet="FY 2024-25: INR 6.80 Crore"),
        ExtractedEntity(document_id=docs_b2[2].id, entity_type="OIL_GAS_PROJECT", entity_value="IOCL Mathura-Tundla Spur Pipeline", normalized_value="iocl mathura tundla spur pipeline", confidence=0.94, page_number=1, context_snippet="Construction of 60 km spur pipeline for IOCL."),
        ExtractedEntity(document_id=docs_b2[2].id, entity_type="PIPELINE_LENGTH_KM", entity_value="60.0 km", normalized_value="60.0", confidence=0.96, page_number=1, context_snippet="Construction of 60 km spur pipeline for IOCL"),
        ExtractedEntity(document_id=docs_b2[3].id, entity_type="MANPOWER_RECORD", entity_value="Pankaj Verma (Pipeline Engineer - 8.5 years)", normalized_value="8.5", confidence=0.95, page_number=1, context_snippet="Pankaj Verma (Pipeline Engineer) - 8.5 years"),
        ExtractedEntity(document_id=docs_b2[3].id, entity_type="MANPOWER_RECORD", entity_value="Sunil Kumar (Mechanical Engineer - 9.0 years)", normalized_value="9.0", confidence=0.95, page_number=1, context_snippet="Sunil Kumar (Mechanical Engineer) - 9.0 years"),
        ExtractedEntity(document_id=docs_b2[3].id, entity_type="MANPOWER_RECORD", entity_value="Ankit Mishra (Safety Officer - 8.0 years)", normalized_value="8.0", confidence=0.95, page_number=1, context_snippet="Ankit Mishra (Safety Officer) - 8.0 years")
    ]
    for ent in entities_b2:
        db.add(ent)
    db.commit()


    # =============================================================
    # BIDDER 3: PETROCON ENERGY PROJECTS LLP (REVIEW - MEDIUM RISK, SCORE: 85%)
    # =============================================================
    b3 = Bidder(
        tender_id=tender1.id,
        legal_name="PetroCon Energy Projects LLP",
        trade_name="PetroCon Energy",
        pan="AABCP9012M",
        gstin="24AABCP9012M1Z8",
        registered_address="PetroCon Heights, SG Highway, Ahmedabad, Gujarat 380054",
        contact_information={"email": "info@petroconenergy.in", "phone": "+91 79 2685 4100"},
        bidder_type="LIMITED_LIABILITY_PARTNERSHIP",
        country="INDIA",
        oil_gas_experience_years=15.0,
        pipeline_experience_years=11.0,
        udyam_number="UDYAM-GJ-01-0038914",
        cin="AAA-9012",
        email="info@petroconenergy.in",
        phone="+91 79 2685 4100",
        contact_person="Ketan B. Patel (Designated Partner)",
        status="SUBMITTED"
    )
    db.add(b3)
    db.commit()
    db.refresh(b3)

    bid3 = Bid(
        tender_id=tender1.id,
        bidder_id=b3.id,
        bid_reference_number="BID-GAIL-2026-PETROCON-003",
        submission_date=datetime.now(timezone.utc) - timedelta(days=1),
        technical_bid_status="UNDER_EVALUATION",
        financial_bid_amount=2280000000.0,
        currency="INR"
    )
    db.add(bid3)

    p3_1 = BidderProject(
        bidder_id=b3.id,
        project_name="Gujarat Gas City Gas Distribution Steel Grid Laying",
        client_name="Gujarat Gas Limited",
        client_type="PUBLIC_SECTOR_UNDERTAKING",
        sector="CITY_GAS_DISTRIBUTION",
        project_type="PIPELINE_LAYING",
        pipeline_type="CGD_STEEL_NETWORK",
        pipeline_length_km=95.0,
        pipeline_diameter="16 inch NB API 5L X52",
        project_value=1150000000.0,
        currency="INR",
        location="Surat & Navsari",
        start_date=datetime.now(timezone.utc) - timedelta(days=365*2),
        completion_date=datetime.now(timezone.utc) - timedelta(days=180),
        scope_of_work="Steel pipeline laying and pressure regulating skids",
        bidder_role="JV_PARTNER",
        contract_reference="GGL/CGD/SURAT/2022/11"
    )
    db.add(p3_1)

    staff_b3 = [
        BidderPersonnel(bidder_id=b3.id, name="Hardik Shah", designation="Senior Pipeline Engineer", qualification="B.Tech Mechanical", years_of_experience=10.0, pipeline_experience_years=10.0),
        BidderPersonnel(bidder_id=b3.id, name="Bhavesh Joshi", designation="Mechanical Engineer", qualification="B.E. Mechanical", years_of_experience=9.0, pipeline_experience_years=9.0),
        BidderPersonnel(bidder_id=b3.id, name="Chirag Dave", designation="Welding Inspector", qualification="B.E. Metallurgy", years_of_experience=8.5, pipeline_experience_years=8.5),
        BidderPersonnel(bidder_id=b3.id, name="Manish Vyas", designation="NDT Level II Inspector", qualification="Diploma Mechanical", years_of_experience=8.0, pipeline_experience_years=8.0),
        BidderPersonnel(bidder_id=b3.id, name="Nilesh Parmar", designation="Assistant Pipeline Engineer", qualification="B.Tech Mechanical", years_of_experience=7.5, pipeline_experience_years=7.5)
    ]
    for s in staff_b3:
        db.add(s)

    b3_stat_pdf = os.path.join(settings.UPLOAD_DIR, "PetroCon_Statutory_GST_PAN.pdf")
    b3_fin_pdf = os.path.join(settings.UPLOAD_DIR, "PetroCon_Audited_Financials.pdf")
    b3_exp_pdf = os.path.join(settings.UPLOAD_DIR, "PetroCon_95km_CGD_Experience.pdf")
    b3_man_pdf = os.path.join(settings.UPLOAD_DIR, "PetroCon_Manpower_CVs.pdf")

    create_sample_pdf(
        b3_stat_pdf,
        "PETROCON ENERGY PROJECTS - STATUTORY CERTIFICATES",
        [
            ("1. Legal Entity & GST Registration", "Entity: PetroCon Energy Projects LLP (formerly PetroCon Infra JV)\nGSTIN: 24AABCP9012M1Z8 (Gujarat)\nPAN: AABCP9012M\nStatus: ACTIVE")
        ]
    )

    create_sample_pdf(
        b3_fin_pdf,
        "PETROCON ENERGY PROJECTS - FINANCIAL TURNOVER",
        [
            ("1. Turnover Figures", "FY 2022-23: INR 12.00 Crore\nFY 2023-24: INR 14.00 Crore\nFY 2024-25: INR 11.50 Crore\nAverage Annual Turnover: INR 12.50 Crore (Exceeds ₹10.00 Cr requirement).")
        ]
    )

    create_sample_pdf(
        b3_exp_pdf,
        "PETROCON ENERGY PROJECTS - GAS PIPELINE EXPERIENCE CERTIFICATE",
        [
            ("1. Gujarat Gas City Gas Distribution Pipeline Network", "Issued to: PetroCon Infra JV (Affiliate Entity of PetroCon Energy Projects LLP).\nScope: Laying of 95 km, 12-inch and 16-inch medium-pressure natural gas network in Surat-Navsari Geographical Area.\nStatus: Executed 95 km length. Requires officer discretion on affiliate entity certificate and diameter threshold.")
        ]
    )

    create_sample_pdf(
        b3_man_pdf,
        "PETROCON ENERGY PROJECTS - KEY PERSONNEL CVs",
        [
            ("1. Technical Team", "1. Hardik Shah (Senior Pipeline Engineer) - 10 years experience\n2. Bhavesh Joshi (Mechanical Engineer) - 9 years experience\n3. Chirag Dave (Welding Inspector) - 8.5 years experience\n4. Manish Vyas (NDT Level II) - 8.0 years experience\n5. Nilesh Parmar (Assistant Pipeline Engineer) - 7.5 years experience (Slightly under 8 yrs).")
        ]
    )

    docs_b3 = [
        Document(bidder_id=b3.id, tender_id=tender1.id, document_name="PetroCon_Statutory_GST_PAN.pdf", file_path=b3_stat_pdf, document_type="GST_CERTIFICATE", page_count=1, extracted_text="PetroCon Energy Projects LLP\nGSTIN: 24AABCP9012M1Z8\nPAN: AABCP9012M"),
        Document(bidder_id=b3.id, tender_id=tender1.id, document_name="PetroCon_Turnover.pdf", file_path=b3_fin_pdf, document_type="FINANCIAL_STATEMENT", page_count=1, extracted_text="FY 2022-23: 12.00 Crore\nFY 2023-24: 14.00 Crore\nFY 2024-25: 11.50 Crore\nAverage: 12.50 Cr"),
        Document(bidder_id=b3.id, tender_id=tender1.id, document_name="PetroCon_95km_CGD_Certificate.pdf", file_path=b3_exp_pdf, document_type="PIPELINE_PROJECT_DOCUMENT", page_count=1, extracted_text="Laying of 95 km natural gas network for Gujarat Gas. Issued to PetroCon Infra JV.\nHydrocarbon and natural gas project experience."),
        Document(bidder_id=b3.id, tender_id=tender1.id, document_name="PetroCon_Manpower_List.pdf", file_path=b3_man_pdf, document_type="PERSONNEL_CV", page_count=1, extracted_text="Hardik Shah (Pipeline Engineer) - 10 years\nBhavesh Joshi (Mechanical Engineer) - 9 years\nChirag Dave (Welding Inspector) - 8.5 years\nManish Vyas (NDT Level II) - 8.0 years\nNilesh Parmar (Assistant Engineer) - 7.5 years")
    ]
    for d in docs_b3:
        db.add(d)
    db.commit()

    entities_b3 = [
        ExtractedEntity(document_id=docs_b3[0].id, entity_type="GSTIN", entity_value="24AABCP9012M1Z8", normalized_value="24AABCP9012M1Z8", confidence=0.98, page_number=1, context_snippet="GSTIN: 24AABCP9012M1Z8 Active"),
        ExtractedEntity(document_id=docs_b3[0].id, entity_type="PAN", entity_value="AABCP9012M", normalized_value="AABCP9012M", confidence=0.98, page_number=1, context_snippet="PAN: AABCP9012M"),
        ExtractedEntity(document_id=docs_b3[0].id, entity_type="COMPANY_NAME", entity_value="PetroCon Energy Projects LLP", normalized_value="petrocon energy projects llp", confidence=0.98, page_number=1, context_snippet="PetroCon Energy Projects LLP"),
        ExtractedEntity(document_id=docs_b3[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2022-23: ₹12.00 Cr", normalized_value="120000000.0", confidence=0.95, page_number=1, context_snippet="FY 2022-23: INR 12.00 Crore"),
        ExtractedEntity(document_id=docs_b3[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2023-24: ₹14.00 Cr", normalized_value="140000000.0", confidence=0.95, page_number=1, context_snippet="FY 2023-24: INR 14.00 Crore"),
        ExtractedEntity(document_id=docs_b3[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2024-25: ₹11.50 Cr", normalized_value="115000000.0", confidence=0.95, page_number=1, context_snippet="FY 2024-25: INR 11.50 Crore"),
        ExtractedEntity(document_id=docs_b3[2].id, entity_type="OIL_GAS_PROJECT", entity_value="Gujarat Gas CGD Network Laying", normalized_value="gujarat gas cgd network", confidence=0.94, page_number=1, context_snippet="Laying of 95 km natural gas network for Gujarat Gas."),
        ExtractedEntity(document_id=docs_b3[2].id, entity_type="PIPELINE_LENGTH_KM", entity_value="95.0 km", normalized_value="95.0", confidence=0.96, page_number=1, context_snippet="Laying of 95 km natural gas network"),
        ExtractedEntity(document_id=docs_b3[3].id, entity_type="MANPOWER_RECORD", entity_value="Hardik Shah (Pipeline Engineer - 10 years)", normalized_value="10.0", confidence=0.95, page_number=1, context_snippet="Hardik Shah (Pipeline Engineer) - 10 years"),
        ExtractedEntity(document_id=docs_b3[3].id, entity_type="MANPOWER_RECORD", entity_value="Bhavesh Joshi (Mechanical Engineer - 9 years)", normalized_value="9.0", confidence=0.95, page_number=1, context_snippet="Bhavesh Joshi (Mechanical Engineer) - 9 years"),
        ExtractedEntity(document_id=docs_b3[3].id, entity_type="MANPOWER_RECORD", entity_value="Chirag Dave (Welding Inspector - 8.5 years)", normalized_value="8.5", confidence=0.95, page_number=1, context_snippet="Chirag Dave (Welding Inspector) - 8.5 years"),
        ExtractedEntity(document_id=docs_b3[3].id, entity_type="MANPOWER_RECORD", entity_value="Manish Vyas (NDT Level II - 8.0 years)", normalized_value="8.0", confidence=0.95, page_number=1, context_snippet="Manish Vyas (NDT Level II) - 8.0 years"),
        ExtractedEntity(document_id=docs_b3[3].id, entity_type="MANPOWER_RECORD", entity_value="Nilesh Parmar (Assistant Engineer - 7.5 years)", normalized_value="7.5", confidence=0.95, page_number=1, context_snippet="Nilesh Parmar (Assistant Engineer) - 7.5 years")
    ]
    for ent in entities_b3:
        db.add(ent)
    db.commit()


    # =============================================================
    # BIDDER 4: VANGUARD HYDROCARBON SOLUTIONS (CRITICAL RISK - IDENTITY MISMATCH)
    # =============================================================
    b4 = Bidder(
        tender_id=tender1.id,
        legal_name="Vanguard Hydrocarbon Solutions Limited",
        trade_name="Vanguard Hydrocarbon",
        pan="AABCV4321P",
        gstin="29AABCV4321P1Z9",
        registered_address="Vanguard Tech Park, Whitefield, Bengaluru, Karnataka 560066",
        contact_information={"email": "legal@vanguardhydrocarbon.com", "phone": "+91 80 4910 3200"},
        bidder_type="INDIAN_EPC_CONTRACTOR",
        country="INDIA",
        oil_gas_experience_years=8.0,
        pipeline_experience_years=5.0,
        udyam_number="UDYAM-KA-02-0045812",
        cin="U23200KA2016PLC091240",
        email="legal@vanguardhydrocarbon.com",
        phone="+91 80 4910 3200",
        contact_person="Vijay R. Nair (Managing Director)",
        status="SUBMITTED"
    )
    db.add(b4)
    db.commit()
    db.refresh(b4)

    bid4 = Bid(
        tender_id=tender1.id,
        bidder_id=b4.id,
        bid_reference_number="BID-GAIL-2026-VANGUARD-004",
        submission_date=datetime.now(timezone.utc) - timedelta(days=1),
        technical_bid_status="DISQUALIFIED",
        financial_bid_amount=2450000000.0,
        currency="INR"
    )
    db.add(bid4)

    b4_stat_pdf = os.path.join(settings.UPLOAD_DIR, "Vanguard_Statutory_GST_PAN.pdf")
    b4_fin_pdf = os.path.join(settings.UPLOAD_DIR, "Vanguard_Financials.pdf")

    create_sample_pdf(
        b4_stat_pdf,
        "VANGUARD HYDROCARBON - STATUTORY REGISTRATION & DISCLOSURES",
        [
            ("1. Statutory Details", "Bidder Name: Vanguard Hydrocarbon Solutions Limited\nGSTIN Registered Legal Name: Vanguard Energy Ventures Pvt Ltd (Identity Mismatch)\nPAN: AABCV4321P (Assigned to Vanguard Trading Corp)\nFlagged in CPPP Central Debarment list.")
        ]
    )

    create_sample_pdf(
        b4_fin_pdf,
        "VANGUARD HYDROCARBON - FINANCIAL TURNOVER",
        [
            ("1. Financial Breakdown", "FY 2022-23: INR 15.00 Crore\nFY 2023-24: INR 16.50 Crore\nFY 2024-25: INR 14.00 Crore\nAverage: INR 15.17 Crore.")
        ]
    )

    docs_b4 = [
        Document(bidder_id=b4.id, tender_id=tender1.id, document_name="Vanguard_Statutory_GST_PAN.pdf", file_path=b4_stat_pdf, document_type="GST_CERTIFICATE", page_count=1, extracted_text="Vanguard Hydrocarbon Solutions Limited\nGSTIN Registered Legal Name: Vanguard Energy Ventures Pvt Ltd\nPAN: AABCV4321P"),
        Document(bidder_id=b4.id, tender_id=tender1.id, document_name="Vanguard_Turnover.pdf", file_path=b4_fin_pdf, document_type="FINANCIAL_STATEMENT", page_count=1, extracted_text="FY 2022-23: 15.00 Crore\nFY 2023-24: 16.50 Crore\nFY 2024-25: 14.00 Crore\nAverage: 15.17 Cr")
    ]
    for d in docs_b4:
        db.add(d)
    db.commit()

    entities_b4 = [
        ExtractedEntity(document_id=docs_b4[0].id, entity_type="GSTIN", entity_value="29AABCV4321P1Z9", normalized_value="29AABCV4321P1Z9", confidence=0.98, page_number=1, context_snippet="GSTIN: 29AABCV4321P1Z9"),
        ExtractedEntity(document_id=docs_b4[0].id, entity_type="PAN", entity_value="AABCV4321P", normalized_value="AABCV4321P", confidence=0.98, page_number=1, context_snippet="PAN: AABCV4321P"),
        ExtractedEntity(document_id=docs_b4[0].id, entity_type="COMPANY_NAME", entity_value="Vanguard Energy Ventures Pvt Ltd", normalized_value="vanguard energy ventures pvt ltd", confidence=0.90, page_number=1, context_snippet="Vanguard Energy Ventures Pvt Ltd"),
        ExtractedEntity(document_id=docs_b4[0].id, entity_type="BLACKLIST_DECLARATION", entity_value="FLAGGED: Blacklisting / Debarment Disclosed", normalized_value="DEBARRED", confidence=0.95, page_number=1, context_snippet="Flagged in CPPP Central Debarment list."),
        ExtractedEntity(document_id=docs_b4[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2022-23: ₹15.00 Cr", normalized_value="150000000.0", confidence=0.95, page_number=1, context_snippet="FY 2022-23: INR 15.00 Crore"),
        ExtractedEntity(document_id=docs_b4[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2023-24: ₹16.50 Cr", normalized_value="165000000.0", confidence=0.95, page_number=1, context_snippet="FY 2023-24: INR 16.50 Crore"),
        ExtractedEntity(document_id=docs_b4[1].id, entity_type="FINANCIAL_TURNOVER", entity_value="FY 2024-25: ₹14.00 Cr", normalized_value="140000000.0", confidence=0.95, page_number=1, context_snippet="FY 2024-25: INR 14.00 Crore")
    ]
    for ent in entities_b4:
        db.add(ent)
    db.commit()

    # -------------------------------------------------------------
    # EXECUTE AUTOMATED COMPLIANCE VERIFICATION ON ALL 4 BIDDERS
    # -------------------------------------------------------------
    logger.info("Executing 7 Core Checkers on all 4 Demonstration Bidders...")
    for b in [b1, b2, b3, b4]:
        res = ComplianceEngine.run_full_verification(db=db, bidder_id=b.id, officer_id=officer_user.id, officer_name=officer_user.name)
        logger.info(f"Verified Bidder '{b.legal_name}' -> Score: {res['score']['overall_score']}%, Risk: {res['risk']['risk_level']}, Status: {res['status']}")

    db.close()
    logger.info("Database seeding successfully completed!")

if __name__ == "__main__":
    seed()
