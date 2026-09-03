import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="PROCUREMENT_OFFICER")  # ADMIN, PROCUREMENT_OFFICER
    department = Column(String(255), default="Ministry of Petroleum & Natural Gas - Tender Evaluation Cell")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
    
    tenders_created = relationship("Tender", back_populates="creator")
    officer_reviews = relationship("OfficerReview", back_populates="officer")
    audit_logs = relationship("AuditLog", back_populates="user")

class Tender(Base):
    """
    Petroleum & Natural Gas Pipeline Tender Specification Entity
    """
    __tablename__ = "tenders"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_number = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    issuing_organization = Column(String(255), nullable=False, default="GAIL (India) Limited")
    ministry = Column(String(255), nullable=False, default="Ministry of Petroleum & Natural Gas")
    sector = Column(String(100), default="OIL_AND_GAS")
    tender_type = Column(String(100), default="PIPELINE_PROCUREMENT")
    project_type = Column(String(100), default="PIPELINE_CONSTRUCTION")
    pipeline_type = Column(String(100), default="CROSS_COUNTRY_PIPELINE")
    location = Column(String(255), default="National Gas Grid, India")
    category = Column(String(100), default="Petroleum & Pipeline Infrastructure")
    description = Column(Text, nullable=True)
    estimated_value = Column(Float, default=0.0)
    tender_issue_date = Column(DateTime, default=get_utc_now)
    submission_deadline = Column(DateTime, nullable=True)
    evaluation_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="ACTIVE", index=True)  # DRAFT, ACTIVE, UNDER_REVIEW, CLOSED
    raw_pdf_path = Column(String(500), nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
    
    # Backward compatibility alias properties
    @property
    def organization(self):
        return self.issuing_organization

    @organization.setter
    def organization(self, value):
        self.issuing_organization = value

    @property
    def issue_date(self):
        return self.tender_issue_date

    @issue_date.setter
    def issue_date(self, value):
        self.tender_issue_date = value

    
    creator = relationship("User", back_populates="tenders_created")
    requirements = relationship("Requirement", back_populates="tender", cascade="all, delete-orphan")
    bidders = relationship("Bidder", back_populates="tender", cascade="all, delete-orphan")
    bids = relationship("Bid", back_populates="tender", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="tender", cascade="all, delete-orphan")

class Requirement(Base):
    """
    Structured Petroleum Tender Eligibility & Compliance Criteria
    """
    __tablename__ = "requirements"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id"), nullable=False, index=True)
    clause_number = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    original_text = Column(Text, nullable=True)
    normalized_requirement = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    mandatory = Column(Boolean, default=True)
    threshold = Column(Float, nullable=True)
    threshold_unit = Column(String(50), nullable=True)
    comparison_operator = Column(String(20), default=">=")
    required_years = Column(Float, nullable=True)
    required_project_count = Column(Integer, default=1)
    required_pipeline_length_km = Column(Float, nullable=True)
    required_project_value = Column(Float, nullable=True)
    required_pipeline_type = Column(String(100), nullable=True)
    required_sector = Column(String(100), default="OIL_AND_GAS")
    required_qualification = Column(String(255), nullable=True)
    required_manpower_count = Column(Integer, default=5)
    required_evidence_type = Column(String(100), nullable=True)
    conditions = Column(JSON, default=dict)
    extraction_confidence = Column(Float, default=1.0)
    period = Column(String(100), nullable=True)
    evidence_required = Column(JSON, default=list)
    verification_method = Column(String(50), default="RULE_AND_PORTAL")
    rule_version = Column(String(20), default="2.0")
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
    
    tender = relationship("Tender", back_populates="requirements")
    compliance_checks = relationship("ComplianceCheck", back_populates="requirement", cascade="all, delete-orphan")

# Alias for TenderRequirement
TenderRequirement = Requirement

class Bidder(Base):
    """
    Petroleum Engineering & EPC Bidder Corporate Entity
    """
    __tablename__ = "bidders"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id"), nullable=False, index=True)
    legal_name = Column(String(255), nullable=False, index=True)
    trade_name = Column(String(255), nullable=True)
    pan = Column(String(20), nullable=True, index=True)
    gstin = Column(String(50), nullable=True, index=True)
    registered_address = Column(Text, nullable=True)
    contact_information = Column(JSON, default=dict)
    bidder_type = Column(String(100), default="INDIAN_EPC_CONTRACTOR")  # EPC_CONTRACTOR, JV, CONSORTIUM
    country = Column(String(100), default="INDIA")
    oil_gas_experience_years = Column(Float, default=0.0)
    pipeline_experience_years = Column(Float, default=0.0)
    udyam_number = Column(String(50), nullable=True, index=True)
    cin = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    contact_person = Column(String(255), nullable=True)
    status = Column(String(50), default="SUBMITTED", index=True)
    submitted_at = Column(DateTime, default=get_utc_now)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
    
    # Compatibility properties
    @property
    def bidder_name(self):
        return self.legal_name

    @bidder_name.setter
    def bidder_name(self, value):
        self.legal_name = value
    
    tender = relationship("Tender", back_populates="bidders")
    bids = relationship("Bid", back_populates="bidder", cascade="all, delete-orphan")
    projects = relationship("BidderProject", back_populates="bidder", cascade="all, delete-orphan")
    personnel = relationship("BidderPersonnel", back_populates="bidder", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="bidder", cascade="all, delete-orphan")
    compliance_checks = relationship("ComplianceCheck", back_populates="bidder", cascade="all, delete-orphan")
    portal_verifications = relationship("PortalVerification", back_populates="bidder", cascade="all, delete-orphan")
    compliance_score = relationship("ComplianceScore", uselist=False, back_populates="bidder", cascade="all, delete-orphan")
    risk_assessment = relationship("RiskAssessment", uselist=False, back_populates="bidder", cascade="all, delete-orphan")
    recommendation = relationship("Recommendation", uselist=False, back_populates="bidder", cascade="all, delete-orphan")
    officer_reviews = relationship("OfficerReview", back_populates="bidder", cascade="all, delete-orphan")

class Bid(Base):
    """
    Formal Bid Submission Record linking Bidder and Tender
    """
    __tablename__ = "bids"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tender_id = Column(String(36), ForeignKey("tenders.id"), nullable=False, index=True)
    bidder_id = Column(String(36), ForeignKey("bidders.id"), nullable=False, index=True)
    bid_reference_number = Column(String(100), unique=True, index=True, nullable=False)
    submission_date = Column(DateTime, default=get_utc_now)
    technical_bid_status = Column(String(50), default="UNDER_EVALUATION")  # SUBMITTED, UNDER_EVALUATION, QUALIFIED, DISQUALIFIED
    financial_bid_amount = Column(Float, nullable=True)
    currency = Column(String(10), default="INR")
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    tender = relationship("Tender", back_populates="bids")
    bidder = relationship("Bidder", back_populates="bids")

class BidderProject(Base):
    """
    Prior Petroleum & Pipeline Project Execution Experience Record
    """
    __tablename__ = "bidder_projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    bidder_id = Column(String(36), ForeignKey("bidders.id"), nullable=False, index=True)
    project_name = Column(String(500), nullable=False)
    client_name = Column(String(255), nullable=False)  # e.g., GAIL, IOCL, ONGC, BPCL
    client_type = Column(String(100), default="PUBLIC_SECTOR_UNDERTAKING")  # PSU, PRIVATE, MULTINATIONAL
    sector = Column(String(100), default="OIL_AND_GAS")  # OIL_AND_GAS, PETROLEUM, REFINERY, NATURAL_GAS
    project_type = Column(String(100), default="PIPELINE_CONSTRUCTION")
    pipeline_type = Column(String(100), default="NATURAL_GAS")
    pipeline_length_km = Column(Float, nullable=True)
    pipeline_diameter = Column(String(100), nullable=True)  # e.g., '24 inch NB API 5L X70'
    project_value = Column(Float, default=0.0)
    currency = Column(String(10), default="INR")
    location = Column(String(255), nullable=True)
    start_date = Column(DateTime, nullable=True)
    completion_date = Column(DateTime, nullable=True)
    scope_of_work = Column(Text, nullable=True)  # PIPELINE_LAYING, HYDROTESTING, HDD, WELDING, EPC
    bidder_role = Column(String(100), default="EPC_CONTRACTOR")  # EPC_CONTRACTOR, MAIN_CONTRACTOR, JV_PARTNER
    contract_reference = Column(String(100), nullable=True)
    evidence_document_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    bidder = relationship("Bidder", back_populates="projects")

class BidderPersonnel(Base):
    """
    Key Technical & Engineering Personnel deployed for Petroleum Pipeline projects
    """
    __tablename__ = "bidder_personnel"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    bidder_id = Column(String(36), ForeignKey("bidders.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    designation = Column(String(255), nullable=False)  # Lead Pipeline Manager, Welding Inspector
    qualification = Column(String(255), nullable=False)  # B.Tech Mechanical, B.E. Civil
    specialization = Column(String(255), nullable=True)  # Cross-country Gas Pipeline, HDD Crossing
    years_of_experience = Column(Float, default=0.0)
    oil_gas_experience_years = Column(Float, default=0.0)
    pipeline_experience_years = Column(Float, default=0.0)
    certifications = Column(JSON, default=list)  # NDT Level II, NDT Level III, NEBOSH, CSWIP 3.1
    relevant_projects = Column(JSON, default=list)
    document_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    bidder = relationship("Bidder", back_populates="personnel")

class Document(Base):
    """
    Uploaded Technical, Financial, and Statutory Pipeline Procurement Document
    """
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    bidder_id = Column(String(36), ForeignKey("bidders.id"), nullable=True, index=True)
    tender_id = Column(String(36), ForeignKey("tenders.id"), nullable=True, index=True)
    document_name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=True)
    document_type = Column(String(100), default="PIPELINE_PROJECT_DOCUMENT")
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    mime_type = Column(String(100), default="application/pdf")
    is_scanned = Column(Boolean, default=False)
    extraction_method = Column(String(50), default="PDF_TEXT")  # PDF_TEXT, TESSERACT_OCR, MANUAL_REVIEW
    page_count = Column(Integer, default=1)
    extracted_text = Column(Text, nullable=True)
    uploaded_by = Column(String(36), nullable=True)
    upload_timestamp = Column(DateTime, default=get_utc_now)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
    
    bidder = relationship("Bidder", back_populates="documents")
    tender = relationship("Tender", back_populates="documents")
    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    entities = relationship("ExtractedEntity", back_populates="document", cascade="all, delete-orphan")

class DocumentPage(Base):
    """
    Individual page text and OCR extraction telemetry
    """
    __tablename__ = "document_pages"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False)
    page_text = Column(Text, nullable=True)
    has_tables = Column(Boolean, default=False)
    ocr_applied = Column(Boolean, default=False)
    extraction_method = Column(String(50), default="PDF_TEXT")  # PDF_TEXT, TESSERACT_OCR
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=get_utc_now)
    
    document = relationship("Document", back_populates="pages")

