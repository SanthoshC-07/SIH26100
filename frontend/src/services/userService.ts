import api from './api';
import { User } from '../types';

export interface CreateUserData {
  email: string;
  username: string;
  name: string;
  role: 'ADMIN' | 'PROCUREMENT_OFFICER' | 'BIDDER';
  password: string;
  department?: string;
  bidder_id?: string;
}

export interface UpdateUserData {
  name?: string;
  email?: string;
  role?: 'ADMIN' | 'PROCUREMENT_OFFICER' | 'BIDDER';
  department?: string;
  is_active?: boolean;
  bidder_id?: string;
  password?: string;
}

export const userService = {
  getUsers: async (role?: string): Promise<User[]> => {
    const params = role ? { role } : {};
    const res = await api.get('/users', { params });
    return res.data;
  },

  getUser: async (id: string): Promise<User> => {
    const res = await api.get(`/users/${id}`);
    return res.data;
  },

  createUser: async (userData: CreateUserData): Promise<User> => {
    const res = await api.post('/users', userData);
    return res.data;
  },

  updateUser: async (id: string, userData: UpdateUserData): Promise<User> => {
    const res = await api.patch(`/users/${id}`, userData);
    return res.data;
  },

  deleteUser: async (id: string): Promise<{ message: string }> => {
    const res = await api.delete(`/users/${id}`);
    return res.data;
  }
};
