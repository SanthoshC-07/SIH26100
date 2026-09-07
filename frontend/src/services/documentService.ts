import api from './api';
import { Document } from '../types';

export const documentService = {
  uploadTenderDocument: async (tenderId: string, file: File, documentType = 'TENDER_SPECIFICATION'): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    const res = await api.post(`/tenders/${tenderId}/documents`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  uploadBidderDocument: async (bidderId: string, file: File, documentType = 'GENERAL'): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    const res = await api.post(`/bidders/${bidderId}/documents`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  inspectDocument: async (file: File, category?: string): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    if (category) formData.append('category', category);
    const res = await api.post('/bidders/inspect-document', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  }
};
