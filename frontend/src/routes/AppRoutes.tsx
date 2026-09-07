import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from '../layouts/MainLayout';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';
import { BidderDashboardPage } from '../pages/BidderDashboardPage';
import { UsersPage } from '../pages/UsersPage';
import { TendersPage } from '../pages/TendersPage';
import { CreateTenderPage } from '../pages/CreateTenderPage';
import { TenderDetailPage } from '../pages/TenderDetailPage';
import { BidderApplicationPage } from '../pages/BidderApplicationPage';
import { BiddersPage } from '../pages/BiddersPage';
import { BidderDetailPage } from '../pages/BidderDetailPage';
import { ComplianceReviewPage } from '../pages/ComplianceReviewPage';
import { ReviewQueuePage } from '../pages/ReviewQueuePage';
import { DocumentRepositoryPage } from '../pages/DocumentRepositoryPage';
import { RiskAnalysisPage } from '../pages/RiskAnalysisPage';
import { ReportsPage } from '../pages/ReportsPage';
import { AuditTrailPage } from '../pages/AuditTrailPage';
import { EngineRulesPage } from '../pages/EngineRulesPage';
import { SettingsPage } from '../pages/SettingsPage';
import { RequirementReviewPage } from '../pages/RequirementReviewPage';
import { OfficerReviewWorkspace } from '../pages/OfficerReviewWorkspace';
import { ProtectedRoute } from '../components/ProtectedRoute';
import { authService } from '../services';

const DashboardRedirect: React.FC = () => {
  const user = authService.getUserFromStorage();
  if (!user) return <Navigate to="/login" replace />;
  if (user.role === 'ADMIN') return <Navigate to="/admin/dashboard" replace />;
  if (user.role === 'PROCUREMENT_OFFICER') return <Navigate to="/officer/dashboard" replace />;
  return <Navigate to="/bidder/dashboard" replace />;
};

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      
      <Route path="/" element={<MainLayout />}>
        <Route index element={<DashboardRedirect />} />
        <Route path="dashboard" element={<DashboardRedirect />} />

        {/* Dedicated Role Dashboards */}
        <Route
          path="admin/dashboard"
          element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="officer/dashboard"
          element={
            <ProtectedRoute allowedRoles={['PROCUREMENT_OFFICER']}>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="bidder/dashboard"
          element={
            <ProtectedRoute allowedRoles={['BIDDER']}>
              <BidderDashboardPage />
            </ProtectedRoute>
          }
        />

        {/* User Management (ADMIN Only) */}
        <Route
          path="admin/users"
          element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <UsersPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="users"
          element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <UsersPage />
            </ProtectedRoute>
          }
        />
        
        {/* Tenders Module */}
        <Route
          path="tenders"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'PROCUREMENT_OFFICER', 'BIDDER']}>
              <TendersPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="tenders/create"
          element={
            <ProtectedRoute allowedRoles={['PROCUREMENT_OFFICER']}>
              <CreateTenderPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="tenders/:id"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'PROCUREMENT_OFFICER', 'BIDDER']}>
              <TenderDetailPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="tenders/:id/apply"
          element={
            <ProtectedRoute allowedRoles={['BIDDER']}>
              <BidderApplicationPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="apply"
          element={
            <ProtectedRoute allowedRoles={['BIDDER']}>
              <BidderApplicationPage />
            </ProtectedRoute>
          }
        />
        
        {/* Bidders Module */}
        <Route
          path="bidders"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'PROCUREMENT_OFFICER', 'BIDDER']}>
              <BiddersPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="bids"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'PROCUREMENT_OFFICER', 'BIDDER']}>
              <BiddersPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="bidders/:id"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'PROCUREMENT_OFFICER', 'BIDDER']}>
              <BidderDetailPage />
            </ProtectedRoute>
          }
        />

        {/* Dedicated Officer Review Workspace (PROCUREMENT_OFFICER Only) */}
        <Route
          path="officer-review"
          element={
            <ProtectedRoute allowedRoles={['PROCUREMENT_OFFICER']}>
              <OfficerReviewWorkspace />
            </ProtectedRoute>
          }
        />
        <Route
          path="officer-review/:bidId"
          element={
            <ProtectedRoute allowedRoles={['PROCUREMENT_OFFICER']}>
              <OfficerReviewWorkspace />
            </ProtectedRoute>
          }
        />
        
        {/* Compliance Review */}
        <Route
          path="compliance-review"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'PROCUREMENT_OFFICER', 'BIDDER']}>
              <ComplianceReviewPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="compliance-review/:bidId"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'PROCUREMENT_OFFICER', 'BIDDER']}>
              <ComplianceReviewPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="verification"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'PROCUREMENT_OFFICER', 'BIDDER']}>
              <ComplianceReviewPage />
            </ProtectedRoute>
          }
        />
        
        {/* Evidence Center & Repository */}
        <Route
          path="evidence-center"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'PROCUREMENT_OFFICER', 'BIDDER']}>
              <DocumentRepositoryPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="documents"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'PROCUREMENT_OFFICER', 'BIDDER']}>
              <DocumentRepositoryPage />
            </ProtectedRoute>
          }
        />
        
        {/* Review Queue (PROCUREMENT_OFFICER Only) */}
        <Route
          path="review-queue"
          element={
            <ProtectedRoute allowedRoles={['PROCUREMENT_OFFICER']}>
              <ReviewQueuePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="reviews"
          element={
            <ProtectedRoute allowedRoles={['PROCUREMENT_OFFICER']}>
              <ReviewQueuePage />
            </ProtectedRoute>
          }
        />
        
        {/* Risk Analytics (ADMIN and PROCUREMENT_OFFICER; Bidder Forbidden) */}
        <Route
          path="risk-analysis"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'PROCUREMENT_OFFICER']}>
              <RiskAnalysisPage />
            </ProtectedRoute>
          }
        />
        
        {/* Reports & Compliance Dossiers */}
        <Route
          path="reports"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'PROCUREMENT_OFFICER', 'BIDDER']}>
              <ReportsPage />
            </ProtectedRoute>
          }
        />
        
        {/* Audit Trail (ADMIN and PROCUREMENT_OFFICER; Bidder Forbidden) */}
        <Route
          path="audit-trail"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'PROCUREMENT_OFFICER']}>
              <AuditTrailPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="audit"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'PROCUREMENT_OFFICER']}>
              <AuditTrailPage />
            </ProtectedRoute>
          }
        />
        
        {/* Engine Rules & Thresholds (ADMIN Only) */}
        <Route
          path="engine-rules"
          element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <EngineRulesPage />
            </ProtectedRoute>
          }
        />
        
        {/* Requirement Dataset & Review (ADMIN and PROCUREMENT_OFFICER; Bidder Forbidden) */}
        <Route
          path="requirement-dataset"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'PROCUREMENT_OFFICER']}>
              <RequirementReviewPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="requirement-review"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'PROCUREMENT_OFFICER']}>
              <RequirementReviewPage />
            </ProtectedRoute>
          }
        />
        
        {/* Platform Settings (ADMIN Only) */}
        <Route
          path="settings"
          element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <SettingsPage />
            </ProtectedRoute>
          }
        />
      </Route>

      <Route path="*" element={<DashboardRedirect />} />
    </Routes>
  );
};
