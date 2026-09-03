import api from './api';
import { ComplianceCheck, OfficerReview } from '../types';

export const complianceService = {
  getPendingReviews: async (): Promise<ComplianceCheck[]> => {
    const res = await api.get('/compliance/pending-reviews');
    return res.data;
  },

  submitOfficerReview: async (checkId: string, reviewData: {
    action_type: string;
    new_status: string;
    remarks: string;
    requirement_id?: string;
  }): Promise<OfficerReview> => {
    const res = await api.post(`/compliance/checks/${checkId}/review`, reviewData);
    return res.data;
  },
};
