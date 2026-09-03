import api from './api';
import { AuditLog } from '../types';

export const auditService = {
  getAuditLogs: async (params?: { action?: string; limit?: number }): Promise<AuditLog[]> => {
    const res = await api.get('/audit/logs', { params });
    return res.data;
  },
};
