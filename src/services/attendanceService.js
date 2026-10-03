/**
 * EduManage Attendance API Service
 * Encapsulates all attendance interactions using the centralized apiRequest utility.
 */

import { apiRequest } from './api';

export const attendanceService = {
  /**
   * Fetches paginated attendance records with optional filtering.
   * @param {Object} [params={}] - Filter parameters
   * @param {number} [params.page=1] - 1-indexed page number
   * @param {number} [params.limit=20] - Number of items per page
   * @param {string} [params.student_id] - Institutional student identifier
   * @param {string} [params.date] - Date string (YYYY-MM-DD)
   * @param {string} [params.start_date] - Start date (YYYY-MM-DD)
   * @param {string} [params.end_date] - End date (YYYY-MM-DD)
   * @param {string} [params.status] - Status (present, absent, late, excused)
   * @returns {Promise<{ items: Array, page: number, limit: number, total: number, pages: number }>}
   */
  async getAttendance(params = {}) {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.append('page', String(params.page));
    if (params.limit) searchParams.append('limit', String(params.limit));
    if (params.student_id && params.student_id.trim()) searchParams.append('student_id', params.student_id.trim());
    if (params.date && params.date.trim()) searchParams.append('date', params.date.trim());
    if (params.start_date && params.start_date.trim()) searchParams.append('start_date', params.start_date.trim());
    if (params.end_date && params.end_date.trim()) searchParams.append('end_date', params.end_date.trim());
    if (params.status && params.status.trim() && params.status !== 'All') {
      searchParams.append('status', params.status.trim().toLowerCase());
    }

    const queryString = searchParams.toString();
    return apiRequest(`/api/attendance/${queryString ? `?${queryString}` : ''}`);
  },

  /**
   * Fetches a single attendance record by attendance_id or MongoDB _id.
   * @param {string} attendanceId
   * @returns {Promise<Object>}
   */
  async getAttendanceById(attendanceId) {
    if (!attendanceId) {
      throw new Error('Attendance identifier is required.');
    }
    return apiRequest(`/api/attendance/${encodeURIComponent(attendanceId)}`);
  },

  /**
   * Fetches paginated attendance records for a specific student.
   * @param {string} studentId
   * @param {Object} [params={}]
   * @returns {Promise<{ items: Array, page: number, limit: number, total: number, pages: number }>}
   */
  async getStudentAttendance(studentId, params = {}) {
    if (!studentId) {
      throw new Error('Student identifier is required.');
    }
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.append('page', String(params.page));
    if (params.limit) searchParams.append('limit', String(params.limit));
    if (params.start_date && params.start_date.trim()) searchParams.append('start_date', params.start_date.trim());
    if (params.end_date && params.end_date.trim()) searchParams.append('end_date', params.end_date.trim());
    if (params.status && params.status.trim() && params.status !== 'All') {
      searchParams.append('status', params.status.trim().toLowerCase());
    }

    const queryString = searchParams.toString();
    return apiRequest(`/api/attendance/student/${encodeURIComponent(studentId)}${queryString ? `?${queryString}` : ''}`);
  },

  /**
   * Fetches consolidated attendance summary for a specific student.
   * @param {string} studentId
   * @returns {Promise<{ student_id: string, total_days: number, present_days: number, absent_days: number, late_days: number, excused_days: number, attendance_percentage: number }>}
   */
  async getStudentAttendanceSummary(studentId) {
    if (!studentId) {
      throw new Error('Student identifier is required.');
    }
    return apiRequest(`/api/attendance/student/${encodeURIComponent(studentId)}/summary`);
  },

  /**
   * Retrieves the authenticated student's own attendance records.
   * @param {Object} [params={}]
   * @returns {Promise<{ items: Array, page: number, limit: number, total: number, pages: number }>}
   */
  async getMyAttendance(params = {}) {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.append('page', String(params.page));
    if (params.limit) searchParams.append('limit', String(params.limit));
    if (params.start_date && params.start_date.trim()) searchParams.append('start_date', params.start_date.trim());
    if (params.end_date && params.end_date.trim()) searchParams.append('end_date', params.end_date.trim());
    if (params.status && params.status.trim() && params.status !== 'All') {
      searchParams.append('status', params.status.trim().toLowerCase());
    }

    const queryString = searchParams.toString();
    return apiRequest(`/api/attendance/me${queryString ? `?${queryString}` : ''}`);
  },

  /**
   * Retrieves the authenticated student's own attendance summary metrics.
   * @returns {Promise<{ student_id: string, total_days: number, present_days: number, absent_days: number, late_days: number, excused_days: number, attendance_percentage: number }>}
   */
  async getMyAttendanceSummary() {
    return apiRequest('/api/attendance/me/summary');
  },

  /**
   * Records a new attendance entry (Admin or Teacher).
   * @param {Object} data - { student_id, date, status, remarks }
   * @returns {Promise<Object>}
   */
  async createAttendance(data) {
    return apiRequest('/api/attendance/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Updates an existing attendance record (Admin or Teacher).
   * @param {string} attendanceId
   * @param {Object} data - { status, remarks, date }
   * @returns {Promise<Object>}
   */
  async updateAttendance(attendanceId, data) {
    if (!attendanceId) {
      throw new Error('Attendance identifier is required.');
    }
    return apiRequest(`/api/attendance/${encodeURIComponent(attendanceId)}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Deletes an attendance record (Admin only).
   * @param {string} attendanceId
   * @returns {Promise<Object>}
   */
  async deleteAttendance(attendanceId) {
    if (!attendanceId) {
      throw new Error('Attendance identifier is required.');
    }
    return apiRequest(`/api/attendance/${encodeURIComponent(attendanceId)}`, {
      method: 'DELETE',
    });
  },
};

export default attendanceService;
