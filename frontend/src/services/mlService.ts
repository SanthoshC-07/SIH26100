import api from './api';

export interface ClassifyRequirementResult {
  text: string;
  predicted_class: string;
  confidence: number;
  all_scores: Record<string, number>;
  classifier_type: string;
  model_ready: boolean;
  error?: string;
}

export interface ClassifierInfo {
  model_type: string;
  algorithm: string;
  classes: string[];
  num_classes: number;
  model_ready: boolean;
  model_path?: string | null;
  load_error?: string | null;
  description: string;
}

export const mlService = {
  /**
   * Classify a requirement clause text using the scikit-learn domain classifier.
   * Returns the predicted class (one of 10 locked classes) and confidence.
   */
  classifyRequirement: async (text: string): Promise<ClassifyRequirementResult> => {
    const res = await api.post('/ml/classify-requirement', { text });
    return res.data;
  },

  /**
   * Classify multiple clauses in a single request.
   */
  classifyBatch: async (texts: string[]): Promise<ClassifyRequirementResult[]> => {
    const res = await api.post('/ml/classify-batch', { texts });
    return res.data;
  },

  /**
   * Get metadata about the requirement classifier.
   */
  getClassifierInfo: async (): Promise<ClassifierInfo> => {
    const res = await api.get('/ml/classifier-info');
    return res.data;
  },

  /**
   * Get the list of locked requirement classes.
   */
  getRequirementClasses: async (): Promise<{ classes: string[]; count: number }> => {
    const res = await api.get('/ml/classes');
    return res.data;
  },
};
