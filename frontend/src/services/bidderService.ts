import api from './api';
import { Bidder, BidderDetail, Document, DebarmentRecord } from '../types';

export const bidderService = {
  getBidders: async (tenderId?: string): Promise<Bidder[]> => {
    const res = await api.get('/bidders', { params: { tender_id: tenderId } });
    return res.data;
  },

  getBids: async (): Promise<any[]> => {
    const res = await api.get('/bids');
    return res.data;
  },

  getBidderDetail: async (bidderId: string): Promise<BidderDetail> => {
    const res = await api.get(`/bidders/${bidderId}`);
    return res.data;
  },

  createBidder: async (bidderData: Partial<Bidder>): Promise<Bidder> => {
    const res = await api.post('/bidders', bidderData);
    return res.data;
  },

  createBidderWithDocuments: async (formData: FormData): Promise<Bidder> => {
    const res = await api.post('/bidders/with-documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  verifyBidder: async (bidderId: string): Promise<any> => {
    const res = await api.post(`/bidders/${bidderId}/verify`);
    return res.data;
  },

  uploadBidderDoc: async (bidderId: string, file: File, documentType = 'GENERAL'): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    const res = await api.post(`/bidders/${bidderId}/documents`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  uploadRequirementEvidence: async (
    bidderId: string,
    file: File,
    requirementId?: string,
    category?: string
  ): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    if (requirementId) formData.append('requirement_id', requirementId);
    if (category) formData.append('category', category);
    const res = await api.post(`/bidders/${bidderId}/upload-requirement-evidence`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  getDebarmentCheck: async (bidderId: string): Promise<DebarmentRecord> => {
    const res = await api.get(`/bidders/${bidderId}/debarment-check`);
    return res.data;
  },

  recordSelectingAuthorityDecision: async (
    bidderId: string,
    payload: {
      decision: string;
      remarks: string;
      statutory_rule?: string;
      technical_score?: number;
      financial_cleared?: boolean;
    }
  ): Promise<any> => {
    const res = await api.post(`/bidders/${bidderId}/selecting-authority`, payload);
    return res.data;
  }
};
