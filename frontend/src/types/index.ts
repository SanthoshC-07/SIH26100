export type ComplianceStatus = 'PASS' | 'FAIL' | 'REVIEW' | 'INSUFFICIENT' | 'NOT_APPLICABLE';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type TenderStatus = 'DRAFT' | 'ACTIVE' | 'UNDER_REVIEW' | 'CLOSED' | 'EVALUATION' | 'OPEN' | 'AWARDED';

export interface User {
  id: string;
  name: string;
  email: string;
  username: string;
  role: 'ADMIN' | 'PROCUREMENT_OFFICER' | 'BIDDER';
  department?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface SelectingAuthorityPayload {
  decision: 'ELIGIBLE' | 'INELIGIBLE' | 'QUALIFIED' | 'DISQUALIFIED' | 'SHORTLISTED' | 'UNDER_REVIEW' | string;
  remarks: string;
  statutory_rule?: string;
  technical_score?: number;
  financial_cleared?: boolean;
}

export interface SelectingAuthorityResult {
  bidder_id: string;
  bidder_name: string;
  decision: string;
  status: string;
  officer_id: string;
  officer_name: string;
  remarks: string;
  statutory_rule?: string;
  timestamp: string;
}

export interface Requirement {
  id: string;
  tender_id: string;
  category: string;
  clause_number?: string;
  description: string;
  threshold?: number;
  threshold_unit?: string;
  period?: string;
  mandatory: boolean;
  evidence_required: string[];
  verification_method: string;
  rule_version: string;
  created_at: string;
}

export interface Tender {
  id: string;
  tender_number: string;
  title: string;
  organization: string;
  issuing_organization?: string;
  ministry?: string;
  department?: string;
  sector?: string;
  tender_type?: string;
  project_type?: string;
  pipeline_type?: string;
  location?: string;
  category: string;
  description?: string;
  estimated_value: number;
  issue_date?: string;
  tender_issue_date?: string;
  submission_deadline?: string;
  evaluation_date?: string;
  status: TenderStatus | string;
  raw_pdf_path?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
  requirements_count?: number;
  bidders_count?: number;
  compliance_status?: string;
}

export interface TenderDocument {
  id: string;
  bidder_id?: string;
  tender_id?: string;
  document_name: string;
  original_filename?: string;
  document_type: string;
  file_size: number;
  mime_type: string;
  is_scanned: boolean;
  page_count: number;
  extraction_method?: string;
  extracted_text?: string;
  text_quality?: string;
  ocr_status?: string;
  processing_status?: string;
  uploaded_by?: string;
  upload_timestamp?: string;
  entities_count?: number;
}

export type Document = TenderDocument;

export interface ExtractedEntity {
  id: string;
  entity_type: string;
  entity_value: string;
  normalized_value?: string;
  confidence: number;
  page_number: number;
  context_snippet?: string;
  created_at: string;
}

export interface EvidenceItem {
  id: string;
  document_id?: string;
  document_name?: string;
  page_number: number;
  snippet: string;
  confidence: number;
  extraction_method?: string;
  calculation_breakdown?: Record<string, any>;
  verified_source: string;
  created_at: string;
}

export interface ComplianceCheck {
  id: string;
  bidder_id: string;
  requirement_id: string;
  clause_number?: string;
  category?: string;
  requirement_category?: string;
  requirement_description?: string;
  requirement_mandatory?: boolean;
  status: ComplianceStatus;
  confidence: number;
  score_contribution?: number;
  reason: string;
  evidence_text?: string;
  document_id?: string;
  document_name?: string;
  page_number?: number;
  verification_source?: string;
  verification_method?: string;
  rule_version?: string;
  verified_at?: string;
  created_at?: string;
  evidence_items?: EvidenceItem[];
}

export interface ComplianceScore {
  id: string;
  bidder_id: string;
  overall_score: number;
  statutory_score: number;
  financial_score: number;
  tender_specific_score: number;
  documentation_score: number;
  other_score: number;
  weights_applied: Record<string, number>;
  calculated_at: string;
}

export interface RiskAssessment {
  id: string;
  bidder_id: string;
  risk_level: RiskLevel;
  primary_risk_factors: string[];
  risk_score: number;
  assessed_at: string;
}

export interface Recommendation {
  id: string;
  bidder_id: string;
  recommendation_type: string;
  summary: string;
  detailed_reasons: string[];
  generated_at: string;
}

export interface OfficerReview {
  id: string;
  bidder_id: string;
  requirement_id?: string;
  officer_id: string;
  officer_name: string;
  previous_status: string;
  new_status: string;
  action_type: string;
  remarks: string;
  reviewed_at: string;
}

export interface BidderProject {
  id: string;
  bidder_id: string;
  project_name: string;
  client_name: string;
  client_type?: string;
  sector?: string;
  project_type?: string;
  pipeline_type?: string;
  pipeline_length_km?: number;
  pipeline_diameter?: string;
  project_value?: number;
  currency?: string;
  location?: string;
  start_date?: string;
  completion_date?: string;
  scope_of_work?: string;
  bidder_role?: string;
  contract_reference?: string;
  evidence_document_id?: string;
}

export interface BidderPersonnel {
  id: string;
  bidder_id: string;
  name: string;
  designation: string;
  qualification: string;
  specialization?: string;
  years_of_experience: number;
  oil_gas_experience_years?: number;
  pipeline_experience_years?: number;
  certifications: string[];
  relevant_projects: string[];
  document_id?: string;
}

export interface Bidder {
  id: string;
  tender_id: string;
  legal_name?: string;
  trade_name?: string;
  bidder_name: string;
  gstin?: string;
  pan?: string;
  registered_address?: string;
  contact_information?: Record<string, any>;
  bidder_type?: string;
  country?: string;
  oil_gas_experience_years?: number;
  pipeline_experience_years?: number;
  udyam_number?: string;
  cin?: string;
  email?: string;
  phone?: string;
  contact_person?: string;
  status: string;
  submitted_at: string;
  created_at: string;
  compliance_score?: number;
  risk_level?: RiskLevel;
  recommendation_type?: string;
  documents_count?: number;
}

export interface BidderDetail extends Bidder {
  documents: TenderDocument[];
  projects?: BidderProject[];
  personnel?: BidderPersonnel[];
  compliance_checks: ComplianceCheck[];
  compliance_score_detail?: ComplianceScore;
  risk_assessment_detail?: RiskAssessment;
  recommendation_detail?: Recommendation;
  officer_reviews: OfficerReview[];
}

export interface AuditLog {
  id: string;
  user_id?: string;
  user_name: string;
  action: string;
  entity_type: string;
  entity_id: string;
  tender_id?: string;
  bidder_id?: string;
  previous_state?: Record<string, any>;
  new_state?: Record<string, any>;
  reason?: string;
  source: string;
  model_version: string;
  rule_version: string;
  ip_address: string;
  timestamp: string;
}

export interface DashboardStats {
  total_tenders: number;
  active_tenders: number;
  total_bidders: number;
  verified_bidders: number;
  pending_reviews: number;
  high_risk_bidders: number;
  average_compliance_score: number;
  risk_distribution: Record<string, number>;
  compliance_distribution: Record<string, number>;
  top_failed_requirements: { category: string; count: number }[];
  recent_audit_logs: AuditLog[];
}

export interface TenderClause {
  id: string;
  tender_id: string;
  clause_number?: string;
  clause_type: string;
  original_text: string;
  normalized_text?: string;
  page_number: number;
  category?: string;
  confidence: number;
  is_requirement: boolean;
  extracted_entities: Record<string, any>;
  created_at: string;
}

export interface PreBidQuery {
  query_id: string;
  bidder: string;
  clause_reference: string;
  bidder_query: string;
  official_clarification: string;
  status: string;
  date: string;
}

export interface PreBidInfo {
  tender_id: string;
  tender_number: string;
  pre_bid_meeting_date: string;
  meeting_venue: string;
  status: string;
  queries_received_count: number;
  clarifications_issued_count: number;
  minutes_of_meeting_published: boolean;
  queries: PreBidQuery[];
}

export interface Corrigendum {
  corrigendum_number: string;
  issue_date: string;
  subject: string;
  description: string;
  revised_submission_deadline: string;
  document_filename: string;
  status: string;
}

export interface TenderComplianceSummary {
  tender_id: string;
  tender_number: string;
  total_bidders: number;
  verified_bidders: number;
  pending_reviews: number;
  disqualified_bidders: number;
  average_score: number;
  requirements_evaluated: number;
  requirement_breakdown: {
    requirement_id: string;
    clause_number?: string;
    category: string;
    description: string;
    mandatory: boolean;
    total_evaluated: number;
    pass_count: number;
    review_count: number;
    fail_count: number;
  }[];
}

export interface DebarmentRecord {
  bidder_id: string;
  vendor: string;
  pan?: string;
  reason: string;
  source: string;
  effective_date: string;
  end_date: string;
  status: 'ACTIVE' | 'EXPIRED' | 'NOT_FOUND' | 'REVIEW';
  supporting_document: string;
  verification_status: string;
  is_mock_adapter: boolean;
  mock_disclaimer: string;
}

export interface DocumentPipelineStep {
  step: number;
  name: string;
  status: 'COMPLETED' | 'FALLBACK' | 'SCANNED_DETECTED' | 'TEXT_VERIFIED' | 'SKIPPED' | 'PARTIAL' | 'PENDING';
  detail: string;
  engine?: string;
}

export interface EvidenceSearchResult {
  document_id: string;
  document_name: string;
  page_number: number;
  text: string;
  normalized_text?: string;
  similarity_score: number;
  confidence: number;
  extraction_method?: string;
  extracted_entities?: Record<string, any>;
}

// ----------------- PHASE 5 TYPES -----------------
export interface RiskFactor {
  id: string;
  risk_assessment_id?: string;
  bid_id: string;
  requirement_id?: string;
  compliance_check_id?: string;
  factor_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  description: string;
  evidence_snippet?: string;
  source_document?: string;
  page_number?: number;
  created_at?: string;
}

export interface RiskAssessmentDetail {
  bidder_id: string;
  bidder_name?: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  risk_score: number;
  primary_risk_factors: string[];
  factors: RiskFactor[];
  assessed_at?: string;
}

export interface OfficerRequirementRow {
  requirement_id: string;
  clause_number: string;
  category: string;
  title: string;
  requirement_text: string;
  required_evidence: string[];
  submitted_evidence: string;
  source_document: string;
  page: number;
  extracted_value: any;
  rule_result: any;
  semantic_score: number;
  confidence: number;
  ai_status: string;
  risk: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  officer_decision?: {
    decision: string;
    reason: string;
    officer_name: string;
    is_override: boolean;
    timestamp?: string;
  } | null;
}

export interface OfficerReviewWorkspace {
  tender: {
    id: string;
    tender_number: string;
    title: string;
    organization: string;
    category: string;
    estimated_value: number;
  };
  bidder: {
    id: string;
    legal_name: string;
    trade_name?: string;
    pan?: string;
    gstin?: string;
    country?: string;
  };
  submission_date: string;
  compliance_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  recommendation: string;
  governance_notice: string;
  requirements: OfficerRequirementRow[];
  final_decision?: {
    decision: string;
    remarks: string;
    officer_name: string;
    timestamp: string;
  } | null;
}

export interface AuditEvent {
  event_id: string;
  timestamp: string;
  user_id?: string;
  user_name: string;
  role: string;
  action: string;
  entity_type: string;
  entity_id: string;
  tender_id?: string;
  bidder_id?: string;
  description: string;
  metadata_payload?: Record<string, any>;
}

export interface ComplianceReport {
  id: string;
  bid_id: string;
  tender_id?: string;
  report_number: string;
  title: string;
  generated_by_name: string;
  assessment_date: string;
  compliance_score: number;
  risk_level: string;
  risk_score: number;
  ai_recommendation: string;
  final_officer_decision?: string;
  executive_summary: Record<string, any>;
  requirement_summary: Array<{
    clause_number: string;
    requirement: string;
    category: string;
    status: string;
    confidence: number;
    risk: string;
  }>;
  detailed_findings: Array<{
    requirement_id: string;
    clause_number: string;
    category: string;
    requirement_text: string;
    required_threshold: string;
    extracted_value: string;
    evidence: string;
    source_document: string;
    page: number;
    rule_result: string;
    semantic_score: number;
    confidence: number;
    explanation: string;
    external_verification: string;
  }>;
  officer_decisions: Array<{
    id: string;
    requirement_id?: string;
    decision_type: string;
    ai_status: string;
    officer_status: string;
    is_override: boolean;
    officer_reason: string;
    officer_name: string;
    timestamp: string;
  }>;
  risk_analysis: {
    risk_level: string;
    risk_score: number;
    risk_factors: RiskFactor[];
  };
  audit_information: Record<string, any>;
  pdf_path?: string;
  html_content?: string;
  created_at: string;
}


