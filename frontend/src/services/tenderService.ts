import api from './api';
import { Tender, Requirement, Document } from '../types';

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

  getRequirements: async (tenderId: string): Promise<Requirement[]> => {
    const res = await api.get(`/tenders/${tenderId}/requirements`);
    return res.data;
  },

  addRequirement: async (tenderId: string, req: Partial<Requirement>): Promise<Requirement> => {
    const res = await api.post(`/tenders/${tenderId}/requirements`, req);
    return res.data;
  }
};
