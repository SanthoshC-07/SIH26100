import React, { useState } from 'react';
import {
  Settings,
  ShieldCheck,
  CheckCircle2,
  Save,
  KeyRound,
  Lock,
  UserCheck,
  Server,
  Database,
  Check
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [officerName, setOfficerName] = useState('Rajesh Sharma');
  const [officerRole, setOfficerRole] = useState('Senior Procurement Officer');
  const [officerDept, setOfficerDept] = useState('Pipeline Procurement & Technical Evaluation Directorate');
  const [sessionTimeout, setSessionTimeout] = useState('30');
  const [auditRetentionDays, setAuditRetentionDays] = useState('365');
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div className="space-y-5 font-sans">
      
      {/* Header Banner */}
      <div className="bg-[#FFFFFF] border border-[#D9DEDA] p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-sharp">
        <div>
          <div className="text-[10px] font-mono font-semibold tracking-wider text-[#B08A3E] uppercase flex items-center gap-1.5">
            <Settings className="w-3.5 h-3.5" />
            SYSTEM PREFERENCES & SECURITY
          </div>
          <h1 className="text-xl font-bold tracking-tight text-[#17201C] mt-0.5">
            Platform Settings & Officer Profile
          </h1>
          <p className="text-xs text-[#66736D]">
            Manage procurement officer identity, security encryption parameters, and regulatory audit retention policies.
          </p>
        </div>

        {savedSuccess && (
          <div className="px-3 py-1.5 bg-[#EAF5F0] border border-[#A8D9C5] text-[#237A57] font-mono text-xs font-bold flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4" />
            <span>PREFERENCES SAVED</span>
          </div>
        )}
      </div>

      <form onSubmit={handleSave} className="space-y-5 font-mono text-xs">
        
        {/* Section 1: Officer Profile */}
        <div className="bg-[#FFFFFF] border border-[#D9DEDA] p-5 shadow-sharp space-y-4">
          <div className="border-b border-[#D9DEDA] pb-2 font-bold text-[#102A24] uppercase flex items-center gap-2">
            <UserCheck className="w-4 h-4 text-[#B08A3E]" />
            <span>1. Officer Profile & Statutory Identity</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-1">
              <label className="block text-[10px] font-bold text-[#66736D] uppercase">
                Officer Legal Name
              </label>
              <input
                type="text"
                value={officerName}
                onChange={(e) => setOfficerName(e.target.value)}
                className="w-full px-3 py-1.5 bg-[#F5F6F3] border border-[#D9DEDA] text-xs text-[#17201C] focus:bg-white focus:border-[#176B55] outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="block text-[10px] font-bold text-[#66736D] uppercase">
                Official Designation
              </label>
              <input
                type="text"
                value={officerRole}
                onChange={(e) => setOfficerRole(e.target.value)}
                className="w-full px-3 py-1.5 bg-[#F5F6F3] border border-[#D9DEDA] text-xs text-[#17201C] focus:bg-white focus:border-[#176B55] outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="block text-[10px] font-bold text-[#66736D] uppercase">
                Directorate / Ministry Unit
              </label>
              <input
                type="text"
                value={officerDept}
                onChange={(e) => setOfficerDept(e.target.value)}
                className="w-full px-3 py-1.5 bg-[#F5F6F3] border border-[#D9DEDA] text-xs text-[#17201C] focus:bg-white focus:border-[#176B55] outline-none"
              />
            </div>
          </div>
        </div>

        {/* Section 2: Security & Audit Retention */}
        <div className="bg-[#FFFFFF] border border-[#D9DEDA] p-5 shadow-sharp space-y-4">
          <div className="border-b border-[#D9DEDA] pb-2 font-bold text-[#102A24] uppercase flex items-center gap-2">
            <Lock className="w-4 h-4 text-[#B08A3E]" />
            <span>2. Session Security & GFR 2017 Audit Policies</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-3.5 bg-[#F5F6F3] border border-[#D9DEDA] space-y-1.5">
              <label className="block text-[10px] font-bold text-[#17201C] uppercase">
                Session Idle Timeout (Minutes)
              </label>
              <input
                type="number"
                value={sessionTimeout}
                onChange={(e) => setSessionTimeout(e.target.value)}
                className="w-full px-3 py-1.5 bg-white border border-[#D9DEDA] text-xs text-[#17201C] focus:border-[#176B55] outline-none"
              />
              <p className="text-[10px] text-[#66736D]">
                Automatically locks procurement verification workspace after inactivity.
              </p>
            </div>

            <div className="p-3.5 bg-[#F5F6F3] border border-[#D9DEDA] space-y-1.5">
              <label className="block text-[10px] font-bold text-[#17201C] uppercase">
                GFR 2017 Audit Log Retention (Days)
              </label>
              <input
                type="number"
                value={auditRetentionDays}
                onChange={(e) => setAuditRetentionDays(e.target.value)}
                className="w-full px-3 py-1.5 bg-white border border-[#D9DEDA] text-xs text-[#17201C] focus:border-[#176B55] outline-none"
              />
              <p className="text-[10px] text-[#66736D]">
                Immutable cryptographic ledger retention window for statutory audits.
              </p>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            className="px-5 py-2.5 bg-[#102A24] hover:bg-[#1E5A47] text-white font-bold flex items-center gap-2 transition-colors border border-[#176B55]"
          >
            <Save className="w-4 h-4 text-[#B08A3E]" />
            <span>SAVE PLATFORM PREFERENCES</span>
          </button>
        </div>

      </form>

    </div>
  );
};
