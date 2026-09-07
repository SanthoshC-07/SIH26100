import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  FileSpreadsheet,
  Users,
  ShieldCheck,
  FileSearch,
  ListFilter,
  AlertTriangle,
  FileText,
  History,
  Sliders,
  LogOut,
  ChevronRight,
  Database,
  UserCheck,
  Briefcase
} from 'lucide-react';
import { authService } from '../services';

interface SidebarProps {
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onCloseMobile }) => {
  const navigate = useNavigate();

  const userObj = authService.getUserFromStorage();
  const activeRole = userObj?.role || 'BIDDER';

  let userName = userObj?.name || 'User';
  let userRoleTitle = 'Registered Bidder';

  if (activeRole === 'ADMIN') {
    userRoleTitle = 'System Administrator';
  } else if (activeRole === 'PROCUREMENT_OFFICER') {
    userRoleTitle = 'Procurement Officer';
  } else {
    userRoleTitle = 'Registered Bidder';
  }

  // Calculate initials
  const initials = userName
    .split(' ')
    .map((n: string) => n[0])
    .filter(Boolean)
    .join('')
    .slice(0, 2)
    .toUpperCase() || 'PB';

  // Section 6: Precise Role Navigation Lists
  let navigationItems: Array<{ name: string; path: string; icon: any; shortDesc: string }> = [];

  if (activeRole === 'ADMIN') {
    navigationItems = [
      { name: 'Dashboard', path: '/admin/dashboard', icon: LayoutDashboard, shortDesc: 'System administration overview' },
      { name: 'User Management', path: '/admin/users', icon: UserCheck, shortDesc: 'Manage accounts & RBAC' },
      { name: 'Tenders', path: '/tenders', icon: FileSpreadsheet, shortDesc: 'View-only tender catalog' },
      { name: 'Bidder Records', path: '/bidders', icon: Users, shortDesc: 'View-only contractor registry' },
      { name: 'Compliance Results', path: '/compliance-review', icon: ShieldCheck, shortDesc: 'View-only GFR 2017 results' },
      { name: 'Risk Analysis', path: '/risk-analysis', icon: AlertTriangle, shortDesc: 'View-only risk profiling' },
      { name: 'Reports', path: '/reports', icon: FileText, shortDesc: 'View-only compliance dossiers' },
      { name: 'Audit Trail', path: '/audit-trail', icon: History, shortDesc: 'GFR 2017 immutable audit trail' },
      { name: 'System Settings', path: '/settings', icon: Sliders, shortDesc: 'Configure platform parameters' },
    ];
  } else if (activeRole === 'PROCUREMENT_OFFICER') {
    navigationItems = [
      { name: 'Dashboard', path: '/officer/dashboard', icon: LayoutDashboard, shortDesc: 'Officer dashboard & metrics' },
      { name: 'Tenders', path: '/tenders', icon: FileSpreadsheet, shortDesc: 'Pipeline tenders & specifications' },
      { name: 'Req Dataset', path: '/requirement-dataset', icon: Database, shortDesc: 'PDF extracted clauses' },
      { name: 'Bidder Records', path: '/bidders', icon: Users, shortDesc: 'EPC contractor registry' },
      { name: 'Officer Review', path: '/officer-review', icon: UserCheck, shortDesc: 'Procurement officer workspace' },
      { name: 'Compliance Review', path: '/compliance-review', icon: ShieldCheck, shortDesc: 'GFR 2017 checks & validation' },
      { name: 'Evidence Center', path: '/evidence-center', icon: FileSearch, shortDesc: 'Document workspace' },
      { name: 'Review Queue', path: '/review-queue', icon: ListFilter, shortDesc: 'Officer verification queue' },
      { name: 'Risk Analysis', path: '/risk-analysis', icon: AlertTriangle, shortDesc: 'Bid risk profiling' },
      { name: 'Reports', path: '/reports', icon: FileText, shortDesc: 'Compliance dossiers & export' },
      { name: 'Audit Trail', path: '/audit-trail', icon: History, shortDesc: 'GFR 2017 action log' },
    ];
  } else {
    // BIDDER
    navigationItems = [
      { name: 'Dashboard', path: '/bidder/dashboard', icon: LayoutDashboard, shortDesc: 'Contractor dashboard' },
      { name: 'Active Tenders', path: '/tenders', icon: FileSpreadsheet, shortDesc: 'Open pipeline tenders' },
      { name: 'My Bids', path: '/bidders', icon: Briefcase, shortDesc: 'My submitted applications' },
      { name: 'My Documents', path: '/evidence-center', icon: FileSearch, shortDesc: 'My uploaded evidence' },
      { name: 'My Compliance', path: '/compliance-review', icon: ShieldCheck, shortDesc: 'My technical compliance status' },
      { name: 'My Reports', path: '/reports', icon: FileText, shortDesc: 'My compliance dossiers' },
    ];
  }

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  const NavItem = ({ item }: { item: { name: string; path: string; icon: any; shortDesc: string } }) => {
    const Icon = item.icon;
    return (
      <NavLink
        key={item.path}
        to={item.path}
        onClick={onCloseMobile}
        title={item.shortDesc}
        className={({ isActive }) =>
          `group flex items-center gap-3 px-3.5 py-2.5 mx-3 rounded-md text-[12.5px] font-sans transition-all duration-150 ${
            isActive
              ? 'bg-[#D98A16] text-[#10283A] font-bold shadow-sm'
              : 'text-[#B0C0D0] hover:text-white hover:bg-[#18374D] font-normal'
          }`
        }
      >
        {({ isActive }) => (
          <>
            <Icon 
              className={`w-4 h-4 shrink-0 transition-colors ${
                isActive ? 'text-[#10283A]' : 'text-[#8A9BA8] group-hover:text-white'
              }`} 
            />
            <span className="truncate leading-tight">{item.name}</span>
            <ChevronRight 
              className={`w-3.5 h-3.5 ml-auto shrink-0 transition-opacity ${
                isActive ? 'opacity-30 text-[#10283A]' : 'opacity-0 group-hover:opacity-40 text-white'
              }`} 
            />
          </>
        )}
      </NavLink>
    );
  };

  return (
    <aside className="w-[230px] bg-[#10283A] border-r border-[#18374D] text-[#D9DEE3] flex flex-col justify-between shrink-0 h-screen sticky top-0 font-sans z-30 select-none relative overflow-hidden">

      {/* ── Background Industrial Refinery Image (from PDF Pages 3-8) ── */}
      <div 
        className="absolute inset-x-0 bottom-0 pointer-events-none z-0 h-80 bg-cover bg-bottom bg-no-repeat opacity-35 mix-blend-screen"
        style={{
          backgroundImage: 'url(/images/refinery_nav.jpg)',
          maskImage: 'linear-gradient(to top, rgba(0,0,0,1) 0%, rgba(0,0,0,0.5) 60%, rgba(0,0,0,0) 100%)',
          WebkitMaskImage: 'linear-gradient(to top, rgba(0,0,0,1) 0%, rgba(0,0,0,0.5) 60%, rgba(0,0,0,0) 100%)'
        }}
      />

      {/* ── Top Brand Header (from PDF) ── */}
      <div className="relative z-10">
        <div className="px-4 pt-5 pb-4 border-b border-[#18374D]/80">
          <div className="flex items-center gap-3">
            {/* Square Logo Badge */}
            <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center p-1 shrink-0 shadow-sm aspect-square overflow-hidden">
              <img 
                src="/images/petrobid_emblem_square.png" 
                alt="PetroBid" 
                className="w-full h-full object-contain"
              />
            </div>
            
            <div className="min-w-0">
              <div className="font-serif font-bold text-base tracking-tight text-white leading-tight">
                PetroBid
              </div>
              <div className="text-[10px] text-[#8A9BA8] tracking-normal mt-0.5 leading-none">
                Compliance &amp; Procurement
              </div>
            </div>
          </div>
        </div>

        {/* ── Module Navigation (Role-based) ── */}
        <nav className="py-3 space-y-1 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 160px)' }}>
          {navigationItems.map((item) => (
            <NavItem key={item.path} item={item} />
          ))}
        </nav>
      </div>

      {/* ── Bottom User Profile (from PDF) ── */}
      <div className="relative z-10 border-t border-[#18374D] bg-[#0C1E2B]/90 backdrop-blur-sm p-3">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2.5 min-w-0">
            {/* Circle Avatar with Initials */}
            <div className="w-8 h-8 rounded-full bg-white text-[#10283A] font-bold text-xs flex items-center justify-center shrink-0 shadow-sm">
              {initials}
            </div>
            <div className="min-w-0">
              <div className="text-xs font-semibold text-white truncate leading-tight">
                {userName}
              </div>
              <div className="text-[10px] text-[#8A9BA8] truncate leading-tight mt-0.5">
                {userRoleTitle}
              </div>
            </div>
          </div>

          <button
            onClick={handleLogout}
            title="Sign Out"
            className="p-1.5 hover:bg-[#18374D] text-[#8A9BA8] hover:text-[#C83B32] transition-colors rounded shrink-0"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>

    </aside>
  );
};
