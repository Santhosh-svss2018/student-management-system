/**
 * EduManage Marks & Grade Management API Service
 * Encapsulates all assessment marks interactions using the centralized apiRequest client.
 */

import { apiRequest } from './api';

export const marksService = {
  /**
   * Fetches paginated marks records with optional multi-parameter filtering.
   * @param {Object} [params={}] - Query and filter parameters
   * @param {number} [params.page=1] - 1-indexed page number
   * @param {number} [params.limit=20] - Number of items per page
   * @param {string} [params.student_id] - Institutional student identifier
   * @param {string} [params.subject_code] - Subject/course code
   * @param {number} [params.semester] - Academic semester (1-8)
   * @param {string} [params.exam_type] - Assessment type (internal_1, internal_2, model, semester, assignment)
   * @param {string} [params.academic_year] - Academic year (e.g. 2024-2025)
   * @param {string} [params.search] - Search keyword
   * @returns {Promise<{ items: Array, page: number, limit: number, total: number, pages: number }>}
   */
  async getMarks(params = {}) {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.append('page', String(params.page));
    if (params.limit) searchParams.append('limit', String(params.limit));
    if (params.student_id && params.student_id.trim()) searchParams.append('student_id', params.student_id.trim());
    if (params.subject_code && params.subject_code.trim() && params.subject_code !== 'All') {
      searchParams.append('subject_code', params.subject_code.trim().toUpperCase());
    }
    if (params.semester && params.semester !== 'All') {
      searchParams.append('semester', String(params.semester));
    }
    if (params.exam_type && params.exam_type.trim() && params.exam_type !== 'All') {
      searchParams.append('exam_type', params.exam_type.trim().toLowerCase());
    }
    if (params.academic_year && params.academic_year.trim() && params.academic_year !== 'All') {
      searchParams.append('academic_year', params.academic_year.trim());
    }
    if (params.search && params.search.trim()) {
      searchParams.append('search', params.search.trim());
    }

    const queryString = searchParams.toString();
    return apiRequest(`/api/marks/${queryString ? `?${queryString}` : ''}`);
  },

  /**
   * Fetches a single marks record by marks_id or MongoDB ObjectId.
   * @param {string} marksId
   * @returns {Promise<Object>}
   */
  async getMarksById(marksId) {
    if (!marksId) {
      throw new Error('Marks identifier is required.');
    }
    return apiRequest(`/api/marks/${encodeURIComponent(marksId)}`);
  },

  /**
   * Records a new assessment score (Admin or Teacher).
   * @param {Object} data - { student_id, subject_code, subject_name, semester, exam_type, marks_obtained, max_marks, academic_year, remarks }
   * @returns {Promise<Object>}
   */
  async createMarks(data) {
    return apiRequest('/api/marks/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Modifies an existing marks record (Admin or Teacher).
   * @param {string} marksId
   * @param {Object} data - Updated attributes
   * @returns {Promise<Object>}
   */
  async updateMarks(marksId, data) {
    if (!marksId) {
      throw new Error('Marks identifier is required.');
    }
    return apiRequest(`/api/marks/${encodeURIComponent(marksId)}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Deletes a marks record (Admin only).
   * @param {string} marksId
   * @returns {Promise<Object>}
   */
  async deleteMarks(marksId) {
    if (!marksId) {
      throw new Error('Marks identifier is required.');
    }
    return apiRequest(`/api/marks/${encodeURIComponent(marksId)}`, {
      method: 'DELETE',
    });
  },

  /**
   * Fetches marks records for a specific student (Admin or Teacher).
   * @param {string} studentId
   * @param {Object} [params={}]
   * @returns {Promise<{ items: Array, page: number, limit: number, total: number, pages: number }>}
   */
  async getStudentMarks(studentId, params = {}) {
    if (!studentId) {
      throw new Error('Student identifier is required.');
    }
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.append('page', String(params.page));
    if (params.limit) searchParams.append('limit', String(params.limit));
    if (params.semester && params.semester !== 'All') searchParams.append('semester', String(params.semester));
    if (params.exam_type && params.exam_type !== 'All') searchParams.append('exam_type', params.exam_type.trim().toLowerCase());
    if (params.academic_year && params.academic_year !== 'All') searchParams.append('academic_year', params.academic_year.trim());

    const queryString = searchParams.toString();
    return apiRequest(`/api/marks/student/${encodeURIComponent(studentId)}${queryString ? `?${queryString}` : ''}`);
  },

  /**
   * Fetches marks performance summary for a specific student (Admin or Teacher).
   * @param {string} studentId
   * @param {Object} [params={}]
   * @returns {Promise<{ student_id: string, total_subjects: number, total_marks_obtained: number, total_max_marks: number, overall_percentage: number, passed_subjects: number, failed_subjects: number, grade_distribution: Object }>}
   */
  async getStudentMarksSummary(studentId, params = {}) {
    if (!studentId) {
      throw new Error('Student identifier is required.');
    }
    const searchParams = new URLSearchParams();
    if (params.semester && params.semester !== 'All') searchParams.append('semester', String(params.semester));
    if (params.academic_year && params.academic_year !== 'All') searchParams.append('academic_year', params.academic_year.trim());

    const queryString = searchParams.toString();
    return apiRequest(`/api/marks/student/${encodeURIComponent(studentId)}/summary${queryString ? `?${queryString}` : ''}`);
  },

  /**
   * Retrieves the authenticated student's own marks records (Student role only).
   * @param {Object} [params={}]
   * @returns {Promise<{ items: Array, page: number, limit: number, total: number, pages: number }>}
   */
  async getMyMarks(params = {}) {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.append('page', String(params.page));
    if (params.limit) searchParams.append('limit', String(params.limit));
    if (params.semester && params.semester !== 'All') searchParams.append('semester', String(params.semester));
    if (params.exam_type && params.exam_type !== 'All') searchParams.append('exam_type', params.exam_type.trim().toLowerCase());
    if (params.academic_year && params.academic_year !== 'All') searchParams.append('academic_year', params.academic_year.trim());

    const queryString = searchParams.toString();
    return apiRequest(`/api/marks/me${queryString ? `?${queryString}` : ''}`);
  },

  /**
   * Retrieves the authenticated student's own marks summary metrics (Student role only).
   * @param {Object} [params={}]
   * @returns {Promise<{ student_id: string, total_subjects: number, total_marks_obtained: number, total_max_marks: number, overall_percentage: number, passed_subjects: number, failed_subjects: number, grade_distribution: Object }>}
   */
  async getMyMarksSummary(params = {}) {
    const searchParams = new URLSearchParams();
    if (params.semester && params.semester !== 'All') searchParams.append('semester', String(params.semester));
    if (params.academic_year && params.academic_year !== 'All') searchParams.append('academic_year', params.academic_year.trim());

    const queryString = searchParams.toString();
    return apiRequest(`/api/marks/me/summary${queryString ? `?${queryString}` : ''}`);
  },

  /**
   * Alias for getMarks for listing compatibility.
   */
  async getMarksList(params = {}) {
    return this.getMarks(params);
  },
};

export default marksService;
