import React, { useState } from 'react';
import {
  FileText,
  Calendar,
  Plus,
  TrendingUp,
  Clock,
  ShieldCheck,
  AlertTriangle,
  Download,
  ArrowRight,
  FileSpreadsheet,
  CheckCircle2
} from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'SUMMARY' | 'HISTORY' | 'TEMPLATES'>('SUMMARY');

  return (
    <div className="space-y-6">
      
      {/* 1. Header & Actions (Matching Page 10 from PDF) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">
            Compliance Reports
          </h1>
          <p className="text-xs text-slate-500">
            Generate, schedule, and manage comprehensive audit and compliance documentation for MoPNG.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button className="px-3.5 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-2xs">
            <Calendar className="w-3.5 h-3.5 text-slate-500" /> Schedule
          </button>
          <button className="px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold flex items-center gap-1.5 shadow-sm">
            <Plus className="w-4 h-4" /> New Report
          </button>
        </div>
      </div>

      {/* 2. Top 4 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-4 space-y-1.5">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>TOTAL REPORTS</span>
            <FileText className="w-4 h-4 text-blue-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900 font-mono">1,284</div>
          <div className="text-[11px] text-emerald-600 font-medium">+12% from last month</div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-4 space-y-1.5">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>COMPLIANCE AVG.</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900 font-mono">94.2%</div>
          <div className="text-[11px] text-emerald-600 font-medium">+2.4% from last month</div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-4 space-y-1.5">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>FLAGGED BIDS</span>
            <AlertTriangle className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900 font-mono">18</div>
          <div className="text-[11px] text-rose-600 font-medium">-4% from last month</div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-card p-4 space-y-1.5">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>AUDIT COVERAGE</span>
            <Clock className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900 font-mono">88.0%</div>
          <div className="text-[11px] text-emerald-600 font-medium">+5.1% from last month</div>
        </div>
      </div>

      {/* 3. Tabs Bar */}
      <div className="flex border-b border-slate-200 text-xs font-semibold gap-6 text-slate-500">
        <button
          onClick={() => setActiveTab('SUMMARY')}
          className={`pb-2.5 border-b-2 transition-all ${
            activeTab === 'SUMMARY' ? 'border-blue-600 text-blue-600' : 'border-transparent hover:text-slate-800'
          }`}
        >
          Dashboard Summary
        </button>
        <button
          onClick={() => setActiveTab('HISTORY')}
          className={`pb-2.5 border-b-2 transition-all ${
            activeTab === 'HISTORY' ? 'border-blue-600 text-blue-600' : 'border-transparent hover:text-slate-800'
          }`}
        >
          Report History
        </button>
        <button
          onClick={() => setActiveTab('TEMPLATES')}
          className={`pb-2.5 border-b-2 transition-all ${
            activeTab === 'TEMPLATES' ? 'border-blue-600 text-blue-600' : 'border-transparent hover:text-slate-800'
          }`}
        >
          Templates
        </button>
      </div>

      {/* 4. Middle Grid: Quick Generate & Compliance Score Trend */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Quick Generate Cards (1 col) */}
        <div className="space-y-3">
          <div className="text-xs font-bold uppercase text-slate-500 tracking-wider flex items-center gap-1.5">
            <FileText className="w-4 h-4 text-blue-600" /> Quick Generate
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-card hover:border-blue-300 hover:shadow-md transition-all cursor-pointer space-y-1.5">
            <div className="flex items-center gap-2 font-bold text-xs text-slate-900">
              <FileSpreadsheet className="w-4 h-4 text-blue-600" />
              <span>Full Compliance Audit</span>
            </div>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              Comprehensive analysis of all pending and approved bids against federal pipeline standards.
            </p>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-card hover:border-blue-300 hover:shadow-md transition-all cursor-pointer space-y-1.5">
            <div className="flex items-center gap-2 font-bold text-xs text-slate-900">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Vendor Risk Profile</span>
            </div>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              Analyze specific vendor histories, past pipeline track records, and safety reliability scores.
            </p>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-card hover:border-blue-300 hover:shadow-md transition-all cursor-pointer space-y-1.5">
            <div className="flex items-center gap-2 font-bold text-xs text-slate-900">
              <TrendingUp className="w-4 h-4 text-indigo-600" />
              <span>Operational Summary</span>
            </div>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              Metrics on processing time, throughput, OCR accuracy, and officer review speed.
            </p>
          </div>
        </div>

        {/* Compliance Trend Chart (2 cols) */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-card p-6 space-y-4 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-900">Compliance Score Trend</h2>
              <p className="text-xs text-slate-500">Monthly average across all government bidding portals</p>
            </div>
            <select className="text-xs border border-slate-200 rounded px-2 py-1 bg-slate-50">
              <option>Last 6 Months</option>
              <option>Last 12 Months</option>
            </select>
          </div>

          <div className="h-44 w-full pt-4">
            <svg className="w-full h-full" viewBox="0 0 500 130" preserveAspectRatio="none">
              <line x1="0" y1="100" x2="500" y2="100" stroke="#F1F5F9" strokeWidth="1" />
              <line x1="0" y1="50" x2="500" y2="50" stroke="#F1F5F9" strokeWidth="1" />
              <path d="M 0,80 Q 120,95 240,65 T 500,30" fill="none" stroke="#2563EB" strokeWidth="2.5" />
            </svg>
            <div className="flex justify-between text-[11px] font-mono text-slate-400 mt-2">
              <span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span><span>May</span>
            </div>
          </div>

          <div className="flex items-center justify-center gap-6 pt-2 text-xs border-t border-slate-100">
            <span className="flex items-center gap-1.5 text-slate-700"><span className="w-2.5 h-2.5 rounded-full bg-blue-600"></span> Compliance Score</span>
            <span className="flex items-center gap-1.5 text-slate-400"><span className="w-2.5 h-2.5 rounded-full bg-slate-300"></span> Department Target</span>
          </div>
        </div>

      </div>

      {/* 5. Bottom Need Custom Report Banner */}
      <div className="bg-[#0B132B] text-white rounded-xl p-6 shadow-md flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="font-bold text-sm text-blue-400">Need a Custom Report?</div>
          <p className="text-xs text-slate-300">Contact our data engineering team to build specialized compliance queries for your department.</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold shrink-0">
          Request Custom View
        </button>
      </div>

    </div>
  );
};
