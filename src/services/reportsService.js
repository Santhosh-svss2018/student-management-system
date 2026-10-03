/**
 * Reports & Data Export Service
 * Connects frontend reporting tables, filters, and CSV/PDF export buttons to FastAPI backend.
 */

import { apiRequest, getStoredToken } from './api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

/**
 * Utility helper to download binary blobs (CSV, PDF) with JWT authorization header.
 */
async function triggerBlobDownload(endpoint, defaultFilename) {
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  const token = getStoredToken();

  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, { headers });
  if (!response.ok) {
    let errMsg = 'Failed to download report.';
    try {
      const errJson = await response.json();
      if (errJson.detail) errMsg = errJson.detail;
    } catch (_) {
      // fallback
    }
    throw new Error(errMsg);
  }

  // Extract filename from Content-Disposition if present
  let filename = defaultFilename;
  const disposition = response.headers.get('content-disposition');
  if (disposition && disposition.includes('filename=')) {
    const match = disposition.match(/filename="?([^"]+)"?/);
    if (match && match[1]) {
      filename = match[1];
    }
  }

  const blob = await response.blob();
  const blobUrl = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = blobUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(blobUrl);
}

export const reportsService = {
  /**
   * Fetches filtered students report.
   */
  async getStudentsReport(filters = {}) {
    const params = new URLSearchParams();
    if (filters.department && filters.department !== 'All' && filters.department !== 'All Departments') {
      params.append('department', filters.department);
    }
    if (filters.year) params.append('year', filters.year);
    if (filters.section && filters.section !== 'All') params.append('section', filters.section);
    if (filters.is_active !== undefined && filters.is_active !== '') {
      params.append('is_active', filters.is_active);
    }
    if (filters.search) params.append('search', filters.search);
    if (filters.page) params.append('page', filters.page);
    if (filters.limit) params.append('limit', filters.limit);

    const query = params.toString() ? `?${params.toString()}` : '';
    return apiRequest(`/api/reports/students${query}`);
  },

  /**
   * Fetches filtered attendance report.
   */
  async getAttendanceReport(filters = {}) {
    const params = new URLSearchParams();
    if (filters.department && filters.department !== 'All' && filters.department !== 'All Departments') {
      params.append('department', filters.department);
    }
    if (filters.year) params.append('year', filters.year);
    if (filters.section && filters.section !== 'All') params.append('section', filters.section);
    if (filters.date_from) params.append('date_from', filters.date_from);
    if (filters.date_to) params.append('date_to', filters.date_to);
    if (filters.student_id) params.append('student_id', filters.student_id);
    if (filters.status && filters.status !== 'All') params.append('status', filters.status);
    if (filters.page) params.append('page', filters.page);
    if (filters.limit) params.append('limit', filters.limit);

    const query = params.toString() ? `?${params.toString()}` : '';
    return apiRequest(`/api/reports/attendance${query}`);
  },

  /**
   * Fetches filtered marks & evaluations report.
   */
  async getMarksReport(filters = {}) {
    const params = new URLSearchParams();
    if (filters.department && filters.department !== 'All' && filters.department !== 'All Departments') {
      params.append('department', filters.department);
    }
    if (filters.semester && filters.semester !== 'All' && filters.semester !== 'All Semesters') {
      const semNum = String(filters.semester).replace(/\D/g, '');
      if (semNum) params.append('semester', semNum);
    }
    if (filters.subject_code && filters.subject_code !== 'All') {
      params.append('subject_code', filters.subject_code);
    }
    if (filters.exam_type && filters.exam_type !== 'All') {
      params.append('exam_type', filters.exam_type);
    }
    if (filters.academic_year && filters.academic_year !== 'All') {
      params.append('academic_year', filters.academic_year);
    }
    if (filters.student_id) params.append('student_id', filters.student_id);
    if (filters.page) params.append('page', filters.page);
    if (filters.limit) params.append('limit', filters.limit);

    const query = params.toString() ? `?${params.toString()}` : '';
    return apiRequest(`/api/reports/marks${query}`);
  },

  /**
   * Fetches institutional academic summary report.
   */
  async getAcademicSummaryReport(filters = {}) {
    const params = new URLSearchParams();
    if (filters.department && filters.department !== 'All' && filters.department !== 'All Departments') {
      params.append('department', filters.department);
    }
    if (filters.semester && filters.semester !== 'All') {
      const semNum = String(filters.semester).replace(/\D/g, '');
      if (semNum) params.append('semester', semNum);
    }
    if (filters.academic_year && filters.academic_year !== 'All') {
      params.append('academic_year', filters.academic_year);
    }
    if (filters.page) params.append('page', filters.page);
    if (filters.limit) params.append('limit', filters.limit);

    const query = params.toString() ? `?${params.toString()}` : '';
    return apiRequest(`/api/reports/academic-summary${query}`);
  },

  /**
   * Exports Students CSV file.
   */
  async exportStudentsCsv(filters = {}) {
    const params = new URLSearchParams();
    if (filters.department && filters.department !== 'All' && filters.department !== 'All Departments') {
      params.append('department', filters.department);
    }
    if (filters.year) params.append('year', filters.year);
    if (filters.section && filters.section !== 'All') params.append('section', filters.section);
    if (filters.is_active !== undefined && filters.is_active !== '') {
      params.append('is_active', filters.is_active);
    }

    const query = params.toString() ? `?${params.toString()}` : '';
    return triggerBlobDownload(`/api/reports/students/export${query}`, 'edumanage_students_report.csv');
  },

  /**
   * Exports Attendance CSV file.
   */
  async exportAttendanceCsv(filters = {}) {
    const params = new URLSearchParams();
    if (filters.department && filters.department !== 'All' && filters.department !== 'All Departments') {
      params.append('department', filters.department);
    }
    if (filters.year) params.append('year', filters.year);
    if (filters.section && filters.section !== 'All') params.append('section', filters.section);
    if (filters.date_from) params.append('date_from', filters.date_from);
    if (filters.date_to) params.append('date_to', filters.date_to);
    if (filters.student_id) params.append('student_id', filters.student_id);
    if (filters.status && filters.status !== 'All') params.append('status', filters.status);

    const query = params.toString() ? `?${params.toString()}` : '';
    return triggerBlobDownload(`/api/reports/attendance/export${query}`, 'edumanage_attendance_report.csv');
  },

  /**
   * Exports Marks CSV file.
   */
  async exportMarksCsv(filters = {}) {
    const params = new URLSearchParams();
    if (filters.department && filters.department !== 'All' && filters.department !== 'All Departments') {
      params.append('department', filters.department);
    }
    if (filters.semester && filters.semester !== 'All') {
      const semNum = String(filters.semester).replace(/\D/g, '');
      if (semNum) params.append('semester', semNum);
    }
    if (filters.subject_code && filters.subject_code !== 'All') {
      params.append('subject_code', filters.subject_code);
    }
    if (filters.exam_type && filters.exam_type !== 'All') {
      params.append('exam_type', filters.exam_type);
    }
    if (filters.academic_year && filters.academic_year !== 'All') {
      params.append('academic_year', filters.academic_year);
    }
    if (filters.student_id) params.append('student_id', filters.student_id);

    const query = params.toString() ? `?${params.toString()}` : '';
    return triggerBlobDownload(`/api/reports/marks/export${query}`, 'edumanage_marks_report.csv');
  },

  /**
   * Exports official Student PDF report.
   */
  async exportStudentPdf(studentId) {
    if (!studentId) throw new Error('Student ID is required for PDF export.');
    return triggerBlobDownload(`/api/reports/student/${encodeURIComponent(studentId)}/pdf`, `edumanage_${studentId}_report.pdf`);
  },
};

export default reportsService;
