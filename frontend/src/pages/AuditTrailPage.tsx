import React, { useEffect, useState } from 'react';
import {
  History,
  Download,
  Search,
  RefreshCw,
  Clock,
  ShieldCheck,
  Building,
  Check,
  Filter,
  FileSpreadsheet,
  AlertOctagon,
  UserCheck,
  FileText
} from 'lucide-react';
import { auditService, bidderService } from '../services';
import { AuditEvent, Bidder } from '../types';

export const AuditTrailPage: React.FC = () => {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [bidders, setBidders] = useState<Bidder[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAction, setSelectedAction] = useState('ALL');
  const [selectedRole, setSelectedRole] = useState('ALL');
  const [selectedBidder, setSelectedBidder] = useState('ALL');
  const [exportNotice, setExportNotice] = useState(false);

  const actionList = [
    'ALL',
    'LOGIN',
    'LOGOUT',
    'TENDER_CREATED',
    'TENDER_UPDATED',
    'TENDER_PUBLISHED',
    'BID_SUBMITTED',
    'DOCUMENT_UPLOADED',
    'OCR_COMPLETED',
    'REQUIREMENT_EXTRACTED',
    'EVIDENCE_RETRIEVED',
    'COMPLIANCE_RUN',
    'COMPLIANCE_REVERIFIED',
    'OFFICER_REVIEWED',
    'AI_RESULT_OVERRIDDEN',
    'FINAL_BID_DECISION',
    'REPORT_GENERATED'
  ];

  const loadAuditData = async () => {
    setLoading(true);
    try {
      const params: any = { limit: 150 };
      if (selectedAction !== 'ALL') params.action = selectedAction;
      if (selectedRole !== 'ALL') params.role = selectedRole;
      if (selectedBidder !== 'ALL') params.bidder_id = selectedBidder;
      if (searchQuery.trim()) params.search = searchQuery.trim();

      const data = await auditService.getAuditEvents(params);
      setEvents(data);
    } catch (e) {
      console.error("Failed to load audit events:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    bidderService.getBidders().then(setBidders).catch(() => []);
  }, []);

  useEffect(() => {
    loadAuditData();
  }, [selectedAction, selectedRole, selectedBidder]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadAuditData();
  };

  const handleExportCsv = () => {
    const params: any = {};
    if (selectedAction !== 'ALL') params.action = selectedAction;
    if (selectedRole !== 'ALL') params.role = selectedRole;
    if (selectedBidder !== 'ALL') params.bidder_id = selectedBidder;
    const url = auditService.exportCsvUrl(params);
    window.open(url, '_blank');
    setExportNotice(true);
    setTimeout(() => setExportNotice(false), 4000);
  };

  return (
    <div className="space-y-5 font-sans">
      {/* ── Top Header ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#D9DEE3] pb-4">
        <div>
          <div className="text-[11px] font-mono tracking-widest text-[#66717C] uppercase font-bold">
            SECTION 4 GENERAL FINANCIAL RULES (GFR 2017)
          </div>
          <h1 className="text-2xl font-serif font-bold text-[#10283A] tracking-tight mt-0.5">
            Immutable Audit Trail
          </h1>
          <p className="text-xs text-[#66717C] mt-0.5">
            Cryptographically sealed activity log of all AI assessments, officer overrides, and procurement decisions.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={handleExportCsv}
            className="px-4 py-2 border border-[#D9DEE3] bg-[#FFFFFF] hover:bg-[#F3F4F6] text-[#10283A] text-xs font-semibold rounded shadow-sm inline-flex items-center gap-1.5 transition-colors"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-[#1E5A47]" />
            <span>Export Official CSV</span>
          </button>

          <button
            onClick={loadAuditData}
            className="p-2 border border-[#D9DEE3] bg-[#FFFFFF] hover:bg-[#F3F4F6] text-[#10283A] rounded shadow-sm"
            title="Reload Audit Logs"
          >
            <RefreshCw className="w-4 h-4 text-[#66717C]" />
          </button>
        </div>
      </div>

      {exportNotice && (
        <div className="bg-[#EAF5F0] border-l-4 border-[#1E5A47] p-3 text-xs text-[#1E5A47] font-medium flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4" />
            <span>Audit trail successfully downloaded for regulatory archiving.</span>
          </div>
        </div>
      )}

      {/* ── Filters & Search Toolbar ── */}
      <div className="bg-white border border-[#D9DEE3] p-4 rounded shadow-sm space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row gap-3 items-center">
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-[#66717C]" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search description, entity, action, or officer name..."
              className="w-full pl-9 pr-4 py-2 text-xs border border-[#D9DEE3] rounded focus:outline-none focus:border-[#10283A]"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
            {/* Action Filter */}
            <select
              value={selectedAction}
              onChange={(e) => setSelectedAction(e.target.value)}
              className="border border-[#D9DEE3] text-[#10283A] text-xs rounded px-2.5 py-2 bg-white focus:outline-none font-mono"
            >
              {actionList.map((act) => (
                <option key={act} value={act}>
                  Action: {act}
                </option>
              ))}
            </select>

            {/* Role Filter */}
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              className="border border-[#D9DEE3] text-[#10283A] text-xs rounded px-2.5 py-2 bg-white focus:outline-none font-mono"
            >
              <option value="ALL">Role: ALL</option>
              <option value="ADMIN">ADMIN</option>
              <option value="PROCUREMENT_OFFICER">OFFICER</option>
              <option value="BIDDER">BIDDER</option>
              <option value="SYSTEM">SYSTEM</option>
            </select>

            {/* Bidder Filter */}
            <select
              value={selectedBidder}
              onChange={(e) => setSelectedBidder(e.target.value)}
              className="border border-[#D9DEE3] text-[#10283A] text-xs rounded px-2.5 py-2 bg-white focus:outline-none"
            >
              <option value="ALL">All Bidders</option>
              {bidders.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.legal_name.slice(0, 25)}...
                </option>
              ))}
            </select>

            <button
              type="submit"
              className="px-4 py-2 bg-[#10283A] hover:bg-[#18374D] text-white text-xs font-semibold rounded transition-colors shadow-sm"
            >
              Filter
            </button>
          </div>
        </form>
      </div>

      {/* ── Dense Audit Event Table ── */}
      <div className="bg-white border border-[#D9DEE3] rounded shadow-sm overflow-hidden">
        <div className="p-3 border-b border-[#D9DEE3] bg-[#F8FAFC] flex items-center justify-between">
          <div className="text-xs font-bold text-[#10283A] font-mono uppercase tracking-wider">
            GFR 2017 Audit Telemetry ({events.length} Events Recorded)
          </div>
          <div className="text-[11px] text-[#66717C] font-mono">
            Immutable Storage &bull; Zero Silent Deletions
          </div>
        </div>

        {loading ? (
          <div className="p-12 text-center text-xs text-[#66717C]">
            <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-[#10283A]" />
            Loading cryptographic audit records...
          </div>
        ) : events.length === 0 ? (
          <div className="p-12 text-center text-xs text-[#66717C]">
            No audit records match the selected filters.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-[#EDF2F7] border-b border-[#CBD5E0] text-[#4A5568] font-mono text-[10px] uppercase tracking-wider">
                  <th className="py-2.5 px-3 w-40">Timestamp (UTC)</th>
                  <th className="py-2.5 px-3 w-36">User / Actor</th>
                  <th className="py-2.5 px-2 text-center w-24">Role</th>
                  <th className="py-2.5 px-3 w-48">Action</th>
                  <th className="py-2.5 px-2 w-28">Entity</th>
                  <th className="py-2.5 px-3">Description &amp; Context</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E2E8F0]">
                {events.map((ev) => {
                  const isOverride = ev.action === 'AI_RESULT_OVERRIDDEN';
                  const isFinal = ev.action === 'FINAL_BID_DECISION';
                  const isReport = ev.action === 'REPORT_GENERATED';
                  const isCompliance = ev.action.includes('COMPLIANCE');

                  return (
                    <tr
                      key={ev.event_id}
                      className={`hover:bg-[#F8FAFC] transition-colors ${
                        isOverride ? 'bg-[#FFFDF5]' : isFinal ? 'bg-[#F0FDF4]' : ''
                      }`}
                    >
                      <td className="py-2.5 px-3 font-mono text-[11px] text-[#66717C] whitespace-nowrap">
                        {new Date(ev.timestamp).toLocaleString('en-GB', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                          second: '2-digit',
                          hour12: false
                        })}
                      </td>
                      <td className="py-2.5 px-3 font-medium text-[#10283A] truncate max-w-[150px]" title={ev.user_name}>
                        {ev.user_name}
                      </td>
                      <td className="py-2.5 px-2 text-center">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                          ev.role === 'ADMIN' ? 'bg-[#EDE9FE] text-[#6D28D9]' :
                          ev.role === 'PROCUREMENT_OFFICER' ? 'bg-[#E0E7FF] text-[#3730A3]' :
                          ev.role === 'BIDDER' ? 'bg-[#FEF3C7] text-[#92400E]' : 'bg-[#F1F5F9] text-[#475569]'
                        }`}>
                          {ev.role === 'PROCUREMENT_OFFICER' ? 'OFFICER' : ev.role}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 font-mono">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          isOverride ? 'bg-[#FEF2F2] text-[#991B1B] border border-[#FECACA]' :
                          isFinal ? 'bg-[#DCFCE7] text-[#15803D] border border-[#BBF7D0]' :
                          isReport ? 'bg-[#E0F2FE] text-[#0369A1]' :
                          isCompliance ? 'bg-[#EAF5F0] text-[#1E5A47]' : 'bg-[#F1F5F9] text-[#334155]'
                        }`}>
                          {ev.action}
                        </span>
                      </td>
                      <td className="py-2.5 px-2 font-mono text-[11px] text-[#64748B]">
                        {ev.entity_type}
                      </td>
                      <td className="py-2.5 px-3 text-[#2D3748] leading-relaxed">
                        {ev.description}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
