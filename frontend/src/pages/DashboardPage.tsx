import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  Clock,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  FileText,
  ArrowUpRight,
  Filter,
  Download,
  Search,
  ExternalLink,
  ChevronRight,
  Sparkles
} from 'lucide-react';
import { analyticsService, bidderService } from '../services';
import { DashboardStats, Bidder } from '../types';
import { RiskBadge } from '../components/RiskBadge';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [bidders, setBidders] = useState<Bidder[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    Promise.all([
      analyticsService.getDashboardStats().catch(() => null),
      bidderService.getBidders().catch(() => [])
    ]).then(([st, b]) => {
      if (st) setStats(st);
      setBidders(b);
    }).finally(() => setLoading(false));
  }, []);

  const filteredBidders = bidders.filter(b => 
    b.legal_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (b.pan && b.pan.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (b.gstin && b.gstin.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      
      {/* 1. Hero Welcome Card (Matching Page 3 from PDF) */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-card p-6 flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
        <div className="space-y-3 z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 bg-blue-50 text-blue-700 rounded-md text-[11px] font-bold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            Platform Overview • Petroleum Pipeline Cell
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Welcome back, Alex Rivera
          </h1>
          <p className="text-xs text-slate-600 leading-relaxed">
            Verification engine is operating at full capacity. You have <strong className="text-slate-900 font-bold">{stats?.pending_reviews || 4} pending bids</strong> requiring compliance clearance today across MoPNG pipeline procurement tenders.
          </p>
          
          <div className="flex flex-wrap items-center gap-3 pt-1">
            <button
              onClick={() => navigate('/verification')}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold transition-all shadow-sm flex items-center gap-2"
            >
              <AlertTriangle className="w-4 h-4" />
              Review High Risk Flags
            </button>
            <button
              onClick={() => navigate('/reports')}
              className="px-4 py-2 bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 rounded-lg text-xs font-semibold transition-all flex items-center gap-2"
            >
              <FileText className="w-4 h-4 text-slate-500" />
              Upload Audit Report
            </button>
          </div>
        </div>

        {/* Right Abstract Visual Decoration */}
        <div className="hidden lg:block w-72 h-36 rounded-lg bg-gradient-to-br from-slate-900 to-blue-950 p-4 text-white relative shadow-md">
          <div className="text-[10px] uppercase font-mono text-blue-300 font-bold">Live Model Telemetry</div>
          <div className="text-xl font-bold font-mono mt-2">7 Core Checkers</div>
          <div className="text-[11px] text-slate-300 mt-1">Rule Engine + Tesseract OCR Active</div>
          <div className="mt-4 flex items-center justify-between text-[10px] font-mono text-slate-400 border-t border-white/10 pt-2">
            <span>Accuracy: 99.4%</span>
            <span className="text-emerald-400 font-bold">FIPS-Ready</span>
          </div>
        </div>
      </div>

      {/* 2. Top 4 Stat KPI Cards (Matching Page 3 from PDF) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Card 1: Average Compliance Score */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-5 space-y-3">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Average Compliance Score</span>
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold tracking-tight text-slate-900">
            {stats ? `${stats.average_compliance_score.toFixed(1)}%` : '94.2%'}
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-emerald-600 font-medium">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>+2.4% Across all active bids</span>
          </div>
        </div>

        {/* Card 2: Pending Verifications */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-5 space-y-3">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Pending Verifications</span>
            <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold tracking-tight text-slate-900">
            {stats ? stats.pending_reviews : '28'}
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-amber-600 font-medium">
            <span>Requires auditor review</span>
          </div>
        </div>

        {/* Card 3: High Risk Flags */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-5 space-y-3">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">High Risk Flags</span>
            <div className="w-8 h-8 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold tracking-tight text-slate-900">
            {stats ? stats.high_risk_bidders : '3'}
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-rose-600 font-medium">
            <span>Immediate action required</span>
          </div>
        </div>

        {/* Card 4: Verified This Month */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-5 space-y-3">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">Verified This Month</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold tracking-tight text-slate-900">
            {stats ? stats.total_bidders : '142'}
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-emerald-600 font-medium">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>+12% Finalized procurement checks</span>
          </div>
        </div>

      </div>

      {/* 3. Charts Section (Matching Page 3 from PDF) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Compliance Integrity Trend (2 cols) */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-blue-600" />
                Compliance Integrity Trend
              </h2>
              <p className="text-xs text-slate-500">
                Monthly aggregate compliance scores vs. federal benchmark.
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs font-medium">
              <span className="flex items-center gap-1.5 text-slate-700">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-600"></span> Actual Compliance
              </span>
              <span className="flex items-center gap-1.5 text-slate-400">
                <span className="w-2.5 h-0.5 bg-slate-400"></span> Benchmark
              </span>
            </div>
          </div>

          {/* SVG Trend Graph */}
          <div className="h-48 w-full pt-4">
            <svg className="w-full h-full" viewBox="0 0 500 150" preserveAspectRatio="none">
              <defs>
                <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#2563EB" stopOpacity="0.25" />
                  <stop offset="100%" stopColor="#2563EB" stopOpacity="0.0" />
                </linearGradient>
              </defs>
              <line x1="0" y1="120" x2="500" y2="120" stroke="#F1F5F9" strokeWidth="1" />
              <line x1="0" y1="80" x2="500" y2="80" stroke="#F1F5F9" strokeWidth="1" />
              <line x1="0" y1="40" x2="500" y2="40" stroke="#F1F5F9" strokeWidth="1" />
              <line x1="0" y1="75" x2="500" y2="75" stroke="#94A3B8" strokeWidth="1.5" strokeDasharray="4 4" />
              <path d="M 0,90 Q 80,105 160,85 T 320,60 T 500,45 L 500,150 L 0,150 Z" fill="url(#grad)" />
              <path d="M 0,90 Q 80,105 160,85 T 320,60 T 500,45" fill="none" stroke="#2563EB" strokeWidth="2.5" />
            </svg>
            <div className="flex justify-between text-[11px] font-mono text-slate-400 mt-2 px-1">
              <span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span><span>May</span><span>Jun</span>
            </div>
          </div>
        </div>

        {/* Risk Distribution Doughnut (1 col) */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-6 space-y-4 flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Risk Distribution</h2>
            <p className="text-xs text-slate-500">Breakdown of current pipeline by risk category</p>
          </div>

          <div className="flex items-center justify-center my-2">
            <div className="relative w-36 h-36 flex items-center justify-center">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#E2E8F0" strokeWidth="3.5" />
                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#10B981" strokeWidth="3.5" strokeDasharray="65 35" strokeDashoffset="0" />
                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#F59E0B" strokeWidth="3.5" strokeDasharray="20 80" strokeDashoffset="-65" />
                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#EF4444" strokeWidth="3.5" strokeDasharray="10 90" strokeDashoffset="-85" />
                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#881337" strokeWidth="3.5" strokeDasharray="5 95" strokeDashoffset="-95" />
              </svg>
              <div className="absolute text-center">
                <div className="text-xl font-bold text-slate-900">100%</div>
                <div className="text-[10px] text-slate-400 uppercase font-mono font-medium">Bids</div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
              <span className="text-slate-600">Low Risk <strong className="text-slate-900">65%</strong></span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
              <span className="text-slate-600">Medium <strong className="text-slate-900">20%</strong></span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
              <span className="text-slate-600">High Risk <strong className="text-slate-900">10%</strong></span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-900"></span>
              <span className="text-slate-600">Critical <strong className="text-slate-900">5%</strong></span>
            </div>
          </div>
        </div>

      </div>

      {/* 4. Recent Bids Activity Table (Matching Page 3 from PDF) */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-card overflow-hidden">
        
        {/* Table Header Bar */}
        <div className="p-5 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Recent Bids Activity</h2>
            <p className="text-xs text-slate-500">Detailed overview of latest procurement submissions and status</p>
          </div>

          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Filter by ID or entity..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500 w-48 sm:w-60"
              />
            </div>
            <button className="px-3 py-1.5 border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1.5">
              <Filter className="w-3.5 h-3.5" /> Filter
            </button>
            <button className="px-3 py-1.5 border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1.5">
              <Download className="w-3.5 h-3.5" /> Export
            </button>
          </div>
        </div>

        {/* Table Body */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-5">Bid ID</th>
                <th className="py-3 px-5">Submitting Entity</th>
                <th className="py-3 px-5">Procurement Type</th>
                <th className="py-3 px-5">Submission Date</th>
                <th className="py-3 px-5 text-center">Compliance Score</th>
                <th className="py-3 px-5 text-center">Risk Level</th>
                <th className="py-3 px-5 text-center">Current Status</th>
                <th className="py-3 px-5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 text-slate-700">
              {filteredBidders.map((b, idx) => {
                const score = b.compliance_score !== null && b.compliance_score !== undefined ? b.compliance_score : 88;
                const scoreColor = score >= 80 ? 'text-emerald-600 bg-emerald-50 border-emerald-200' : score >= 60 ? 'text-amber-600 bg-amber-50 border-amber-200' : 'text-rose-600 bg-rose-50 border-rose-200';

                return (
                  <tr key={b.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-5 font-mono text-[11px] font-bold text-slate-900">
                      BID-2026-00{idx + 1}
                    </td>
                    <td className="py-3.5 px-5">
                      <div className="font-bold text-slate-900">{b.legal_name}</div>
                      <div className="text-[10px] text-blue-600 font-medium">Certified Vendor • {b.pan || 'BSZPP1234K'}</div>
                    </td>
                    <td className="py-3.5 px-5 text-slate-600 font-medium">
                      Natural Gas Pipeline EPC
                    </td>
                    <td className="py-3.5 px-5 font-mono text-[11px] text-slate-500">
                      2026-09-03
                    </td>
                    <td className="py-3.5 px-5 text-center">
                      <span className={`inline-flex items-center justify-center px-2.5 py-1 rounded-full text-[11px] font-bold border font-mono ${scoreColor}`}>
                        {score}%
                      </span>
                    </td>
                    <td className="py-3.5 px-5 text-center">
                      <RiskBadge level={b.risk_level || 'LOW'} size="sm" />
                    </td>
                    <td className="py-3.5 px-5 text-center">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        ● Verified
                      </span>
                    </td>
                    <td className="py-3.5 px-5 text-right">
                      <button
                        onClick={() => navigate(`/bidders/${b.id}`)}
                        className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1 ml-auto"
                      >
                        View Details <ArrowUpRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Table Pagination / Footer */}
        <div className="p-4 border-t border-slate-200 bg-slate-50/50 flex items-center justify-between text-xs text-slate-500">
          <span>Showing {filteredBidders.length} procurement submissions</span>
          <div className="flex items-center gap-2">
            <button className="px-2.5 py-1 border border-slate-200 rounded bg-white text-slate-600 hover:bg-slate-50 disabled:opacity-50" disabled>
              Previous
            </button>
            <button className="px-2.5 py-1 border border-slate-200 rounded bg-white text-slate-600 hover:bg-slate-50">
              Next
            </button>
          </div>
        </div>

      </div>

    </div>
  );
};
