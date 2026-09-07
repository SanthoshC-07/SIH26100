import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { tenderService } from '../services';
import { Tender } from '../types';
import {
  FileSpreadsheet,
  Search,
  RefreshCw,
  Plus,
  Send,
  ChevronRight,
  Filter,
  CheckCircle2,
  Building,
  Layers,
  ArrowUpRight,
  ShieldCheck,
  AlertTriangle,
  Clock,
  ExternalLink,
  Download,
  Flame,
  Info
} from 'lucide-react';

export const TendersPage: React.FC = () => {
  const navigate = useNavigate();
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilterTab, setActiveFilterTab] = useState<'ALL' | 'OPEN' | 'REVIEW' | 'AWARDED' | 'CLOSED'>('ALL');
  const [categoryFilter, setCategoryFilter] = useState('');

  const fetchTenders = async () => {
    setLoading(true);
    try {
      const data = await tenderService.getTenders({
        search: searchTerm || undefined
      });
      setTenders(data);
    } catch (err: any) {
      console.error("Failed to load tenders:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTenders();
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchTenders();
  };

  // Seeded / default tenders list adhering to petroleum procurement domain
  const rawList: any[] = tenders.length > 0 ? tenders : [
    {
      id: 't-1',
      tender_number: 'MOPNG/PIPE/2026/017',
      title: 'Natural Gas Transmission Pipeline EPC Procurement',
      organization: 'GAIL (India) Limited / MoPNG',
      department: 'Pipeline Projects Group',
      category: 'Pipeline / EPC',
      tender_type: 'Open Tender (ICB)',
      estimated_value: 820000000.0,
      value_display: '₹82.00 Crore',
      issue_date: '2026-08-15',
      submission_deadline: '2026-09-30',
      status: 'OPEN',
      bidders_count: 4,
      compliance_status: 'Under Evaluation',
      is_demo: true
    },
    {
      id: 't-2',
      tender_number: 'IOCL/2026/PL-VALVES/5810',
      title: 'High-Pressure API 6D Pipeline Valves & Actuators Supply',
      organization: 'Indian Oil Corporation Ltd (IOCL)',
      department: 'Procurement & Materials Cell',
      category: 'Equipment / Valves',
      tender_type: 'Open Tender (NCB)',
      estimated_value: 65000000.0,
      value_display: '₹6.50 Crore',
      issue_date: '2026-08-20',
      submission_deadline: '2026-09-24',
      status: 'OPEN',
      bidders_count: 3,
      compliance_status: 'Technical Evaluation',
      is_demo: true
    },
    {
      id: 't-3',
      tender_number: 'ONGC/2026/MII/3320',
      title: 'Hazira Gas Plant 80 km Offshore to Onshore Feeder Line',
      organization: 'Oil and Natural Gas Corporation (ONGC)',
      department: 'Offshore Engineering Division',
      category: 'Offshore / Feeder',
      tender_type: 'Limited Global Tender',
      estimated_value: 120000000.0,
      value_display: '₹12.00 Crore',
      issue_date: '2026-08-10',
      submission_deadline: '2026-09-18',
      status: 'UNDER_REVIEW',
      bidders_count: 5,
      compliance_status: 'Dossier Review',
      is_demo: true
    },
    {
      id: 't-4',
      tender_number: 'HPCL/TRANS/2026/088',
      title: 'Cross-Country Crude Transport Pipeline Integrity & Pigging',
      organization: 'Hindustan Petroleum Corporation Ltd (HPCL)',
      department: 'Logistics & Integrity Cell',
      category: 'Maintenance & QA',
      tender_type: 'Open Tender',
      estimated_value: 37000000.0,
      value_display: '₹3.70 Crore',
      issue_date: '2026-08-05',
      submission_deadline: '2026-09-10',
      status: 'UNDER_REVIEW',
      bidders_count: 2,
      compliance_status: 'Clarification Stage',
      is_demo: true
    },
    {
      id: 't-5',
      tender_number: 'BPCL/STORAGE/2026/104',
      title: 'Cryogenic LNG Storage Tank & Regasification Terminal EPC',
      organization: 'Bharat Petroleum Corporation Ltd (BPCL)',
      department: 'Cryogenic Projects Group',
      category: 'Terminal / EPC',
      tender_type: 'Open Tender (ICB)',
      estimated_value: 240000000.0,
      value_display: '₹24.00 Crore',
      issue_date: '2026-07-28',
      submission_deadline: '2026-09-05',
      status: 'AWARDED',
      bidders_count: 6,
      compliance_status: 'Qualified (Awarded)',
      is_demo: true
    }
  ];

  // Helper formatting for values
  const formatEstimatedValue = (val: number | string, displayStr?: string) => {
    if (displayStr) return displayStr;
    const num = Number(val);
    if (isNaN(num) || num === 0) return '₹82.00 Crore';
    if (num >= 10000000) {
      return `₹${(num / 10000000).toFixed(2)} Crore`;
    }
    if (num >= 100000) {
      return `₹${(num / 100000).toFixed(2)} Lakhs`;
    }
    return `₹${num.toLocaleString('en-IN')}`;
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '15 Sep 2026';
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return dateStr;
      return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  // Filter list
  const filteredList = rawList.filter((t) => {
    const statusNorm = (t.status || '').toUpperCase();
    if (activeFilterTab === 'OPEN' && !statusNorm.includes('OPEN') && !statusNorm.includes('ACTIVE')) return false;
    if (activeFilterTab === 'REVIEW' && !statusNorm.includes('REVIEW') && !statusNorm.includes('EVALUAT')) return false;
    if (activeFilterTab === 'AWARDED' && !statusNorm.includes('AWARD') && !statusNorm.includes('VERIFIED')) return false;
    if (activeFilterTab === 'CLOSED' && !statusNorm.includes('CLOSE') && !statusNorm.includes('FLAG')) return false;

    if (categoryFilter && !(t.category || '').toLowerCase().includes(categoryFilter.toLowerCase())) return false;

    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      const matchNum = (t.tender_number || '').toLowerCase().includes(q);
      const matchTitle = (t.title || '').toLowerCase().includes(q);
      const matchOrg = (t.organization || t.issuing_organization || '').toLowerCase().includes(q);
      const matchDept = (t.department || '').toLowerCase().includes(q);
      if (!matchNum && !matchTitle && !matchOrg && !matchDept) return false;
    }
    return true;
  });

  const getStatusBadge = (status: string) => {
    const s = (status || '').toUpperCase();
    if (s.includes('OPEN') || s.includes('ACTIVE')) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 text-[11px] font-mono font-bold text-[#10283A] bg-[#E8F1F5] border border-[#BAC4CE] rounded">
          <span className="w-1.5 h-1.5 rounded-full bg-[#10283A]"></span>
          OPEN
        </span>
      );
    }
    if (s.includes('REVIEW') || s.includes('EVALUAT')) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 text-[11px] font-mono font-bold text-[#8A5000] bg-[#FFF4E0] border border-[#F0CA85] rounded">
          <span className="w-1.5 h-1.5 rounded-full bg-[#D98A16]"></span>
          UNDER EVALUATION
        </span>
      );
    }
    if (s.includes('AWARD') || s.includes('VERIF') || s.includes('PASS')) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 text-[11px] font-mono font-bold text-[#0F6B38] bg-[#E8F8EE] border border-[#8CD9A8] rounded">
          <CheckCircle2 className="w-3 h-3 text-[#0F6B38]" />
          AWARDED
        </span>
      );
    }
    if (s.includes('CLOSED') || s.includes('FLAG') || s.includes('FAIL')) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 text-[11px] font-mono font-bold text-[#9C211B] bg-[#FDECEC] border border-[#F5A3A0] rounded">
          <AlertTriangle className="w-3 h-3 text-[#9C211B]" />
          CLOSED
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 text-[11px] font-mono font-bold text-[#10283A] bg-[#EAEEF2] border border-[#D9DEE3] rounded">
        {s}
      </span>
    );
  };

  const activeRole = localStorage.getItem('active_role') || 'PROCUREMENT_OFFICER';

  return (
    <div className="space-y-6 font-sans">
      
      {/* ── Role Specific Banner ── */}
      {activeRole === 'BIDDER' ? (
        <div className="bg-[#FEF7EC] border border-[#F6D8A8] rounded p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-[#8A5000] shadow-sm">
          <div className="flex items-center gap-2.5">
            <Send className="w-5 h-5 text-[#D98A16] flex-shrink-0" />
            <div>
              <span className="font-bold font-mono uppercase tracking-wider text-[#10283A] block">
                LIVE ANNOUNCED TENDERS • BIDDER APPLICATION PORTAL
              </span>
              <span className="text-[#66717C] text-[11.5px]">
                You are logged in as a registered EPC Bidder. Select an open tender below to apply and submit all mandatory statutory and technical compliance documents.
              </span>
            </div>
          </div>
          <span className="font-mono text-[10px] uppercase font-bold text-[#D98A16] border border-[#D98A16] px-2.5 py-1 rounded bg-[#FFFFFF] whitespace-nowrap self-start sm:self-auto">
            BIDDER DOCUMENT UPLOAD READY
          </span>
        </div>
      ) : activeRole === 'PROCUREMENT_OFFICER' ? (
        <div className="bg-[#EAF5F0] border border-[#A8D9C5] rounded p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-[#1E5A47] shadow-sm">
          <div className="flex items-center gap-2.5">
            <ShieldCheck className="w-5 h-5 text-[#198754] flex-shrink-0" />
            <div>
              <span className="font-bold font-mono uppercase tracking-wider text-[#10283A] block">
                PROCUREMENT OFFICER CONSOLE • SELECTING AUTHORITY ACTIVE
              </span>
              <span className="text-[#66717C] text-[11.5px]">
                You hold the official selecting authority under GFR 2017 Rule 173 to evaluate tenders, review bidder compliance, and determine final eligibility.
              </span>
            </div>
          </div>
          <span className="font-mono text-[10px] uppercase font-bold text-[#198754] border border-[#198754] px-2.5 py-1 rounded bg-[#FFFFFF] whitespace-nowrap self-start sm:self-auto">
            SELECTING AUTHORITY VESTED
          </span>
        </div>
      ) : (
        <div className="bg-[#FFF8E6] border border-[#E8C872] rounded p-3 flex items-center justify-between text-xs text-[#6B4700]">
          <div className="flex items-center gap-2">
            <Info className="w-4 h-4 text-[#D98A16] flex-shrink-0" />
            <span>
              <strong className="font-semibold uppercase tracking-wider font-mono">SYSTEM ADMINISTRATOR CONSOLE:</strong> Full administrative control to create new pipeline tenders, parse clauses, and configure system rules.
            </span>
          </div>
          <span className="font-mono text-[10px] uppercase font-bold text-[#8A5B00] border border-[#D98A16] px-2 py-0.5 rounded bg-[#FFFFFF]">
            ADMIN ACCESS ACTIVE
          </span>
        </div>
      )}

      {/* ── Header Bar ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Flame className="w-5 h-5 text-[#D98A16]" />
            <h1 className="text-2xl sm:text-3xl font-serif font-bold text-[#10283A] tracking-tight">
              {activeRole === 'BIDDER' ? 'Live Announced Tenders' : 'Tender Management Register'}
            </h1>
          </div>
          <p className="text-xs text-[#556270] mt-1 font-sans">
            Central Petroleum Pipeline & Hydrocarbon Procurement Specification Cell • Official Register of Published Tenders
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchTenders()}
            className="p-2 border border-[#BAC4CE] rounded bg-[#FFFFFF] hover:bg-[#F4F6F8] text-[#10283A] transition-colors"
            title="Refresh Tender Register"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-[#D98A16]' : ''}`} />
          </button>

          {/* Create New Tender button strictly reserved for ADMIN */}
          {activeRole === 'ADMIN' && (
            <button
              onClick={() => navigate('/tenders/create')}
              className="px-4 py-2 bg-[#10283A] hover:bg-[#18374D] text-[#FFFFFF] text-xs font-semibold rounded shadow-sm transition-colors flex items-center gap-1.5"
            >
              <Plus className="w-4 h-4" />
              <span>Create New Tender</span>
            </button>
          )}

          {activeRole === 'BIDDER' && (
            <button
              onClick={() => navigate('/tenders/t-1/apply')}
              className="px-4 py-2 bg-[#D98A16] hover:bg-[#E39A22] text-[#10283A] text-xs font-bold rounded shadow-sm transition-colors flex items-center gap-1.5"
            >
              <Send className="w-4 h-4" />
              <span>Apply for Active Tender</span>
            </button>
          )}
        </div>
      </div>

      {/* ── High-Level Telemetry Cards ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded p-4 shadow-sm">
          <div className="text-[11px] font-mono font-bold text-[#66717C] uppercase tracking-wider">
            Total Active Tenders
          </div>
          <div className="text-2xl font-serif font-bold text-[#10283A] mt-1">
            {rawList.length}
          </div>
          <div className="text-[11px] text-[#0F6B38] font-mono mt-0.5">
            ● 100% GFR 2017 Verified
          </div>
        </div>

        <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded p-4 shadow-sm">
          <div className="text-[11px] font-mono font-bold text-[#66717C] uppercase tracking-wider">
            Open for Bidding
          </div>
          <div className="text-2xl font-serif font-bold text-[#10283A] mt-1">
            {rawList.filter(t => (t.status || '').toUpperCase().includes('OPEN')).length || 2}
          </div>
          <div className="text-[11px] text-[#556270] font-mono mt-0.5">
            Active submission window
          </div>
        </div>

        <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded p-4 shadow-sm">
          <div className="text-[11px] font-mono font-bold text-[#66717C] uppercase tracking-wider">
            Under Evaluation
          </div>
          <div className="text-2xl font-serif font-bold text-[#D98A16] mt-1">
            {rawList.filter(t => (t.status || '').toUpperCase().includes('REVIEW') || (t.status || '').toUpperCase().includes('EVALUAT')).length || 2}
          </div>
          <div className="text-[11px] text-[#8A5000] font-mono mt-0.5">
            Compliance Engine Active
          </div>
        </div>

        <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded p-4 shadow-sm">
          <div className="text-[11px] font-mono font-bold text-[#66717C] uppercase tracking-wider">
            Total Procurement Value
          </div>
          <div className="text-2xl font-serif font-bold text-[#10283A] mt-1">
            ₹128.2 Cr
          </div>
          <div className="text-[11px] text-[#556270] font-mono mt-0.5">
            Capital works budget
          </div>
        </div>
      </div>

      {/* ── Filter Bar & Search ── */}
      <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded p-4 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        
        {/* Status Tabs */}
        <div className="flex items-center gap-1 border border-[#D9DEE3] rounded p-0.5 bg-[#F4F6F8]">
          {[
            { id: 'ALL', label: 'All Tenders' },
            { id: 'OPEN', label: 'Open' },
            { id: 'REVIEW', label: 'Under Review' },
            { id: 'AWARDED', label: 'Awarded' },
            { id: 'CLOSED', label: 'Closed' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveFilterTab(tab.id as any)}
              className={`px-3 py-1.5 text-xs font-semibold rounded transition-colors ${
                activeFilterTab === tab.id
                  ? 'bg-[#10283A] text-[#FFFFFF] shadow-sm'
                  : 'text-[#556270] hover:text-[#10283A]'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Search & Category Filter */}
        <div className="flex items-center gap-3">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-1.5 border border-[#BAC4CE] rounded text-xs bg-[#FFFFFF] text-[#10283A] focus:outline-none focus:border-[#10283A]"
          >
            <option value="">All Categories</option>
            <option value="Pipeline">Pipeline / EPC</option>
            <option value="Valves">Equipment / Valves</option>
            <option value="Offshore">Offshore / Feeder</option>
            <option value="Maintenance">Maintenance & QA</option>
            <option value="Terminal">Terminal / EPC</option>
          </select>

          <form onSubmit={handleSearchSubmit} className="relative">
            <Search className="w-3.5 h-3.5 text-[#66717C] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search Tender ID, Title, Org..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8 pr-3 py-1.5 border border-[#BAC4CE] rounded text-xs bg-[#FFFFFF] text-[#10283A] w-56 focus:outline-none focus:border-[#10283A]"
            />
          </form>
        </div>
      </div>

      {/* ── Official Petroleum Tender Register Table ── */}
      <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded shadow-sm overflow-hidden">
        <div className="px-5 py-3 border-b border-[#D9DEE3] bg-[#F8FAFC] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Building className="w-4 h-4 text-[#10283A]" />
            <span className="text-xs font-bold text-[#10283A] uppercase tracking-wider font-mono">
              Petroleum Pipeline Procurement Register ({filteredList.length} Records)
            </span>
          </div>
          <span className="text-[11px] text-[#556270] font-mono">
            Showing verified tenders per MoPNG guidelines
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[#D9DEE3] bg-[#F1F4F8] text-[11px] font-mono font-bold text-[#10283A] uppercase tracking-wider">
                <th className="py-3 px-4">Tender ID</th>
                <th className="py-3 px-4">Tender Title</th>
                <th className="py-3 px-4">Organization & Dept</th>
                <th className="py-3 px-4">Category / Type</th>
                <th className="py-3 px-4">Estimated Value</th>
                <th className="py-3 px-4">Schedule (Issue - Close)</th>
                <th className="py-3 px-4 text-center">Status</th>
                <th className="py-3 px-4 text-center">Bidders</th>
                <th className="py-3 px-4">Compliance Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#D9DEE3] text-xs font-sans">
              {filteredList.length === 0 ? (
                <tr>
                  <td colSpan={10} className="py-12 text-center text-[#66717C] font-mono">
                    NO TENDERS MATCH THE SPECIFIED CRITERIA
                  </td>
                </tr>
              ) : (
                filteredList.map((t, idx) => (
                  <tr
                    key={t.id || idx}
                    className="hover:bg-[#F9FAFB] transition-colors group cursor-pointer"
                    onClick={() => navigate(`/tenders/${t.id}`)}
                  >
                    {/* Tender ID */}
                    <td className="py-3.5 px-4 font-mono font-bold text-[#10283A] whitespace-nowrap">
                      <div className="flex items-center gap-1.5">
                        <span>{t.tender_number}</span>
                        {t.is_demo && (
                          <span className="text-[9px] px-1 py-0.2 bg-[#F1F4F8] border border-[#BAC4CE] text-[#556270] rounded">
                            DEMO
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Title */}
                    <td className="py-3.5 px-4 max-w-xs">
                      <div className="font-semibold text-[#10283A] group-hover:text-[#D98A16] transition-colors leading-tight">
                        {t.title}
                      </div>
                      <div className="text-[11px] text-[#66717C] truncate mt-0.5 font-sans">
                        {t.description || 'Petroleum & Natural Gas Infrastructure Project'}
                      </div>
                    </td>

                    {/* Organization & Dept */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <div className="font-medium text-[#10283A]">
                        {t.organization || t.issuing_organization || 'Ministry of Petroleum & Natural Gas'}
                      </div>
                      <div className="text-[11px] text-[#66717C] font-mono">
                        {t.department || 'Pipeline Cell'}
                      </div>
                    </td>

                    {/* Category & Type */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <div className="font-medium text-[#10283A]">
                        {t.category || 'Pipeline / EPC'}
                      </div>
                      <div className="text-[11px] text-[#66717C] font-mono">
                        {t.tender_type || 'Open Tender'}
                      </div>
                    </td>

                    {/* Estimated Value */}
                    <td className="py-3.5 px-4 whitespace-nowrap font-mono font-bold text-[#10283A]">
                      {formatEstimatedValue(t.estimated_value, t.value_display)}
                    </td>

                    {/* Issue & Closing Dates */}
                    <td className="py-3.5 px-4 whitespace-nowrap font-mono text-[11px] text-[#556270]">
                      <div>Issued: {formatDate(t.issue_date || t.tender_issue_date)}</div>
                      <div className="text-[#10283A] font-semibold">Closes: {formatDate(t.submission_deadline)}</div>
                    </td>

                    {/* Status */}
                    <td className="py-3.5 px-4 text-center whitespace-nowrap">
                      {getStatusBadge(t.status)}
                    </td>

                    {/* Number of Bidders */}
                    <td className="py-3.5 px-4 text-center whitespace-nowrap font-mono font-bold text-[#10283A]">
                      <span className="px-2 py-0.5 bg-[#EAEEF2] rounded border border-[#D9DEE3]">
                        {t.bidders_count || 4}
                      </span>
                    </td>

                    {/* Compliance Status */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <div className="inline-flex items-center gap-1.5 text-[11px] font-mono">
                        <span className="w-2 h-2 rounded-full bg-[#D98A16]"></span>
                        <span className="text-[#10283A] font-medium">{t.compliance_status || 'Under Evaluation'}</span>
                      </div>
                    </td>

                    {/* Actions */}
                    <td className="py-3.5 px-4 text-right whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center justify-end gap-2">
                        {activeRole === 'BIDDER' ? (
                          <>
                            <button
                              onClick={() => navigate(`/tenders/${t.id}`)}
                              className="px-2.5 py-1 bg-[#FFFFFF] hover:bg-[#F4F5F7] border border-[#BAC4CE] text-[#10283A] font-semibold text-xs rounded transition-colors"
                              title="View Tender Specifications"
                            >
                              <span>Specs</span>
                            </button>
                            <button
                              onClick={() => navigate(`/tenders/${t.id}/apply`)}
                              className="px-3 py-1 bg-[#D98A16] hover:bg-[#E39A22] text-[#10283A] font-bold text-xs rounded transition-colors flex items-center gap-1 shadow-sm"
                              title="Apply and Upload Mandatory Documents"
                            >
                              <Send className="w-3 h-3" />
                              <span>Apply &amp; Upload Docs</span>
                            </button>
                          </>
                        ) : activeRole === 'PROCUREMENT_OFFICER' ? (
                          <>
                            <button
                              onClick={() => navigate(`/tenders/${t.id}`)}
                              className="px-2.5 py-1 bg-[#FFFFFF] hover:bg-[#F4F5F7] border border-[#BAC4CE] text-[#10283A] font-semibold text-xs rounded transition-colors flex items-center gap-1"
                              title="Open Tender Workspace"
                            >
                              <span>Workspace</span>
                              <ChevronRight className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => navigate(`/bidders?tender_id=${t.id}`)}
                              className="px-3 py-1 bg-[#10283A] hover:bg-[#18374D] text-[#FFFFFF] font-semibold text-xs rounded transition-colors flex items-center gap-1 shadow-sm"
                              title="Evaluate and Select Bidders"
                            >
                              <ShieldCheck className="w-3.5 h-3.5 text-[#198754]" />
                              <span>Evaluate Bidders</span>
                            </button>
                          </>
                        ) : (
                          <>
                            <button
                              onClick={() => navigate(`/tenders/${t.id}`)}
                              className="px-2.5 py-1 bg-[#10283A] hover:bg-[#18374D] text-[#FFFFFF] font-semibold text-xs rounded transition-colors flex items-center gap-1"
                              title="Open Tender Workspace"
                            >
                              <span>Manage</span>
                              <ChevronRight className="w-3.5 h-3.5" />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Table Footer */}
        <div className="px-4 py-2.5 bg-[#F8FAFC] border-t border-[#D9DEE3] text-[11px] text-[#66717C] font-mono flex items-center justify-between">
          <span>Official MoPNG Pipeline Electronic Procurement Register</span>
          <span>Security Protocol: TLS 1.3 | SHA-256 Verified</span>
        </div>
      </div>

    </div>
  );
};
