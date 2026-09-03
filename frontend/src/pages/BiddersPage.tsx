import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { bidderService } from '../services';
import { Bidder } from '../types';
import { RiskBadge } from '../components/RiskBadge';
import { Search, Users, ArrowRight, FileText, CheckCircle2, AlertTriangle, ShieldCheck, Filter } from 'lucide-react';

export const BiddersPage: React.FC = () => {
  const navigate = useNavigate();
  const [bidders, setBidders] = useState<Bidder[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    bidderService.getBidders().then(setBidders).finally(() => setLoading(false));
  }, []);

  const filtered = bidders.filter((b) => {
    const matchSearch =
      b.bidder_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (b.gstin && b.gstin.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (b.pan && b.pan.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchRisk = riskFilter ? b.risk_level === riskFilter : true;
    return matchSearch && matchRisk;
  });

  return (
    <div className="space-y-6">
      
      {/* Header Banner */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="text-[10px] font-mono uppercase tracking-widest text-emerald-700 font-bold">
            BIDDER DIRECTORY & ELIGIBILITY VERIFICATION
          </div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900 mt-0.5">
            Submitted Bidder Compliance Dossiers
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Audit ground-truth evidence, examine cross-document entity matches, and record officer reviews
          </p>
        </div>
        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 font-bold border border-slate-200">
            TOTAL DOSSIERS: {bidders.length}
          </span>
        </div>
      </div>

      {/* Search & Risk Filter Toolbar */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 flex flex-col sm:flex-row gap-3 items-center justify-between font-mono text-xs">
        <div className="relative w-full sm:max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search bidder legal name, GSTIN, or PAN..."
            className="w-full rounded-lg border border-slate-300 pl-9 pr-3 py-2 text-slate-800 outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
          <Filter className="w-4 h-4 text-slate-400" />
          <span className="text-[10px] font-bold text-slate-500 uppercase">RISK FILTER:</span>
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="rounded-lg border border-slate-300 p-2 bg-white text-slate-800 outline-none text-xs font-semibold"
          >
            <option value="">ALL RISK LEVELS</option>
            <option value="LOW">LOW RISK</option>
            <option value="MEDIUM">MEDIUM RISK</option>
            <option value="HIGH">HIGH RISK</option>
            <option value="CRITICAL">CRITICAL RISK</option>
          </select>
        </div>
      </div>

      {/* Bidders Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-500 font-mono text-xs">
            RETRIEVING BIDDER COMPLIANCE DOSSIERS...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="border-b border-slate-200 bg-slate-50/70 text-slate-600 text-[10px] uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-3.5">BIDDER LEGAL ENTITY</th>
                  <th className="px-6 py-3.5">IDENTIFIERS (GSTIN / PAN / UDYAM)</th>
                  <th className="px-6 py-3.5 text-center">SCORE</th>
                  <th className="px-6 py-3.5 text-center">RISK LEVEL</th>
                  <th className="px-6 py-3.5">AI RECOMMENDATION</th>
                  <th className="px-6 py-3.5 text-center">ATTACHMENTS</th>
                  <th className="px-6 py-3.5 text-right">AUDIT ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-800">
                {filtered.map((b) => (
                  <tr key={b.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-4 font-bold font-sans">
                      <div className="text-xs text-slate-900 font-bold">{b.bidder_name}</div>
                      <div className="text-[11px] font-mono text-slate-500 font-normal mt-0.5">{b.contact_person || "Authorized Representative"}</div>
                    </td>
                    <td className="px-6 py-4 text-[11px] space-y-0.5 whitespace-nowrap">
                      <div className="font-bold text-slate-900">{b.gstin || "NO GSTIN"}</div>
                      <div className="text-slate-500">{b.pan ? `PAN: ${b.pan}` : ""}</div>
                      {b.udyam_number && <div className="text-emerald-700 font-semibold text-[10px]">{b.udyam_number}</div>}
                    </td>
                    <td className="px-6 py-4 text-center font-bold text-sm">
                      {b.compliance_score !== null && b.compliance_score !== undefined ? (
                        <span className={`px-2 py-0.5 rounded ${b.compliance_score >= 90 ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : (b.compliance_score >= 75 ? 'bg-amber-50 text-amber-700 border border-amber-200' : 'bg-red-50 text-red-700 border border-red-200')}`}>
                          {b.compliance_score}/100
                        </span>
                      ) : (
                        <span className="text-slate-400">EVALUATING</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-center whitespace-nowrap">
                      {b.risk_level ? (
                        <RiskBadge level={b.risk_level} size="sm" />
                      ) : (
                        <span className="text-slate-400">PENDING</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-xs font-sans text-slate-800">
                      {b.recommendation_type === "RECOMMENDED_FOR_QUALIFICATION" && "Eligible for Qualification"}
                      {b.recommendation_type === "NOT_RECOMMENDED" && "Mandatory Failure / Disqualified"}
                      {b.recommendation_type === "REQUIRES_PROCUREMENT_OFFICER_REVIEW" && "Requires Officer Review"}
                      {!b.recommendation_type && "Under Verification"}
                    </td>
                    <td className="px-6 py-4 text-center whitespace-nowrap">
                      <span className="px-2 py-0.5 rounded border border-slate-200 bg-slate-50 text-slate-600 text-[10px] font-semibold">
                        {b.documents_count || 1} FILES
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right whitespace-nowrap">
                      <button
                        onClick={() => navigate(`/bidders/${b.id}`)}
                        className="px-3.5 py-1.5 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs shadow-sm transition-all flex items-center gap-1 ml-auto"
                      >
                        <span>Audit Dossier</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
};
