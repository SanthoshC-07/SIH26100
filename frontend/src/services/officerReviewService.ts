import api from './api';
import { OfficerReviewWorkspace } from '../types';

export interface RequirementDecisionPayload {
  decision: 'ACCEPT_AI_RESULT' | 'PASS' | 'FAIL' | 'REVIEW' | 'INSUFFICIENT' | string;
  reason?: string;
  officer_name?: string;
}

export interface FinalBidDecisionPayload {
  decision: 'QUALIFIED' | 'DISQUALIFIED' | 'REVIEW / HOLD' | string;
  remarks: string;
  confirmed: boolean;
  officer_name?: string;
}

export const officerReviewService = {
  getWorkspace: async (bidId: string): Promise<OfficerReviewWorkspace> => {
    const res = await api.get(`/officer-review/${bidId}`);
    return res.data;
  },

  submitRequirementDecision: async (
    bidId: string,
    requirementId: string,
    payload: RequirementDecisionPayload
  ): Promise<any> => {
    const res = await api.post(`/officer-review/${bidId}/requirements/${requirementId}/decision`, payload);
    return res.data;
  },

  submitFinalDecision: async (
    bidId: string,
    payload: FinalBidDecisionPayload
  ): Promise<any> => {
    const res = await api.post(`/officer-review/${bidId}/final-decision`, payload);
    return res.data;
  }
};
