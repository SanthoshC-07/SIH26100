import React from 'react';
import { Outlet } from 'react-router-dom';
import { Topbar } from '../components/Topbar';

export const MainLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#F4F5F2] flex flex-col font-sans antialiased text-[#17201C]">
      
      {/* Top Navigation Bar */}
      <Topbar />

      {/* Main Page Viewport */}
      <main className="flex-1 p-6 md:p-8 max-w-[1500px] w-full mx-auto">
        <Outlet />
      </main>

      {/* Institutional System Footer */}
      <footer className="h-10 bg-[#EDEFEA] border-t border-[#D8DCD6] px-8 flex items-center justify-between text-[10px] font-mono text-[#59625D] mt-auto">
        <div>
          GOVERNMENT e-MARKETPLACE • <strong>SIH26100</strong> BID COMPLIANCE & ELIGIBILITY VERIFICATION PLATFORM
        </div>
        <div>
          AI-ASSISTED PROCUREMENT DECISION SUPPORT • GFR SECTION 4 AUDIT COMPLIANT
        </div>
      </footer>

    </div>
  );
};
