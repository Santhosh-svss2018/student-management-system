/**
 * Authentication Service
 * Handles user login and profile verification with the FastAPI backend.
 */

import { apiRequest, getStoredToken, setStoredToken, removeStoredToken } from './api';

export const authService = {
  /**
   * Authenticates user against POST /api/auth/login
   * @param {string} email
   * @param {string} password
   * @returns {Promise<{ access_token: string, token_type: string }>}
   */
  async login(email, password) {
    const payload = {
      email: email.trim().toLowerCase(),
      password
    };

    return await apiRequest('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  /**
   * Retrieves authenticated user details from GET /api/auth/me
   * @param {string} [token] - Optional token override
   * @returns {Promise<{ id: string, full_name: string, email: string, role: string, is_active: boolean, created_at: string }>}
   */
  async getCurrentUser(token) {
    return await apiRequest('/api/auth/me', {
      method: 'GET',
      token
    });
  },

  getStoredToken,
  setStoredToken,
  removeStoredToken
};

export default authService;
