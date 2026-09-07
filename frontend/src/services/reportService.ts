import api from './api';
import { ComplianceReport } from '../types';

export const reportService = {
  generateReport: async (bidId: string): Promise<ComplianceReport> => {
    const res = await api.post(`/reports/${bidId}/generate`);
    return res.data;
  },

  getReport: async (bidId: string): Promise<ComplianceReport> => {
    const res = await api.get(`/reports/${bidId}`);
    return res.data;
  },

  getDownloadUrl: (bidId: string): string => {
    return `/api/reports/${bidId}/download`;
  }
};
