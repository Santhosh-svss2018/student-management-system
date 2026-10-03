/**
 * Analytics Service
 * Connects frontend dashboard widgets and charts to live FastAPI analytics endpoints.
 */

import { apiRequest } from './api';

export const analyticsService = {
  /**
   * Retrieves comprehensive institutional overview metrics.
   * Admin only.
   */
  async getAdminOverview() {
    return apiRequest('/api/analytics/admin/overview');
  },

  /**
   * Retrieves department-level performance metrics.
   * Admin only.
   */
  async getAdminDepartments() {
    return apiRequest('/api/analytics/admin/departments');
  },

  /**
   * Retrieves institutional academic performance breakdown.
   * Admin only.
   */
  async getAdminAcademic() {
    return apiRequest('/api/analytics/admin/academic');
  },

  /**
   * Retrieves institutional attendance metrics and defaulters.
   * Admin only.
   */
  async getAdminAttendance() {
    return apiRequest('/api/analytics/admin/attendance');
  },

  /**
   * Retrieves teacher class & instructional overview.
   * Teacher & Admin.
   * @param {string} [department] - Optional department filter
   */
  async getTeacherOverview(department = '') {
    const params = new URLSearchParams();
    if (department && department !== 'All' && department !== 'All Departments') {
      params.append('department', department);
    }
    const query = params.toString() ? `?${params.toString()}` : '';
    return apiRequest(`/api/analytics/teacher/overview${query}`);
  },

  /**
   * Retrieves personalized analytics for the authenticated student.
   * Student only.
   */
  async getStudentAnalytics() {
    return apiRequest('/api/analytics/student/me');
  },
};

export default analyticsService;
