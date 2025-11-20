/**
 * Authentication Service
 * Handles user authentication and token management
 */

import { authAPI } from './api';

export const authService = {
    /**
     * Login user
     */
    login: async (email, password) => {
        try {
            const response = await authAPI.login({ email, password });

            if (response.data.status === 'success') {
                const { token, user } = response.data;
                localStorage.setItem('token', token);
                localStorage.setItem('user', JSON.stringify(user));
                return { success: true, user };
            }

            return { success: false, message: response.data.message };
        } catch (error) {
            return {
                success: false,
                message: error.response?.data?.message || 'Login failed'
            };
        }
    },

    /**
     * Signup new user
     */
    signup: async (username, email, password) => {
        try {
            const response = await authAPI.signup({ username, email, password });

            if (response.data.status === 'success') {
                const { token, user } = response.data;
                localStorage.setItem('token', token);
                localStorage.setItem('user', JSON.stringify(user));
                return { success: true, user };
            }

            return { success: false, message: response.data.message };
        } catch (error) {
            return {
                success: false,
                message: error.response?.data?.message || 'Signup failed'
            };
        }
    },

    /**
     * Logout user
     */
    logout: () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    },

    /**
     * Get current user from localStorage
     */
    getCurrentUser: () => {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    },

    /**
     * Check if user is authenticated
     */
    isAuthenticated: () => {
        return !!localStorage.getItem('token');
    },

    /**
     * Get auth token
     */
    getToken: () => {
        return localStorage.getItem('token');
    }
};
