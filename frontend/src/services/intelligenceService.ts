import api from './api';

export interface ExtractedRequirement {
  requirement_text: string;
  category: string;
  threshold?: number | null;
  unit?: string | null;
  value?: number | null;
  minimum_value?: number | null;
  maximum_value?: number | null;
  time_period_years?: number | null;
  project_type?: string | null;
  sector?: string | null;
  diameter_inch?: number | null;
  length_km?: number | null;
  experience_years?: number | null;
  required_count?: number | null;
  role?: string | null;
  qualification?: string | null;
  scope?: string | null;
  entities: string[];
  extraction_method: string;
  confidence: number;
  status: 'VERIFICATION_READY' | 'REVIEW';
}

export interface RetrievedEvidenceItem {
  document_id: string;
  document_name: string;
  page_number: number;
  chunk_id?: string;
  text: string;
  extraction_method: string;
  similarity_score: number;
}

export interface RequirementEvidenceRetrievalResponse {
  requirement_id: string;
  requirement_text: string;
  query: string;
  category: string;
  top_similarity: number;
  evidence_status: 'VERIFICATION_READY' | 'REVIEW' | 'NO_EVIDENCE';
  evidence: RetrievedEvidenceItem[];
}

export const intelligenceService = {
  async extractRequirement(requirementText: string, category?: string): Promise<ExtractedRequirement> {
    const response = await api.post<ExtractedRequirement>('/intelligence/extract-requirement', {
      requirement_text: requirementText,
      category,
    });
    return response.data;
  },

  async extractStoredRequirement(requirementId: string): Promise<ExtractedRequirement> {
    const response = await api.post<ExtractedRequirement>(`/intelligence/extract-requirement/${requirementId}`);
    return response.data;
  },

  async retrieveEvidence(bidId: string, requirementId: string, topK: number = 5): Promise<RequirementEvidenceRetrievalResponse> {
    const response = await api.post<RequirementEvidenceRetrievalResponse>(
      `/evidence/retrieve/${bidId}/${requirementId}?top_k=${topK}`
    );
    return response.data;
  },

  async searchEvidence(bidId: string, query: string, topK: number = 5) {
    const response = await api.get(`/evidence/search/${bidId}`, {
      params: { q: query, top_k: topK },
    });
    return response.data;
  },

  async indexBidderEvidence(bidId: string) {
    const response = await api.post(`/evidence/index/${bidId}`);
    return response.data;
  },
};

export default intelligenceService;
