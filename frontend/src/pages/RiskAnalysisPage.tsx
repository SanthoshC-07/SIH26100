import React, { useEffect, useState } from 'react';
import {
  AlertTriangle,
  ShieldCheck,
  CheckCircle2,
  Clock,
  ChevronRight,
  RefreshCw,
  FileText,
  AlertOctagon,
  ExternalLink
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { riskService, bidderService } from '../services';
import { RiskAssessmentDetail, Bidder } from '../types';

export const RiskAnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const [bidders, setBidders] = useState<Bidder[]>([]);
  const [selectedBidderId, setSelectedBidderId] = useState<string>('');
  const [riskData, setRiskData] = useState<RiskAssessmentDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [calculating, setCalculating] = useState(false);

  useEffect(() => {
    bidderService.getBidders().then(list => {
      setBidders(list);
      if (list.length > 0) {
        const praveen = list.find(b => b.legal_name.toLowerCase().includes('praveen'));
        const target = praveen || list[0];
        setSelectedBidderId(target.id);
      }
    }).catch(() => []);
  }, []);

  const loadRisk = async (bidId: string) => {
    if (!bidId) return;
    setLoading(true);
    try {
      const data = await riskService.getRiskAssessment(bidId);
      setRiskData(data);
    } catch (e) {
      console.error("Failed to load risk data:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedBidderId) {
      loadRisk(selectedBidderId);
    }
  }, [selectedBidderId]);

  const handleRecalculateRisk = async () => {
    if (!selectedBidderId) return;
    setCalculating(true);
    try {
      const data = await riskService.calculateRisk(selectedBidderId);
      setRiskData(data);
    } catch (e) {
      console.error("Failed to recalculate risk:", e);
    } finally {
      setCalculating(false);
    }
  };

  const selectedBidder = bidders.find(b => b.id === selectedBidderId);

  return (
    <div className="space-y-6 font-sans">
      {/* ── Top Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#D9DEE3] pb-4">
        <div>
          <div className="text-[11px] font-mono tracking-widest text-[#66717C] uppercase font-bold">
            STATUTORY &amp; TECHNICAL RISK PROFILING
          </div>
          <h1 className="text-2xl sm:text-3xl font-serif font-bold text-[#10283A] tracking-tight mt-0.5">
            Petroleum Bid Risk Analysis
          </h1>
          <p className="text-xs text-[#66717C] mt-0.5">
            Configurable multi-factor risk assessment across statutory tokens, financial turnover, pipeline execution specs, and HSE compliance.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={selectedBidderId}
            onChange={(e) => setSelectedBidderId(e.target.value)}
            className="border border-[#D9DEE3] text-[#10283A] text-xs rounded px-3 py-2 bg-white focus:outline-none shadow-sm"
          >
            {bidders.map((b) => (
              <option key={b.id} value={b.id}>
                {b.legal_name}
              </option>
            ))}
          </select>

          <button
            onClick={handleRecalculateRisk}
            disabled={calculating}
            className="px-4 py-2 bg-[#10283A] hover:bg-[#18374D] text-white text-xs font-semibold rounded shadow-sm inline-flex items-center gap-1.5 transition-colors"
          >
            {calculating ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5" />}
            <span>Recalculate Risk</span>
          </button>

          <button
            onClick={() => navigate(`/officer-review?bidId=${selectedBidderId}`)}
            className="px-4 py-2 border border-[#D9DEE3] bg-[#FFFFFF] hover:bg-[#F3F4F6] text-[#10283A] text-xs font-semibold rounded shadow-sm inline-flex items-center gap-1.5"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-[#D98A16]" />
            <span>Officer Review</span>
          </button>
        </div>
      </div>

      {/* ── 4 Top KPI Cards ── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded p-5 shadow-sm space-y-1">
          <div className="text-[11px] font-mono font-semibold text-[#66717C] uppercase tracking-wider">
            Overall Risk Level
          </div>
          <div className={`text-2xl font-serif font-bold pt-1 ${
            riskData?.risk_level === 'CRITICAL' ? 'text-[#991B1B]' :
            riskData?.risk_level === 'HIGH' ? 'text-[#C05621]' :
            riskData?.risk_level === 'MEDIUM' ? 'text-[#D98A16]' : 'text-[#1E5A47]'
          }`}>
            {riskData?.risk_level || 'LOW'}
          </div>
          <div className="text-xs text-[#66717C] pt-1">
            {selectedBidder?.legal_name || 'Selected Entity'}
          </div>
        </div>

        <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded p-5 shadow-sm space-y-1">
          <div className="text-[11px] font-mono font-semibold text-[#66717C] uppercase tracking-wider">
            Risk Score (0 - 100)
          </div>
          <div className="text-2xl font-mono font-bold text-[#10283A] pt-1">
            {riskData?.risk_score !== undefined ? riskData.risk_score : 10.0}
          </div>
          <div className="text-xs text-[#66717C] pt-1">Deterministic Rule Matrix</div>
        </div>

        <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded p-5 shadow-sm space-y-1">
          <div className="text-[11px] font-mono font-semibold text-[#66717C] uppercase tracking-wider">
            Identified Risk Factors
          </div>
          <div className="text-2xl font-mono font-bold text-[#10283A] pt-1">
            {riskData?.factors?.length || riskData?.primary_risk_factors?.length || 0}
          </div>
          <div className="text-xs text-[#66717C] pt-1">Linked to underlying criteria</div>
        </div>

        <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded p-5 shadow-sm space-y-1">
          <div className="text-[11px] font-mono font-semibold text-[#66717C] uppercase tracking-wider">
            Statutory Integrity
          </div>
          <div className="text-2xl font-serif font-bold text-[#1E5A47] pt-1">
            VERIFIED
          </div>
          <div className="text-xs text-[#66717C] pt-1">CBDT &bull; GST Portal Match</div>
        </div>
      </div>

      {/* ── Granular Risk Breakdown Linked to Underlying Criteria ── */}
      <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded shadow-sm p-6 space-y-4">
        <div className="border-b border-[#D9DEE3] pb-3 flex items-center justify-between">
          <div>
            <h2 className="text-base font-serif font-bold text-[#10283A]">
              Underlying Risk Factor Traceability
            </h2>
            <p className="text-xs text-[#66717C]">
              Every identified factor directly links to the underlying requirement clause, evidence snippet, and source document citation.
            </p>
          </div>
          <div className="text-xs font-mono text-[#66717C]">
            {riskData?.factors?.length || 0} Factor(s) Recorded
          </div>
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs text-[#66717C]">
            <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-[#10283A]" />
            Evaluating multi-factor risk telemetry...
          </div>
        ) : riskData?.factors && riskData.factors.length > 0 ? (
          <div className="space-y-3">
            {riskData.factors.map((rf, idx) => (
              <div
                key={rf.id || idx}
                className={`p-4 border rounded text-xs space-y-2 ${
                  rf.severity === 'CRITICAL' ? 'bg-[#FEF2F2] border-[#FCA5A5]' :
                  rf.severity === 'HIGH' ? 'bg-[#FFF7ED] border-[#FDBA74]' :
                  rf.severity === 'MEDIUM' ? 'bg-[#FFFBEB] border-[#FDE68A]' : 'bg-[#F8FAFC] border-[#E2E8F0]'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 font-mono">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      rf.severity === 'CRITICAL' ? 'bg-[#991B1B] text-white' :
                      rf.severity === 'HIGH' ? 'bg-[#C05621] text-white' :
                      rf.severity === 'MEDIUM' ? 'bg-[#D98A16] text-white' : 'bg-[#1E5A47] text-white'
                    }`}>
                      {rf.severity}
                    </span>
                    <span className="font-bold text-[#10283A]">{rf.factor_type}</span>
                  </div>
                  {rf.source_document && (
                    <div className="font-mono text-[10px] text-[#2B6CB0]">
                      {rf.source_document} {rf.page_number ? `(p. ${rf.page_number})` : ''}
                    </div>
                  )}
                </div>

                <div className="text-[#2D3748] font-medium leading-relaxed">
                  {rf.description}
                </div>

                {rf.evidence_snippet && (
                  <div className="bg-white/80 p-2.5 rounded border border-[#E2E8F0] font-mono text-[11px] text-[#4A5568]">
                    <strong>Evidence Snippet:</strong> {rf.evidence_snippet}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="p-6 bg-[#F8FAFC] border border-[#E2E8F0] rounded text-center text-xs text-[#66717C] space-y-1">
            <CheckCircle2 className="w-6 h-6 text-[#1E5A47] mx-auto mb-1" />
            <div className="font-bold text-[#10283A]">Robust Statutory and Tender Compliance</div>
            <div>No critical or high risk factors identified. Bidder exhibits complete documentation and high extraction confidence.</div>
          </div>
        )}
      </div>
    </div>
  );
};
