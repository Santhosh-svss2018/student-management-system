/**
 * EduManage User Service
 * Handles user management and Admin password management APIs.
 */

import { apiRequest } from './api';

export const userService = {
  /**
   * Admin-only API to change another user's password (student or teacher).
   * @param {string} userIdentifier - BSON ObjectId, email, or student_id
   * @param {string} newPassword - New password (minimum 8 characters)
   * @returns {Promise<{ message: string, status: string }>}
   */
  async changeUserPassword(userIdentifier, newPassword) {
    if (!userIdentifier) {
      throw new Error('User identifier is required.');
    }
    if (!newPassword || newPassword.trim().length < 8) {
      throw new Error('New password must be at least 8 characters long.');
    }

    return apiRequest(`/api/users/${encodeURIComponent(userIdentifier)}/password`, {
      method: 'PUT',
      body: JSON.stringify({
        new_password: newPassword
      })
    });
  },

  /**
   * Fetches paginated user accounts (Admin only).
   * @param {number} [skip=0]
   * @param {number} [limit=50]
   * @returns {Promise<Array>}
   */
  async getUsers(skip = 0, limit = 50) {
    return apiRequest(`/api/users/?skip=${skip}&limit=${limit}`);
  },

  /**
   * Fetches a single user profile by ID.
   * @param {string} userId
   * @returns {Promise<Object>}
   */
  async getUser(userId) {
    if (!userId) {
      throw new Error('User ID is required.');
    }
    return apiRequest(`/api/users/${encodeURIComponent(userId)}`);
  }
};

export default userService;
