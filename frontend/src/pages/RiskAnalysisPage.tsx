import React from 'react';
import {
  BarChart3,
  Download,
  FileSpreadsheet,
  AlertTriangle,
  TrendingUp,
  ShieldCheck,
  CheckCircle2,
  Filter,
  Info
} from 'lucide-react';

export const RiskAnalysisPage: React.FC = () => {
  return (
    <div className="space-y-6">
      
      {/* 1. Header & Actions (Matching Page 9 from PDF) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">
            Risk Analytics Engine
          </h1>
          <p className="text-xs text-slate-500">
            Advanced AI-driven distribution analysis of procurement risks across technical, financial, and operational vectors.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button className="px-3 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-2xs">
            <Info className="w-3.5 h-3.5 text-slate-500" /> View Assessment Methodology
          </button>
          <button className="px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold flex items-center gap-1.5 shadow-sm">
            <Download className="w-3.5 h-3.5" /> Generate Comprehensive Report
          </button>
        </div>
      </div>

      {/* 2. Top 4 Stat KPI Cards (Matching Page 9 from PDF) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-4 space-y-1.5">
          <div className="text-xs text-slate-500 font-medium">Aggregate Risk Score</div>
          <div className="text-2xl font-extrabold text-slate-900 font-mono">64.8</div>
          <div className="text-[11px] text-emerald-600 font-medium">Slightly above historical 30-day baseline</div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-4 space-y-1.5">
          <div className="text-xs text-slate-500 font-medium">Compliance Rate</div>
          <div className="text-2xl font-extrabold text-slate-900 font-mono">92.1%</div>
          <div className="text-[11px] text-slate-500">Down due to new regulatory amendments</div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-4 space-y-1.5">
          <div className="text-xs text-slate-500 font-medium">Flagged Indicators</div>
          <div className="text-2xl font-extrabold text-rose-600 font-mono">18</div>
          <div className="text-[11px] text-rose-600 font-medium">Critical alerts requiring auditor manual review</div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-4 space-y-1.5">
          <div className="text-xs text-slate-500 font-medium">Audit Readiness</div>
          <div className="text-2xl font-extrabold text-emerald-600">High</div>
          <div className="text-[11px] text-slate-500">System health and data integrity validated</div>
        </div>
      </div>

      {/* 3. Middle Grid: Stacked Bar Chart & Factor Doughnut */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Risk Magnitude Distribution (2 cols) */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-900">Risk Magnitude Distribution</h2>
              <p className="text-xs text-slate-500">Monthly volume of flagged risks categorized by severity level</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 bg-slate-100 text-slate-700 text-xs font-semibold rounded">6 Months</span>
              <button className="px-2.5 py-1 border border-slate-200 text-slate-700 text-xs font-semibold rounded flex items-center gap-1">
                <Filter className="w-3 h-3" /> Filter
              </button>
            </div>
          </div>

          {/* Stacked Bars Visual */}
          <div className="h-56 flex items-end justify-between gap-4 pt-6 px-4">
            {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'].map((month, i) => {
              const heights = [
                { low: 40, med: 25, high: 20, crit: 15 },
                { low: 45, med: 20, high: 25, crit: 10 },
                { low: 35, med: 30, high: 20, crit: 15 },
                { low: 50, med: 20, high: 20, crit: 10 },
                { low: 55, med: 15, high: 20, crit: 10 },
                { low: 48, med: 22, high: 18, crit: 12 },
              ][i];

              return (
                <div key={month} className="flex-1 flex flex-col items-center gap-2 h-full justify-end">
                  <div className="w-full max-w-[48px] flex flex-col-reverse rounded-t overflow-hidden h-44">
                    <div style={{ height: `${heights.low}%` }} className="bg-emerald-500" title="Low Risk" />
                    <div style={{ height: `${heights.med}%` }} className="bg-amber-500" title="Medium Risk" />
                    <div style={{ height: `${heights.high}%` }} className="bg-rose-500" title="High Risk" />
                    <div style={{ height: `${heights.crit}%` }} className="bg-rose-900" title="Critical" />
                  </div>
                  <span className="text-[11px] font-mono text-slate-500">{month}</span>
                </div>
              );
            })}
          </div>

          <div className="flex items-center justify-center gap-6 pt-2 text-xs border-t border-slate-100">
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Low Risk</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Medium Risk</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span> High Risk</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-rose-900"></span> Critical Risk</span>
          </div>
        </div>

        {/* Factor Distribution (1 col) */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-6 space-y-4 flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Factor Distribution</h2>
            <p className="text-xs text-slate-500">Primary risk drivers across the active procurement portfolio</p>
          </div>

          <div className="flex items-center justify-center my-2">
            <div className="relative w-36 h-36 flex items-center justify-center">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#0284C7" strokeWidth="4" strokeDasharray="35 65" strokeDashoffset="0" />
                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#10B981" strokeWidth="4" strokeDasharray="25 75" strokeDashoffset="-35" />
                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#F59E0B" strokeWidth="4" strokeDasharray="20 80" strokeDashoffset="-60" />
                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#6366F1" strokeWidth="4" strokeDasharray="12 88" strokeDashoffset="-80" />
                <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#EC4899" strokeWidth="4" strokeDasharray="8 92" strokeDashoffset="-92" />
              </svg>
            </div>
          </div>

          <div className="space-y-1.5 text-xs">
            <div className="flex items-center justify-between"><span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-sky-600"></span> Technical (Pipeline Dia/Len)</span> <strong className="font-mono">35%</strong></div>
            <div className="flex items-center justify-between"><span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Financial (Turnover 3-Yr)</span> <strong className="font-mono">25%</strong></div>
            <div className="flex items-center justify-between"><span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Operational / Manpower</span> <strong className="font-mono">20%</strong></div>
            <div className="flex items-center justify-between"><span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-indigo-500"></span> Compliance & HSE</span> <strong className="font-mono">12%</strong></div>
            <div className="flex items-center justify-between"><span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-pink-500"></span> Legal / OEM Auth</span> <strong className="font-mono">8%</strong></div>
          </div>
        </div>

      </div>

      {/* 4. Critical Risk Monitoring Table (Matching Page 9 from PDF) */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-card overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Critical Risk Monitoring</h2>
            <p className="text-xs text-slate-500">Entities with risk scores exceeding established MoPNG thresholds</p>
          </div>
          <input
            type="text"
            placeholder="Filter vendors..."
            className="text-xs px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none"
          />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase text-[10px]">
              <tr>
                <th className="py-3 px-5">Entity ID</th>
                <th className="py-3 px-5">Vendor Name</th>
                <th className="py-3 px-5 text-center">Risk Score</th>
                <th className="py-3 px-5 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              <tr className="hover:bg-slate-50">
                <td className="py-3.5 px-5 font-mono text-[11px] font-bold text-slate-900">V-8821</td>
                <td className="py-3.5 px-5"><div className="font-bold">Global Infra Solutions</div><div className="text-[10px] text-slate-500">Financial Discrepancy</div></td>
                <td className="py-3.5 px-5 text-center font-mono font-bold text-rose-600">88</td>
                <td className="py-3.5 px-5 text-right"><span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">Critical</span></td>
              </tr>
              <tr className="hover:bg-slate-50">
                <td className="py-3.5 px-5 font-mono text-[11px] font-bold text-slate-900">V-4412</td>
                <td className="py-3.5 px-5"><div className="font-bold">TechBridge Systems</div><div className="text-[10px] text-slate-500">Security & HSE Lapses</div></td>
                <td className="py-3.5 px-5 text-center font-mono font-bold text-amber-600">72</td>
                <td className="py-3.5 px-5 text-right"><span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">High</span></td>
              </tr>
              <tr className="hover:bg-slate-50">
                <td className="py-3.5 px-5 font-mono text-[11px] font-bold text-slate-900">V-9011</td>
                <td className="py-3.5 px-5"><div className="font-bold">Apex Logistics LLC</div><div className="text-[10px] text-slate-500">Operational Delay Risk</div></td>
                <td className="py-3.5 px-5 text-center font-mono font-bold text-blue-600">65</td>
                <td className="py-3.5 px-5 text-right"><span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">High</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
