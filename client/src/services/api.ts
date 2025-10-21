import axios from 'axios';

const API_BASE_URL = 'http://localhost:8002';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Chat API
export const chatApi = {
  sendMessage: async (walletAddress: string, message: string, file?: File) => {
    if (file) {
      // Send message with file attachment
      const formData = new FormData();
      formData.append('wallet_address', walletAddress);
      formData.append('message', message);
      formData.append('file', file);
      
      const response = await api.post('/chat/query-with-file', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } else {
      // Send text-only message
      const response = await api.post('/chat/query', {
        wallet_address: walletAddress,
        message,
      });
      return response.data;
    }
  },

  getHistory: async (walletAddress: string, limit = 10) => {
    const response = await api.get(`/chat/history/${walletAddress}?limit=${limit}`);
    return response.data;
  },

  clearHistory: async (walletAddress: string) => {
    const response = await api.delete(`/chat/history/${walletAddress}`);
    return response.data;
  },

  getAgentsStatus: async () => {
    const response = await api.get('/chat/agents/status');
    return response.data;
  },
};

// Upload API
export const uploadApi = {
  uploadFile: async (file: File, walletAddress: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_wallet', walletAddress);
    formData.append('upload_type', 'sustainability_document'); // Required field

    const response = await api.post('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 120000, // 2 minutes for processing
    });
    return response.data;
  },

  getUploadStatus: async (uploadId: string) => {
    const response = await api.get(`/upload/${uploadId}/status`);
    return response.data;
  },
};

// Analytics API
export const analyticsApi = {
  getUserAnalytics: async (walletAddress: string) => {
    const response = await api.get(`/analytics/user/${walletAddress}`);
    return response.data;
  },

  getLeaderboard: async (limit = 10) => {
    const response = await api.get(`/analytics/leaderboard?limit=${limit}`);
    return response.data;
  },

  getSystemOverview: async () => {
    const response = await api.get('/analytics/stats/overview');
    return response.data;
  },

  getRecentActivity: async (walletAddress: string, limit = 20) => {
    const response = await api.get(`/analytics/user/${walletAddress}/recent?limit=${limit}`);
    return response.data;
  },
};

// Health check
export const healthApi = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  checkChat: async () => {
    const response = await api.get('/chat/health');
    return response.data;
  },
};

export default api;
