import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { DashboardLayout } from './layouts/DashboardLayout';

import { DashboardPage } from './pages/DashboardPage';
import { DatasetsPage } from './pages/DatasetsPage';
import { DatasetDetailPage } from './pages/DatasetDetailPage';
import { UploadPage } from './pages/UploadPage';
import { PreprocessPage } from './pages/PreprocessPage';
import { GenerateDataPage } from './pages/GenerateDataPage';
import { PrivacyBudgetPage } from './pages/PrivacyBudgetPage';
import { ModelManagementPage } from './pages/ModelManagementPage';
import { ReportsPage } from './pages/ReportsPage';
import { AuditLogsPage } from './pages/AuditLogsPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { isAuthenticated, loading, hasRole } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <div className="animate-spin w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !hasRole(allowedRoles)) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Auth Routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Authenticated Application Routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<DashboardPage />} />
              <Route path="datasets" element={<DatasetsPage />} />
              <Route path="datasets/:id" element={<DatasetDetailPage />} />
              <Route
                path="upload"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN', 'HR_ANALYST']}>
                    <UploadPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="preprocess"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN', 'HR_ANALYST']}>
                    <PreprocessPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="preprocess/:datasetId"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN', 'HR_ANALYST']}>
                    <PreprocessPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="generate"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN', 'HR_ANALYST']}>
                    <GenerateDataPage />
                  </ProtectedRoute>
                }
              />
              <Route path="privacy" element={<PrivacyBudgetPage />} />
              <Route path="models" element={<ModelManagementPage />} />
              <Route path="reports" element={<ReportsPage />} />
              <Route
                path="audit"
                element={
                  <ProtectedRoute allowedRoles={['ADMIN']}>
                    <AuditLogsPage />
                  </ProtectedRoute>
                }
              />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}
