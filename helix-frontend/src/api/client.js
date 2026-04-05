import axios from 'axios';

const apiToken = import.meta.env.VITE_API_TOKEN || 'dev-token';

const api = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL || 'https://reworked-echo.onrender.com',
  timeout: 60000, // 60s timeout for Render cold starts
  headers: {
    'Content-Type': 'application/json',
    'x-api-token': apiToken,
  },
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      error.message = 'Request timed out — server may be cold starting';
    }
    return Promise.reject(error);
  }
);

export const coreAPI = {
  getStatus: () => api.get('/api/status', { timeout: 10000 }), // Shorter timeout for health checks
};

export const userAPI = {
  getProfile: (userId) => api.get(`/api/users/${userId}/profile`),
  updateProfile: (userId, profile) => api.put(`/api/users/${userId}/profile`, { ...profile, user_id: userId }),
  getHistory: (userId) => api.get(`/api/users/${userId}/history`),
  clearHistory: (userId) => api.post(`/api/users/${userId}/clear`),
};

export const textAPI = {
  process: (payload) => api.post('/api/chat/stream', payload),
};

export const feedbackAPI = {
  submit: (payload) => api.post('/api/feedback', payload),
};

export const modelAPI = {
  listVersions: () => api.get('/api/model/versions'),
  runTraining: (payload) => api.post('/api/training/run', payload),
};

export default api;
