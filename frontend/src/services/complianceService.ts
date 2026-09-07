import api from './api';
import { ComplianceCheck, OfficerReview } from '../types';

export interface ComplianceEvaluationDossier {
  bidder_id: string;
  bidder_name: string;
  tender_id: string;
  tender_number: string;
  overall_status: string;
  status_summary: string;
  mandatory_compliance: boolean;
  compliance_score: number;
  score_breakdown: Record<string, any>;
  risk_assessment: Record<string, any>;
  recommendation: Record<string, any>;
  cross_document_consistency: Record<string, any>;
  summary_counts: {
    total: number;
    pass: number;
    fail: number;
    review: number;
    insufficient: number;
  };
  requirements: Array<{
    requirement_id: string;
    clause_number?: string;
    category: string;
    description: string;
    mandatory: boolean;
    status: string;
    confidence: number;
    confidence_gate?: string;
    evidence: string;
    source_document: string;
    document_name?: string;
    page_number: number;
    source_text: string;
    extracted_entities: Record<string, any>;
    rule_result: any;
    semantic_score: number;
    explanation: string;
    verification_details?: Record<string, any>;
  }>;
}

export const complianceService = {
  runComplianceEvaluation: async (bidId: string): Promise<ComplianceEvaluationDossier> => {
    const res = await api.post(`/compliance/run/${bidId}`);
    return res.data;
  },

  getComplianceDossier: async (bidId: string): Promise<ComplianceEvaluationDossier> => {
    const res = await api.get(`/compliance/${bidId}`);
    return res.data;
  },

  getBidComplianceRequirements: async (bidId: string): Promise<any[]> => {
    const res = await api.get(`/compliance/${bidId}/requirements`);
    return res.data;
  },

  getSingleRequirementCompliance: async (bidId: string, requirementId: string): Promise<any> => {
    const res = await api.get(`/compliance/${bidId}/requirements/${requirementId}`);
    return res.data;
  },

  verifyRequirement: async (bidId: string, requirementId: string): Promise<any> => {
    const res = await api.post(`/compliance/${bidId}/requirements/${requirementId}/verify`);
    return res.data;
  },

  reverifyRequirement: async (bidId: string, requirementId: string): Promise<any> => {
    const res = await api.post(`/compliance/${bidId}/requirements/${requirementId}/reverify`);
    return res.data;
  },

  getComplianceSummary: async (bidId: string): Promise<any> => {
    const res = await api.get(`/compliance/${bidId}/summary`);
    return res.data;
  },

  getPendingReviews: async (): Promise<ComplianceCheck[]> => {
    const res = await api.get('/compliance/reviews/pending');
    return res.data;
  },

  submitOfficerReview: async (
    checkIdOrData?: string | any,
    reviewData?: {
      bidder_id?: string;
      action_type: string;
      new_status: string;
      remarks: string;
      requirement_id?: string;
      clause_number?: string;
    }
  ): Promise<OfficerReview> => {
    if (typeof checkIdOrData === 'object' && checkIdOrData !== null) {
      const data = checkIdOrData;
      const checkId = data.check_id;
      const payload = {
        bidder_id: data.bidder_id,
        action_type: data.action_type || 'APPROVE',
        new_status: data.status || data.new_status || 'PASSED',
        remarks: data.officer_notes || data.remarks || '',
        requirement_id: data.requirement_id,
        clause_number: data.clause_number,
      };
      const url = checkId && checkId !== 'mock-check-id' && checkId !== 'undefined'
        ? `/compliance/${checkId}/review`
        : '/compliance/review';
      const res = await api.post(url, payload);
      return res.data;
    }

    const checkId = checkIdOrData;
    const url = checkId && checkId !== 'mock-check-id' && checkId !== 'undefined'
      ? `/compliance/${checkId}/review`
      : '/compliance/review';
    const res = await api.post(url, reviewData);
    return res.data;
  },
};
