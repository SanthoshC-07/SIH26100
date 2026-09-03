import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileSpreadsheet,
  ShieldCheck,
  FolderOpen,
  BarChart3,
  FileText,
  History,
  Settings,
  Shield
} from 'lucide-react';

interface SidebarProps {
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onCloseMobile }) => {
  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Bids', path: '/bids', icon: FileSpreadsheet },
    { name: 'Verification', path: '/verification', icon: ShieldCheck },
    { name: 'Documents', path: '/documents', icon: FolderOpen },
    { name: 'Risk Analysis', path: '/risk-analysis', icon: BarChart3 },
    { name: 'Reports', path: '/reports', icon: FileText },
    { name: 'Audit Trail', path: '/audit', icon: History },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-[#0B132B] border-r border-[#1E293B] text-slate-300 flex flex-col justify-between shrink-0 select-none h-screen sticky top-0">
      
      {/* Brand & Logo Header */}
      <div>
        <div className="h-16 px-6 flex items-center gap-3 border-b border-[#1E293B]/70 bg-[#090F22]">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center shadow-glow">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-bold text-sm tracking-tight text-white flex items-center gap-1.5">
              <span>BidVerify AI</span>
              <span className="text-[9px] px-1.5 py-0.2 bg-blue-500/20 text-blue-400 border border-blue-400/30 rounded font-mono font-normal">
                MoPNG
              </span>
            </div>
            <div className="text-[10px] text-slate-400 tracking-wider uppercase font-medium">
              Pipeline Compliance
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-3.5 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onCloseMobile}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-blue-600 text-white font-semibold shadow-sm shadow-blue-500/30'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-[#152244]'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer System Version Badge */}
      <div className="p-4 border-t border-[#1E293B]/70 bg-[#090F22]/50 text-[11px] font-mono text-slate-500 flex items-center justify-between">
        <span>Version 2.4.0</span>
        <span className="flex items-center gap-1.5 text-emerald-400 text-[10px]">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          Live Secure
        </span>
      </div>

    </aside>
  );
};