class ExtractedEntity(Base):
    """
    Extracted domain tokens (GSTIN, PAN, Pipeline Km, Turnover, Manpower, HSE)
    """
    __tablename__ = "extracted_entities"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False, index=True)
    entity_value = Column(Text, nullable=False)
    normalized_value = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0)
    page_number = Column(Integer, default=1)
    context_snippet = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    
    document = relationship("Document", back_populates="entities")

class PortalVerification(Base):
    __tablename__ = "portal_verifications"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    bidder_id = Column(String(36), ForeignKey("bidders.id"), nullable=False, index=True)
    portal_name = Column(String(100), nullable=False, index=True)
    identifier_queried = Column(String(100), nullable=False)
    verification_status = Column(String(50), nullable=False)
    response_payload = Column(JSON, default=dict)
    source_label = Column(String(100), default="DEMO / MOCK GOVERNMENT SOURCE")
    verified_at = Column(DateTime, default=get_utc_now)
    created_at = Column(DateTime, default=get_utc_now)
    
    bidder = relationship("Bidder", back_populates="portal_verifications")

class ComplianceCheck(Base):
    """
    Compliance Determination Record for a specific Tender Requirement
    """
    __tablename__ = "compliance_checks"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    bidder_id = Column(String(36), ForeignKey("bidders.id"), nullable=False, index=True)
    requirement_id = Column(String(36), ForeignKey("requirements.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)  # PASS, FAIL, REVIEW, INSUFFICIENT, NOT_APPLICABLE
    confidence = Column(Float, default=1.0)
    score_contribution = Column(Float, default=0.0)
    reason = Column(Text, nullable=False)
    evidence_text = Column(Text, nullable=True)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=True)
    document_name = Column(String(255), nullable=True)
    page_number = Column(Integer, nullable=True)
    verification_source = Column(String(100), default="HYBRID")
    verification_method = Column(String(50), default="RULE_AND_PORTAL")
    rule_version = Column(String(20), default="1.0")
    verified_at = Column(DateTime, default=get_utc_now)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
    
    @property
    def requirement_category(self):
        return self.requirement.category if self.requirement else None

    @property
    def requirement_description(self):
        return self.requirement.description if self.requirement else None

    @property
    def requirement_mandatory(self):
        return self.requirement.mandatory if self.requirement else True
    
    bidder = relationship("Bidder", back_populates="compliance_checks")
    requirement = relationship("Requirement", back_populates="compliance_checks")
    evidence_items = relationship("Evidence", back_populates="compliance_check", cascade="all, delete-orphan")

# Alias for Verification / ComplianceResult
Verification = ComplianceCheck
ComplianceResult = ComplianceCheck

class Evidence(Base):
    """
    Auditable Evidence Item citing exact Document, Page, and Extracted Text
    """
    __tablename__ = "evidences"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    compliance_check_id = Column(String(36), ForeignKey("compliance_checks.id"), nullable=False, index=True)
    document_id = Column(String(36), nullable=True)
    document_name = Column(String(255), nullable=True)
    page_number = Column(Integer, default=1)
    source_text = Column(Text, nullable=False)
    extraction_method = Column(String(50), default="PDF_TEXT")  # PDF_TEXT, TESSERACT_OCR, MANUAL_REVIEW
    extracted_entities = Column(JSON, default=dict)
    confidence = Column(Float, default=1.0)
    calculation_breakdown = Column(JSON, nullable=True)
    verified_source = Column(String(100), default="DEMO / MOCK GOVERNMENT SOURCE")
    created_at = Column(DateTime, default=get_utc_now)
    
    # Compatibility property
    @property
    def snippet(self):
        return self.source_text

    @snippet.setter
    def snippet(self, value):
        self.source_text = value

    compliance_check = relationship("ComplianceCheck", back_populates="evidence_items")

class ComplianceScore(Base):
    __tablename__ = "compliance_scores"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    bidder_id = Column(String(36), ForeignKey("bidders.id"), unique=True, nullable=False)
    overall_score = Column(Float, default=0.0)
    statutory_score = Column(Float, default=0.0)
    financial_score = Column(Float, default=0.0)
    tender_specific_score = Column(Float, default=0.0)
    documentation_score = Column(Float, default=0.0)
    other_score = Column(Float, default=0.0)
    weights_applied = Column(JSON, default=dict)
    calculated_at = Column(DateTime, default=get_utc_now)
    created_at = Column(DateTime, default=get_utc_now)
    
    bidder = relationship("Bidder", back_populates="compliance_score")

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    bidder_id = Column(String(36), ForeignKey("bidders.id"), unique=True, nullable=False)
    risk_level = Column(String(50), nullable=False, index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    primary_risk_factors = Column(JSON, default=list)
    risk_score = Column(Float, default=0.0)
    assessed_at = Column(DateTime, default=get_utc_now)
    created_at = Column(DateTime, default=get_utc_now)
    
    bidder = relationship("Bidder", back_populates="risk_assessment")

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    bidder_id = Column(String(36), ForeignKey("bidders.id"), unique=True, nullable=False)
    recommendation_type = Column(String(50), nullable=False, index=True)
    summary = Column(Text, nullable=False)
    detailed_reasons = Column(JSON, default=list)
    generated_at = Column(DateTime, default=get_utc_now)
    created_at = Column(DateTime, default=get_utc_now)
    
    bidder = relationship("Bidder", back_populates="recommendation")

class OfficerReview(Base):
    __tablename__ = "officer_reviews"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    bidder_id = Column(String(36), ForeignKey("bidders.id"), nullable=False, index=True)
    requirement_id = Column(String(36), ForeignKey("requirements.id"), nullable=True, index=True)
    officer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    officer_name = Column(String(255), nullable=False)
    previous_status = Column(String(50), nullable=False)
    new_status = Column(String(50), nullable=False)
    action_type = Column(String(50), nullable=False)
    remarks = Column(Text, nullable=False)
    reviewed_at = Column(DateTime, default=get_utc_now)
    created_at = Column(DateTime, default=get_utc_now)
    
    bidder = relationship("Bidder", back_populates="officer_reviews")
    officer = relationship("User", back_populates="officer_reviews")

class AuditLog(Base):
    """
    Section 4 GFR 2017 Compliant Immutable Audit Record
    """
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    user_name = Column(String(255), default="SYSTEM")
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(36), nullable=False, index=True)
    tender_id = Column(String(36), nullable=True, index=True)
    bidder_id = Column(String(36), nullable=True, index=True)
    previous_state = Column(JSON, nullable=True)
    new_state = Column(JSON, nullable=True)
    reason = Column(Text, nullable=True)
    source = Column(String(100), default="MoPNG_PIPELINE_PORTAL")
    model_version = Column(String(50), default="SIH26100-v2.0")
    rule_version = Column(String(50), default="2.0")
    ip_address = Column(String(50), default="127.0.0.1")
    timestamp = Column(DateTime, default=get_utc_now, index=True)
    created_at = Column(DateTime, default=get_utc_now)
    
    user = relationship("User", back_populates="audit_logs")
