/**
 * API Service
 * Centralized API calls to backend gateway
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Unauthorized - clear token and redirect to login
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Authentication APIs
export const authAPI = {
    signup: (data) => api.post('/api/auth/signup', data),
    login: (data) => api.post('/api/auth/login', data),
    getCurrentUser: () => api.get('/api/auth/me'),
    verifyToken: () => api.get('/api/auth/verify'),
};

// Stock APIs
export const stockAPI = {
    getLatest: (symbol) => api.get(`/api/stocks/latest/${symbol}`),
    getHistory: (symbol, params) => api.get(`/api/stocks/history/${symbol}`, { params }),
    getAnalytics: (symbol) => api.get(`/api/stocks/analytics/${symbol}`),
    getDashboard: () => api.get('/api/stocks/dashboard'),
};

// Watchlist APIs
export const watchlistAPI = {
    getWatchlist: () => api.get('/api/watchlist'),
    addToWatchlist: (symbol) => api.post('/api/watchlist', { symbol }),
    removeFromWatchlist: (itemId) => api.delete(`/api/watchlist/${itemId}`),
    checkInWatchlist: (symbol) => api.get(`/api/watchlist/check/${symbol}`),
};

// Alert APIs
export const alertAPI = {
    getUserAlerts: (userId, params) => api.get(`/api/alerts/${userId}`, { params }),
    markAsRead: (alertId) => api.put(`/api/alerts/${alertId}/read`),
    createAlertRule: (data) => api.post('/api/alert-rules', data),
    getUserAlertRules: (userId) => api.get(`/api/alert-rules/${userId}`),
    deleteAlertRule: (ruleId) => api.delete(`/api/alert-rules/${ruleId}`),
};

export default api;
