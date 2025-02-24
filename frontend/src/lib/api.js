// File: src/lib/api.js
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  }
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export const tasksApi = {
  getTasks: async () => {
    try {
      const response = await api.get('/tasks');
      return response.data;
    } catch (error) {
      console.error('Error fetching tasks:', error);
      return { tasks: [] };
    }
  },

  createTask: async (taskData) => {
    try {
      const response = await api.post('/tasks', taskData);
      return response.data;
    } catch (error) {
      console.error('Error creating task:', error);
      throw error;
    }
  },

  updateTask: async (id, taskData) => {
    try {
      // Only send the fields that are actually changing
      const cleanedData = {};
      if (taskData.title !== undefined) cleanedData.title = taskData.title;
      if (taskData.description !== undefined) cleanedData.description = taskData.description;
      if (taskData.status !== undefined) cleanedData.status = taskData.status;
      if (taskData.priority !== undefined) cleanedData.priority = taskData.priority;
      if (taskData.assigned_to !== undefined) {
        cleanedData.assigned_to = taskData.assigned_to ? Number(taskData.assigned_to) : null;
      }

      console.log('Sending update data:', cleanedData); // For debugging

      const response = await api.put(`/tasks/${id}`, cleanedData);
      return response.data;
    } catch (error) {
      console.error('Error updating task:', error);
      if (error.response?.status === 422) {
        console.error('Validation error:', error.response.data);
      }
      throw error;
    }
},

  getUsers: async () => {
    try {
      const response = await api.get('/users');
      return response.data;
    } catch (error) {
      console.error('Error fetching users:', error);
      return [];
    }
  }
};

export default api;