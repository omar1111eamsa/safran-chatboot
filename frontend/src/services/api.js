/**
 * API service for backend communication
 */

import axios from 'axios';
import config from '../config';

// Create axios instance
const api = axios.create({
    baseURL: config.apiBaseUrl,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // If error is 401 and we haven't tried to refresh yet
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');
                if (!refreshToken) {
                    throw new Error('No refresh token');
                }

                // Try to refresh the token
                const response = await axios.post(
                    `${config.apiBaseUrl}/api/auth/refresh`,
                    { refresh_token: refreshToken }
                );

                const { access_token, refresh_token } = response.data;

                // Store new tokens
                localStorage.setItem('access_token', access_token);
                localStorage.setItem('refresh_token', refresh_token);

                // Retry original request with new token
                originalRequest.headers.Authorization = `Bearer ${access_token}`;
                return api(originalRequest);
            } catch (refreshError) {
                // Refresh failed, clear tokens and redirect to login
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                localStorage.removeItem('user_profile');
                window.location.href = '/';
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

/**
 * Authentication API
 */
export const authAPI = {
    /**
     * Login user
     */
    login: async (username, password) => {
        const response = await axios.post(`${config.apiBaseUrl}/api/auth/login`, {
            username,
            password,
        });
        return response.data;
    },

    /**
     * Refresh access token
     */
    refresh: async (refreshToken) => {
        const response = await axios.post(`${config.apiBaseUrl}/api/auth/refresh`, {
            refresh_token: refreshToken,
        });
        return response.data;
    },
};

/**
 * User API
 */
export const userAPI = {
    /**
     * Get current user profile
     */
    getProfile: async () => {
        const response = await api.get('/api/profile');
        return response.data;
    },
};

/**
 * Chat API
 */
export const chatAPI = {
    /**
     * Send message to chatbot
     */
    sendMessage: async (message) => {
        const response = await api.post('/api/chat', { message });
        return response.data;
    },
};

export default api;
