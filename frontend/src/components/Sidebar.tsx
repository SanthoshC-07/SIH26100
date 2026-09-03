import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileSpreadsheet,
  Users,
  CheckSquare,
  History,
  Settings,
  Shield,
  FileText
} from 'lucide-react';

interface NavItem {
  name: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

export const Sidebar: React.FC = () => {
  const sections: NavSection[] = [
    {
      title: 'OVERVIEW',
      items: [
        { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
      ],
    },
    {
      title: 'PROCUREMENT',
      items: [
        { name: 'Tenders', path: '/tenders', icon: FileSpreadsheet },
        { name: 'Bidders', path: '/bidders', icon: Users },
      ],
    },
    {
      title: 'VERIFICATION',
      items: [
        { name: 'Review Queue', path: '/reviews', icon: CheckSquare },
      ],
    },
    {
      title: 'GOVERNANCE',
      items: [
        { name: 'Audit Trail', path: '/audit', icon: History },
      ],
    },
    {
      title: 'SYSTEM',
      items: [
        { name: 'Settings', path: '/settings', icon: Settings },
      ],
    },
  ];

  return (
    <aside className="w-60 bg-[#101A17] text-[#EDEFEA] flex flex-col shrink-0 border-r border-[#22322C] min-h-screen">
      
      {/* Brand / Platform Identity Header */}
      <div className="h-16 px-5 flex items-center gap-3 border-b border-[#22322C] bg-[#0C1412]">
        <div className="w-7 h-7 bg-[#163C32] border border-[#2D5A4E] flex items-center justify-center text-white font-mono font-bold text-xs">
          GeM
        </div>
        <div className="flex flex-col">
          <span className="font-mono text-xs font-bold tracking-widest text-white uppercase">
            CPCL / COMPLIANCE
          </span>
          <span className="text-[10px] tracking-wider text-[#808B84] uppercase font-mono">
            EVALUATION ENGINE
          </span>
        </div>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 py-4 px-3 space-y-6 overflow-y-auto">
        {sections.map((section, idx) => (
          <div key={idx} className="space-y-1">
            <div className="px-3 pb-1 text-[10px] font-mono uppercase tracking-widest text-[#5F6E66]">
              {section.title}
            </div>
            <nav className="space-y-0.5">
              {section.items.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-2.5 px-3 py-2 text-xs font-medium transition-colors border-l-2 ${
                      isActive
                        ? 'bg-[#1D2D27] text-white border-[#A7833B] font-semibold'
                        : 'text-[#9DAAA2] hover:bg-[#15221E] hover:text-white border-transparent'
                    }`
                  }
                >
                  <item.icon className="w-4 h-4 shrink-0 opacity-70" />
                  <span>{item.name}</span>
                </NavLink>
              ))}
            </nav>
          </div>
        ))}
      </div>

      {/* System Status / Governance Footer */}
      <div className="p-4 border-t border-[#22322C] bg-[#0C1412] text-[10px] font-mono text-[#808B84] space-y-1">
        <div className="flex items-center justify-between">
          <span>SYSTEM STATE</span>
          <span className="text-[#4E9F7F] font-bold">OPERATIONAL</span>
        </div>
        <div className="text-[9px] text-[#5F6E66]">
          GFR SEC 4 AUDIT ACTIVE
        </div>
      </div>

    </aside>
  );
};
