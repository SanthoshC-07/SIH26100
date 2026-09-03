import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from '../layouts/MainLayout';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';
import { TendersPage } from '../pages/TendersPage';
import { CreateTenderPage } from '../pages/CreateTenderPage';
import { TenderDetailPage } from '../pages/TenderDetailPage';
import { BiddersPage } from '../pages/BiddersPage';
import { BidderDetailPage } from '../pages/BidderDetailPage';
import { ReviewQueuePage } from '../pages/ReviewQueuePage';
import { DocumentRepositoryPage } from '../pages/DocumentRepositoryPage';
import { RiskAnalysisPage } from '../pages/RiskAnalysisPage';
import { ReportsPage } from '../pages/ReportsPage';
import { AuditTrailPage } from '../pages/AuditTrailPage';
import { SettingsPage } from '../pages/SettingsPage';

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        
        {/* Tenders & Bids */}
        <Route path="bids" element={<BiddersPage />} />
        <Route path="bidders" element={<BiddersPage />} />
        <Route path="bidders/:id" element={<BidderDetailPage />} />
        <Route path="tenders" element={<TendersPage />} />
        <Route path="tenders/create" element={<CreateTenderPage />} />
        <Route path="tenders/:id" element={<TenderDetailPage />} />
        
        {/* Verification & Audit Modules */}
        <Route path="verification" element={<ReviewQueuePage />} />
        <Route path="reviews" element={<ReviewQueuePage />} />
        <Route path="documents" element={<DocumentRepositoryPage />} />
        <Route path="risk-analysis" element={<RiskAnalysisPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="audit" element={<AuditTrailPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};
