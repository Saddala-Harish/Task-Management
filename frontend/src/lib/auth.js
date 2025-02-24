'use client';

import { create } from 'zustand';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export const useAuth = create((set) => ({
  user: null,
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);
      
      const response = await axios.post(`${API_URL}/auth/login`, formData);
      localStorage.setItem('token', response.data.access_token);
      
      // Get user data
      const userResponse = await axios.get(`${API_URL}/users/me`, {
        headers: {
          Authorization: `Bearer ${response.data.access_token}`
        }
      });
      
      set({ user: userResponse.data, isLoading: false });
    } catch (error) {
      set({
        error: error?.response?.data?.detail || 'Login failed',
        isLoading: false
      });
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    set({ user: null });
  },

  loadUser: async () => {
    if (typeof window === 'undefined') return;
    
    const token = localStorage.getItem('token');
    if (!token) return;

    set({ isLoading: true });
    try {
      const response = await axios.get(`${API_URL}/users/me`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      set({ user: response.data, isLoading: false });
    } catch (error) {
      set({ user: null, isLoading: false });
      localStorage.removeItem('token');
    }
  }
}));