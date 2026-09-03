export type ComplianceStatus = 'PASS' | 'FAIL' | 'REVIEW' | 'NOT_APPLICABLE';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type TenderStatus = 'DRAFT' | 'ACTIVE' | 'UNDER_REVIEW' | 'CLOSED' | 'EVALUATION';

export interface User {
  id: string;
  name: string;
  email: string;
  username: string;
  role: 'ADMIN' | 'PROCUREMENT_OFFICER';
  department?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
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
  category: string;
  description?: string;
  estimated_value: number;
  issue_date?: string;
  submission_deadline?: string;
  status: TenderStatus;
  raw_pdf_path?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
  requirements_count?: number;
  bidders_count?: number;
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
  uploaded_by?: string;
  upload_timestamp: string;
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
  calculation_breakdown?: Record<string, any>;
  verified_source: string;
  created_at: string;
}

export interface ComplianceCheck {
  id: string;
  bidder_id: string;
  requirement_id: string;
  requirement_category?: string;
  requirement_description?: string;
  requirement_mandatory?: boolean;
  status: ComplianceStatus;
  confidence: number;
  score_contribution: number;
  reason: string;
  evidence_text?: string;
  document_id?: string;
  document_name?: string;
  page_number?: number;
  verification_source: string;
  verification_method: string;
  rule_version: string;
  verified_at: string;
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
  risk_distribution: Record<RiskLevel, number>;
  compliance_distribution: Record<ComplianceStatus, number>;
  top_failed_requirements: { category: string; count: number }[];
  recent_audit_logs: AuditLog[];
}
