import api from './api';
import { DashboardStats } from '../types';

export const analyticsService = {
  getDashboardStats: async (): Promise<DashboardStats> => {
    const res = await api.get('/analytics/dashboard');
    return res.data;
  },
};
