/**
 * EduManage API Client
 * Centralized HTTP request utility with JWT token attachment and error normalization.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const TOKEN_KEY = 'edumanage_token';

export const getStoredToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

export const setStoredToken = (token) => {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
};

export const removeStoredToken = () => {
  localStorage.removeItem(TOKEN_KEY);
};

/**
 * Standard fetch wrapper for backend API endpoints.
 * @param {string} endpoint - API path (e.g., '/api/auth/login')
 * @param {RequestInit} [options] - Standard Fetch API request options
 * @returns {Promise<any>}
 */
export async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  // Automatically attach JWT Bearer token if present
  const token = options.token || getStoredToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers
  };

  try {
    const response = await fetch(url, config);

    // Handle 204 No Content
    if (response.status === 204) {
      return null;
    }

    let responseData = null;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      responseData = await response.json();
    } else {
      responseData = await response.text();
    }

    if (!response.ok) {
      let errorMessage = 'An unexpected error occurred.';

      if (responseData && typeof responseData === 'object') {
        if (responseData.detail) {
          if (Array.isArray(responseData.detail)) {
            // Pydantic validation error array
            errorMessage = responseData.detail.map(d => d.msg || d.message).join(', ');
          } else {
            errorMessage = responseData.detail;
          }
        } else if (responseData.message) {
          errorMessage = responseData.message;
        }
      } else if (typeof responseData === 'string' && responseData.trim()) {
        errorMessage = responseData;
      }

      const error = new Error(errorMessage);
      error.status = response.status;
      error.data = responseData;
      throw error;
    }

    return responseData;
  } catch (err) {
    if (err.name === 'TypeError' && err.message.includes('Failed to fetch')) {
      const networkError = new Error('Unable to connect to the backend server. Please ensure the server is running at ' + API_BASE_URL);
      networkError.status = 0;
      throw networkError;
    }
    throw err;
  }
}

export default apiRequest;
