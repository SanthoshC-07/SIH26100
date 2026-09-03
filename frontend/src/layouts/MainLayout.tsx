import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';
import { Topbar } from '../components/Topbar';

export const MainLayout: React.FC = () => {
  return (
    <div className="flex min-h-screen bg-[#F8FAFC]">
      {/* Dark Navy Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Topbar />
        
        <main className="flex-1 p-6 sm:p-8 max-w-[1600px] w-full mx-auto">
          <Outlet />
        </main>

        {/* Global Institutional Footer */}
        <footer className="border-t border-slate-200 bg-white py-3.5 px-8 text-[11px] font-mono text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span>© 2026 BidVerify AI • MoPNG Pipeline Procurement Platform</span>
            <span className="hidden md:inline">•</span>
            <span className="hidden md:inline text-slate-400">GovProcure Professional Suite v2.4.0</span>
          </div>
          <div className="flex items-center gap-4 text-slate-500">
            <span className="hover:text-slate-800 cursor-pointer">System Logs</span>
            <span className="hover:text-slate-800 cursor-pointer">Audit Policy</span>
            <span className="hover:text-slate-800 cursor-pointer">Support</span>
          </div>
        </footer>
      </div>
    </div>
  );
};
