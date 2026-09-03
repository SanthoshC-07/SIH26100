import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileSpreadsheet,
  Search,
  Filter,
  Download,
  RefreshCw,
  Plus,
  Clock,
  AlertTriangle,
  CheckCircle2,
  FileCheck,
  ArrowRight,
  ShieldCheck,
  ChevronRight
} from 'lucide-react';
import { bidderService, tenderService } from '../services';
import { Bidder, Tender } from '../types';
import { RiskBadge } from '../components/RiskBadge';

export const BiddersPage: React.FC = () => {
  const navigate = useNavigate();
  const [bidders, setBidders] = useState<Bidder[]>([]);
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [priorityFilter, setPriorityFilter] = useState('ALL');

  const loadData = () => {
    setLoading(true);
    Promise.all([
      bidderService.getBidders().catch(() => []),
      tenderService.getTenders().catch(() => [])
    ]).then(([b, t]) => {
      setBidders(b);
      setTenders(t);
    }).finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredBidders = bidders.filter(b => {
    const matchSearch = b.legal_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (b.pan && b.pan.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (b.gstin && b.gstin.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchStatus = statusFilter === 'ALL' || b.status === statusFilter;
    const matchPriority = priorityFilter === 'ALL' || b.risk_level === priorityFilter;
    return matchSearch && matchStatus && matchPriority;
  });

  return (
    <div className="space-y-6">
      
      {/* 1. Header & Actions (Matching Page 4 from PDF) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">
            Bid Management
          </h1>
          <p className="text-xs text-slate-500">
            Oversee and audit active procurement bids across petroleum and pipeline departments.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={loadData}
            className="px-3 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-2xs"
          >
            <RefreshCw className="w-3.5 h-3.5 text-slate-500" /> Refresh List
          </button>
          <button className="px-3 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-2xs">
            <Download className="w-3.5 h-3.5 text-slate-500" /> Export CSV
          </button>
          <button
            onClick={() => navigate('/tenders')}
            className="px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold flex items-center gap-1.5 shadow-sm"
          >
            <Plus className="w-4 h-4" /> Create New RFP / Tender
          </button>
        </div>
      </div>

      {/* 2. Top 4 Stat Cards (Matching Page 4 from PDF) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-4 space-y-1.5">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Total Bids</span>
            <FileSpreadsheet className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900">{bidders.length || 7}</div>
          <div className="text-[11px] text-emerald-600 font-medium">+12% from last month</div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-4 space-y-1.5">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Awaiting Review</span>
            <Clock className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900">4</div>
          <div className="text-[11px] text-slate-500 font-mono">Avg. wait: 4.2 days</div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-4 space-y-1.5">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Compliance Flags</span>
            <AlertTriangle className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900">2</div>
          <div className="text-[11px] text-rose-600 font-medium">Critical issues detected</div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-4 space-y-1.5">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Verified This Week</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900">5</div>
          <div className="text-[11px] text-slate-500 font-mono">Target: 20/week</div>
        </div>
      </div>

      {/* 3. Search and Filters Bar */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-card p-4 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by vendor, project name, or bid ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:outline-none focus:border-blue-500 focus:bg-white"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <div className="flex items-center gap-1.5 text-slate-500">
            <span>Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg font-semibold text-slate-800 outline-none"
            >
              <option value="ALL">All Statuses</option>
              <option value="SUBMITTED">Submitted</option>
              <option value="UNDER_EVALUATION">Under Evaluation</option>
              <option value="VERIFIED">Verified</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5 text-slate-500">
            <span>Priority:</span>
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg font-semibold text-slate-800 outline-none"
            >
              <option value="ALL">All Priorities</option>
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
            </select>
          </div>

          <button
            onClick={() => { setSearchQuery(''); setStatusFilter('ALL'); setPriorityFilter('ALL'); }}
            className="px-3 py-1.5 text-slate-500 hover:text-slate-800 font-semibold"
          >
            Reset Filters
          </button>
        </div>
      </div>

      {/* 4. Active Bid Ledger Table (Matching Page 4 from PDF) */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-card overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50/50 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 font-bold text-slate-900">
            <FileCheck className="w-4 h-4 text-blue-600" />
            <span>Active Bid Ledger</span>
            <span className="text-slate-400 font-normal font-mono">({filteredBidders.length} Records Found)</span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-500 font-semibold uppercase text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-5">Bid Ref</th>
                <th className="py-3 px-5">Vendor & Project</th>
                <th className="py-3 px-5">Submission</th>
                <th className="py-3 px-5">Estimated Value</th>
                <th className="py-3 px-5 text-center">Score</th>
                <th className="py-3 px-5 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 text-slate-700">
              {filteredBidders.map((b, idx) => {
                const score = b.compliance_score !== null && b.compliance_score !== undefined ? b.compliance_score : 90;
                return (
                  <tr
                    key={b.id}
                    onClick={() => navigate(`/bidders/${b.id}`)}
                    className="hover:bg-slate-50 cursor-pointer transition-colors"
                  >
                    <td className="py-3.5 px-5 font-mono text-[11px] font-bold text-slate-900">
                      RFQ-GAIL-0{idx + 1}
                    </td>
                    <td className="py-3.5 px-5">
                      <div className="font-bold text-slate-900">{b.legal_name}</div>
                      <div className="text-[10px] text-slate-500">120 KM Natural Gas Pipeline EPC Package</div>
                    </td>
                    <td className="py-3.5 px-5 font-mono text-[11px] text-slate-500">
                      2026-09-03
                    </td>
                    <td className="py-3.5 px-5 font-mono font-bold text-slate-800">
                      ₹150,00,00,000.00
                    </td>
                    <td className="py-3.5 px-5 text-center font-mono font-bold text-blue-700">
                      AI SCORE {score}%
                    </td>
                    <td className="py-3.5 px-5 text-right">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        <CheckCircle2 className="w-3 h-3" />
                        Verified
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="p-4 border-t border-slate-200 bg-slate-50/50 flex items-center justify-between text-xs text-slate-500">
          <span>Showing {filteredBidders.length} of {bidders.length} procurement records</span>
          <div className="flex items-center gap-1.5 font-mono">
            <button className="px-2 py-1 border border-slate-200 rounded bg-white" disabled>Previous</button>
            <span className="px-2 py-1 bg-blue-600 text-white rounded font-bold">1</span>
            <button className="px-2 py-1 border border-slate-200 rounded bg-white">Next</button>
          </div>
        </div>
      </div>

      {/* 5. Bottom Two Cards: Audit Intelligence & Compliance Deadlines (Matching Page 4 from PDF) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Left: Audit Intelligence Card */}
        <div className="bg-[#0B132B] text-white rounded-xl p-6 shadow-md flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-blue-400 font-bold text-sm">
              <ShieldCheck className="w-5 h-5" />
              <span>Audit Intelligence</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              BidVerify AI has detected high-risk pattern anomalies in newly submitted bidder dossiers. Immediate human compliance review is recommended before final award.
            </p>
          </div>

          <button
            onClick={() => navigate('/verification')}
            className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold transition-all flex items-center justify-between"
          >
            <span>Review Priority Queue</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        {/* Right: Compliance Deadlines */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900">Compliance Deadlines</h2>
            <span className="text-[11px] text-slate-500">Bids requiring verification within 48h</span>
          </div>

          <div className="space-y-3">
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg flex items-center justify-between text-xs">
              <div>
                <div className="font-bold text-slate-900 font-mono">RFQ-GAIL-01</div>
                <div className="text-[10px] text-slate-500">Praveen B S Engineering Services</div>
              </div>
              <div className="text-right">
                <span className="text-[11px] font-bold text-amber-600 flex items-center gap-1 font-mono">
                  <Clock className="w-3.5 h-3.5" /> 14h remaining
                </span>
                <span className="text-[9px] uppercase font-bold text-rose-600">HIGH PRIORITY</span>
              </div>
            </div>

            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg flex items-center justify-between text-xs">
              <div>
                <div className="font-bold text-slate-900 font-mono">RFQ-IOCL-02</div>
                <div className="text-[10px] text-slate-500">Larsen & Toubro Hydrocarbon</div>
              </div>
              <div className="text-right">
                <span className="text-[11px] font-bold text-slate-600 flex items-center gap-1 font-mono">
                  <Clock className="w-3.5 h-3.5" /> 22h remaining
                </span>
                <span className="text-[9px] uppercase font-bold text-emerald-600">MEDIUM PRIORITY</span>
              </div>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};
