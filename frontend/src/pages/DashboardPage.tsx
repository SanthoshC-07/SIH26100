import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import {
  FileSpreadsheet, Users, AlertTriangle, ShieldCheck,
  CheckCircle2, XCircle, ArrowRight, Sparkles, Filter, ExternalLink, RefreshCw,
  Flame, Gauge, HardHat, FileText, CheckCheck, Award
} from 'lucide-react';
import { DashboardCard } from '../components/DashboardCard';
import { analyticsService, bidderService } from '../services';
import { DashboardStats, Bidder } from '../types';
import { ComplianceBadge } from '../components/ComplianceBadge';
import { RiskBadge } from '../components/RiskBadge';

const COMPLIANCE_PALETTE = {
  PASS: '#059669',      // Emerald 600
  FAIL: '#DC2626',      // Red 600
  REVIEW: '#D97706',    // Amber 600
  NOT_APPLICABLE: '#64748B' // Slate 500
};

const RISK_PALETTE = {
  LOW: '#059669',
  MEDIUM: '#D97706',
  HIGH: '#DC2626',
  CRITICAL: '#7F1D1D'
};

const SEVEN_CORE_CHECKS = [
  { id: '1', name: 'Check 1: GST Statutory', type: 'Active Status & Return Filing', icon: ShieldCheck, desc: 'GSTIN format, mock portal active status, legal name consistency.' },
  { id: '2', name: 'Check 2: PAN & Identity', type: 'Income Tax Legal Entity', icon: Award, desc: 'PAN entity match against GST/ROC documents and cross-check.' },
  { id: '3', name: 'Check 3: Turnover Arithmetic', type: 'Exact 3-Year Python Avg', icon: Gauge, desc: 'Deterministic calculation: Avg(FY1, FY2, FY3) >= ₹10.00 Cr threshold.' },
  { id: '4', name: 'Check 4: Oil & Gas Experience', type: 'Semantic Sector Relevance', icon: Flame, desc: 'NLP semantic understanding of refinery, hydrocarbon & gas projects.' },
  { id: '5', name: 'Check 5: Similar Pipeline', type: 'Length (km) & Diameter Spec', icon: HardHat, desc: 'FAISS/Semantic retrieval + threshold gating (e.g. >= 100 km length).' },
  { id: '6', name: 'Check 6: Technical Manpower', type: 'Qualified Engineers Count', icon: Users, desc: 'CV extraction and deterministic count: >= 5 engineers with >= 8 yrs exp.' },
  { id: '7', name: 'Check 7: Configurable Check', type: 'HSE / OEM / Local Content', icon: CheckCheck, desc: 'Auto-detected from tender: ISO 45001 safety, line pipe MAF, or MII %.' }
];

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [bidders, setBidders] = useState<Bidder[]>([]);
  const [filterClause, setFilterClause] = useState<string>('ALL');
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [s, b] = await Promise.all([
        analyticsService.getDashboardStats(),
        bidderService.getBidders()
      ]);
      setStats(s);
      setBidders(b);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading || !stats) {
    return (
      <div className="flex items-center justify-center h-72 text-slate-500 font-mono text-xs gap-3">
        <RefreshCw className="w-5 h-5 animate-spin text-emerald-600" />
        <span>COMPUTING REAL-TIME PETROLEUM PIPELINE COMPLIANCE TELEMETRY...</span>
      </div>
    );
  }

  const totalChecks = (stats.compliance_distribution.PASS || 0) +
    (stats.compliance_distribution.FAIL || 0) +
    (stats.compliance_distribution.REVIEW || 0) +
    (stats.compliance_distribution.NOT_APPLICABLE || 0);

  const complianceChartData = [
    { name: 'PASS', value: stats.compliance_distribution.PASS || 0, color: COMPLIANCE_PALETTE.PASS },
    { name: 'FAIL', value: stats.compliance_distribution.FAIL || 0, color: COMPLIANCE_PALETTE.FAIL },
    { name: 'REVIEW', value: stats.compliance_distribution.REVIEW || 0, color: COMPLIANCE_PALETTE.REVIEW },
    { name: 'N/A', value: stats.compliance_distribution.NOT_APPLICABLE || 0, color: COMPLIANCE_PALETTE.NOT_APPLICABLE },
  ];

  const riskChartData = [
    { name: 'LOW', count: stats.risk_distribution.LOW || 0, fill: RISK_PALETTE.LOW },
    { name: 'MEDIUM', count: stats.risk_distribution.MEDIUM || 0, fill: RISK_PALETTE.MEDIUM },
    { name: 'HIGH', count: stats.risk_distribution.HIGH || 0, fill: RISK_PALETTE.HIGH },
    { name: 'CRITICAL', count: stats.risk_distribution.CRITICAL || 0, fill: RISK_PALETTE.CRITICAL },
  ];

  return (
    <div className="space-y-6">
      
      {/* Executive Command Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 text-white rounded-xl p-6 shadow-md border border-slate-700/80 flex flex-col md:flex-row md:items-center justify-between gap-5 relative overflow-hidden">
        <div className="space-y-1.5 relative z-10">
          <div className="flex items-center gap-2 text-[10px] font-mono font-bold text-emerald-400 tracking-widest uppercase">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span>PETROLEUM & NATURAL GAS PROCUREMENT VERIFICATION CELL</span>
            <span>•</span>
            <span className="text-slate-400">TENDER: GAIL/2026/PL-NC/4182</span>
          </div>
          <h1 className="text-xl font-bold tracking-tight text-white font-sans">
            AI-Powered Pipeline Bid Compliance Verification Platform
          </h1>
          <p className="text-xs text-slate-300 font-mono max-w-2xl">
            Decision support for Procurement Officers evaluating cross-country natural gas pipeline tenders across 7 Core Compliance Checks with deterministic arithmetic and hybrid PyMuPDF/Tesseract OCR.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0 relative z-10">
          <button
            onClick={() => navigate('/reviews')}
            className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-mono font-bold shadow-md flex items-center gap-2 transition-all"
          >
            <AlertTriangle className="w-4 h-4 text-amber-200" />
            <span>OFFICER REVIEW QUEUE ({stats.pending_reviews})</span>
          </button>
          <button
            onClick={() => navigate('/bidders')}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-mono font-bold shadow-md flex items-center gap-2 transition-all"
          >
            <span>INSPECT BIDDERS</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* 7 Core Compliance Checks Architecture Banner */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Flame className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
              7 CORE MODULAR PROCUREMENT COMPLIANCE CHECKS (PETROLEUM & NATURAL GAS DOMAIN)
            </span>
          </div>
          <span className="text-[10px] font-mono text-slate-400">
            HYBRID NLP + DETERMINISTIC RULES + EXTENSION STUBS
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7 gap-3">
          {SEVEN_CORE_CHECKS.map((chk) => (
            <div key={chk.id} className="bg-slate-800/80 border border-slate-700/70 rounded-lg p-3 space-y-1.5 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between text-[11px] font-mono font-bold text-emerald-400">
                  <span>{chk.name.split(':')[0]}</span>
                  <chk.icon className="w-3.5 h-3.5 text-slate-400" />
                </div>
                <div className="text-xs font-bold text-slate-100 mt-1">
                  {chk.name.split(':')[1]}
                </div>
                <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                  {chk.type}
                </div>
              </div>
              <p className="text-[10px] text-slate-400 font-sans line-clamp-2 border-t border-slate-700/50 pt-1.5">
                {chk.desc}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <DashboardCard
          title="ACTIVE PIPELINE TENDERS"
          value={stats.total_tenders.toString()}
          subtitle="GAIL / IOCL / ONGC Specifications"
          icon={<FileSpreadsheet className="w-5 h-5" />}
          trend="3 Active"
        />
        <DashboardCard
          title="EVALUATED BIDDERS"
          value={stats.total_bidders.toString()}
          subtitle="Pass / Fail / Review Profiles"
          icon={<Users className="w-5 h-5" />}
          trend="4 Verified"
        />
        <DashboardCard
          title="STATUTORY & CLAUSE CHECKS"
          value={totalChecks.toString()}
          subtitle="Deterministic Rules & NLP"
          icon={<ShieldCheck className="w-5 h-5" />}
          trend={`${stats.compliance_distribution.PASS || 0} Passed`}
        />
        <DashboardCard
          title="OFFICER REVIEWS PENDING"
          value={stats.pending_reviews.toString()}
          subtitle="Ambiguity & GFR Flags"
          icon={<AlertTriangle className="w-5 h-5" />}
          trend="Action Req."
        />
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        
        {/* Compliance Checks Distribution */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
              COMPLIANCE STATUS RATIO
            </span>
            <span className="text-[10px] font-mono text-slate-400">
              TOTAL: {totalChecks} CHECKS
            </span>
          </div>

          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={complianceChartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {complianceChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '11px', fontFamily: 'monospace' }}
                  itemStyle={{ color: '#e2e8f0' }}
                />
                <Legend
                  wrapperStyle={{ fontSize: '10px', fontFamily: 'monospace', paddingTop: '8px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Classification Distribution */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
              BID RISK CLASSIFICATION
            </span>
            <span className="text-[10px] font-mono text-slate-400">
              4 FACTORS EVALUATED
            </span>
          </div>

          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={riskChartData}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={10} fontFamily="monospace" />
                <YAxis stroke="#64748b" fontSize={10} fontFamily="monospace" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '11px', fontFamily: 'monospace' }}
                  itemStyle={{ color: '#e2e8f0' }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {riskChartData.map((entry, index) => (
                    <Cell key={`bar-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Decision Support Intelligence Summary */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3.5 flex flex-col justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
                OFFICER DECISION SUPPORT
              </span>
            </div>
            <p className="text-xs text-slate-300 font-sans leading-relaxed">
              AI evaluates statutory format validity, 3-year turnover arithmetic, and pipeline length criteria. Disqualification remains strictly under the Procurement Officer's authority.
            </p>
          </div>

          <div className="space-y-2 bg-slate-800/80 p-3 rounded-lg border border-slate-700/80 text-[11px] font-mono">
            <div className="flex justify-between">
              <span className="text-slate-400">Primary Tender:</span>
              <span className="text-emerald-400 font-bold">GAIL/2026/PL-NC/4182</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Scope:</span>
              <span className="text-slate-200">150 km 24" API 5L Pipeline</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Est. Value:</span>
              <span className="text-slate-200">₹240.00 Crore</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Legal Audit Standard:</span>
              <span className="text-slate-200 font-bold">Section 4 GFR 2017</span>
            </div>
          </div>

          <button
            onClick={() => navigate('/tenders')}
            className="w-full py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-lg text-xs font-mono font-bold flex items-center justify-center gap-2 transition-all"
          >
            <span>VIEW ALL PIPELINE TENDERS</span>
            <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
          </button>
        </div>

      </div>

      {/* Bidder Compliance Registry Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
        
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div>
            <h2 className="text-sm font-mono font-bold uppercase tracking-wider text-slate-100 flex items-center gap-2">
              <span>PETROLEUM PIPELINE BIDDER COMPLIANCE DOSSIER</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                {bidders.length} ENTITIES EVALUATED
              </span>
            </h2>
            <p className="text-xs text-slate-400 font-sans mt-0.5">
              Click any bidder record to open side-by-side Requirement vs Evidence verification screen.
            </p>
          </div>

          <div className="flex items-center gap-2 font-mono text-xs">
            <span className="text-slate-400 flex items-center gap-1">
              <Filter className="w-3 h-3 text-slate-500" /> Filter:
            </span>
            {['ALL', 'PASS', 'FAIL', 'REVIEW'].map((status) => (
              <button
                key={status}
                onClick={() => setFilterClause(status)}
                className={`px-2.5 py-1 rounded text-[11px] font-mono font-bold transition-all border ${
                  filterClause === status
                    ? 'bg-emerald-600 text-white border-emerald-500 shadow-sm'
                    : 'bg-slate-800 text-slate-400 border-slate-700 hover:bg-slate-700 hover:text-slate-200'
                }`}
              >
                {status}
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-sans">
            <thead>
              <tr className="bg-slate-800/80 text-slate-300 font-mono text-[11px] uppercase tracking-wider border-b border-slate-700">
                <th className="py-2.5 px-3">Bidder Corporate Legal Name</th>
                <th className="py-2.5 px-3">GSTIN / PAN</th>
                <th className="py-2.5 px-3 text-center">Compliance Score</th>
                <th className="py-2.5 px-3 text-center">Risk Level</th>
                <th className="py-2.5 px-3 text-center">Outcome Status</th>
                <th className="py-2.5 px-3">AI Recommendation Summary</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-sans text-slate-200">
              {bidders
                .filter((b) => {
                  const score = b.compliance_score || 0;
                  const risk = b.risk_level || 'MEDIUM';
                  if (filterClause === 'ALL') return true;
                  if (filterClause === 'PASS') return score >= 90;
                  if (filterClause === 'FAIL') return risk === 'HIGH' || risk === 'CRITICAL';
                  if (filterClause === 'REVIEW') return b.status === 'UNDER_REVIEW' || risk === 'MEDIUM';
                  return true;
                })
                .map((b) => {
                  const score = b.compliance_score || 0;
                  const risk = b.risk_level || 'MEDIUM';
                  
                  return (
                    <tr
                      key={b.id}
                      onClick={() => navigate(`/bidders/${b.id}`)}
                      className="hover:bg-slate-800/60 cursor-pointer transition-colors group"
                    >
                      <td className="py-3 px-3">
                        <div className="font-bold text-slate-100 group-hover:text-emerald-400 transition-colors">
                          {b.bidder_name}
                        </div>
                        <div className="text-[10px] font-mono text-slate-400">
                          Contact: {b.contact_person || 'Authorized Signatory'}
                        </div>
                      </td>

                      <td className="py-3 px-3 font-mono text-[11px]">
                        <div className="text-slate-200">{b.gstin || 'N/A'}</div>
                        <div className="text-[10px] text-slate-400">PAN: {b.pan || 'N/A'}</div>
                      </td>

                      <td className="py-3 px-3 text-center">
                        <div className="font-mono font-bold text-sm text-slate-100">
                          {score.toFixed(1)}%
                        </div>
                        <div className="w-16 bg-slate-800 h-1.5 rounded-full overflow-hidden mx-auto mt-1 border border-slate-700">
                          <div
                            className={`h-full ${
                              score >= 90 ? 'bg-emerald-500' : score >= 75 ? 'bg-amber-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${score}%` }}
                          ></div>
                        </div>
                      </td>

                      <td className="py-3 px-3 text-center">
                        <RiskBadge level={risk} />
                      </td>

                      <td className="py-3 px-3 text-center">
                        <ComplianceBadge
                          status={score >= 90 ? 'PASS' : risk === 'CRITICAL' || risk === 'HIGH' ? 'FAIL' : 'REVIEW'}
                        />
                      </td>

                      <td className="py-3 px-3 text-slate-300 text-xs max-w-xs truncate">
                        {b.recommendation_type?.replace(/_/g, ' ') || 'Evaluation completed.'}
                      </td>

                      <td className="py-3 px-3 text-right">
                        <span className="text-[11px] font-mono text-emerald-400 group-hover:underline inline-flex items-center gap-1 font-bold">
                          Inspect Dossier →
                        </span>
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>

      </div>

    </div>
  );
};
