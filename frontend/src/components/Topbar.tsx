import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { Search, Shield, ChevronRight, UserCheck, Sliders, FileSpreadsheet, CheckCircle2 } from 'lucide-react';

export type UserRole = 'PROCUREMENT_OFFICER' | 'ADMIN' | 'BIDDER';

export const Topbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchTerm, setSearchTerm] = useState('');
  const [currentRole, setCurrentRole] = useState<UserRole>(() => {
    return (localStorage.getItem('active_role') as UserRole) || 'PROCUREMENT_OFFICER';
  });
  const [showRoleMenu, setShowRoleMenu] = useState(false);

  useEffect(() => {
    localStorage.setItem('active_role', currentRole);
  }, [currentRole]);

  const handleRoleChange = (newRole: UserRole) => {
    setCurrentRole(newRole);
    localStorage.setItem('active_role', newRole);
    
    // Sync local user object
    const userMap = {
      ADMIN: { username: 'admin', name: 'Sunil Verma, Chief Procurement Officer', role: 'ADMIN' },
      PROCUREMENT_OFFICER: { username: 'procurement_officer', name: 'Rajesh Sharma, Senior Procurement Officer', role: 'PROCUREMENT_OFFICER' },
      BIDDER: { username: 'bidder', name: 'Praveen B S, EPC Contractor', role: 'BIDDER' }
    };
    localStorage.setItem('user', JSON.stringify(userMap[newRole]));

    setShowRoleMenu(false);
    if (newRole === 'BIDDER') {
      navigate('/tenders');
    } else if (newRole === 'ADMIN') {
      navigate('/dashboard');
    } else {
      navigate('/dashboard');
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      navigate(`/bidders?search=${encodeURIComponent(searchTerm.trim())}`);
    }
  };

  // Generate breadcrumb items from pathname
  const getBreadcrumbs = () => {
    const path = location.pathname;
    if (path.includes('/dashboard')) return ['Dashboard', 'Overview'];
    if (path.includes('/tenders/create')) return ['Dashboard', 'Tenders', 'Create Tender (Admin Only)'];
    if (path.includes('/apply')) return ['Dashboard', 'Tenders', 'Bidder Application & Required Docs'];
    if (path.includes('/tenders/')) return ['Dashboard', 'Tenders', 'Tender Specification'];
    if (path.includes('/tenders')) return ['Dashboard', 'Live Announced Tenders'];
    if (path.includes('/bidders/')) return ['Dashboard', 'Bidders', 'Compliance Verification & Selecting Authority'];
    if (path.includes('/bidders')) return ['Dashboard', 'Bidders'];
    if (path.includes('/compliance-review')) return ['Dashboard', 'Compliance Review & Selecting Authority'];
    if (path.includes('/evidence-center') || path.includes('/documents')) return ['Dashboard', 'Evidence Center'];
    if (path.includes('/review-queue') || path.includes('/reviews')) return ['Dashboard', 'Review Queue (Officer Decision)'];
    if (path.includes('/risk-analysis')) return ['Dashboard', 'Risk Analysis'];
    if (path.includes('/reports')) return ['Dashboard', 'Reports & Dossiers'];
    if (path.includes('/audit-trail') || path.includes('/audit')) return ['Dashboard', 'Audit Trail (GFR 2017)'];
    if (path.includes('/engine-rules')) return ['Dashboard', 'Engine Rules & Thresholds'];
    if (path.includes('/settings')) return ['Dashboard', 'System Settings'];
    return ['Dashboard', 'PetroBid Verify'];
  };

  const breadcrumbs = getBreadcrumbs();

  const roleDetails = {
    PROCUREMENT_OFFICER: {
      tag: 'PO',
      name: 'Rajesh Sharma',
      title: 'Procurement Officer • Selecting Authority',
      badgeColor: 'bg-[#10283A] text-white border-[#BAC4CE]',
      roleBadge: 'bg-[#EAF5F0] text-[#198754] border-[#8CD9A8]'
    },
    ADMIN: {
      tag: 'ADM',
      name: 'Sunil Verma',
      title: 'System Admin • Creates Tenders',
      badgeColor: 'bg-[#10283A] text-white border-[#BAC4CE]',
      roleBadge: 'bg-[#FEF7EC] text-[#D98A16] border-[#F6D8A8]'
    },
    BIDDER: {
      tag: 'BID',
      name: 'Praveen B S',
      title: 'EPC Bidder • Submits & Uploads Docs',
      badgeColor: 'bg-[#D98A16] text-white border-[#BAC4CE]',
      roleBadge: 'bg-[#EAF5F0] text-[#10283A] border-[#BAC4CE]'
    }
  };

  const activeUser = roleDetails[currentRole];

  return (
    <header className="h-14 bg-[#FFFFFF] border-b border-[#D9DEE3] px-5 py-2.5 flex items-center justify-between sticky top-0 z-20 font-sans">
      
      {/* Left: Breadcrumbs & Tender Context */}
      <div className="flex items-center gap-2 text-xs text-[#66717C] min-w-0">
        {breadcrumbs.map((crumb, idx) => (
          <React.Fragment key={idx}>
            {idx > 0 && <ChevronRight className="w-3.5 h-3.5 text-[#A0AEC0] shrink-0" />}
            <span
              className={
                idx === breadcrumbs.length - 1
                  ? 'font-semibold text-[#17212B] truncate'
                  : 'hover:text-[#10283A] cursor-pointer truncate hidden sm:inline'
              }
            >
              {crumb}
            </span>
          </React.Fragment>
        ))}

        <div className="hidden xl:flex items-center gap-2 ml-4 pl-4 border-l border-[#D9DEE3] text-[11px] font-mono">
          <span className="text-[#66717C]">Tender:</span>
          <Link
            to="/tenders"
            className="font-bold text-[#10283A] hover:underline"
          >
            MOPNG/PIPE/2026/017
          </Link>
          <span className="pill-under-review text-[10px] py-0.5 px-2">
            EVALUATION
          </span>
        </div>
      </div>

      {/* Center & Right: Search, Notification, Profile (Matches PDF Pages 3-8) */}
      <div className="flex items-center gap-3">
        
        {/* Global Search Bar (from PDF: Search records...) */}
        <form onSubmit={handleSearch} className="relative w-48 sm:w-60 md:w-64 hidden sm:block">
          <Search className="w-3.5 h-3.5 text-[#66717C] absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search records..."
            className="w-full pl-8 pr-3 py-1.5 bg-[#FFFFFF] border border-[#D9DEE3] text-xs text-[#17212B] placeholder-[#8C9BA5] focus:outline-none focus:border-[#10283A] rounded font-sans transition-colors"
          />
        </form>

        {/* Profile Dropdown (from PDF: dark circle avatar AR, Name, Role) */}
        <div className="relative">
          <button
            onClick={() => setShowRoleMenu(!showRoleMenu)}
            className="flex items-center gap-2 pl-1.5 pr-2 py-1 rounded hover:bg-[#F4F5F7] border border-transparent hover:border-[#D9DEE3] transition-colors"
          >
            {/* Dark Navy Circle Avatar (from PDF: AR) */}
            <div className="w-7 h-7 rounded-full bg-[#10283A] text-white flex items-center justify-center font-bold text-[11px] shrink-0">
              {activeUser.tag === 'PO' ? 'AR' : activeUser.tag === 'ADM' ? 'SV' : 'PB'}
            </div>
            <div className="hidden sm:block text-left">
              <div className="text-xs font-semibold text-[#10283A] leading-tight">
                {activeUser.tag === 'PO' ? 'Alex Rivera' : activeUser.name}
              </div>
              <div className="text-[10px] text-[#66717C] leading-none mt-0.5">
                {activeUser.tag === 'PO' ? 'Verification Officer' : activeUser.title}
              </div>
            </div>
            <ChevronRight className={`w-3 h-3 text-[#66717C] transition-transform ${showRoleMenu ? 'rotate-90' : ''}`} />
          </button>

          {/* Role Selection Dropdown */}
          {showRoleMenu && (
            <div className="absolute right-0 top-full mt-1.5 w-64 bg-white border border-[#D9DEDA] shadow-modal z-50 p-2 space-y-1 font-mono text-xs">
              <div className="px-2 py-1 text-[10px] text-[#66736D] uppercase font-bold border-b border-[#D9DEDA] pb-1">
                SWITCH ACTIVE USER ROLE
              </div>

              {/* 1. Procurement Officer */}
              <button
                type="button"
                onClick={() => handleRoleChange('PROCUREMENT_OFFICER')}
                className={`w-full text-left p-2 transition-colors flex items-center justify-between ${
                  currentRole === 'PROCUREMENT_OFFICER' ? 'bg-[#EAF5F0] border-l-2 border-l-[#198754]' : 'hover:bg-[#F4F5F7]'
                }`}
              >
                <div>
                  <div className="font-bold text-[#10283A]">Procurement Officer</div>
                  <div className="text-[10px] text-[#66717C] font-sans">Rajesh Sharma • Selecting &amp; Evaluating Authority</div>
                </div>
                {currentRole === 'PROCUREMENT_OFFICER' && <CheckCircle2 className="w-3.5 h-3.5 text-[#198754]" />}
              </button>

              {/* 2. Bidder */}
              <button
                type="button"
                onClick={() => handleRoleChange('BIDDER')}
                className={`w-full text-left p-2 transition-colors flex items-center justify-between ${
                  currentRole === 'BIDDER' ? 'bg-[#FEF7EC] border-l-2 border-l-[#D98A16]' : 'hover:bg-[#F4F5F7]'
                }`}
              >
                <div>
                  <div className="font-bold text-[#10283A]">Bidder / EPC Contractor</div>
                  <div className="text-[10px] text-[#66717C] font-sans">Praveen B S • Live Tenders &amp; Uploads Required Docs</div>
                </div>
                {currentRole === 'BIDDER' && <CheckCircle2 className="w-3.5 h-3.5 text-[#D98A16]" />}
              </button>

              {/* 3. System Admin */}
              <button
                type="button"
                onClick={() => handleRoleChange('ADMIN')}
                className={`w-full text-left p-2 transition-colors flex items-center justify-between ${
                  currentRole === 'ADMIN' ? 'bg-[#EAF5F0] border-l-2 border-l-[#10283A]' : 'hover:bg-[#F4F5F7]'
                }`}
              >
                <div>
                  <div className="font-bold text-[#10283A]">System Admin</div>
                  <div className="text-[10px] text-[#66717C] font-sans">Sunil Verma • Creates Tenders &amp; Manages Rules</div>
                </div>
                {currentRole === 'ADMIN' && <CheckCircle2 className="w-3.5 h-3.5 text-[#10283A]" />}
              </button>
            </div>
          )}
        </div>

      </div>

    </header>
  );
};

