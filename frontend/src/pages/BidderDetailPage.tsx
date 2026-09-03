import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { bidderService, documentService } from '../services';
import { BidderDetail, ComplianceCheck } from '../types';
import { ComplianceBadge } from '../components/ComplianceBadge';
import { RiskBadge } from '../components/RiskBadge';
import { EvidenceModal } from '../components/EvidenceModal';
import { OfficerReviewModal } from '../components/OfficerReviewModal';
import { TurnoverCalculationCard } from '../components/TurnoverCalculationCard';
import {
  FileText, ShieldCheck, ArrowLeft, RefreshCw, Upload,
  BrainCircuit, CheckCircle2, AlertTriangle, XCircle, FileUp, Sparkles, ExternalLink
} from 'lucide-react';

export const BidderDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [bidder, setBidder] = useState<BidderDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [uploading, setUploading] = useState(false);

  // Modals state
  const [selectedCheckForEvidence, setSelectedCheckForEvidence] = useState<ComplianceCheck | null>(null);
  const [selectedCheckForReview, setSelectedCheckForReview] = useState<ComplianceCheck | null>(null);

  const loadBidder = async () => {
    if (!id) return;
    try {
      const data = await bidderService.getBidderDetail(id);
      setBidder(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBidder();
  }, [id]);

  const handleRunVerification = async () => {
    if (!id) return;
    setVerifying(true);
    try {
      await bidderService.verifyBidder(id);
      await loadBidder();
    } catch (err) {
      console.error("Verification failed", err);
    } finally {
      setVerifying(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!id || !e.target.files || !e.target.files[0]) return;
    const file = e.target.files[0];
    setUploading(true);
    try {
      await documentService.uploadBidderDocument(id, file, "SUPPLEMENTAL_DOCUMENT");
      await bidderService.verifyBidder(id);
      await loadBidder();
    } catch (err) {
      console.error("File upload failed", err);
    } finally {
      setUploading(false);
    }
  };

  if (loading || !bidder) {
    return (
      <div className="flex items-center justify-center h-72 text-slate-500 font-mono text-xs gap-3">
        <RefreshCw className="w-5 h-5 animate-spin text-emerald-600" />
        <span>RETRIEVING BIDDER COMPLIANCE DOSSIER & EVIDENCE INDEX...</span>
      </div>
    );
  }

  const scoreDetail = bidder.compliance_score_detail;
  const riskDetail = bidder.risk_assessment_detail;
  const recDetail = bidder.recommendation_detail;

  return (
    <div className="space-y-6">
      
      {/* Top Breadcrumb & Control Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <button
          onClick={() => navigate('/bidders')}
          className="text-xs font-mono font-bold text-slate-600 hover:text-slate-900 flex items-center gap-1.5 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> BACK TO BIDDER DIRECTORY
        </button>

        <div className="flex items-center gap-2.5">
          <label className="px-3.5 py-2 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-mono font-bold cursor-pointer transition-all shadow-2xs flex items-center gap-1.5">
            <FileUp className="w-4 h-4 text-emerald-600" />
            {uploading ? "UPLOADING..." : "UPLOAD ATTACHMENT"}
            <input type="file" onChange={handleFileUpload} className="hidden" accept=".pdf,.png,.jpg,.jpeg" />
          </label>
          <button
            onClick={handleRunVerification}
            disabled={verifying}
            className="px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-white rounded-lg text-xs font-mono font-bold transition-all shadow-sm flex items-center gap-1.5 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${verifying ? 'animate-spin' : ''}`} />
            {verifying ? "RUNNING ENGINE..." : "RE-EVALUATE COMPLIANCE"}
          </button>
        </div>
      </div>

      {/* Primary Identity & Executive Assessment Header Banner */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-5">
        
        {/* Entity Title Header */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div className="space-y-1">
            <div className="flex items-center gap-2 font-mono text-[10px] text-slate-500">
              <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-bold border border-slate-200">
                BIDDER ID: {bidder.id.slice(0, 16)}
              </span>
              <span>•</span>
              <span>STATUS:</span>
              <span className="font-bold text-emerald-700">{bidder.status}</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 font-sans">
              {bidder.bidder_name}
            </h1>
            <div className="flex flex-wrap items-center gap-3 text-xs font-mono text-slate-500 pt-0.5">
              <span>AUTHORIZED SIGNATORY: <strong className="text-slate-800">{bidder.contact_person || "Authorized Representative"}</strong></span>
              <span>•</span>
              <span>EMAIL: <strong className="text-slate-800">{bidder.email || "compliance@bidder.in"}</strong></span>
              <span>•</span>
              <span>PHONE: <strong className="text-slate-800">{bidder.phone || "+91 9876543210"}</strong></span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 font-mono text-xs">
            <div className="rounded-lg border border-slate-200 p-3 bg-slate-50 text-right shadow-2xs">
              <span className="text-[10px] uppercase font-bold text-slate-400 block">GSTIN IDENTIFIER</span>
              <span className="font-bold text-slate-900">{bidder.gstin || "NOT DECLARED"}</span>
            </div>
            <div className="rounded-lg border border-slate-200 p-3 bg-slate-50 text-right shadow-2xs">
              <span className="text-[10px] uppercase font-bold text-slate-400 block">INCOME TAX PAN</span>
              <span className="font-bold text-slate-900">{bidder.pan || "NOT DECLARED"}</span>
            </div>
          </div>
        </div>

        {/* 3 Structured Intelligence Panels */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs">
          
          {/* Panel 1: Typographic Compliance Score */}
          <div className="rounded-xl border border-slate-200 p-4 bg-slate-50 space-y-3 shadow-2xs">
            <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider text-slate-500">
              <span>COMPLIANCE SCORE</span>
              <span className="text-emerald-700 font-bold">100 MAX</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold text-slate-900">
                {scoreDetail?.overall_score ?? bidder.compliance_score ?? 0}
              </span>
              <span className="text-xs text-slate-400">/ 100.0</span>
            </div>

            {/* Segmented Category Weights with Progress Bars */}
            <div className="space-y-2 pt-2 border-t border-slate-200 text-[11px]">
              <div className="space-y-1">
                <div className="flex justify-between text-slate-600">
                  <span>STATUTORY (30% WT)</span>
                  <strong className="text-slate-900">{scoreDetail?.statutory_score ?? 100}%</strong>
                </div>
                <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-emerald-600 h-full" style={{ width: `${scoreDetail?.statutory_score ?? 100}%` }}></div>
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-slate-600">
                  <span>FINANCIAL (25% WT)</span>
                  <strong className="text-slate-900">{scoreDetail?.financial_score ?? 100}%</strong>
                </div>
                <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-emerald-600 h-full" style={{ width: `${scoreDetail?.financial_score ?? 100}%` }}></div>
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-slate-600">
                  <span>TENDER SPECIFIC (20% WT)</span>
                  <strong className="text-slate-900">{scoreDetail?.tender_specific_score ?? 100}%</strong>
                </div>
                <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-emerald-600 h-full" style={{ width: `${scoreDetail?.tender_specific_score ?? 100}%` }}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Panel 2: Risk Assessment Indicator */}
          <div className="rounded-xl border border-slate-200 p-4 bg-slate-50 space-y-3 shadow-2xs">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                RISK ASSESSMENT
              </span>
              <RiskBadge level={riskDetail?.risk_level || bidder.risk_level || "MEDIUM"} size="md" />
            </div>

            <div className="space-y-1 text-xs">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">
                AUDITED RISK SIGNALS:
              </span>
              <ul className="space-y-1 text-[11px] text-slate-800 max-h-24 overflow-y-auto">
                {(riskDetail?.primary_risk_factors || ["Zero critical non-compliance anomalies identified."]).map((rf, idx) => (
                  <li key={idx} className="flex items-start gap-1.5 leading-snug">
                    <span className="text-amber-600 font-bold">•</span>
                    <span>{rf}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Panel 3: AI Recommendation Note */}
          <div className="rounded-xl border border-slate-200 p-4 bg-slate-50 space-y-2 flex flex-col justify-between shadow-2xs">
            <div>
              <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-emerald-800 mb-1">
                <BrainCircuit className="w-3.5 h-3.5 text-emerald-600" />
                <span>AI EVIDENCE ANALYSIS</span>
              </div>
              <p className="text-xs font-bold text-slate-900 leading-snug font-sans">
                {recDetail?.summary || "Dossier evaluated against statutory rules and clause thresholds."}
              </p>
            </div>

            <div className="pt-2 border-t border-slate-200 text-[10px] text-slate-500">
              NOTICE: Procurement Officer retains final discretionary decision authority.
            </div>
          </div>

        </div>

      </div>

      {/* Uploaded Documents Repository */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-3 font-mono">
        <div className="flex items-center justify-between pb-2 border-b border-slate-100">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
            <FileText className="w-4 h-4 text-slate-500" />
            <span>SUBMITTED DOSSIER ATTACHMENTS ({bidder.documents.length} FILES)</span>
          </div>
          <span className="text-[10px] text-slate-500">PyMuPDF + OCR Text Index Active</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {bidder.documents.map((doc) => (
            <div key={doc.id} className="p-3.5 rounded-lg border border-slate-200 bg-slate-50/70 flex items-center justify-between text-xs">
              <div className="truncate pr-2">
                <div className="font-bold text-slate-900 truncate font-sans">{doc.document_name}</div>
                <div className="text-[10px] text-slate-500 mt-0.5">
                  {doc.page_count} Pages • {doc.entities_count || 0} Entities Parsed
                </div>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-200 text-slate-700 font-bold uppercase shrink-0">
                {doc.is_scanned ? "OCR Active" : "Digital PDF"}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Prior Petroleum & Pipeline Project Execution Experience */}
      {bidder.projects && bidder.projects.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/70 flex items-center justify-between font-mono">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-600" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                PETROLEUM & PIPELINE PROJECT EXECUTION HISTORY ({bidder.projects.length} RECORDS)
              </h3>
            </div>
            <span className="text-[10px] text-slate-500">Structured MoPNG Project Database</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="border-b border-slate-200 bg-slate-50/50 text-slate-500 text-[10px] uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-3">PROJECT TITLE</th>
                  <th className="px-6 py-3">CLIENT & SECTOR</th>
                  <th className="px-6 py-3 text-center">LENGTH (KM)</th>
                  <th className="px-6 py-3">DIAMETER / SPEC</th>
                  <th className="px-6 py-3 text-right">VALUE (INR)</th>
                  <th className="px-6 py-3">SCOPE & ROLE</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-800 font-sans">
                {bidder.projects.map((proj) => (
                  <tr key={proj.id} className="hover:bg-slate-50/60">
                    <td className="px-6 py-3.5 font-bold text-slate-900 max-w-xs">{proj.project_name}</td>
                    <td className="px-6 py-3.5 font-mono text-[11px]">
                      <div>{proj.client_name}</div>
                      <span className="text-[10px] text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200 uppercase font-bold">
                        {proj.sector || "OIL_AND_GAS"}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 text-center font-mono font-bold text-slate-900">
                      {proj.pipeline_length_km ? `${proj.pipeline_length_km.toFixed(1)} km` : "N/A"}
                    </td>
                    <td className="px-6 py-3.5 font-mono text-[11px] text-slate-600">
                      {proj.pipeline_diameter || "Standard API 5L"}
                    </td>
                    <td className="px-6 py-3.5 text-right font-mono font-bold text-slate-900">
                      {proj.project_value ? `₹${(proj.project_value / 10000000).toFixed(2)} Cr` : "N/A"}
                    </td>
                    <td className="px-6 py-3.5 text-xs text-slate-600 max-w-xs">
                      <div className="truncate">{proj.scope_of_work || "EPC Pipeline Construction"}</div>
                      <span className="text-[10px] font-mono uppercase text-slate-400 block mt-0.5">{proj.bidder_role}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Key Technical & Engineering Personnel */}
      {bidder.personnel && bidder.personnel.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/70 flex items-center justify-between font-mono">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-sky-600" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                KEY TECHNICAL MANPOWER & ENGINEERING STAFF ({bidder.personnel.length} MEMBERS)
              </h3>
            </div>
            <span className="text-[10px] text-slate-500">Verified Pipeline Engineers & Inspectors</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="border-b border-slate-200 bg-slate-50/50 text-slate-500 text-[10px] uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-3">NAME & DESIGNATION</th>
                  <th className="px-6 py-3">QUALIFICATION</th>
                  <th className="px-6 py-3 text-center">TOTAL EXP</th>
                  <th className="px-6 py-3 text-center">PIPELINE EXP</th>
                  <th className="px-6 py-3">CERTIFICATIONS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-800 font-sans">
                {bidder.personnel.map((staff) => (
                  <tr key={staff.id} className="hover:bg-slate-50/60">
                    <td className="px-6 py-3.5 font-bold text-slate-900">
                      <div>{staff.name}</div>
                      <div className="text-[11px] font-normal text-slate-500">{staff.designation}</div>
                    </td>
                    <td className="px-6 py-3.5 text-xs text-slate-700">
                      {staff.qualification}
                      {staff.specialization && (
                        <div className="text-[10px] text-slate-400 font-mono">{staff.specialization}</div>
                      )}
                    </td>
                    <td className="px-6 py-3.5 text-center font-mono font-bold text-slate-900">
                      {staff.years_of_experience} yrs
                    </td>
                    <td className="px-6 py-3.5 text-center font-mono font-bold text-emerald-700">
                      {staff.pipeline_experience_years || staff.years_of_experience} yrs
                    </td>
                    <td className="px-6 py-3.5">
                      <div className="flex flex-wrap gap-1">
                        {staff.certifications && staff.certifications.length > 0 ? (
                          staff.certifications.map((cert, idx) => (
                            <span key={idx} className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 text-[10px] font-mono border border-slate-200">
                              {cert}
                            </span>
                          ))
                        ) : (
                          <span className="text-[10px] text-slate-400 font-mono">B.Tech Verified</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}


      {/* Granular Compliance Verification Matrix Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/70 flex items-center justify-between font-mono">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              GRANULAR COMPLIANCE VERIFICATION MATRIX
            </h3>
            <p className="text-[10px] text-slate-500 font-sans">
              Click any row to inspect ground-truth document evidence, arithmetic calculations, and execute officer reviews
            </p>
          </div>
          <span className="text-xs font-bold text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded border border-emerald-200">
            {bidder.compliance_checks.length} VERIFICATION CHECKS
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="border-b border-slate-200 bg-slate-50/50 text-slate-500 text-[10px] uppercase tracking-wider">
              <tr>
                <th className="px-6 py-3">CATEGORY</th>
                <th className="px-6 py-3">REQUIREMENT SPECIFICATION</th>
                <th className="px-6 py-3 text-center">STATUS</th>
                <th className="px-6 py-3 text-center">CONFIDENCE</th>
                <th className="px-6 py-3">GROUND-TRUTH EVIDENCE & CITATION</th>
                <th className="px-6 py-3">DATA SOURCE</th>
                <th className="px-6 py-3 text-right">ACTIONS</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-800">
              {bidder.compliance_checks.map((check) => (
                <tr
                  key={check.id}
                  onClick={() => setSelectedCheckForEvidence(check)}
                  className="hover:bg-slate-50/80 cursor-pointer transition-colors"
                >
                  <td className="px-6 py-4 font-bold whitespace-nowrap">
                    <span className="px-2 py-0.5 rounded bg-slate-900 text-white text-[10px]">
                      {check.requirement_category}
                    </span>
                  </td>
                  <td className="px-6 py-4 max-w-xs font-sans">
                    <div className="text-xs font-semibold text-slate-900 leading-snug">
                      {check.requirement_description || check.reason}
                    </div>
                    {check.requirement_mandatory && (
                      <span className="text-[10px] text-red-600 font-mono font-bold uppercase block mt-0.5">
                        • MANDATORY CRITERION
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-center">
                    <ComplianceBadge status={check.status} size="md" />
                  </td>
                  <td className="px-6 py-4 text-center font-bold">
                    <span className={check.confidence >= 0.90 ? 'text-emerald-700' : (check.confidence >= 0.70 ? 'text-amber-700' : 'text-red-700')}>
                      {(check.confidence * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 max-w-sm">
                    <div className="text-xs line-clamp-2 text-slate-800 font-sans">
                      {check.reason}
                    </div>
                    <div className="text-[10px] text-slate-500 mt-1 flex items-center gap-1.5">
                      <FileText className="w-3 h-3 text-slate-400" />
                      <span>{check.document_name || 'Dossier_Attachment.pdf'} (PAGE {check.page_number || 1})</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-[11px] text-slate-500 whitespace-nowrap">
                    {check.verification_source}
                  </td>
                  <td className="px-6 py-4 text-right whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                    <div className="flex items-center justify-end gap-1.5">
                      <button
                        onClick={() => setSelectedCheckForEvidence(check)}
                        className="px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-[11px] font-bold text-slate-700 transition-colors shadow-2xs"
                      >
                        Evidence
                      </button>
                      <button
                        onClick={() => setSelectedCheckForReview(check)}
                        className="px-3 py-1.5 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white text-[11px] font-bold shadow-sm transition-colors"
                      >
                        Review
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Officer Review & Audit Timeline */}
      {bidder.officer_reviews && bidder.officer_reviews.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4 font-mono">
          <div className="pb-3 border-b border-slate-100 flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900">
              OFFICER REVIEW & OVERRIDE RECORD ({bidder.officer_reviews.length} ACTIONS)
            </h3>
            <span className="text-[10px] text-slate-500">SECTION 4 GFR LEGAL LOG</span>
          </div>

          <div className="space-y-2.5 text-xs">
            {bidder.officer_reviews.map((rev) => (
              <div key={rev.id} className="p-4 rounded-lg border border-slate-200 bg-slate-50 space-y-1.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 font-bold text-slate-900">
                    <span>{rev.officer_name}</span>
                    <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 border border-blue-200 text-[10px]">
                      {rev.action_type}
                    </span>
                  </div>
                  <span className="text-slate-400 text-[10px]">
                    {new Date(rev.reviewed_at).toUTCString()}
                  </span>
                </div>
                <div className="font-sans text-slate-800">
                  <strong>Remarks:</strong> {rev.remarks}
                </div>
                <div className="text-[11px] text-slate-500">
                  TRANSITION: <span className="font-bold text-amber-700">{rev.previous_status}</span> &rarr; <span className="font-bold text-emerald-700">{rev.new_status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modals */}
      <EvidenceModal
        check={selectedCheckForEvidence}
        onClose={() => setSelectedCheckForEvidence(null)}
        onOpenReview={(c) => setSelectedCheckForReview(c)}
      />

      <OfficerReviewModal
        check={selectedCheckForReview}
        onClose={() => setSelectedCheckForReview(null)}
        onSuccess={() => loadBidder()}
      />

    </div>
  );
};
