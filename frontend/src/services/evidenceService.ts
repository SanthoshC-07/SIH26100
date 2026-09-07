import api from './api';
import { EvidenceSearchResult } from '../types';

export interface SearchEvidenceParams {
  query: string;
  bidder_id?: string;
  document_id?: string;
  top_k?: number;
}

export const evidenceService = {
  searchEvidenceForRequirement: async (
    requirementId: string,
    params: { bidder_id?: string; document_id?: string; top_k?: number } = {}
  ): Promise<{ requirement_id: string; results: EvidenceSearchResult[] }> => {
    const res = await api.post(`/requirements/${requirementId}/evidence/search`, params);
    return res.data;
  },

  searchEvidence: async (params: SearchEvidenceParams): Promise<EvidenceSearchResult[]> => {
    const res = await api.post('/evidence/search', params);
    return res.data;
  },

  getDocumentChunks: async (documentId: string): Promise<any[]> => {
    const res = await api.get(`/documents/${documentId}/chunks`);
    return res.data;
  },

  getDocumentPages: async (documentId: string): Promise<any[]> => {
    const res = await api.get(`/documents/${documentId}/pages`);
    return res.data;
  },

  getAllDocuments: async (params?: { bidder_id?: string; tender_id?: string; document_type?: string }): Promise<any[]> => {
    const res = await api.get('/documents', { params });
    return res.data;
  },

  getExtractedEntities: async (params?: { bidder_id?: string; document_id?: string; entity_type?: string }): Promise<any[]> => {
    const res = await api.get('/extracted-entities', { params });
    return res.data;
  },

  getDocumentEntities: async (documentId: string): Promise<any[]> => {
    const res = await api.get(`/documents/${documentId}/entities`);
    return res.data;
  }
};
