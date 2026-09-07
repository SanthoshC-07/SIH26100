import api from './api';
import { RiskAssessmentDetail } from '../types';

export const riskService = {
  getRiskAssessment: async (bidId: string): Promise<RiskAssessmentDetail> => {
    const res = await api.get(`/risk/${bidId}`);
    return res.data;
  },

  calculateRisk: async (bidId: string): Promise<RiskAssessmentDetail> => {
    const res = await api.post(`/risk/${bidId}/calculate`);
    return res.data;
  }
};
