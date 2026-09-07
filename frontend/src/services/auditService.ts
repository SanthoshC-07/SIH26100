import api from './api';
import { AuditLog, AuditEvent } from '../types';

export interface AuditFilterParams {
  tender_id?: string;
  bidder_id?: string;
  user_id?: string;
  action?: string;
  role?: string;
  search?: string;
  start_date?: string;
  end_date?: string;
  limit?: number;
  offset?: number;
}

export const auditService = {
  getAuditEvents: async (params?: AuditFilterParams): Promise<AuditEvent[]> => {
    const res = await api.get('/audit', { params });
    return res.data;
  },

  getBidAuditEvents: async (bidId: string): Promise<AuditEvent[]> => {
    const res = await api.get(`/audit/${bidId}`);
    return res.data;
  },

  getAuditLogs: async (params?: { action?: string; limit?: number }): Promise<AuditLog[]> => {
    const res = await api.get('/audit/logs', { params });
    return res.data;
  },

  exportCsvUrl: (params?: AuditFilterParams): string => {
    const query = new URLSearchParams();
    if (params?.tender_id) query.set('tender_id', params.tender_id);
    if (params?.bidder_id) query.set('bidder_id', params.bidder_id);
    if (params?.action) query.set('action', params.action);
    if (params?.role) query.set('role', params.role);
    return `/api/audit/export/csv?${query.toString()}`;
  }
};
