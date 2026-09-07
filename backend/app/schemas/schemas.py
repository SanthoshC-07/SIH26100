from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# ----------------- AUTH SCHEMAS -----------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"

class LoginRequest(BaseModel):
    username_or_email: Optional[str] = None
    username: Optional[str] = None
    password: str

    @property
    def identifier(self) -> str:
        return self.username_or_email or self.username or ""

class UserCreate(BaseModel):
    name: str
    email: str
    username: str
    password: str
    role: str = "PROCUREMENT_OFFICER"
    department: Optional[str] = "Ministry of Petroleum & Natural Gas - Tender Cell"

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    username: str
    role: str
    department: Optional[str] = None
    is_active: bool
    bidder_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None
    bidder_id: Optional[str] = None

# ----------------- REQUIREMENT SCHEMAS -----------------
class RequirementBase(BaseModel):
    category: str
    clause_number: Optional[str] = None
    description: Optional[str] = ""
    threshold: Optional[float] = None
    threshold_unit: Optional[str] = None
    comparison_operator: Optional[str] = ">="
    required_years: Optional[float] = None
    required_project_count: Optional[int] = 1
    required_pipeline_length_km: Optional[float] = None
    required_project_value: Optional[float] = None
    required_pipeline_type: Optional[str] = None
    required_sector: Optional[str] = "OIL_AND_GAS"
    required_qualification: Optional[str] = None
    required_manpower_count: Optional[int] = 5
    required_evidence_type: Optional[str] = None
    period: Optional[str] = None
    mandatory: bool = True
    evidence_required: List[str] = []
    verification_method: str = "RULE_AND_PORTAL"
    rule_version: str = "2.0"

class RequirementCreate(RequirementBase):
    pass

