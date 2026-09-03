import api from './api';
import { Bidder, BidderDetail, Document } from '../types';

export const bidderService = {
  getBidders: async (tenderId?: string): Promise<Bidder[]> => {
    const res = await api.get('/bidders', { params: { tender_id: tenderId } });
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
};
