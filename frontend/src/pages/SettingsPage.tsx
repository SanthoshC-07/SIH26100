import React, { useState } from 'react';
import {
  Settings,
  User,
  Sliders,
  Bell,
  KeyRound,
  Building2,
  Save,
  CheckCircle2
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'PROFILE' | 'ENGINE' | 'NOTIFICATIONS' | 'SECURITY' | 'ORG'>('PROFILE');
  const [firstName, setFirstName] = useState('Alex');
  const [lastName, setLastName] = useState('Rivera');
  const [email, setEmail] = useState('a.rivera@procurement.gov');
  const [phone, setPhone] = useState('+91 98765 43210');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6">
      
      {/* 1. Header (Matching Page 12 from PDF) */}
      <div>
        <h1 className="text-xl font-bold tracking-tight text-slate-900">
          System Settings
        </h1>
        <p className="text-xs text-slate-500">
          Manage your personal profile, organization preferences, and AI compliance thresholds.
        </p>
      </div>

      {/* 2. Settings Tabs Bar */}
      <div className="flex flex-wrap items-center gap-2 bg-slate-100 p-1 rounded-xl text-xs font-semibold w-fit">
        <button
          onClick={() => setActiveTab('PROFILE')}
          className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg transition-all ${
            activeTab === 'PROFILE' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <User className="w-3.5 h-3.5" /> Profile
        </button>
        <button
          onClick={() => setActiveTab('ENGINE')}
          className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg transition-all ${
            activeTab === 'ENGINE' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <Sliders className="w-3.5 h-3.5" /> Compliance Engine
        </button>
        <button
          onClick={() => setActiveTab('NOTIFICATIONS')}
          className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg transition-all ${
            activeTab === 'NOTIFICATIONS' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <Bell className="w-3.5 h-3.5" /> Notifications
        </button>
        <button
          onClick={() => setActiveTab('SECURITY')}
          className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg transition-all ${
            activeTab === 'SECURITY' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <KeyRound className="w-3.5 h-3.5" /> Security & API
        </button>
        <button
          onClick={() => setActiveTab('ORG')}
          className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg transition-all ${
            activeTab === 'ORG' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <Building2 className="w-3.5 h-3.5" /> Organization
        </button>
      </div>

      {/* 3. Main Settings Content Card (Matching Page 12 from PDF) */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-card p-6 sm:p-8 space-y-6">
        
        {activeTab === 'PROFILE' && (
          <form onSubmit={handleSave} className="space-y-6">
            
            <div className="border-b border-slate-100 pb-4">
              <h2 className="text-sm font-bold text-slate-900">Personal Information</h2>
              <p className="text-xs text-slate-500">Update your photo and personal details for the audit trail.</p>
            </div>

            {/* Avatar Row */}
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center font-bold text-lg text-slate-700 font-mono shadow-inner">
                AR
              </div>
              <div className="space-y-1">
                <div className="font-bold text-xs text-slate-900">Alex Rivera</div>
                <div className="text-[11px] text-slate-500">Chief Auditor, Department of Procurement</div>
                <div className="flex items-center gap-3 pt-1">
                  <button type="button" className="text-xs font-semibold text-blue-600 hover:underline">
                    Update Avatar
                  </button>
                  <button type="button" className="text-xs text-rose-600 hover:underline">
                    Remove
                  </button>
                </div>
              </div>
            </div>

            {/* Form Fields Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="space-y-1">
                <label className="block font-bold text-slate-700">First Name</label>
                <input
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-800 focus:outline-none focus:border-blue-500 focus:bg-white"
                />
              </div>

              <div className="space-y-1">
                <label className="block font-bold text-slate-700">Last Name</label>
                <input
                  type="text"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-800 focus:outline-none focus:border-blue-500 focus:bg-white"
                />
              </div>

              <div className="space-y-1">
                <label className="block font-bold text-slate-700">Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-800 focus:outline-none focus:border-blue-500 focus:bg-white font-mono"
                />
                <span className="text-[10px] text-slate-400 block">Email changes require organizational approval.</span>
              </div>

              <div className="space-y-1">
                <label className="block font-bold text-slate-700">Phone Number</label>
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-800 focus:outline-none focus:border-blue-500 focus:bg-white font-mono"
                />
              </div>
            </div>

            {/* Save Buttons */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
              {saved && (
                <span className="text-xs text-emerald-600 font-bold flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4" /> Changes saved successfully
                </span>
              )}
              <button
                type="button"
                className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg text-xs font-semibold hover:bg-slate-50"
              >
                Discard Changes
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold flex items-center gap-1.5 shadow-sm"
              >
                <Save className="w-4 h-4" /> Save Changes
              </button>
            </div>

          </form>
        )}

        {activeTab === 'ENGINE' && (
          <div className="space-y-4 text-xs">
            <h2 className="text-sm font-bold text-slate-900">7 Core Checkers Configuration</h2>
            <div className="space-y-3">
              <div className="p-3 border border-slate-200 rounded-lg flex items-center justify-between">
                <div>
                  <div className="font-bold">Turnover Deterministic Arithmetic</div>
                  <div className="text-slate-500">Evaluates 3-year turnover threshold strictly via audited statements</div>
                </div>
                <span className="text-emerald-600 font-bold font-mono">ENABLED (100%)</span>
              </div>
              <div className="p-3 border border-slate-200 rounded-lg flex items-center justify-between">
                <div>
                  <div className="font-bold">Pipeline Diameter & Length Checker</div>
                  <div className="text-slate-500">Verifies ≥ 100 km and ≥ 24 inch API 5L specifications</div>
                </div>
                <span className="text-emerald-600 font-bold font-mono">ENABLED (100%)</span>
              </div>
            </div>
          </div>
        )}

      </div>

    </div>
  );
};
