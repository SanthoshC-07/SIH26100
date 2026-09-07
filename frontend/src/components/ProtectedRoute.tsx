import React from 'react';
import { Navigate, Link } from 'react-router-dom';
import { ShieldAlert, ArrowLeft, LogOut } from 'lucide-react';
import { authService } from '../services';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: Array<'ADMIN' | 'PROCUREMENT_OFFICER' | 'BIDDER'>;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const token = localStorage.getItem('token');
  const user = authService.getUserFromStorage();

  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    const defaultDashboard =
      user.role === 'ADMIN'
        ? '/admin/dashboard'
        : user.role === 'PROCUREMENT_OFFICER'
        ? '/officer/dashboard'
        : '/bidder/dashboard';

    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center p-6 text-center font-sans">
        <div className="bg-[#FEF2F2] border border-[#F87171] rounded-2xl p-8 max-w-lg w-full shadow-lg">
          <div className="w-16 h-16 bg-[#DC2626] text-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-md">
            <ShieldAlert className="w-8 h-8" />
          </div>

          <h2 className="text-xl font-bold text-[#991B1B] font-serif mb-2">
            Access Denied
          </h2>

          <p className="text-sm text-[#7F1D1D] mb-5 leading-relaxed">
            You do not have permission to access this module. Your current account role does not meet the mandatory procurement security authorization requirements.
          </p>

          <div className="bg-white/80 border border-[#FCA5A5] rounded-lg p-3.5 mb-6 text-left text-xs space-y-1.5 font-mono">
            <div className="flex justify-between">
              <span className="text-[#991B1B] font-semibold font-sans">Your Role:</span>
              <span className="bg-[#FEE2E2] px-2 py-0.5 rounded text-[#991B1B] font-bold">
                {user.role}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#991B1B] font-semibold font-sans">Required Role(s):</span>
              <span className="bg-[#EFF6FF] px-2 py-0.5 rounded text-[#1D4ED8] font-bold">
                {allowedRoles.join(', ')}
              </span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link
              to={defaultDashboard}
              className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-[#10283A] text-white text-xs font-semibold rounded-lg hover:bg-[#18374D] transition-colors shadow-sm"
            >
              <ArrowLeft className="w-4 h-4" />
              Return to My Dashboard
            </Link>

            <button
              onClick={() => {
                authService.logout();
                window.location.href = '/login';
              }}
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-white border border-[#D1D5DB] text-[#4B5563] text-xs font-semibold rounded-lg hover:bg-[#F3F4F6] transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Sign In with Other Role
            </button>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};
