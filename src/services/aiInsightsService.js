/**
 * EduManage AI Insights & Student Risk Analysis Service
 * Encapsulates all risk analysis endpoints using the centralized apiRequest client.
 */

import { apiRequest } from './api';

export const aiInsightsService = {
  /**
   * Retrieves the institutional student risk overview and alerts.
   * @param {Object} [params={}]
   * @param {string} [params.risk_level] - Filter by risk level (LOW, MEDIUM, HIGH, CRITICAL)
   * @param {string} [params.department] - Filter by department
   * @param {number} [params.limit=50] - Maximum records to retrieve
   * @returns {Promise<{ total_students_analyzed: number, critical_count: number, high_count: number, medium_count: number, low_count: number, average_risk_score: number, items: Array }>}
   */
  async getInstitutionalInsights(params = {}) {
    const searchParams = new URLSearchParams();
    if (params.risk_level && params.risk_level !== 'All') {
      searchParams.append('risk_level', params.risk_level.trim().toUpperCase());
    }
    if (params.department && params.department !== 'All') {
      searchParams.append('department', params.department.trim());
    }
    if (params.limit) {
      searchParams.append('limit', String(params.limit));
    }

    const queryString = searchParams.toString();
    return apiRequest(`/api/ai-insights/students${queryString ? `?${queryString}` : ''}`);
  },

  /**
   * Retrieves detailed risk analysis and recommendations for a specific student (Admin / Teacher).
   * @param {string} studentId - Institutional student identifier
   * @returns {Promise<Object>}
   */
  async getStudentRisk(studentId) {
    if (!studentId) {
      throw new Error('Student identifier is required.');
    }
    return apiRequest(`/api/ai-insights/student/${encodeURIComponent(studentId)}`);
  },

  /**
   * Retrieves the current authenticated student's risk analysis (Student role only).
   * @returns {Promise<Object>}
   */
  async getMyRiskAnalysis() {
    return apiRequest('/api/ai-insights/me');
  },
};

export default aiInsightsService;
