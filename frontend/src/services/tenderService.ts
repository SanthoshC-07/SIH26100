import api from './api';
import {
  Tender,
  Requirement,
  Document,
  TenderClause,
  Bidder,
  PreBidInfo,
  Corrigendum,
  TenderComplianceSummary,
  AuditLog
} from '../types';

export const tenderService = {
  getTenders: async (params?: { status?: string; search?: string; skip?: number; limit?: number }): Promise<Tender[]> => {
    const res = await api.get('/tenders', { params });
    return res.data;
  },

  getTenderById: async (id: string): Promise<Tender> => {
    const res = await api.get(`/tenders/${id}`);
    return res.data;
  },

  createTender: async (tenderData: Partial<Tender>): Promise<Tender> => {
    const res = await api.post('/tenders', tenderData);
    return res.data;
  },

  updateTender: async (id: string, tenderData: Partial<Tender>): Promise<Tender> => {
    const res = await api.put(`/tenders/${id}`, tenderData);
    return res.data;
  },

  deleteTender: async (id: string): Promise<{ message: string; id: string }> => {
    const res = await api.delete(`/tenders/${id}`);
    return res.data;
  },

  uploadTenderDoc: async (tenderId: string, file: File, documentType = 'TENDER_SPECIFICATION'): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    const res = await api.post(`/tenders/${tenderId}/documents`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  getTenderDocuments: async (tenderId: string): Promise<Document[]> => {
    const res = await api.get(`/tenders/${tenderId}/documents`);
    return res.data;
  },

  getTenderBidders: async (tenderId: string): Promise<Bidder[]> => {
    const res = await api.get(`/tenders/${tenderId}/bidders`);
    return res.data;
  },

  getPreBidInfo: async (tenderId: string): Promise<PreBidInfo> => {
    const res = await api.get(`/tenders/${tenderId}/pre-bid`);
    return res.data;
  },

  getCorrigenda: async (tenderId: string): Promise<Corrigendum[]> => {
    const res = await api.get(`/tenders/${tenderId}/corrigenda`);
    return res.data;
  },

  getComplianceSummary: async (tenderId: string): Promise<TenderComplianceSummary> => {
    const res = await api.get(`/tenders/${tenderId}/compliance-summary`);
    return res.data;
  },

  getTenderAuditLogs: async (tenderId: string): Promise<AuditLog[]> => {
    const res = await api.get(`/tenders/${tenderId}/audit-trail`);
    return res.data;
  },

  getRequirements: async (tenderId: string): Promise<Requirement[]> => {
    const res = await api.get(`/tenders/${tenderId}/requirements`);
    return res.data;
  },

  addRequirement: async (tenderId: string, req: Partial<Requirement>): Promise<Requirement> => {
    const res = await api.post(`/tenders/${tenderId}/requirements`, req);
    return res.data;
  },

  getTenderClauses: async (tenderId: string): Promise<TenderClause[]> => {
    const res = await api.get(`/tenders/${tenderId}/clauses`);
    return res.data;
  },

  parseTenderClauses: async (tenderId: string, documentId?: string): Promise<{ message: string; clauses_count: number; requirements_created: number }> => {
    const res = await api.post(`/tenders/${tenderId}/parse-clauses`, null, {
      params: documentId ? { document_id: documentId } : undefined
    });
    return res.data;
  }
};
