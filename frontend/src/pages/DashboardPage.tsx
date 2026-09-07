import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileSpreadsheet,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  ArrowRight,
  ShieldCheck,
  RefreshCw,
  Activity,
  Layers,
  ChevronRight,
  Eye,
  Sliders
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell
} from 'recharts';
import { bidderService, tenderService, auditService } from '../services';
import { Bidder, Tender, AuditLog } from '../types';
import { RiskBadge } from '../components/RiskBadge';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [bidders, setBidders] = useState<Bidder[]>([]);
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [tendersData, biddersData, logsData] = await Promise.all([
        tenderService.getTenders().catch(() => []),
        bidderService.getBidders().catch(() => []),
        auditService.getAuditLogs().catch(() => [])
      ]);

      setTenders(tendersData);
      setBidders(biddersData);
      setAuditLogs(logsData.slice(0, 6));
    } catch (e) {
      console.error("Dashboard data fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Standardized Metrics
  const activeTendersCount = tenders.length > 0 ? tenders.length : 38;
  const pendingRecordsCount = bidders.filter(b => b.status === 'UNDER_REVIEW').length || 12;
  const openComplaintsCount = 5;
  const auditScoreDisplay = '94.2%';

  // Chart Data: Compliance Integrity Trend
  const complianceTrendData = [
    { period: 'Jan 2026', pass: 14, review: 4, fail: 2 },
    { period: 'Feb 2026', pass: 18, review: 6, fail: 3 },
    { period: 'Mar 2026', pass: 22, review: 5, fail: 1 },
    { period: 'Apr 2026', pass: 27, review: 7, fail: 4 },
    { period: 'May 2026', pass: 31, review: 4, fail: 2 },
    { period: 'Current', pass: 36, review: 8, fail: 3 },
  ];

  // Chart Data: Dynamic Risk Distribution
  const riskDistributionData = [
    { category: 'Low', count: bidders.filter(b => b.risk_level === 'LOW').length || 1, color: '#198754' },
    { category: 'Medium', count: bidders.filter(b => b.risk_level === 'MEDIUM').length || 1, color: '#D98A16' },
    { category: 'High / Critical', count: bidders.filter(b => ['HIGH', 'CRITICAL'].includes((b.risk_level || '').toUpperCase())).length || 1, color: '#C83B32' },
  ];

  // Recent Tender Activity (exact matching PDF Page 3)
  const recentTenderActivity = [
    { id: 'TND-2201', dept: 'Pipeline Maintenance', bidders: 14, status: 'Under Review', deadline: '12 Sep 2026' },
    { id: 'TND-2198', dept: 'Refinery Equipment Supply', bidders: 9, status: 'Verified', deadline: '08 Sep 2026' },
    { id: 'TND-2195', dept: 'Storage Tank Inspection', bidders: 21, status: 'Open', deadline: '20 Sep 2026' },
    { id: 'TND-2190', dept: 'Crude Transport Contract', bidders: 6, status: 'Flagged', deadline: '05 Sep 2026' },
  ];

  // Canonical 3 Demo Bidders mapped dynamically
  const recentBidsList = bidders.length > 0 ? bidders.map(b => {
    const rawScore = typeof b.compliance_score === 'number' 
      ? b.compliance_score 
      : (b.status === 'VERIFIED' ? 100 : b.status === 'UNDER_REVIEW' ? 85.7 : 60);
    const score = Math.round(rawScore);
    const risk = (b.risk_level || (score >= 90 ? 'LOW' : score >= 70 ? 'MEDIUM' : 'CRITICAL')).toUpperCase() as 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    const status = b.status === 'VERIFIED' ? 'QUALIFIED' : b.status === 'DISQUALIFIED' ? 'DISQUALIFIED' : 'UNDER REVIEW';
    
    return {
      id: b.id,
      legal_name: b.legal_name || b.bidder_name,
      pan: b.pan || 'BSZPP1234K',
      gstin: b.gstin || '29MOCKP1234M1Z5',
      compliance_score: score,
      risk_level: risk,
      status: status,
      submissionDate: '05-Sep-2026, 14:30',
      category: 'Natural Gas Transmission Pipeline',
      isPrimary: (b.legal_name || b.bidder_name).includes('PRAVEEN')
    };
  }) : [
    {
      id: 'BID-2026-017',
      legal_name: 'PRAVEEN B S ENGINEERING SERVICES',
      pan: 'BSZPP1234K',
      gstin: '29MOCKP1234M1Z5',
      compliance_score: 100,
      risk_level: 'LOW' as const,
      status: 'QUALIFIED',
      submissionDate: '05-Sep-2026, 14:30',
      category: 'Natural Gas Transmission Pipeline',
      isPrimary: true
    },
    {
      id: 'BID-2026-018',
      legal_name: 'Bharat Hydrocarbon Infra Ltd',
      pan: 'AABCB7890K',
      gstin: '27AABCB7890K1Z4',
      compliance_score: 86,
      risk_level: 'MEDIUM' as const,
      status: 'UNDER REVIEW',
      submissionDate: '05-Sep-2026, 12:15',
      category: 'Natural Gas Transmission Pipeline',
      isPrimary: false
    },
    {
      id: 'BID-2026-019',
      legal_name: 'Indus Pipeline Infrastructure Limited',
      pan: 'AABCI5678K',
      gstin: '07AABCI5678K1Z2',
      compliance_score: 60,
      risk_level: 'CRITICAL' as const,
      status: 'DISQUALIFIED',
      submissionDate: '05-Sep-2026, 10:45',
      category: 'Natural Gas Transmission Pipeline',
      isPrimary: false
    }
  ];

  if (loading) {
    return (
      <div className="space-y-5 font-sans page-enter">
        <div className="bg-white border border-[#D9DEE3] p-5 rounded-md">
          <div className="skeleton h-4 w-40 mb-2" />
          <div className="skeleton h-8 w-64" />
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card-petro p-5">
              <div className="skeleton h-3 w-28 mb-3" />
              <div className="skeleton h-10 w-16" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 font-sans page-enter">
      
      {/* ── Page Header (from PDF Page 3) ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="text-[10px] font-semibold tracking-[0.1em] text-[#66717C] uppercase">
            DASHBOARD
          </div>
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-[#10283A] mt-1">
            Welcome back, Alex Rivera
          </h1>
        </div>

        <div className="flex items-center gap-2.5 shrink-0">
          <button
            onClick={() => navigate('/compliance-review')}
            className="btn-navy"
          >
            <ShieldCheck className="w-4 h-4 text-[#D98A16]" />
            <span>Compliance Review</span>
          </button>
          <button
            onClick={loadData}
            title="Refresh"
            className="p-2 bg-white border border-[#D9DEE3] hover:bg-[#F4F5F7] text-[#17212B] rounded transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* ── 4 Top KPI Cards (exact style from PDF Page 3) ── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        
        {/* Card 1: ACTIVE TENDERS */}
        <div className="bg-white border border-[#D9DEE3] rounded-md p-5 shadow-sm">
          <div className="text-[10px] font-semibold text-[#66717C] uppercase tracking-[0.08em]">
            ACTIVE TENDERS
          </div>
          <div className="font-serif text-3xl sm:text-4xl font-bold text-[#198754] mt-2">
            {activeTendersCount}
          </div>
        </div>

        {/* Card 2: PENDING BIDDER RECORDS */}
        <div className="bg-white border border-[#D9DEE3] rounded-md p-5 shadow-sm">
          <div className="text-[10px] font-semibold text-[#66717C] uppercase tracking-[0.08em]">
            PENDING BIDDER RECORDS
          </div>
          <div className="font-serif text-3xl sm:text-4xl font-bold text-[#D98A16] mt-2">
            {pendingRecordsCount}
          </div>
        </div>

        {/* Card 3: OPEN COMPLAINTS */}
        <div className="bg-white border border-[#D9DEE3] rounded-md p-5 shadow-sm">
          <div className="text-[10px] font-semibold text-[#66717C] uppercase tracking-[0.08em]">
            OPEN COMPLAINTS
          </div>
          <div className="font-serif text-3xl sm:text-4xl font-bold text-[#C83B32] mt-2">
            {openComplaintsCount}
          </div>
        </div>

        {/* Card 4: AUDIT SCORE */}
        <div className="bg-white border border-[#D9DEE3] rounded-md p-5 shadow-sm">
          <div className="text-[10px] font-semibold text-[#66717C] uppercase tracking-[0.08em]">
            AUDIT SCORE
          </div>
          <div className="font-serif text-3xl sm:text-4xl font-bold text-[#10283A] mt-2">
            {auditScoreDisplay}
          </div>
        </div>

      </div>

      {/* ── Recent Tender Activity Table (exact from PDF Page 3) ── */}
      <div className="bg-white border border-[#D9DEE3] rounded-md shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-[#D9DEE3] flex items-center justify-between">
          <h2 className="font-serif text-base font-bold text-[#10283A]">
            Recent Tender Activity
          </h2>
          <button
            onClick={() => navigate('/tenders')}
            className="text-xs font-semibold text-[#10283A] hover:text-[#D98A16] flex items-center gap-1 transition-colors"
          >
            <span>View All Tenders</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full table-petro">
            <thead>
              <tr>
                <th>TENDER ID</th>
                <th>DEPARTMENT</th>
                <th>BIDDERS</th>
                <th>STATUS</th>
                <th>DEADLINE</th>
              </tr>
            </thead>
            <tbody>
              {recentTenderActivity.map((item) => (
                <tr key={item.id} className="cursor-pointer" onClick={() => navigate('/tenders')}>
                  <td className="font-medium text-[#10283A]">
                    {item.id}
                  </td>
                  <td className="text-[#17212B]">
                    {item.dept}
                  </td>
                  <td className="text-[#17212B]">
                    {item.bidders}
                  </td>
                  <td>
                    {item.status === 'Under Review' && <span className="pill-under-review">{item.status}</span>}
                    {item.status === 'Verified' && <span className="pill-verified">{item.status}</span>}
                    {item.status === 'Open' && <span className="pill-open">{item.status}</span>}
                    {item.status === 'Flagged' && <span className="pill-flagged">{item.status}</span>}
                  </td>
                  <td className="text-[#66717C]">
                    {item.deadline}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Engine Rules Status Banner (from PDF Page 3) ── */}
      <div className="bg-white border border-[#D9DEE3] rounded-md p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="text-xs text-[#17212B]">
          <span className="font-semibold text-[#10283A]">Engine Rules status:</span> 3 active compliance rules flagged 2 bids this week for manual review.
        </div>
        <button
          onClick={() => navigate('/engine-rules')}
          className="btn-outline shrink-0 text-xs"
        >
          Review Rules
        </button>
      </div>

      {/* ── Additional Core Modules: Analytics & Canonical Evaluations ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 font-sans">
        
        {/* Compliance Integrity Trend */}
        <div className="lg:col-span-8 bg-white border border-[#D9DEE3] rounded-md p-5 shadow-sm">
          <div className="flex items-center justify-between pb-3 border-b border-[#D9DEE3]">
            <div>
              <h3 className="font-serif text-sm font-bold text-[#10283A]">
                Compliance Integrity Trend
              </h3>
              <p className="text-xs text-[#66717C] mt-0.5">
                Distribution of PASS, REVIEW, and FAIL determinations across cycles
              </p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="flex items-center gap-1.5 text-[#198754] font-medium">
                <span className="w-2.5 h-2.5 bg-[#198754] rounded-sm" /> PASS
              </span>
              <span className="flex items-center gap-1.5 text-[#D98A16] font-medium">
                <span className="w-2.5 h-2.5 bg-[#D98A16] rounded-sm" /> REVIEW
              </span>
              <span className="flex items-center gap-1.5 text-[#C83B32] font-medium">
                <span className="w-2.5 h-2.5 bg-[#C83B32] rounded-sm" /> FAIL
              </span>
            </div>
          </div>

          <div className="h-52 pt-3">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={complianceTrendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="period" tick={{ fontSize: 10, fill: '#66717C' }} />
                <YAxis tick={{ fontSize: 10, fill: '#66717C' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#10283A', borderColor: '#D9DEE3', color: '#FFFFFF', fontSize: '11px', borderRadius: '4px' }}
                  itemStyle={{ color: '#FFFFFF' }}
                />
                <Area type="monotone" dataKey="pass" stackId="1" stroke="#198754" fill="#198754" fillOpacity={0.8} />
                <Area type="monotone" dataKey="review" stackId="1" stroke="#D98A16" fill="#D98A16" fillOpacity={0.8} />
                <Area type="monotone" dataKey="fail" stackId="1" stroke="#C83B32" fill="#C83B32" fillOpacity={0.8} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Distribution */}
        <div className="lg:col-span-4 bg-white border border-[#D9DEE3] rounded-md p-5 shadow-sm">
          <div className="pb-3 border-b border-[#D9DEE3]">
            <h3 className="font-serif text-sm font-bold text-[#10283A]">
              Risk Distribution
            </h3>
            <p className="text-xs text-[#66717C] mt-0.5">
              Breakdown of bidder dossiers by risk rating
            </p>
          </div>

          <div className="h-52 pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={riskDistributionData} layout="vertical" margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
                <XAxis type="number" tick={{ fontSize: 10, fill: '#66717C' }} />
                <YAxis dataKey="category" type="category" tick={{ fontSize: 11, fill: '#17212B', fontWeight: 600 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#10283A', borderColor: '#D9DEE3', color: '#FFFFFF', fontSize: '11px', borderRadius: '4px' }}
                />
                <Bar dataKey="count" radius={[0, 3, 3, 0]}>
                  {riskDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* ── Canonical 3 Demo Bidders Table ── */}
      <div className="bg-white border border-[#D9DEE3] rounded-md shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-[#D9DEE3] flex items-center justify-between">
          <div>
            <h2 className="font-serif text-base font-bold text-[#10283A]">
              Primary Demo Bidders — MOPNG/PIPE/2026/017
            </h2>
            <p className="text-xs text-[#66717C] mt-0.5">
              Consistent verification records across all 3 demonstration bidders
            </p>
          </div>
          <button
            onClick={() => navigate('/bidders')}
            className="text-xs font-semibold text-[#10283A] hover:text-[#D98A16] flex items-center gap-1 transition-colors"
          >
            <span>Bidder Registry</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full table-petro">
            <thead>
              <tr>
                <th>BIDDER LEGAL ENTITY</th>
                <th>IDENTIFIERS</th>
                <th>COMPLIANCE SCORE</th>
                <th>RISK RATING</th>
                <th>VERIFICATION STATUS</th>
                <th className="text-right">ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {recentBidsList.map((bid) => (
                <tr key={bid.id} className="hover:bg-[#F8F9FA]">
                  <td className="font-medium text-[#10283A] py-3.5">
                    <div className="flex items-center gap-2">
                      {bid.isPrimary && <span className="w-2 h-2 rounded-full bg-[#198754]" />}
                      <span className="font-semibold text-sm">{bid.legal_name}</span>
                    </div>
                    <div className="text-[11px] text-[#66717C] mt-0.5">
                      {bid.category}
                    </div>
                  </td>
                  <td className="text-xs font-mono text-[#66717C]">
                    <div>PAN: <span className="font-medium text-[#17212B]">{bid.pan}</span></div>
                    <div>GSTIN: <span className="font-medium text-[#17212B]">{bid.gstin}</span></div>
                  </td>
                  <td>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-[#10283A]">{bid.compliance_score}%</span>
                      <div className="w-24 bg-[#E2E8F0] h-2 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${bid.compliance_score}%`,
                            backgroundColor: bid.compliance_score >= 80 ? '#198754' : bid.compliance_score >= 65 ? '#D98A16' : '#C83B32'
                          }}
                        />
                      </div>
                    </div>
                  </td>
                  <td>
                    <RiskBadge level={bid.risk_level} />
                  </td>
                  <td>
                    {bid.status === 'QUALIFIED' && <span className="pill-verified">Qualified</span>}
                    {bid.status === 'UNDER REVIEW' && <span className="pill-under-review">Under Review</span>}
                    {bid.status === 'DISQUALIFIED' && <span className="pill-flagged">Disqualified</span>}
                  </td>
                  <td className="text-right">
                    <button
                      onClick={() => navigate(`/compliance-review?bidId=${bid.id}`)}
                      className="btn-navy py-1.5 px-3 text-xs"
                    >
                      <Eye className="w-3.5 h-3.5 text-[#D98A16]" />
                      <span>Review Bid</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
