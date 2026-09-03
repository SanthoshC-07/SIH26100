import api from './api';
import { User } from '../types';

export const authService = {
  login: async (username_or_email: string, password: string) => {
    const res = await api.post('/auth/login', { username_or_email, password });
    if (res.data.access_token) {
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('user', JSON.stringify(res.data.user));
    }
    return res.data;
  },

  register: async (userData: { name: string; email: string; username: string; password: string; role?: string; department?: string }) => {
    const res = await api.post('/auth/register', userData);
    return res.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const res = await api.get('/auth/me');
    return res.data;
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getUserFromStorage: (): User | null => {
    const u = localStorage.getItem('user');
    return u ? JSON.parse(u) : null;
  }
};
