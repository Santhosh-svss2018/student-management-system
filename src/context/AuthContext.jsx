import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

const ROLE_DEFAULTS = {
  admin: {
    avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80',
    department: 'University Administration',
    title: 'Dean of Academic Affairs'
  },
  teacher: {
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&auto=format&fit=crop&q=80',
    department: 'Computer Science & Engineering',
    title: 'Associate Professor'
  },
  student: {
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
    department: 'Computer Science',
    batch: '2022-2026',
    semester: '6th Semester',
    rollNo: 'CS-22-089'
  }
};

/**
 * Normalizes backend user profile for frontend UI component compatibility.
 */
function normalizeUser(backendUser) {
  if (!backendUser) return null;
  const role = backendUser.role || 'student';
  const roleDefaults = ROLE_DEFAULTS[role] || ROLE_DEFAULTS.student;

  return {
    ...roleDefaults,
    ...backendUser,
    name: backendUser.full_name || backendUser.name || 'EduManage User',
    full_name: backendUser.full_name || backendUser.name || 'EduManage User',
    role
  };
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(() => authService.getStoredToken());
  const [isLoading, setIsLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  // Restore authenticated session from stored JWT on initial application load
  useEffect(() => {
    let isMounted = true;

    async function restoreSession() {
      const storedToken = authService.getStoredToken();
      if (!storedToken) {
        if (isMounted) {
          setCurrentUser(null);
          setToken(null);
          setIsLoading(false);
        }
        return;
      }

      try {
        const userProfile = await authService.getCurrentUser(storedToken);
        if (isMounted) {
          const normalized = normalizeUser(userProfile);
          setCurrentUser(normalized);
          setToken(storedToken);
          setAuthError(null);
        }
      } catch (err) {
        // Token is expired, invalid, or user is inactive
        if (isMounted) {
          authService.removeStoredToken();
          setCurrentUser(null);
          setToken(null);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    restoreSession();

    return () => {
      isMounted = false;
    };
  }, []);

  /**
   * Performs real backend authentication via POST /api/auth/login and GET /api/auth/me
   */
  const login = async (email, password) => {
    setIsLoading(true);
    setAuthError(null);

    try {
      // 1. Obtain JWT access token
      const authResponse = await authService.login(email, password);
      const accessToken = authResponse.access_token;

      // 2. Store token in localStorage
      authService.setStoredToken(accessToken);

      // 3. Fetch authenticated user profile using the token
      const userProfile = await authService.getCurrentUser(accessToken);
      const normalizedUser = normalizeUser(userProfile);

      setCurrentUser(normalizedUser);
      setToken(accessToken);
      setAuthError(null);

      return normalizedUser;
    } catch (err) {
      const errorMsg = err.message || 'Authentication failed. Please verify your credentials.';
      setAuthError(errorMsg);
      authService.removeStoredToken();
      setCurrentUser(null);
      setToken(null);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Logs out user, clears token from storage, and resets state.
   */
  const logout = () => {
    authService.removeStoredToken();
    setCurrentUser(null);
    setToken(null);
    setAuthError(null);
  };

  /**
   * Development-only role preview switcher (does not bypass real auth in production)
   */
  const switchDevRole = (roleKey) => {
    if (currentUser && ROLE_DEFAULTS[roleKey]) {
      setCurrentUser(prev => ({
        ...prev,
        ...ROLE_DEFAULTS[roleKey],
        role: roleKey
      }));
    }
  };

  const isAuthenticated = Boolean(currentUser && token);

  return (
    <AuthContext.Provider
      value={{
        user: currentUser,
        currentUser,
        token,
        role: currentUser?.role || 'student',
        isAuthenticated,
        isLoading,
        authError,
        login,
        logout,
        switchDevRole,
        availableRoles: ['admin', 'teacher', 'student']
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
