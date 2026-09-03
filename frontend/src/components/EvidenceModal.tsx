import React, { useState } from 'react';
import {
  X,
  FileText,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  ExternalLink,
  Download,
  Lock,
  Stamp,
  Maximize2
} from 'lucide-react';
import { ComplianceCheck } from '../types';

interface EvidenceModalProps {
  check: ComplianceCheck | null;
  bidderName?: string;
  onClose: () => void;
  onOpenReview?: (check: ComplianceCheck) => void;
  onConfirmReview?: (status: string, note: string) => void;
}

export const EvidenceModal: React.FC<EvidenceModalProps> = ({
  check,
  bidderName,
  onClose,
  onOpenReview,
  onConfirmReview
}) => {
  if (!check) return null;

  const [complianceNote, setComplianceNote] = useState('');

  const snippet = check.evidence_text || check.reason || 'Evidence verified across uploaded bidder documents.';
  const citation = check.page_number ? `Page ${check.page_number}` : 'Page 1';
  const docName = check.document_name || 'Praveen_BS_Mock_Petroleum_Compliance_Evidence_Pack.pdf';
  const ruleCode = check.rule_version || 'RULE-01';
  const confidence = check.confidence !== undefined ? check.confidence : 0.95;

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-xs flex items-center justify-center p-4 sm:p-6 animate-fadeIn">
      
      {/* Modal Container (Matching Page 5 & Page 8 from PDF) */}
      <div className="bg-white rounded-2xl shadow-modal border border-slate-200 w-full max-w-5xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Modal Top Header Bar */}
        <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="font-bold text-sm flex items-center gap-2">
                <span>Verification Workflow</span>
                <span className="text-[10px] font-mono px-2 py-0.5 bg-blue-500/20 text-blue-300 border border-blue-400/30 rounded">
                  {ruleCode}
                </span>
              </div>
              <div className="text-[11px] text-slate-400">
                {check.requirement_category?.replace(/_/g, ' ')} • Review evidence against regulatory standards
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Split Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-200 overflow-y-auto flex-1">
          
          {/* Left Column: PDF Document Viewer with Highlight & Digital Seal (Matching Page 5) */}
          <div className="p-6 bg-slate-50 flex flex-col justify-between space-y-4">
            
            {/* Document Header */}
            <div className="flex items-center justify-between text-xs text-slate-600 font-medium">
              <div className="flex items-center gap-1.5 font-bold text-slate-900">
                <FileText className="w-4 h-4 text-blue-600" />
                <span className="line-clamp-1">{docName}</span>
              </div>
              <div className="flex items-center gap-2 font-mono text-[11px]">
                <span className="px-1.5 py-0.5 bg-white border border-slate-200 rounded">{citation}</span>
                <button className="p-1 hover:bg-slate-200 rounded text-slate-500">
                  <Download className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* Document Canvas Container with Highlight Box & Digital Stamp */}
            <div className="w-full h-80 bg-white border border-slate-200 rounded-xl shadow-inner relative p-5 flex flex-col justify-between overflow-hidden group">
              
              {/* Document Text Skeleton Lines */}
              <div className="space-y-3 opacity-70">
                <div className="h-3 bg-slate-200 rounded w-3/4"></div>
                <div className="h-3 bg-slate-200 rounded w-full"></div>
                <div className="h-3 bg-slate-200 rounded w-5/6"></div>
              </div>

              {/* Yellow Highlighted Bounding Box (Matching Page 5 from PDF) */}
              <div className="p-3 bg-amber-100/80 border-2 border-amber-400 rounded-lg shadow-sm text-xs font-mono text-slate-900 space-y-1 my-2">
                <div className="text-[10px] font-bold text-amber-800 uppercase flex items-center gap-1">
                  <span>AI Extracted Evidence Match</span>
                </div>
                <p className="text-[11px] font-medium leading-relaxed">
                  "{snippet}"
                </p>
              </div>

              {/* Digital Seal Stamp (Matching Page 5 from PDF) */}
              <div className="self-center my-1 select-none">
                <div className="digital-seal-stamp w-24 h-24 text-center rounded-full flex flex-col items-center justify-center p-2 shadow-lg">
                  <Lock className="w-4 h-4 mb-0.5" />
                  <span className="text-[7px] font-bold tracking-widest uppercase">VERIFIED AUTHENTIC</span>
                  <span className="text-[8px] font-black tracking-wider leading-tight">GOVPROCURE</span>
                  <span className="text-[7px] font-mono text-blue-100">DIGITAL SEAL</span>
                  <span className="text-[6px] text-blue-200 mt-0.5">Diameter 60mm</span>
                </div>
              </div>

              {/* Bottom Doc Footer */}
              <div className="text-[10px] font-mono text-slate-400 text-center border-t border-slate-100 pt-2">
                MoPNG Petroleum Bid Integrity Verification Engine
              </div>
            </div>

            <div className="text-[11px] text-slate-500 font-mono flex items-center justify-between">
              <span>Status: <strong className="text-emerald-600 font-bold">{check.status}</strong></span>
              <span>Confidence: <strong className="text-slate-900 font-bold">{(confidence * 100).toFixed(0)}%</strong></span>
            </div>

          </div>

          {/* Right Column: AI Extracted Fields & Officer Notes */}
          <div className="p-6 bg-white flex flex-col justify-between space-y-5">
            
            <div className="space-y-4">
              <div className="border-b border-slate-100 pb-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  AI Extracted Fields & Metadata
                </h3>
              </div>

              <div className="space-y-3 text-xs">
                <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                  <span className="text-[10px] font-bold text-slate-400 uppercase block mb-0.5">REQUIREMENT CLAUSE</span>
                  <p className="font-semibold text-slate-800">{check.requirement_description || check.requirement_category}</p>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg">
                    <span className="text-[10px] font-bold text-slate-400 uppercase block">VERIFICATION RESULT</span>
                    <span className={`font-bold font-mono text-xs ${
                      check.status === 'PASS' ? 'text-emerald-700' : check.status === 'FAIL' ? 'text-rose-700' : 'text-amber-700'
                    }`}>
                      ● {check.status}
                    </span>
                  </div>
                  <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg">
                    <span className="text-[10px] font-bold text-slate-400 uppercase block">EXTRACTION METHOD</span>
                    <span className="font-bold text-slate-700 font-mono text-xs">
                      {check.verification_method || 'RULE_AND_ARITHMETIC'}
                    </span>
                  </div>
                </div>

                {/* Compliance Note Input */}
                <div className="space-y-1.5 pt-1">
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600">
                    Compliance Note / Officer Observation
                  </label>
                  <textarea
                    rows={3}
                    value={complianceNote}
                    onChange={(e) => setComplianceNote(e.target.value)}
                    placeholder="Add an internal observation or clearance remark..."
                    className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-800 focus:outline-none focus:border-blue-600 focus:bg-white transition-all font-sans"
                  />
                </div>
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition-colors"
              >
                Close Review
              </button>
              {onOpenReview && (
                <button
                  type="button"
                  onClick={() => {
                    onOpenReview(check);
                    onClose();
                  }}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold transition-all shadow-sm"
                >
                  Officer Override Review
                </button>
              )}
              {onConfirmReview && (
                <button
                  type="button"
                  onClick={() => {
                    onConfirmReview('APPROVED', complianceNote);
                    onClose();
                  }}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold transition-all shadow-sm flex items-center gap-1.5"
                >
                  <CheckCircle2 className="w-4 h-4" /> Confirm & Approve
                </button>
              )}
            </div>

          </div>

        </div>

      </div>

    </div>
  );
};
