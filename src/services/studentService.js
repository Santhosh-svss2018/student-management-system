/**
 * EduManage Student API Service
 * Encapsulates all student-related backend interactions using the centralized API client.
 */

import { apiRequest } from './api';

export const studentService = {
  /**
   * Fetches paginated student records with optional search filter.
   * @param {number} [page=1] - 1-indexed page number
   * @param {number} [limit=20] - Number of items per page
   * @param {string} [search=''] - Search query (matches name, roll number, email, student ID, department)
   * @returns {Promise<{ items: Array, page: number, limit: number, total: number, pages: number }>}
   */
  async getStudents(page = 1, limit = 20, search = '') {
    const params = new URLSearchParams();
    params.append('page', String(page));
    params.append('limit', String(limit));
    if (search && search.trim()) {
      params.append('search', search.trim());
    }

    return apiRequest(`/api/students/?${params.toString()}`);
  },

  /**
   * Fetches a single student record by student_id or MongoDB _id.
   * @param {string} studentId - Institutional student ID or MongoDB ObjectId
   * @returns {Promise<Object>}
   */
  async getStudent(studentId) {
    if (!studentId) {
      throw new Error('Student identifier is required.');
    }
    return apiRequest(`/api/students/${encodeURIComponent(studentId)}`);
  },

  /**
   * Registers a new student record (Admin only).
   * @param {Object} data - Student creation payload
   * @returns {Promise<Object>}
   */
  async createStudent(data) {
    return apiRequest('/api/students/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Updates an existing student record (Admin only).
   * @param {string} studentId - Institutional student ID or MongoDB ObjectId
   * @param {Object} data - Student update payload
   * @returns {Promise<Object>}
   */
  async updateStudent(studentId, data) {
    if (!studentId) {
      throw new Error('Student identifier is required.');
    }
    return apiRequest(`/api/students/${encodeURIComponent(studentId)}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Soft-deactivates a student record by setting is_active=false (Admin only).
   * @param {string} studentId - Institutional student ID or MongoDB ObjectId
   * @returns {Promise<Object>}
   */
  async deactivateStudent(studentId) {
    if (!studentId) {
      throw new Error('Student identifier is required.');
    }
    return apiRequest(`/api/students/${encodeURIComponent(studentId)}`, {
      method: 'DELETE',
    });
  },

  /**
   * Retrieves the current authenticated student's profile (Student role only).
   * Uses the authenticated user's JWT automatically.
   * @returns {Promise<Object>}
   */
  async getMyStudentProfile() {
    return apiRequest('/api/students/me');
  }
};

export default studentService;
