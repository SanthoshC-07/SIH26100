import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  FileText,
  Calendar,
  Clock,
  ShieldCheck,
  AlertTriangle,
  Download,
  CheckCircle2,
  FileDown,
  Eye,
  Check,
  Printer,
  X,
  RefreshCw,
  Building,
  UserCheck
} from 'lucide-react';
import { reportService, bidderService } from '../services';
import { ComplianceReport, Bidder } from '../types';

export const ReportsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const queryBidId = searchParams.get('bidId');

  const [bidders, setBidders] = useState<Bidder[]>([]);
  const [selectedBidderId, setSelectedBidderId] = useState<string>('');
  const [liveReport, setLiveReport] = useState<ComplianceReport | null>(null);
  const [loadingReport, setLoadingReport] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState<string | null>(null);

  // Load Bidders
  useEffect(() => {
    bidderService.getBidders().then(list => {
      setBidders(list);
      if (list.length > 0) {
        const target = queryBidId
          ? list.find(b => b.id === queryBidId) || list[0]
          : list.find(b => b.legal_name.toLowerCase().includes('praveen')) || list[0];
        setSelectedBidderId(target.id);
      }
    }).catch(() => []);
  }, [queryBidId]);

  const loadReport = async (bidId: string) => {
    if (!bidId) return;
    setLoadingReport(true);
    try {
      const rep = await reportService.getReport(bidId);
      setLiveReport(rep);
    } catch (e) {
      console.error("Failed to load report:", e);
    } finally {
      setLoadingReport(false);
    }
  };

  useEffect(() => {
    if (selectedBidderId) {
      loadReport(selectedBidderId);
    }
  }, [selectedBidderId]);

  const handleGenerateFreshReport = async () => {
    if (!selectedBidderId) return;
    setLoadingReport(true);
    try {
      const rep = await reportService.generateReport(selectedBidderId);
      setLiveReport(rep);
      setDownloadSuccess("Generated updated official compliance report.");
      setTimeout(() => setDownloadSuccess(null), 3500);
    } catch (e) {
      console.error("Error generating fresh report:", e);
    } finally {
      setLoadingReport(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-6 font-sans">
      {/* ── Header ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#D9DEE3] pb-4">
        <div>
          <div className="text-[11px] font-mono tracking-widest text-[#66717C] uppercase font-bold">
            STATUTORY COMPLIANCE DOSSIERS &bull; GFR 2017
          </div>
          <h1 className="text-2xl font-serif font-bold text-[#10283A] tracking-tight mt-0.5">
            Petroleum Bid Compliance Reports
          </h1>
          <p className="text-xs text-[#66717C] mt-0.5">
            Executive briefings, clause-by-clause evidence citations, officer override logs, and risk analysis.
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
            onClick={handleGenerateFreshReport}
            disabled={loadingReport}
            className="px-4 py-2 bg-[#10283A] hover:bg-[#18374D] text-white text-xs font-semibold rounded shadow-sm inline-flex items-center gap-1.5 transition-colors"
          >
            {loadingReport ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <FileText className="w-3.5 h-3.5 text-[#D98A16]" />}
            <span>Regenerate Report</span>
          </button>
        </div>
      </div>

      {downloadSuccess && (
        <div className="bg-[#EAF5F0] border-l-4 border-[#1E5A47] p-3 text-xs text-[#1E5A47] font-medium flex items-center gap-2 shadow-sm">
          <Check className="w-4 h-4" />
          <span>{downloadSuccess}</span>
        </div>
      )}

      {/* ── Active Report Card ── */}
      {liveReport ? (
        <div className="bg-white border border-[#D9DEE3] rounded p-6 shadow-sm space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#D9DEE3] pb-4">
            <div>
              <div className="text-[10px] font-mono uppercase font-bold text-[#D98A16]">
                Report Ref: {liveReport.report_number} &bull; Official Evaluation Dossier
              </div>
              <h2 className="text-xl font-serif font-bold text-[#10283A] mt-0.5">
                {liveReport.title}
              </h2>
              <div className="text-xs text-[#66717C] mt-1 font-mono">
                Generated by: {liveReport.generated_by_name} &bull; Assessment Date: {new Date(liveReport.assessment_date).toLocaleString()}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowReportModal(true)}
                className="px-4 py-2 border border-[#D9DEE3] hover:bg-[#F3F4F6] text-[#10283A] text-xs font-semibold rounded shadow-sm inline-flex items-center gap-1.5"
              >
                <Eye className="w-3.5 h-3.5 text-[#10283A]" />
                <span>View Full Printable Dossier</span>
              </button>

              <a
                href={reportService.getDownloadUrl(liveReport.bid_id)}
                target="_blank"
                rel="noreferrer"
                className="px-4 py-2 bg-[#1E5A47] hover:bg-[#164738] text-white text-xs font-semibold rounded shadow-sm inline-flex items-center gap-1.5"
              >
                <FileDown className="w-3.5 h-3.5" />
                <span>Open Printable HTML</span>
              </a>
            </div>
          </div>

          {/* Executive Summary Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-[#F8FAFC] border border-[#E2E8F0] p-4 rounded text-xs font-mono">
            <div>
              <div className="text-[10px] text-[#66717C] uppercase font-bold">Compliance Score</div>
              <div className="text-xl font-bold text-[#1E5A47] mt-0.5">{liveReport.compliance_score}%</div>
            </div>
            <div>
              <div className="text-[10px] text-[#66717C] uppercase font-bold">Risk Level</div>
              <div className={`text-xl font-bold mt-0.5 ${
                liveReport.risk_level === 'CRITICAL' ? 'text-[#991B1B]' :
                liveReport.risk_level === 'HIGH' ? 'text-[#C05621]' :
                liveReport.risk_level === 'MEDIUM' ? 'text-[#D98A16]' : 'text-[#1E5A47]'
              }`}>{liveReport.risk_level}</div>
            </div>
            <div>
              <div className="text-[10px] text-[#66717C] uppercase font-bold">AI Recommendation</div>
              <div className="text-xs font-bold text-[#10283A] mt-1 truncate" title={liveReport.ai_recommendation}>
                {liveReport.ai_recommendation}
              </div>
            </div>
            <div>
              <div className="text-[10px] text-[#66717C] uppercase font-bold">Final Officer Decision</div>
              <div className="text-xs font-bold text-[#10283A] mt-1 font-mono">
                {liveReport.final_officer_decision || 'PENDING OFFICER DETERMINATION'}
              </div>
            </div>
          </div>

          {/* Legal Governance Notice */}
          <div className="bg-[#FEF7EC] border-l-4 border-[#D98A16] p-3 text-xs text-[#78350F]">
            <strong>STATUTORY NOTICE:</strong> AI-generated results are decision support. Final procurement decision is made by the Procurement Officer per General Financial Rules (GFR 2017).
          </div>

          {/* Detailed Findings Table */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-[#10283A] uppercase font-mono tracking-wider">
              Detailed Findings &amp; Evidence Traceability ({liveReport.detailed_findings?.length || 0} Clauses)
            </h3>
            <div className="border border-[#D9DEE3] rounded overflow-hidden">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="bg-[#EDF2F7] border-b border-[#CBD5E0] text-[#4A5568] font-mono text-[10px] uppercase">
                    <th className="py-2.5 px-3 w-24">Clause</th>
                    <th className="py-2.5 px-3 w-32">Category</th>
                    <th className="py-2.5 px-3">Requirement &amp; Submitted Evidence</th>
                    <th className="py-2.5 px-3 w-20 text-center">Result</th>
                    <th className="py-2.5 px-3 w-16 text-right">Conf.</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E2E8F0]">
                  {(liveReport.detailed_findings || []).map((f, idx) => (
                    <tr key={idx} className="hover:bg-[#F8FAFC]">
                      <td className="py-2.5 px-3 font-mono font-bold text-[#10283A]">{f.clause_number}</td>
                      <td className="py-2.5 px-3 font-semibold text-[#2D3748]">{f.category}</td>
                      <td className="py-2.5 px-3">
                        <div className="text-[#10283A] font-medium">{f.requirement_text}</div>
                        <div className="text-[11px] text-[#4A5568] mt-1 font-mono">
                          Evidence: <span className="text-[#10283A]">{f.evidence}</span>
                        </div>
                        <div className="text-[10px] text-[#2B6CB0] mt-0.5">
                          Source: {f.source_document} (p. {f.page}) &bull; <span className="font-bold">{f.external_verification}</span>
                        </div>
                      </td>
                      <td className="py-2.5 px-3 text-center">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                          f.rule_result === 'PASS' ? 'bg-[#EAF5F0] text-[#1E5A47]' :
                          f.rule_result === 'REVIEW' ? 'bg-[#FEF7EC] text-[#B7791F]' : 'bg-[#FEF2F2] text-[#991B1B]'
                        }`}>
                          {f.rule_result}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-right font-mono text-[11px] font-bold text-[#10283A]">
                        {(f.confidence * 100).toFixed(0)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Officer Overrides Log */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-[#10283A] uppercase font-mono tracking-wider">
              Procurement Officer Override Determinations
            </h3>
            <div className="border border-[#D9DEE3] rounded overflow-hidden">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="bg-[#EDF2F7] border-b border-[#CBD5E0] text-[#4A5568] font-mono text-[10px] uppercase">
                    <th className="py-2.5 px-3 w-28">Type</th>
                    <th className="py-2.5 px-3 w-24">AI Status</th>
                    <th className="py-2.5 px-3 w-28">Officer Status</th>
                    <th className="py-2.5 px-3">Documented Justification</th>
                    <th className="py-2.5 px-3 w-40">Officer Sign-Off</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E2E8F0]">
                  {liveReport.officer_decisions?.length ? (
                    liveReport.officer_decisions.map((od, i) => (
                      <tr key={i} className="hover:bg-[#F8FAFC]">
                        <td className="py-2.5 px-3 font-mono font-semibold">{od.decision_type}</td>
                        <td className="py-2.5 px-3 font-mono">{od.ai_status}</td>
                        <td className="py-2.5 px-3 font-mono font-bold text-[#1E5A47]">{od.officer_status}</td>
                        <td className="py-2.5 px-3 text-[#2D3748] italic">{od.officer_reason}</td>
                        <td className="py-2.5 px-3 text-[11px] text-[#66717C]">
                          {od.officer_name}<br/>{od.timestamp ? new Date(od.timestamp).toLocaleDateString() : ''}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={5} className="p-4 text-center text-xs text-[#718096]">
                        No officer overrides recorded. All determinations align with AI decision support baseline.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : loadingReport ? (
        <div className="bg-white border border-[#D9DEE3] p-12 text-center text-xs text-[#66717C]">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-[#10283A]" />
          Compiling Petroleum Bid Compliance Report...
        </div>
      ) : null}

      {/* ── Modal: Full Printable HTML Report ── */}
      {showReportModal && liveReport && (
        <div className="fixed inset-0 z-50 bg-[#10283A]/80 flex items-center justify-center p-4">
          <div className="bg-white border border-[#D9DEE3] rounded max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl">
            <div className="p-4 border-b border-[#D9DEE3] flex items-center justify-between bg-[#F8FAFC]">
              <div className="text-xs font-bold font-mono text-[#10283A]">
                Printable Compliance Report: {liveReport.report_number}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handlePrint}
                  className="px-3 py-1.5 bg-[#10283A] text-white text-xs font-semibold rounded flex items-center gap-1"
                >
                  <Printer className="w-3.5 h-3.5" />
                  <span>Print Document</span>
                </button>
                <button
                  onClick={() => setShowReportModal(false)}
                  className="p-1.5 text-[#66717C] hover:text-[#10283A]"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              <div
                dangerouslySetInnerHTML={{ __html: liveReport.html_content || '<p>Report content unavailable</p>' }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
