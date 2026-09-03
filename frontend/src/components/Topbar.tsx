import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { authService } from '../services';
import {
  LayoutDashboard,
  FileSpreadsheet,
  Users,
  CheckSquare,
  History,
  Settings,
  LogOut,
  ShieldCheck,
  Search,
  Bell,
  Cpu,
  Layers,
  ChevronDown
} from 'lucide-react';

export const Topbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const user = authService.getUserFromStorage();
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toUTCString().replace('GMT', 'UTC'));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, tag: 'KPI' },
    { name: 'Tenders', path: '/tenders', icon: FileSpreadsheet, count: '3' },
    { name: 'Bidder Records', path: '/bidders', icon: Users, count: '4' },
    { name: 'Review Queue', path: '/reviews', icon: CheckSquare, alert: true },
    { name: 'Audit Trail', path: '/audit', icon: History, tag: 'GFR' },
    { name: 'Engine Rules', path: '/settings', icon: Settings },
  ];

  return (
    <header className="bg-slate-900 text-slate-100 border-b border-slate-800/80 sticky top-0 z-50 shadow-md">
      
      {/* Upper Command & Telemetry Bar */}
      <div className="h-14 px-6 flex items-center justify-between border-b border-slate-800/60">
        
        {/* Left: Petroleum & Natural Gas Procurement Brand */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-emerald-600 to-teal-700 p-0.5 shadow-lg shadow-emerald-900/30 flex items-center justify-center font-bold font-mono text-white text-sm">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-sm tracking-tight text-white font-sans">
                  SIH26100 AEGIS
                </span>
                <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  MoPNG / GeM PIPELINE
                </span>
              </div>
              <span className="text-[10px] text-slate-400 font-mono tracking-wide block">
                INTEGRATED BID COMPLIANCE & 7-CORE VERIFICATION ENGINE
              </span>
            </div>
          </div>

          <div className="hidden xl:flex items-center gap-2 pl-4 border-l border-slate-800 text-[11px] font-mono text-slate-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span>PORTAL TELEMETRY: <strong className="text-emerald-400">ACTIVE</strong></span>
            <span>•</span>
            <span>GFR SEC 4 LEGAL AUDIT: <strong className="text-slate-200">ENABLED</strong></span>
          </div>
        </div>

        {/* Center: Global Quick Finder */}
        <div className="hidden md:flex items-center relative w-72 lg:w-96">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search tender, bidder name, GSTIN, PAN, pipeline km..."
            className="w-full text-xs font-mono rounded-lg bg-slate-800/80 border border-slate-700/80 pl-9 pr-3 py-1.5 text-slate-200 placeholder:text-slate-500 outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                navigate('/bidders');
              }
            }}
          />
          <span className="absolute right-2.5 top-2 text-[9px] font-mono bg-slate-700 text-slate-400 px-1.5 py-0.5 rounded">
            ↵ ENTER
          </span>
        </div>

        {/* Right: Live UTC Clock & Officer Credentials */}
        <div className="flex items-center gap-3.5 font-mono text-xs">
          
          <div className="hidden lg:block text-[11px] text-slate-400 pr-3 border-r border-slate-800">
            {timeStr}
          </div>

          <div className="flex items-center gap-2.5 pl-1">
            <div className="text-right">
              <div className="text-xs font-bold text-white tracking-tight font-sans">
                {user?.name || "Rajesh Sharma"}
              </div>
              <div className="text-[10px] text-emerald-400 font-mono">
                {user?.role === 'ADMIN' ? 'ADMINISTRATOR' : 'SR. PROCUREMENT OFFICER'}
              </div>
            </div>
            <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 text-emerald-400 font-bold flex items-center justify-center text-xs shadow-inner">
              {user?.name ? user.name.charAt(0) : 'O'}
            </div>
          </div>

          <button
            onClick={handleLogout}
            title="Sign Out Session"
            className="p-2 rounded-lg bg-slate-800/60 hover:bg-red-500/20 hover:text-red-400 border border-slate-700/80 text-slate-400 transition-all"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>

        </div>

      </div>

      {/* Lower Navigation Deck */}
      <div className="px-6 bg-slate-950/70 backdrop-blur-md flex items-center justify-between overflow-x-auto">
        <nav className="flex items-center gap-1">
          {navItems.map((item) => {
            const isActive = location.pathname.startsWith(item.path);
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={
                  `relative flex items-center gap-2 px-4 py-2.5 text-xs font-medium tracking-wide transition-all whitespace-nowrap ${
                    isActive
                      ? 'text-emerald-400 font-bold bg-slate-800/50'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900/60'
                  }`
                }
              >
                <item.icon className={`w-3.5 h-3.5 ${isActive ? 'text-emerald-400' : 'text-slate-500'}`} />
                <span>{item.name}</span>

                {item.tag && (
                  <span className={`text-[9px] font-mono px-1 py-0.2 rounded border ${
                    isActive ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' : 'bg-slate-800 text-slate-400 border-slate-700'
                  }`}>
                    {item.tag}
                  </span>
                )}

                {item.count && (
                  <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                    {item.count}
                  </span>
                )}

                {item.alert && (
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>
                )}

                {isActive && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-emerald-500 shadow-sm shadow-emerald-500"></span>
                )}
              </NavLink>
            );
          })}
        </nav>

        <div className="hidden md:flex items-center gap-2 text-[11px] font-mono text-slate-400 py-1">
          <span className="text-slate-500">PRIMARY PIPELINE TENDER:</span>
          <span className="text-slate-200 font-bold bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
            GAIL/2026/PL-NC/4182
          </span>
        </div>
      </div>

    </header>
  );
};
