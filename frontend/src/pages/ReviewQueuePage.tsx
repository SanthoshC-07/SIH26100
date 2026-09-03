import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  Clock,
  AlertTriangle,
  CheckCircle2,
  Filter,
  Download,
  Search,
  Sliders,
  UserCheck,
  ExternalLink,
  Layers
} from 'lucide-react';

export const ReviewQueuePage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'ALL' | 'HIGH' | 'MY_QUEUE' | 'FLAGGED'>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const mockWorklist = [
    {
      id: 'VER-9821',
      bidder: 'Praveen B S Engineering Services',
      project: 'GAIL 120 KM Pipeline EPC Package',
      urgency: 'high',
      score: 94,
      status: 'PENDING',
      auditor: 'Unassigned',
      bidderId: '1'
    },
    {
      id: 'VER-9822',
      bidder: 'Larsen & Toubro Hydrocarbon',
      project: 'IOCL Crude Pipeline Spooling',
      urgency: 'medium',
      score: 78,
      status: 'IN REVIEW',
      auditor: 'Marcus Thorne',
      bidderId: '2'
    },
    {
      id: 'VER-9823',
      bidder: 'Indus Pipeline Infra Corp',
      project: 'ONGC Offshore Gas Feed',
      urgency: 'high',
      score: 89,
      status: 'FLAGGED',
      auditor: 'Sarah Jenkins',
      bidderId: '3'
    },
    {
      id: 'VER-9824',
      bidder: 'PetroCon Energy Limited',
      project: 'GAIL Compressor Station 04',
      urgency: 'low',
      score: 42,
      status: 'PENDING',
      auditor: 'Unassigned',
      bidderId: '4'
    },
    {
      id: 'VER-9825',
      bidder: 'Vanguard Hydrocarbon Engineering',
      project: 'Assam Gas Grid Extension',
      urgency: 'medium',
      score: 65,
      status: 'VERIFIED',
      auditor: 'Alex Rivera',
      bidderId: '5'
    }
  ];

  const filteredWorklist = mockWorklist.filter(item => {
    if (activeTab === 'HIGH' && item.urgency !== 'high') return false;
    if (activeTab === 'FLAGGED' && item.status !== 'FLAGGED') return false;
    if (activeTab === 'MY_QUEUE' && item.auditor !== 'Alex Rivera') return false;
    return item.bidder.toLowerCase().includes(searchQuery.toLowerCase()) || item.id.toLowerCase().includes(searchQuery.toLowerCase());
  });

  return (
    <div className="space-y-6">
      
      {/* 1. Header & Actions (Matching Page 6 from PDF) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">
            Verification Worklist
          </h1>
          <p className="text-xs text-slate-500">
            Manage and triage pending bid compliance audits and document integrity checks.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button className="px-3 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-2xs">
            <Download className="w-3.5 h-3.5 text-slate-500" /> Export CSV
          </button>
          <button className="px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold flex items-center gap-1.5 shadow-sm">
            <ShieldCheck className="w-4 h-4" /> Bulk Verify
          </button>
        </div>
      </div>

      {/* 2. Top 4 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-4 space-y-1.5">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Awaiting Review</span>
            <Clock className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900">24</div>
          <div className="text-[11px] text-emerald-600 font-medium">+12% today • 8 high priority</div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-4 space-y-1.5">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Active Audits</span>
            <UserCheck className="w-4 h-4 text-blue-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900">15</div>
          <div className="text-[11px] text-slate-500 font-mono">Assigned to 6 auditors</div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-4 space-y-1.5">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Flagged Issues</span>
            <AlertTriangle className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900">03</div>
          <div className="text-[11px] text-rose-600 font-medium">Requires escalation</div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-4 space-y-1.5">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Daily Completion</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900">92%</div>
          <div className="text-[11px] text-slate-500 font-mono">Avg. 4.2h resolution</div>
        </div>
      </div>

      {/* 3. Tab Filter Bar & Search */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-card p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-xs">
        {/* Tabs */}
        <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('ALL')}
            className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
              activeTab === 'ALL' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            All Requests (42)
          </button>
          <button
            onClick={() => setActiveTab('HIGH')}
            className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
              activeTab === 'HIGH' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            High Priority (8)
          </button>
          <button
            onClick={() => setActiveTab('MY_QUEUE')}
            className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
              activeTab === 'MY_QUEUE' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            My Queue (5)
          </button>
          <button
            onClick={() => setActiveTab('FLAGGED')}
            className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
              activeTab === 'FLAGGED' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Flagged (3)
          </button>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Filter by company or ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:outline-none focus:border-blue-500 focus:bg-white"
          />
        </div>
      </div>

      {/* 4. Verification Table (Matching Page 6 from PDF) */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-500 font-semibold uppercase text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-5">Verification ID</th>
                <th className="py-3 px-5">Bidder / Project</th>
                <th className="py-3 px-5 text-center">Urgency</th>
                <th className="py-3 px-5 text-center">Priority Score</th>
                <th className="py-3 px-5 text-center">Status</th>
                <th className="py-3 px-5">Auditor</th>
                <th className="py-3 px-5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 text-slate-700">
              {filteredWorklist.map((item) => {
                const urgencyColor = item.urgency === 'high' ? 'bg-rose-50 text-rose-700 border-rose-200' : item.urgency === 'medium' ? 'bg-amber-50 text-amber-700 border-amber-200' : 'bg-emerald-50 text-emerald-700 border-emerald-200';
                
                return (
                  <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3.5 px-5 font-mono text-[11px] font-bold text-slate-900">
                      {item.id}
                    </td>
                    <td className="py-3.5 px-5">
                      <div className="font-bold text-slate-900">{item.bidder}</div>
                      <div className="text-[10px] text-slate-500">{item.project}</div>
                    </td>
                    <td className="py-3.5 px-5 text-center">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold border capitalize ${urgencyColor}`}>
                        ● {item.urgency}
                      </span>
                    </td>
                    <td className="py-3.5 px-5 text-center font-mono font-bold text-slate-800">
                      {item.score}%
                    </td>
                    <td className="py-3.5 px-5 text-center">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                        {item.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-5 text-slate-600 font-medium">
                      {item.auditor}
                    </td>
                    <td className="py-3.5 px-5 text-right">
                      <button
                        onClick={() => navigate(`/bidders/${item.bidderId}`)}
                        className="px-3 py-1 bg-white border border-slate-300 hover:bg-slate-50 text-slate-800 rounded-lg text-xs font-semibold transition-all shadow-2xs"
                      >
                        Review Audit
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. Bottom Two Cards: Recent Auditor Activity & Compliance Thresholds (Matching Page 6) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Recent Auditor Activity */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900">Recent Auditor Activity</h2>
            <button onClick={() => navigate('/audit')} className="text-xs text-blue-600 font-semibold hover:underline">
              View Audit Trail
            </button>
          </div>

          <div className="space-y-3.5 text-xs">
            <div className="flex items-start justify-between border-b border-slate-100 pb-2.5">
              <div className="space-y-0.5">
                <div className="font-semibold text-slate-800 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                  Document Verified: GST & Financial Statements
                </div>
                <div className="text-[10px] text-slate-500">Praveen B S Engineering Services</div>
              </div>
              <div className="text-right">
                <div className="font-semibold text-slate-700">Alex Rivera</div>
                <div className="text-[10px] text-slate-400 font-mono">12 mins ago</div>
              </div>
            </div>

            <div className="flex items-start justify-between border-b border-slate-100 pb-2.5">
              <div className="space-y-0.5">
                <div className="font-semibold text-slate-800 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-rose-500"></span>
                  Flag Raised: OEM Authorization Expiry Date Check
                </div>
                <div className="text-[10px] text-slate-500">Indus Pipeline Corp</div>
              </div>
              <div className="text-right">
                <div className="font-semibold text-slate-700">Sarah Jenkins</div>
                <div className="text-[10px] text-slate-400 font-mono">45 mins ago</div>
              </div>
            </div>

            <div className="flex items-start justify-between">
              <div className="space-y-0.5">
                <div className="font-semibold text-slate-800 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                  Worklist Assigned: 5 new submissions queued
                </div>
                <div className="text-[10px] text-slate-500">System AI Ingestion</div>
              </div>
              <div className="text-right">
                <div className="font-semibold text-slate-700">System AI</div>
                <div className="text-[10px] text-slate-400 font-mono">2 hours ago</div>
              </div>
            </div>
          </div>
        </div>

        {/* Compliance Thresholds Card */}
        <div className="bg-[#0B132B] text-white rounded-xl p-6 shadow-md flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-blue-400 font-bold text-sm">
              <Sliders className="w-5 h-5" />
              <span>Compliance Thresholds</span>
            </div>
            <p className="text-xs text-slate-300">
              System-wide AI audit settings & sensitivity levels for pipeline compliance checks.
            </p>

            <div className="space-y-2 pt-2 text-xs">
              <div className="flex items-center justify-between p-2.5 bg-slate-900/60 rounded-lg border border-slate-800">
                <span className="text-slate-300 font-medium">Auto-Flag Sensitivity</span>
                <span className="font-bold text-blue-400 font-mono">85%</span>
              </div>
              <div className="flex items-center justify-between p-2.5 bg-slate-900/60 rounded-lg border border-slate-800">
                <span className="text-slate-300 font-medium">Integrity Depth Check</span>
                <span className="font-bold text-emerald-400 font-mono">High (OCR + Rules)</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => navigate('/settings')}
            className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold transition-all"
          >
            Modify Settings →
          </button>
        </div>

      </div>

    </div>
  );
};
