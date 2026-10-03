import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Layout & Guards
import MainLayout from '../components/layout/MainLayout';
import ProtectedRoute from '../components/auth/ProtectedRoute';
import RoleRoute from '../components/auth/RoleRoute';

// Auth Pages
import SignInPage from '../pages/auth/SignInPage';

// Admin Pages
import AdminDashboard from '../pages/admin/AdminDashboard';
import ReportsAnalytics from '../pages/admin/ReportsAnalytics';

// Faculty / Teacher Pages
import TeacherDashboard from '../pages/teacher/TeacherDashboard';
import AttendancePage from '../pages/teacher/AttendancePage';
import MarksManagement from '../pages/teacher/MarksManagement';
import TeacherProfile from '../pages/teacher/TeacherProfile';

// Student Management Pages
import StudentDirectory from '../pages/students/StudentDirectory';
import StudentForm from '../pages/students/StudentForm';
import StudentProfile from '../pages/students/StudentProfile';

// Student Portal Pages
import StudentDashboard from '../pages/student-portal/StudentDashboard';
import EduAIAssistant from '../pages/student-portal/EduAIAssistant';

// AI Intelligence & Showcase
import AIInsights from '../pages/ai/AIInsights';
import StyleguideShowcase from '../pages/showcase/StyleguideShowcase';

// Errors & Fallbacks
import Unauthorized from '../pages/Unauthorized';
import NotFound from '../pages/NotFound';

export function AppRoutes() {
  return (
    <Routes>
      {/* Root Route: Redirects to /login (Requirement 3) */}
      <Route path="/" element={<Navigate to="/login" replace />} />

      {/* Public Authentication Route */}
      <Route path="/login" element={<SignInPage />} />

      {/* Protected Main Application Shell */}
      <Route
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        {/* Admin Portal Routes */}
        <Route
          path="/admin"
          element={
            <RoleRoute allowedRoles={['admin']}>
              <AdminDashboard />
            </RoleRoute>
          }
        />
        <Route
          path="/admin/reports"
          element={
            <RoleRoute allowedRoles={['admin']}>
              <ReportsAnalytics />
            </RoleRoute>
          }
        />

        {/* Student Management Module (Admin & Teacher) */}
        <Route
          path="/students"
          element={
            <RoleRoute allowedRoles={['admin', 'teacher']}>
              <StudentDirectory />
            </RoleRoute>
          }
        />
        <Route
          path="/students/new"
          element={
            <RoleRoute allowedRoles={['admin']}>
              <StudentForm mode="add" />
            </RoleRoute>
          }
        />
        <Route
          path="/students/:id/edit"
          element={
            <RoleRoute allowedRoles={['admin']}>
              <StudentForm mode="edit" />
            </RoleRoute>
          }
        />
        <Route
          path="/students/:id"
          element={
            <RoleRoute allowedRoles={['admin', 'teacher', 'student']}>
              <StudentProfile />
            </RoleRoute>
          }
        />

        {/* Faculty / Teacher Portal Routes */}
        <Route
          path="/teacher"
          element={
            <RoleRoute allowedRoles={['teacher', 'admin']}>
              <TeacherDashboard />
            </RoleRoute>
          }
        />
        <Route
          path="/teacher/attendance"
          element={
            <RoleRoute allowedRoles={['teacher', 'admin']}>
              <AttendancePage />
            </RoleRoute>
          }
        />
        <Route
          path="/teacher/marks"
          element={
            <RoleRoute allowedRoles={['teacher', 'admin']}>
              <MarksManagement />
            </RoleRoute>
          }
        />
        <Route
          path="/teacher/profile"
          element={
            <RoleRoute allowedRoles={['teacher', 'admin']}>
              <TeacherProfile />
            </RoleRoute>
          }
        />

        {/* Student Portal Routes */}
        <Route
          path="/student-portal"
          element={
            <RoleRoute allowedRoles={['student', 'admin']}>
              <StudentDashboard />
            </RoleRoute>
          }
        />
        <Route
          path="/student-portal/ai"
          element={
            <RoleRoute allowedRoles={['student', 'admin', 'teacher']}>
              <EduAIAssistant />
            </RoleRoute>
          }
        />

        {/* AI Insights (Admin & Teacher) */}
        <Route
          path="/ai/insights"
          element={
            <RoleRoute allowedRoles={['admin', 'teacher']}>
              <AIInsights />
            </RoleRoute>
          }
        />

        {/* Global Styleguide Shell */}
        <Route path="/styleguide" element={<StyleguideShowcase />} />

        {/* Access Denied */}
        <Route path="/unauthorized" element={<Unauthorized />} />
      </Route>

      {/* 404 Catch-All */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default AppRoutes;
