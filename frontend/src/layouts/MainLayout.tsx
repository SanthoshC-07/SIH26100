import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';
import { Topbar } from '../components/Topbar';

export const MainLayout: React.FC = () => {
  const location = useLocation();

  return (
    <div className="flex min-h-screen bg-[#F4F5F7] text-[#17212B] font-sans">
      {/* Institutional Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Topbar />
        
        <main
          key={location.pathname}
          className="flex-1 p-6 sm:p-8 w-full max-w-[1600px] mx-auto page-enter overflow-y-auto"
        >
          <Outlet />
        </main>

        {/* Global Footer (matching PDF clean institutional note) */}
        <footer className="border-t border-[#D9DEE3] bg-[#FFFFFF] py-2.5 px-8 text-xs font-sans text-[#66717C] flex flex-col sm:flex-row items-center justify-between gap-2 shrink-0">
          <div className="flex items-center gap-2">
            <span className="font-serif font-bold text-[#10283A]">PetroBid</span>
            <span>•</span>
            <span>Ministry of Petroleum &amp; Natural Gas — Pipeline Procurement Compliance System</span>
          </div>
          <div className="flex items-center gap-3 text-[#66717C]">
            <span>Activity is logged for audit trail</span>
            <span>•</span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#198754] inline-block" />
              GFR 2017 Validated
            </span>
          </div>
        </footer>
      </div>
    </div>
  );
};
