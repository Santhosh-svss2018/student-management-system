import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export function RoleRoute({ allowedRoles = [], children }) {
  const { role, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-background">
        <div className="w-10 h-10 border-3 border-primary/20 border-t-primary rounded-full animate-spin" />
        <p className="mt-4 text-xs font-medium text-on-surface-variant animate-pulse">
          Checking access permissions...
        </p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Admin has access to all internal views for system inspection
  if (role === 'admin' || allowedRoles.includes(role)) {
    return children;
  }

  // If user role is not permitted, redirect to 403 / unauthorized
  return <Navigate to="/unauthorized" replace />;
}

export default RoleRoute;
