import api from './api';

export interface RequirementDatasetItem {
  requirement_id: string;
  source_document: string;
  page_number: number;
  original_text: string;
  normalized_text: string;
  category: string;
  domain_relevance: string;
  minimum_value?: number | null;
  maximum_value?: number | null;
  unit?: string | null;
  currency?: string | null;
  percentage?: number | null;
  count?: number | null;
  length_km?: number | null;
  diameter_inch?: number | null;
  experience_years?: number | null;
  time_period_years?: number | null;
  date?: string | null;
  project_type?: string | null;
  sector?: string | null;
  role?: string | null;
  qualification?: string | null;
  scope?: string | null;
  entities?: string[];
  extraction_method: string;
  classification_confidence: number;
  review_status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'NEEDS_REVIEW';
}

export interface RequirementReviewItem {
  requirement_id: string;
  source_document: string;
  page_number: number;
  original_text: string;
  predicted_category: string;
  classification_confidence: number;
  extraction_method: string;
  review_reason: string;
}

export interface DatasetFilterParams {
  category?: string;
  domain_relevance?: string;
  review_status?: string;
  search?: string;
  skip?: number;
  limit?: number;
}

export const requirementDatasetService = {
  getDataset: async (params?: DatasetFilterParams) => {
    const response = await api.get('/requirements-pipeline/dataset', { params });
    return response.data;
  },

  getReviews: async (params?: { search?: string; skip?: number; limit?: number }) => {
    const response = await api.get('/requirements-pipeline/reviews', { params });
    return response.data;
  },

  updateReview: async (requirementId: string, reviewStatus: string, notes?: string) => {
    const response = await api.post(`/requirements-pipeline/review/${requirementId}`, {
      review_status: reviewStatus,
      notes
    });
    return response.data;
  },

  runPipeline: async (inputDir?: string) => {
    const response = await api.post('/requirements-pipeline/run', { input_dir: inputDir });
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/requirements-pipeline/stats');
    return response.data;
  }
};
