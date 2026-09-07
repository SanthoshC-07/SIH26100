import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  FileText,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  RotateCcw,
  Check,
  UserCheck,
  AlertOctagon,
  RefreshCw,
  Printer,
  FileDown
} from 'lucide-react';
import { officerReviewService, bidderService, reportService, complianceService } from '../services';
import { OfficerReviewWorkspace as IWorkspace, OfficerRequirementRow, Bidder } from '../types';

export const OfficerReviewWorkspace: React.FC = () => {
  const { bidId: paramBidId } = useParams<{ bidId?: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const queryBidId = searchParams.get('bidId');
  const activeBidId = paramBidId || queryBidId;

  const [bidders, setBidders] = useState<Bidder[]>([]);
  const [selectedBidderId, setSelectedBidderId] = useState<string>(activeBidId || '');
  const [workspace, setWorkspace] = useState<IWorkspace | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>({});

  // Override Modal state
  const [overrideModalOpen, setOverrideModalOpen] = useState(false);
  const [activeReqForOverride, setActiveReqForOverride] = useState<OfficerRequirementRow | null>(null);
  const [overrideDecision, setOverrideDecision] = useState<string>('REVIEW');
  const [overrideReason, setOverrideReason] = useState<string>('');
  const [overrideSubmitting, setOverrideSubmitting] = useState(false);
  const [overrideError, setOverrideError] = useState<string | null>(null);

  // Final Decision Modal state
  const [finalModalOpen, setFinalModalOpen] = useState(false);
  const [finalDecisionChoice, setFinalDecisionChoice] = useState<'QUALIFIED' | 'DISQUALIFIED' | 'REVIEW / HOLD'>('QUALIFIED');
  const [finalRemarks, setFinalRemarks] = useState<string>('');
  const [finalConfirmed, setFinalConfirmed] = useState<boolean>(false);
  const [finalSubmitting, setFinalSubmitting] = useState(false);
  const [finalError, setFinalError] = useState<string | null>(null);
  const [notification, setNotification] = useState<string | null>(null);

  // Load Bidders
  useEffect(() => {
    const fetchBidders = async () => {
      try {
        const list = await bidderService.getBidders();
        setBidders(list);
        if (!selectedBidderId && list.length > 0) {
          const praveen = list.find(b => b.legal_name.toLowerCase().includes('praveen'));
          const target = praveen || list[0];
          setSelectedBidderId(target.id);
        }
      } catch (e) {
        console.error("Failed to load bidders list:", e);
      }
    };
    fetchBidders();
  }, []);

  // Load Workspace Data
  const loadWorkspaceData = async (bidId: string) => {
    if (!bidId) return;
    setLoading(true);
    setErrorMessage(null);
    try {
      let data = await officerReviewService.getWorkspace(bidId);
      if (!data || !data.requirements || data.requirements.length === 0) {
        await complianceService.runComplianceEvaluation(bidId);
        data = await officerReviewService.getWorkspace(bidId);
      }
      setWorkspace(data);
    } catch (e: any) {
      console.warn("Retrying officer review workspace after evaluation trigger:", e);
      try {
        await complianceService.runComplianceEvaluation(bidId);
        const data = await officerReviewService.getWorkspace(bidId);
        setWorkspace(data);
      } catch (err2: any) {
        console.error("Failed to load officer review workspace:", err2);
        setErrorMessage(err2.response?.data?.detail || e.response?.data?.detail || "Failed to load procurement dossier.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedBidderId) {
      loadWorkspaceData(selectedBidderId);
    }
  }, [selectedBidderId]);

  const toggleRowExpand = (reqId: string) => {
    setExpandedRows(prev => ({
      ...prev,
      [reqId]: !prev[reqId]
    }));
  };

  // Quick Accept AI Result
  const handleAcceptAi = async (req: OfficerRequirementRow) => {
    if (!selectedBidderId) return;
    try {
      await officerReviewService.submitRequirementDecision(selectedBidderId, req.requirement_id, {
        decision: 'ACCEPT_AI_RESULT',
        reason: `Officer accepted AI baseline determination (${req.ai_status}).`
      });
      setNotification(`Accepted AI result (${req.ai_status}) for Clause ${req.clause_number}`);
      setTimeout(() => setNotification(null), 3500);
      loadWorkspaceData(selectedBidderId);
    } catch (e: any) {
      console.error("Error accepting AI result:", e);
      alert(e.response?.data?.detail || "Failed to accept AI result.");
    }
  };

  // Open Override Modal
  const handleOpenOverride = (req: OfficerRequirementRow) => {
    setActiveReqForOverride(req);
    setOverrideDecision(req.ai_status === 'PASS' ? 'REVIEW' : (req.ai_status === 'FAIL' ? 'PASS' : 'PASS'));
    setOverrideReason('');
    setOverrideError(null);
    setOverrideModalOpen(true);
  };

  // Submit Override
  const handleSubmitOverride = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!overrideReason.trim()) {
      setOverrideError("Mandatory justification is required to override AI baseline.");
      return;
    }
    if (!activeReqForOverride || !selectedBidderId) return;

    setOverrideSubmitting(true);
    setOverrideError(null);
    try {
      await officerReviewService.submitRequirementDecision(selectedBidderId, activeReqForOverride.requirement_id, {
        decision: overrideDecision,
        reason: overrideReason.trim()
      });
      setOverrideModalOpen(false);
      setNotification(`Recorded officer override for ${activeReqForOverride.clause_number}: ${overrideDecision}`);
      setTimeout(() => setNotification(null), 4000);
      loadWorkspaceData(selectedBidderId);
    } catch (err: any) {
      console.error("Override submission failed:", err);
      setOverrideError(err.response?.data?.detail || "Failed to submit override.");
    } finally {
      setOverrideSubmitting(false);
    }
  };

  // Open Final Bid Decision Modal
  const handleOpenFinalDecision = () => {
    if (!workspace) return;
    const hasFails = workspace.requirements.some(r => (r.officer_decision?.decision || r.ai_status) === 'FAIL');
    const hasReviews = workspace.requirements.some(r => (r.officer_decision?.decision || r.ai_status) === 'REVIEW');
    
    if (hasFails) {
      setFinalDecisionChoice('DISQUALIFIED');
    } else if (hasReviews) {
      setFinalDecisionChoice('REVIEW / HOLD');
    } else {
      setFinalDecisionChoice('QUALIFIED');
    }
    setFinalRemarks('');
    setFinalConfirmed(false);
    setFinalError(null);
    setFinalModalOpen(true);
  };

  // Submit Final Decision
  const handleSubmitFinalDecision = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!finalConfirmed) {
      setFinalError("Please confirm your authority as Procurement Officer by checking the confirmation box.");
      return;
    }
    if (!finalRemarks.trim()) {
      setFinalError("Procurement Officer evaluation remarks are mandatory.");
      return;
    }
    if (!selectedBidderId) return;

    setFinalSubmitting(true);
    setFinalError(null);
    try {
      await officerReviewService.submitFinalDecision(selectedBidderId, {
        decision: finalDecisionChoice,
        remarks: finalRemarks.trim(),
        confirmed: true
      });
      setFinalModalOpen(false);
      setNotification(`Final Procurement Determination recorded: ${finalDecisionChoice}`);
      setTimeout(() => setNotification(null), 5000);
      loadWorkspaceData(selectedBidderId);
    } catch (err: any) {
      console.error("Final decision failed:", err);
      setFinalError(err.response?.data?.detail || "Failed to record final decision.");
    } finally {
      setFinalSubmitting(false);
    }
  };

  const overriddenCount = workspace?.requirements.filter(r => r.officer_decision?.is_override).length || 0;
  const highRiskCount = workspace?.requirements.filter(r => r.risk === 'HIGH' || r.risk === 'CRITICAL').length || 0;
  const outstandingReviewCount = workspace?.requirements.filter(r => (r.officer_decision?.decision || r.ai_status) === 'REVIEW').length || 0;

  return (
    <div className="space-y-5 font-sans">
      {/* ── Top Header & Bidder Selector ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#D9DEE3] pb-4">
        <div>
          <div className="text-[11px] font-mono tracking-widest text-[#66717C] uppercase font-bold">
            MINISTRY OF PETROLEUM &amp; NATURAL GAS &bull; TENDER EVALUATION CELL
          </div>
          <h1 className="text-2xl font-serif font-bold text-[#10283A] tracking-tight mt-0.5">
            Procurement Officer Review Workspace
          </h1>
          <p className="text-xs text-[#66717C] mt-0.5">
            GFR 2017 compliant human-in-the-loop eligibility verification and final procurement determination.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={selectedBidderId}
            onChange={(e) => setSelectedBidderId(e.target.value)}
            className="bg-[#FFFFFF] border border-[#D9DEE3] text-[#10283A] text-xs font-medium rounded px-3 py-2 shadow-sm focus:outline-none focus:border-[#10283A]"
          >
            {bidders.map((b) => (
              <option key={b.id} value={b.id}>
                {b.legal_name}
              </option>
            ))}
          </select>

          <button
            onClick={() => loadWorkspaceData(selectedBidderId)}
            className="p-2 border border-[#D9DEE3] bg-[#FFFFFF] hover:bg-[#F3F4F6] text-[#10283A] rounded shadow-sm"
            title="Refresh Evaluation Data"
          >
            <RefreshCw className="w-4 h-4 text-[#66717C]" />
          </button>

          <button
            onClick={() => navigate(`/reports?bidId=${selectedBidderId}`)}
            className="px-4 py-2 border border-[#D9DEE3] bg-[#FFFFFF] hover:bg-[#F3F4F6] text-[#10283A] text-xs font-semibold rounded shadow-sm inline-flex items-center gap-1.5"
          >
            <FileText className="w-3.5 h-3.5 text-[#10283A]" />
            <span>Generate Report</span>
          </button>
        </div>
      </div>

      {/* ── Notification Toast ── */}
      {notification && (
        <div className="bg-[#EAF5F0] border-l-4 border-[#1E5A47] p-3 text-xs text-[#1E5A47] font-medium flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4" />
            <span>{notification}</span>
          </div>
        </div>
      )}

      {/* ── Institutional Legal Disclaimer Banner ── */}
      <div className="bg-[#FEF7EC] border border-[#F3DEB8] border-l-4 border-l-[#D98A16] p-3.5 rounded-sm flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-[#D98A16] flex-shrink-0 mt-0.5" />
        <div className="text-xs text-[#78350F] leading-relaxed">
          <strong>LEGAL MANDATE &bull; GFR 2017:</strong> AI-generated results are decision support. Final procurement decision is made exclusively by the designated Procurement Officer. All overrides preserve the immutable AI baseline and require documented statutory justification.
        </div>
      </div>

      {loading ? (
        <div className="bg-white border border-[#D9DEE3] p-12 text-center text-xs text-[#66717C]">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-[#10283A]" />
          Loading dense procurement dossier...
        </div>
      ) : workspace ? (
        <>
          {/* ── 6 Top KPI / Dossier Cards ── */}
          <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
            <div className="bg-white border border-[#D9DEE3] p-3.5 rounded shadow-sm">
              <div className="text-[10px] font-mono font-semibold text-[#66717C] uppercase">Tender Ref</div>
              <div className="text-xs font-bold text-[#10283A] font-mono truncate mt-1" title={workspace.tender.tender_number}>
                {workspace.tender.tender_number}
              </div>
              <div className="text-[10px] text-[#66717C] truncate">{workspace.tender.organization}</div>
            </div>

            <div className="bg-white border border-[#D9DEE3] p-3.5 rounded shadow-sm">
              <div className="text-[10px] font-mono font-semibold text-[#66717C] uppercase">Bidder Entity</div>
              <div className="text-xs font-bold text-[#10283A] truncate mt-1" title={workspace.bidder.legal_name}>
                {workspace.bidder.legal_name}
              </div>
              <div className="text-[10px] font-mono text-[#66717C]">GSTIN: {workspace.bidder.gstin || 'N/A'}</div>
            </div>

            <div className="bg-white border border-[#D9DEE3] p-3.5 rounded shadow-sm">
              <div className="text-[10px] font-mono font-semibold text-[#66717C] uppercase">Compliance Score</div>
              <div className="text-lg font-mono font-bold text-[#1E5A47] mt-0.5">
                {workspace.compliance_score}%
              </div>
              <div className="text-[10px] text-[#66717C]">Threshold: &ge; 70.0%</div>
            </div>

            <div className="bg-white border border-[#D9DEE3] p-3.5 rounded shadow-sm">
              <div className="text-[10px] font-mono font-semibold text-[#66717C] uppercase">Overall Risk</div>
              <div className={`text-base font-bold font-serif mt-0.5 ${
                workspace.risk_level === 'CRITICAL' ? 'text-[#991B1B]' :
                workspace.risk_level === 'HIGH' ? 'text-[#C05621]' :
                workspace.risk_level === 'MEDIUM' ? 'text-[#D98A16]' : 'text-[#1E5A47]'
              }`}>
                {workspace.risk_level}
              </div>
              <div className="text-[10px] text-[#66717C]">{highRiskCount} critical/high flags</div>
            </div>

            <div className="bg-white border border-[#D9DEE3] p-3.5 rounded shadow-sm">
              <div className="text-[10px] font-mono font-semibold text-[#66717C] uppercase">AI Recommendation</div>
              <div className="text-xs font-bold text-[#10283A] truncate mt-1" title={workspace.recommendation}>
                {workspace.recommendation}
              </div>
              <div className="text-[10px] text-[#66717C]">Decision Support Only</div>
            </div>

            <div className="bg-white border border-[#D9DEE3] p-3.5 rounded shadow-sm flex flex-col justify-between">
              <div>
                <div className="text-[10px] font-mono font-semibold text-[#66717C] uppercase">Final Officer Decision</div>
                <div className={`text-xs font-bold font-mono mt-1 ${
                  workspace.final_decision?.decision === 'QUALIFIED' ? 'text-[#1E5A47]' :
                  workspace.final_decision?.decision === 'DISQUALIFIED' ? 'text-[#991B1B]' : 'text-[#D98A16]'
                }`}>
                  {workspace.final_decision?.decision || 'NOT RECORDED'}
                </div>
              </div>
              <button
                onClick={handleOpenFinalDecision}
                className="mt-1 w-full py-1 bg-[#10283A] hover:bg-[#18374D] text-white text-[11px] font-semibold rounded transition-colors"
              >
                {workspace.final_decision ? 'Update Final Decision' : 'Submit Final Decision'}
              </button>
            </div>
          </div>

          {/* ── Dense Enterprise Requirements Table ── */}
          <div className="bg-white border border-[#D9DEE3] rounded shadow-sm overflow-hidden">
            <div className="p-3 border-b border-[#D9DEE3] bg-[#F8FAFC] flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-[#10283A] uppercase tracking-wider font-mono">
                  Petroleum Tender Eligibility Clauses ({workspace.requirements.length} Requirements)
                </span>
              </div>
              <div className="text-[11px] text-[#66717C] font-mono">
                {overriddenCount} Overridden by Officer &bull; {outstandingReviewCount} In Review
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#EDF2F7] border-b border-[#CBD5E0] text-[#4A5568] font-mono text-[10px] uppercase tracking-wider">
                    <th className="py-2.5 px-3 w-8"></th>
                    <th className="py-2.5 px-3 w-24">Clause</th>
                    <th className="py-2.5 px-3 w-28">Category</th>
                    <th className="py-2.5 px-3 min-w-[200px]">Requirement Text</th>
                    <th className="py-2.5 px-3 min-w-[150px]">Source Doc / Page</th>
                    <th className="py-2.5 px-2 text-center w-16">Rule</th>
                    <th className="py-2.5 px-2 text-center w-14">Semantic</th>
                    <th className="py-2.5 px-2 text-center w-14">Conf.</th>
                    <th className="py-2.5 px-2 text-center w-20">AI Status</th>
                    <th className="py-2.5 px-2 text-center w-16">Risk</th>
                    <th className="py-2.5 px-3 text-center min-w-[200px]">Officer Decision</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E2E8F0]">
                  {workspace.requirements.map((req) => {
                    const isExpanded = !!expandedRows[req.requirement_id];
                    const hasDecision = !!req.officer_decision;
                    const isOverride = !!req.officer_decision?.is_override;
                    const effectiveStatus = req.officer_decision?.decision || req.ai_status;

                    return (
                      <React.Fragment key={req.requirement_id}>
                        <tr className={`hover:bg-[#F8FAFC] transition-colors ${isOverride ? 'bg-[#FFFDF5]' : ''}`}>
                          <td className="py-2.5 px-3 text-center">
                            <button
                              onClick={() => toggleRowExpand(req.requirement_id)}
                              className="text-[#66717C] hover:text-[#10283A]"
                            >
                              {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                            </button>
                          </td>
                          <td className="py-2.5 px-3 font-mono font-semibold text-[#10283A]">
                            {req.clause_number}
                          </td>
                          <td className="py-2.5 px-3 font-semibold text-[#2D3748]">
                            {req.category}
                          </td>
                          <td className="py-2.5 px-3 text-[#2D3748] max-w-xs truncate" title={req.requirement_text}>
                            {req.requirement_text}
                          </td>
                          <td className="py-2.5 px-3 text-[#4A5568] font-mono text-[11px] truncate max-w-[180px]" title={req.source_document}>
                            {req.source_document} (p. {req.page})
                          </td>
                          <td className="py-2.5 px-2 text-center font-mono font-bold">
                            <span className={`px-1.5 py-0.5 rounded text-[10px] ${
                              req.rule_result === 'PASS' ? 'bg-[#EAF5F0] text-[#1E5A47]' : 'bg-[#FEF2F2] text-[#991B1B]'
                            }`}>
                              {typeof req.rule_result === 'string' ? req.rule_result : 'CHECK'}
                            </span>
                          </td>
                          <td className="py-2.5 px-2 text-center font-mono text-[11px] text-[#4A5568]">
                            {req.semantic_score.toFixed(2)}
                          </td>
                          <td className="py-2.5 px-2 text-center font-mono text-[11px] font-bold text-[#10283A]">
                            {(req.confidence * 100).toFixed(0)}%
                          </td>
                          <td className="py-2.5 px-2 text-center">
                            <span className={`px-2 py-0.5 text-[10px] font-bold uppercase rounded ${
                              req.ai_status === 'PASS' ? 'bg-[#EAF5F0] text-[#1E5A47]' :
                              req.ai_status === 'FAIL' ? 'bg-[#FEF2F2] text-[#991B1B]' :
                              req.ai_status === 'REVIEW' ? 'bg-[#FEF7EC] text-[#B7791F]' : 'bg-[#F3F4F6] text-[#4A5568]'
                            }`}>
                              {req.ai_status}
                            </span>
                          </td>
                          <td className="py-2.5 px-2 text-center font-bold text-[10px]">
                            <span className={`${
                              req.risk === 'CRITICAL' ? 'text-[#991B1B]' :
                              req.risk === 'HIGH' ? 'text-[#C05621]' :
                              req.risk === 'MEDIUM' ? 'text-[#D98A16]' : 'text-[#1E5A47]'
                            }`}>
                              {req.risk}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 text-center">
                            <div className="flex items-center justify-center gap-1.5">
                              {hasDecision ? (
                                <div className="text-left font-mono">
                                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                    effectiveStatus === 'PASS' ? 'bg-[#EAF5F0] text-[#1E5A47]' :
                                    effectiveStatus === 'FAIL' ? 'bg-[#FEF2F2] text-[#991B1B]' :
                                    effectiveStatus === 'REVIEW' ? 'bg-[#FEF7EC] text-[#B7791F]' : 'bg-[#F3F4F6] text-[#4A5568]'
                                  }`}>
                                    {isOverride ? `OVERRIDE: ${effectiveStatus}` : `CONFIRMED: ${effectiveStatus}`}
                                  </span>
                                  <button
                                    onClick={() => handleOpenOverride(req)}
                                    className="ml-2 text-[10px] text-[#2B6CB0] underline hover:text-[#1A365D]"
                                  >
                                    Edit
                                  </button>
                                </div>
                              ) : (
                                <>
                                  <button
                                    onClick={() => handleAcceptAi(req)}
                                    className="px-2 py-1 bg-[#EAF5F0] hover:bg-[#D3EEDB] text-[#1E5A47] text-[10px] font-bold rounded border border-[#C6E7D5] transition-colors"
                                  >
                                    Accept AI
                                  </button>
                                  <button
                                    onClick={() => handleOpenOverride(req)}
                                    className="px-2 py-1 bg-[#FFFFFF] hover:bg-[#F3F4F6] text-[#991B1B] text-[10px] font-bold rounded border border-[#E2E8F0] transition-colors"
                                  >
                                    Override
                                  </button>
                                </>
                              )}
                            </div>
                          </td>
                        </tr>

                        {/* Expandable Evidence & Telemetry Row */}
                        {isExpanded && (
                          <tr className="bg-[#F8FAFC]">
                            <td colSpan={11} className="p-4 border-t border-b border-[#E2E8F0]">
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                                <div className="bg-white border border-[#E2E8F0] p-3 rounded">
                                  <div className="text-[10px] font-mono font-bold text-[#66717C] uppercase mb-1">
                                    Submitted Evidence Snippet
                                  </div>
                                  <div className="font-mono text-[11px] text-[#10283A] whitespace-pre-wrap leading-relaxed">
                                    {req.submitted_evidence}
                                  </div>
                                </div>

                                <div className="bg-white border border-[#E2E8F0] p-3 rounded">
                                  <div className="text-[10px] font-mono font-bold text-[#66717C] uppercase mb-1">
                                    Extracted Value &amp; Rule Execution
                                  </div>
                                  <div className="font-mono text-[11px] text-[#2D3748] space-y-1">
                                    <div>Document: <strong>{req.source_document}</strong></div>
                                    <div>Page: <strong>{req.page}</strong></div>
                                    <div>Extracted: <span className="bg-[#FEF7EC] px-1 py-0.5 rounded text-[#78350F]">{JSON.stringify(req.extracted_value)}</span></div>
                                    <div>Rule Check: <strong>{typeof req.rule_result === 'string' ? req.rule_result : JSON.stringify(req.rule_result)}</strong></div>
                                  </div>
                                </div>

                                <div className="bg-white border border-[#E2E8F0] p-3 rounded">
                                  <div className="text-[10px] font-mono font-bold text-[#66717C] uppercase mb-1">
                                    Officer Determination Trail
                                  </div>
                                  {req.officer_decision ? (
                                    <div className="text-[11px] space-y-1">
                                      <div>Officer: <strong>{req.officer_decision.officer_name}</strong></div>
                                      <div>Decision: <strong className="text-[#1E5A47]">{req.officer_decision.decision}</strong></div>
                                      <div>Override: <strong>{req.officer_decision.is_override ? 'YES' : 'NO'}</strong></div>
                                      <div>Justification: <em className="text-[#4A5568]">{req.officer_decision.reason}</em></div>
                                      <div className="text-[10px] text-[#718096]">Timestamp: {req.officer_decision.timestamp}</div>
                                    </div>
                                  ) : (
                                    <div className="text-[11px] text-[#718096] italic">
                                      No officer decision recorded yet. Original AI baseline active.
                                    </div>
                                  )}
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : (
        <div className="bg-white border border-[#D9DEE3] rounded p-12 text-center shadow-sm space-y-4">
          <AlertOctagon className="w-10 h-10 text-[#D98A16] mx-auto" />
          <div className="max-w-md mx-auto">
            <h3 className="text-base font-serif font-bold text-[#10283A]">
              Compliance Evaluation Dossier Not Loaded
            </h3>
            <p className="text-xs text-[#66717C] mt-1.5 leading-relaxed">
              {errorMessage || "The compliance evaluation workspace is ready to be initialized for this bidder. Click below to trigger the AI verification engine."}
            </p>
          </div>
          <button
            onClick={() => loadWorkspaceData(selectedBidderId)}
            className="px-5 py-2.5 bg-[#10283A] hover:bg-[#18374D] text-white text-xs font-bold font-mono rounded shadow-sm inline-flex items-center gap-2 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Execute AI Compliance Evaluation</span>
          </button>
        </div>
      )}

      {/* ── Modal: Override AI Result ── */}
      {overrideModalOpen && activeReqForOverride && (
        <div className="fixed inset-0 z-50 bg-[#10283A]/70 flex items-center justify-center p-4">
          <div className="bg-white border border-[#D9DEE3] rounded max-w-lg w-full p-6 shadow-xl space-y-4">
            <div className="border-b border-[#D9DEE3] pb-3">
              <div className="text-[10px] font-mono font-bold text-[#991B1B] uppercase">
                Section 4 GFR 2017 &bull; Explicit Officer Override
              </div>
              <h2 className="text-lg font-serif font-bold text-[#10283A] mt-0.5">
                Override AI Finding: {activeReqForOverride.clause_number}
              </h2>
              <div className="text-xs text-[#66717C] mt-0.5">{activeReqForOverride.category} &bull; {activeReqForOverride.title}</div>
            </div>

            {/* Baseline Preserved Notice */}
            <div className="bg-[#F8FAFC] border border-[#E2E8F0] p-3 rounded text-xs space-y-1 font-mono">
              <div>Original AI Status: <strong>{activeReqForOverride.ai_status}</strong> (Confidence: {(activeReqForOverride.confidence * 100).toFixed(0)}%)</div>
              <div className="text-[10px] text-[#718096]">Note: The original AI baseline will be permanently preserved in the audit log.</div>
            </div>

            {overrideError && (
              <div className="bg-[#FEF2F2] border-l-4 border-[#991B1B] p-2.5 text-xs text-[#991B1B] font-medium">
                {overrideError}
              </div>
            )}

            <form onSubmit={handleSubmitOverride} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-[#10283A] uppercase mb-1 font-mono">
                  New Officer Decision Status *
                </label>
                <div className="grid grid-cols-4 gap-2">
                  {['PASS', 'FAIL', 'REVIEW', 'INSUFFICIENT'].map((st) => (
                    <button
                      key={st}
                      type="button"
                      onClick={() => setOverrideDecision(st)}
                      className={`py-2 text-xs font-bold font-mono rounded border text-center transition-colors ${
                        overrideDecision === st
                          ? 'bg-[#10283A] text-white border-[#10283A]'
                          : 'bg-white text-[#4A5568] border-[#D9DEE3] hover:bg-[#F3F4F6]'
                      }`}
                    >
                      {st}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-[#10283A] uppercase mb-1 font-mono">
                  Mandatory Override Justification *
                </label>
                <textarea
                  required
                  rows={3}
                  value={overrideReason}
                  onChange={(e) => setOverrideReason(e.target.value)}
                  placeholder="State the regulatory / technical justification for overriding the AI finding..."
                  className="w-full text-xs p-2.5 border border-[#D9DEE3] rounded focus:outline-none focus:border-[#10283A] font-sans"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-[#D9DEE3]">
                <button
                  type="button"
                  onClick={() => setOverrideModalOpen(false)}
                  className="px-4 py-2 border border-[#D9DEE3] text-xs font-medium text-[#4A5568] rounded hover:bg-[#F3F4F6]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={overrideSubmitting}
                  className="px-4 py-2 bg-[#991B1B] hover:bg-[#7F1D1D] text-white text-xs font-bold rounded shadow-sm flex items-center gap-1.5"
                >
                  {overrideSubmitting ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
                  <span>Confirm Override</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Modal: Final Procurement Decision ── */}
      {finalModalOpen && workspace && (
        <div className="fixed inset-0 z-50 bg-[#10283A]/70 flex items-center justify-center p-4">
          <div className="bg-white border border-[#D9DEE3] rounded max-w-xl w-full p-6 shadow-xl space-y-4">
            <div className="border-b border-[#D9DEE3] pb-3">
              <div className="text-[10px] font-mono font-bold text-[#D98A16] uppercase">
                Final Procurement Authority Sign-Off
              </div>
              <h2 className="text-xl font-serif font-bold text-[#10283A] mt-0.5">
                Final Bid Determination: {workspace.bidder.legal_name}
              </h2>
            </div>

            {/* Confirmation Summary Box per Spec Section 6 */}
            <div className="bg-[#F8FAFC] border border-[#E2E8F0] p-3.5 rounded text-xs space-y-2">
              <div className="font-bold text-[#10283A] font-mono uppercase text-[11px]">
                Pre-Determination Assessment Summary
              </div>
              <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                <div>AI Recommendation: <strong>{workspace.recommendation}</strong></div>
                <div>Compliance Score: <strong>{workspace.compliance_score}%</strong></div>
                <div>Overridden Requirements: <strong>{overriddenCount} clause(s)</strong></div>
                <div>High-Risk Issues: <strong className={highRiskCount > 0 ? 'text-[#991B1B]' : 'text-[#1E5A47]'}>{highRiskCount}</strong></div>
                <div>Outstanding Review Items: <strong className={outstandingReviewCount > 0 ? 'text-[#B7791F]' : 'text-[#1E5A47]'}>{outstandingReviewCount}</strong></div>
                <div>Overall Risk: <strong>{workspace.risk_level}</strong></div>
              </div>
            </div>

            {finalError && (
              <div className="bg-[#FEF2F2] border-l-4 border-[#991B1B] p-2.5 text-xs text-[#991B1B] font-medium">
                {finalError}
              </div>
            )}

            <form onSubmit={handleSubmitFinalDecision} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-[#10283A] uppercase mb-1 font-mono">
                  Final Procurement Decision *
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(['QUALIFIED', 'DISQUALIFIED', 'REVIEW / HOLD'] as const).map((ch) => (
                    <button
                      key={ch}
                      type="button"
                      onClick={() => setFinalDecisionChoice(ch)}
                      className={`py-2 text-xs font-bold font-mono rounded border text-center transition-colors ${
                        finalDecisionChoice === ch
                          ? ch === 'QUALIFIED' ? 'bg-[#1E5A47] text-white border-[#1E5A47]' :
                            ch === 'DISQUALIFIED' ? 'bg-[#991B1B] text-white border-[#991B1B]' :
                            'bg-[#D98A16] text-white border-[#D98A16]'
                          : 'bg-white text-[#4A5568] border-[#D9DEE3] hover:bg-[#F3F4F6]'
                      }`}
                    >
                      {ch}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-[#10283A] uppercase mb-1 font-mono">
                  Procurement Officer Findings &amp; Determination Remarks *
                </label>
                <textarea
                  required
                  rows={3}
                  value={finalRemarks}
                  onChange={(e) => setFinalRemarks(e.target.value)}
                  placeholder="Document statutory basis for qualification / disqualification / hold..."
                  className="w-full text-xs p-2.5 border border-[#D9DEE3] rounded focus:outline-none focus:border-[#10283A]"
                />
              </div>

              <div className="bg-[#FEF7EC] border border-[#F3DEB8] p-3 rounded flex items-start gap-2.5">
                <input
                  type="checkbox"
                  id="finalConfirm"
                  checked={finalConfirmed}
                  onChange={(e) => setFinalConfirmed(e.target.checked)}
                  className="mt-0.5"
                />
                <label htmlFor="finalConfirm" className="text-xs text-[#78350F] cursor-pointer">
                  I hereby confirm my authority as Procurement Officer. I verify that AI results provided decision support and that this final determination reflects official statutory scrutiny per GFR 2017.
                </label>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-[#D9DEE3]">
                <button
                  type="button"
                  onClick={() => setFinalModalOpen(false)}
                  className="px-4 py-2 border border-[#D9DEE3] text-xs font-medium text-[#4A5568] rounded hover:bg-[#F3F4F6]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={finalSubmitting}
                  className="px-5 py-2 bg-[#10283A] hover:bg-[#18374D] text-white text-xs font-bold rounded shadow-sm flex items-center gap-1.5"
                >
                  {finalSubmitting ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <UserCheck className="w-3.5 h-3.5" />}
                  <span>Sign &amp; Submit Final Decision</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