class RequirementResponse(RequirementBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tender_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

# ----------------- TENDER SCHEMAS -----------------
class TenderBase(BaseModel):
    tender_number: str
    title: str
    issuing_organization: Optional[str] = "GAIL (India) Limited"
    organization: Optional[str] = "GAIL (India) Limited"
    ministry: Optional[str] = "Ministry of Petroleum & Natural Gas"
    sector: Optional[str] = "OIL_AND_GAS"
    tender_type: Optional[str] = "PIPELINE_PROCUREMENT"
    project_type: Optional[str] = "PIPELINE_CONSTRUCTION"
    pipeline_type: Optional[str] = "CROSS_COUNTRY_PIPELINE"
    location: Optional[str] = "National Gas Grid, India"
    category: Optional[str] = "Petroleum & Pipeline Infrastructure"
    description: Optional[str] = None
    estimated_value: float = 0.0
    tender_issue_date: Optional[datetime] = None
    issue_date: Optional[datetime] = None
    submission_deadline: Optional[datetime] = None
    evaluation_date: Optional[datetime] = None
    status: str = "ACTIVE"


class TenderCreate(TenderBase):
    requirements: Optional[List[RequirementCreate]] = []

class TenderUpdate(BaseModel):
    title: Optional[str] = None
    issuing_organization: Optional[str] = None
    organization: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    estimated_value: Optional[float] = None
    submission_deadline: Optional[datetime] = None
    status: Optional[str] = None

class TenderResponse(TenderBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    raw_pdf_path: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    requirements_count: Optional[int] = 0
    bidders_count: Optional[int] = 0

# ----------------- BIDDER PROJECT EXPERIENCE SCHEMAS -----------------
class BidderProjectBase(BaseModel):
    project_name: str
    client_name: str
    client_type: Optional[str] = "PUBLIC_SECTOR_UNDERTAKING"
    sector: Optional[str] = "OIL_AND_GAS"
    project_type: Optional[str] = "PIPELINE_CONSTRUCTION"
    pipeline_type: Optional[str] = "NATURAL_GAS"
    pipeline_length_km: Optional[float] = None
    pipeline_diameter: Optional[str] = None
    project_value: Optional[float] = 0.0
    currency: Optional[str] = "INR"
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    scope_of_work: Optional[str] = None
    bidder_role: Optional[str] = "EPC_CONTRACTOR"
    contract_reference: Optional[str] = None
    evidence_document_id: Optional[str] = None

class BidderProjectCreate(BidderProjectBase):
    pass

class BidderProjectResponse(BidderProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    bidder_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

# ----------------- TECHNICAL MANPOWER SCHEMAS -----------------
class BidderPersonnelBase(BaseModel):
    name: str
    designation: str
    qualification: str
    specialization: Optional[str] = None
    years_of_experience: float = 0.0
    oil_gas_experience_years: float = 0.0
    pipeline_experience_years: float = 0.0
    certifications: List[str] = []
    relevant_projects: List[str] = []
    document_id: Optional[str] = None

class BidderPersonnelCreate(BidderPersonnelBase):
    pass

class BidderPersonnelResponse(BidderPersonnelBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    bidder_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

# ----------------- DOCUMENT SCHEMAS -----------------
class ExtractedEntityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    entity_type: str
    entity_value: str
    normalized_value: Optional[str] = None
    confidence: float
    page_number: int
    context_snippet: Optional[str] = None
    created_at: datetime

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    bidder_id: Optional[str] = None
    tender_id: Optional[str] = None
    document_name: str
    original_filename: Optional[str] = None
    document_type: str
    file_size: int
    mime_type: str
    is_scanned: bool
    page_count: int
    upload_timestamp: datetime
    entities_count: Optional[int] = 0
    extraction_method: Optional[str] = "PYMUPDF"

class DocumentDetailResponse(DocumentResponse):
    extracted_text: Optional[str] = None
    entities: List[ExtractedEntityResponse] = []

# ----------------- COMPLIANCE & EVIDENCE SCHEMAS -----------------
class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    compliance_check_id: str
    document_id: Optional[str] = None
    document_name: Optional[str] = None
    page_number: int
    source_text: str
    extraction_method: Optional[str] = "PDF_TEXT"
    extracted_entities: Optional[Dict[str, Any]] = None
    confidence: float
    calculation_breakdown: Optional[Dict[str, Any]] = None
    verified_source: str
    created_at: datetime

class ComplianceCheckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    bidder_id: str
    requirement_id: str
    clause_number: Optional[str] = None
    requirement_category: Optional[str] = None
    requirement_description: Optional[str] = None
    requirement_mandatory: Optional[bool] = True
    status: str
    confidence: float
    score_contribution: float
    reason: str
    evidence_text: Optional[str] = None
    document_id: Optional[str] = None
    document_name: Optional[str] = None
    page_number: Optional[int] = None
    verification_source: str
    verification_method: str
    rule_version: str
    verified_at: datetime
    evidence_items: List[EvidenceResponse] = []

class ComplianceScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    bidder_id: str
    overall_score: float
    statutory_score: float
    financial_score: float
    tender_specific_score: float
    documentation_score: float
    other_score: float
    weights_applied: Dict[str, float]
    calculated_at: datetime

class RiskAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    bidder_id: str
    risk_level: str
    primary_risk_factors: List[str]
    risk_score: float
    assessed_at: datetime

class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    bidder_id: str
    recommendation_type: str
    summary: str
    detailed_reasons: List[str]
    generated_at: datetime

class OfficerReviewCreate(BaseModel):
    bidder_id: Optional[str] = None
    requirement_id: Optional[str] = None
    action_type: Optional[str] = "OFFICER_OVERRIDE"
    new_status: str
    remarks: str

class OfficerReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    bidder_id: str
    requirement_id: Optional[str] = None
    officer_id: str
    officer_name: str
    previous_status: str
    new_status: str
    action_type: str
    remarks: str
    reviewed_at: datetime

# ----------------- PROCUREMENT OFFICER SELECTING AUTHORITY SCHEMAS -----------------
class SelectingAuthorityRequest(BaseModel):
    decision: str  # ELIGIBLE, INELIGIBLE, QUALIFIED, DISQUALIFIED, SHORTLISTED
    remarks: str
    statutory_rule: Optional[str] = "GFR 2017 Rule 173 / MoPNG Clause 4.2"
    technical_score: Optional[float] = None
    financial_cleared: Optional[bool] = True

class SelectingAuthorityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bidder_id: str
    bidder_name: str
    decision: str
    status: str
    officer_id: str
    officer_name: str
    remarks: str
    statutory_rule: Optional[str] = None
    timestamp: datetime

# ----------------- BID SCHEMAS -----------------
class BidBase(BaseModel):
    bid_reference_number: str
    submission_date: Optional[datetime] = None
    technical_bid_status: str = "UNDER_EVALUATION"
    financial_bid_amount: Optional[float] = None
    currency: str = "INR"
    remarks: Optional[str] = None

class BidCreate(BidBase):
    tender_id: str
    bidder_id: str

class BidResponse(BidBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tender_id: str
    bidder_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

# ----------------- BIDDER SCHEMAS -----------------
import re
from pydantic import field_validator, model_validator

class BidderBase(BaseModel):
    tender_id: str
    legal_name: Optional[str] = None
    bidder_name: Optional[str] = None
    trade_name: Optional[str] = None
    pan: Optional[str] = None
    gstin: Optional[str] = None
    registered_address: Optional[str] = None
    contact_information: Optional[Dict[str, Any]] = None
    bidder_type: Optional[str] = "INDIAN_EPC_CONTRACTOR"
    country: Optional[str] = "INDIA"
    oil_gas_experience_years: Optional[float] = 0.0
    pipeline_experience_years: Optional[float] = 0.0
    udyam_number: Optional[str] = None
    cin: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    contact_person: Optional[str] = None
    status: str = "SUBMITTED"

class BidderCreate(BidderBase):
    @field_validator("pan", mode="before")
    @classmethod
    def validate_pan_format(cls, v):
        if not v:
            return None
        v_clean = str(v).strip().upper()
        if not v_clean:
            return None
        if not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", v_clean):
            raise ValueError("PAN format is invalid (expected 5 uppercase letters, 4 digits, 1 uppercase letter, e.g. BSZPP1234K)")
        return v_clean

    @field_validator("gstin", mode="before")
    @classmethod
    def validate_gstin_format(cls, v):
        if not v:
            return None
        v_clean = str(v).strip().upper()
        if not v_clean:
            return None
        if not re.match(r"^[0-9]{2}[A-Z0-9]{10}[A-Z0-9]{1}[Z]{1}[A-Z0-9]{1}$", v_clean):
            raise ValueError("GSTIN format is invalid (expected 15 alphanumeric characters matching state and entity format, e.g. 29MOCKP1234M1Z5)")
        return v_clean

    @model_validator(mode="after")
    def validate_name_presence(self):
        name = self.legal_name or self.bidder_name
        if not name or not name.strip():
            raise ValueError("Company / Legal name is required to register a bidder.")
        self.legal_name = name.strip()
        self.bidder_name = name.strip()
        return self



class BidderResponse(BidderBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    submitted_at: datetime
    created_at: datetime
    bidder_name: Optional[str] = None
    compliance_score: Optional[float] = None
    risk_level: Optional[str] = None
    recommendation_type: Optional[str] = None
    documents_count: Optional[int] = 0

class BidderUpdate(BaseModel):
    legal_name: Optional[str] = None
    trade_name: Optional[str] = None
    registered_address: Optional[str] = None
    contact_information: Optional[Dict[str, Any]] = None
    bidder_type: Optional[str] = None
    country: Optional[str] = None
    oil_gas_experience_years: Optional[float] = None
    pipeline_experience_years: Optional[float] = None
    udyam_number: Optional[str] = None
    cin: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    contact_person: Optional[str] = None

class BidderDetailResponse(BidderResponse):
    model_config = ConfigDict(from_attributes=True)

    documents: List[DocumentResponse] = []
    projects: List[BidderProjectResponse] = []
    personnel: List[BidderPersonnelResponse] = []
    compliance_checks: List[ComplianceCheckResponse] = []
    compliance_score_detail: Optional[ComplianceScoreResponse] = None
    risk_assessment_detail: Optional[RiskAssessmentResponse] = None
    recommendation_detail: Optional[RecommendationResponse] = None
    officer_reviews: List[OfficerReviewResponse] = []

# ----------------- AUDIT LOG SCHEMAS -----------------
class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: Optional[str] = None
    user_name: str
    action: str
    entity_type: str
    entity_id: str
    tender_id: Optional[str] = None
    bidder_id: Optional[str] = None
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
    source: str
    model_version: str
    rule_version: str
    ip_address: str
    timestamp: datetime

class TopFailedRequirement(BaseModel):
    category: str
    count: int

class DashboardStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_tenders: int
    active_tenders: int
    total_bidders: int
    verified_bidders: int
    pending_reviews: int
    high_risk_bidders: int
    average_compliance_score: float
    risk_distribution: Dict[str, int]
    compliance_distribution: Dict[str, int]
    top_failed_requirements: List[TopFailedRequirement]
    recent_audit_logs: List[AuditLogResponse]

class SettingsUpdate(BaseModel):
    scoring_weights: Dict[str, float]
    confidence_high: float = 0.90
    confidence_medium: float = 0.70

# ----------------- PHASE 2 NLP & EVIDENCE SCHEMAS -----------------
class TenderClauseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tender_id: str
    clause_number: Optional[str] = None
    clause_type: str = "REQUIREMENT"
    original_text: str
    normalized_text: Optional[str] = None
    page_number: int = 1
    category: Optional[str] = None
    confidence: float = 1.0
    is_requirement: bool = True
    extracted_entities: Dict[str, Any] = {}
    created_at: datetime

class EvidenceChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    bidder_id: Optional[str] = None
    requirement_id: Optional[str] = None
    page_number: int = 1
    chunk_index: int = 0
    text: str
    normalized_text: Optional[str] = None
    category: Optional[str] = None
    confidence: float = 1.0
    similarity_score: float = 0.0
    created_at: datetime

class EvidenceSearchRequest(BaseModel):
    requirement_id: Optional[str] = None
    bidder_id: Optional[str] = None
    query: str
    top_k: int = 5
    category: Optional[str] = None

class EvidenceSearchResult(BaseModel):
    document_id: str
    document_name: str
    page_number: int
    text: str
    normalized_text: Optional[str] = None
    similarity_score: float
    confidence: float
    extraction_method: str = "PDF_TEXT"
    extracted_entities: Dict[str, Any] = {}

class StructuredRequirementConstraints(BaseModel):
    category: str
    mandatory: bool = True
    threshold: Optional[float] = None
    unit: Optional[str] = None
    comparison: Optional[str] = ">="
    lookback_years: Optional[float] = None
    minimum_project_count: Optional[int] = 1
    pipeline_type: Optional[str] = None
    minimum_pipeline_length_km: Optional[float] = None
    minimum_diameter_inch: Optional[float] = None
    qualification: Optional[str] = None
    minimum_personnel: Optional[int] = None
    financial_year_count: Optional[int] = None
    required_certifications: List[str] = []
    completion_required: bool = True
    confidence: float = 0.95

# ----------------- PHASE 5 SCHEMAS -----------------
class RiskFactorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    risk_assessment_id: Optional[str] = None
    bid_id: str
    requirement_id: Optional[str] = None
    compliance_check_id: Optional[str] = None
    factor_type: str
    severity: str
    description: str
    evidence_snippet: Optional[str] = None
    source_document: Optional[str] = None
    page_number: Optional[int] = None
    created_at: datetime

class RiskAssessmentDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bidder_id: str
    risk_level: str
    risk_score: float
    primary_risk_factors: List[str] = []
    factors: List[RiskFactorResponse] = []
    assessed_at: Optional[datetime] = None

class RequirementDecisionRequest(BaseModel):
    decision: str  # ACCEPT_AI_RESULT, PASS, FAIL, REVIEW, INSUFFICIENT
    reason: Optional[str] = ""  # Mandatory when overriding
    officer_name: Optional[str] = None

class RequirementDecisionResponse(BaseModel):
    id: str
    bid_id: str
    requirement_id: Optional[str] = None
    compliance_check_id: Optional[str] = None
    decision_type: str
    ai_status: str
    ai_confidence: float
    officer_status: str
    officer_reason: str
    is_override: bool
    officer_id: Optional[str] = None
    officer_name: str
    decision_timestamp: datetime

class FinalBidDecisionRequest(BaseModel):
    decision: str  # QUALIFIED, DISQUALIFIED, REVIEW / HOLD
    remarks: str
    confirmed: bool = True
    officer_name: Optional[str] = None

class FinalBidDecisionResponse(BaseModel):
    id: str
    bid_id: str
    tender_id: Optional[str] = None
    decision: str
    remarks: str
    officer_id: Optional[str] = None
    officer_name: str
    timestamp: datetime
    summary: Dict[str, Any] = {}

class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    timestamp: datetime
    user_id: Optional[str] = None
    user_name: str
    role: str
    action: str
    entity_type: str
    entity_id: str
    tender_id: Optional[str] = None
    bidder_id: Optional[str] = None
    description: str
    metadata_payload: Optional[Dict[str, Any]] = None

class ComplianceReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    bid_id: str
    tender_id: Optional[str] = None
    report_number: str
    title: str
    generated_by_name: str
    assessment_date: datetime
    compliance_score: float
    risk_level: str
    risk_score: float
    ai_recommendation: str
    final_officer_decision: Optional[str] = None
    executive_summary: Dict[str, Any] = {}
    requirement_summary: List[Dict[str, Any]] = []
    detailed_findings: List[Dict[str, Any]] = []
    officer_decisions: List[Dict[str, Any]] = []
    risk_analysis: Dict[str, Any] = {}
    audit_information: Dict[str, Any] = {}
    pdf_path: Optional[str] = None
    html_content: Optional[str] = None
    created_at: datetime

