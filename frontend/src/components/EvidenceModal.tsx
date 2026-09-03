import React from 'react';
import { ComplianceCheck } from '../types';
import { ComplianceBadge } from './ComplianceBadge';
import { TurnoverCalculationCard } from './TurnoverCalculationCard';

interface EvidenceModalProps {
  check: ComplianceCheck | null;
  onClose: () => void;
  onOpenReview?: (check: ComplianceCheck) => void;
}

export const EvidenceModal: React.FC<EvidenceModalProps> = ({ check, onClose, onOpenReview }) => {
  if (!check) return null;

  const firstEvidence = check.evidence_items && check.evidence_items.length > 0 ? check.evidence_items[0] : null;
  const isTurnover = check.requirement_category === 'TURNOVER';

  return (
    <div className="fixed inset-0 z-50 bg-[#101A17]/70 backdrop-blur-none flex items-center justify-center p-4">
      <div className="bg-white border border-[#22322C] max-w-3xl w-full shadow-2xl flex flex-col max-h-[90vh]">
        
        {/* Header Bar */}
        <div className="bg-[#101A17] text-white px-6 py-4 flex items-center justify-between border-b border-[#22322C]">
          <div className="flex items-center gap-3">
            <span className="px-2 py-0.5 bg-[#163C32] border border-[#2D5A4E] text-[10px] font-mono font-bold tracking-widest uppercase">
              {check.requirement_category}
            </span>
            <div>
              <h3 className="text-xs font-mono font-bold tracking-wide uppercase text-[#EDEFEA]">
                EVIDENCE GROUND-TRUTH INSPECTOR
              </h3>
              <p className="text-[10px] text-[#808B84] font-mono">
                RULE VERIFICATION ID: {check.id.slice(0, 12)}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-[#808B84] hover:text-white p-1 font-mono text-sm"
          >
            ✕ CLOSE
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-5 overflow-y-auto flex-1 text-xs">
          
          {/* Requirement Metadata Header Grid */}
          <div className="border border-[#D8DCD6] p-4 bg-[#FCFCFA] space-y-2">
            <div className="text-[10px] font-mono font-bold uppercase tracking-wider text-[#59625D]">
              TARGET REQUIREMENT SPECIFICATION
            </div>
            <div className="font-semibold text-sm text-[#17201C] leading-snug">
              {check.requirement_description || check.reason}
            </div>
            <div className="pt-2 border-t border-[#D8DCD6] flex flex-wrap items-center justify-between gap-2 text-[11px] font-mono text-[#59625D]">
              <div>
                <span>STATUS: </span>
                <ComplianceBadge status={check.status} size="sm" />
              </div>
              <div>
                <span>AI CONFIDENCE: </span>
                <strong className="text-[#17201C]">{(check.confidence * 100).toFixed(0)}%</strong>
              </div>
              <div>
                <span>VERIFICATION METHOD: </span>
                <strong className="text-[#17201C]">{check.verification_method}</strong>
              </div>
            </div>
          </div>

          {/* If Turnover Rule, Show Deterministic Arithmetic Card */}
          {isTurnover && (
            <TurnoverCalculationCard breakdown={firstEvidence?.calculation_breakdown} />
          )}

          {/* Forensic Evidence Text Box */}
          <div className="border border-[#D8DCD6] p-4 bg-white space-y-2">
            <div className="flex items-center justify-between text-[10px] font-mono font-bold uppercase tracking-wider text-[#59625D]">
              <span>GROUND-TRUTH DOCUMENT SNIPPET</span>
              <span className="text-[#808B84]">
                SOURCE: {check.document_name || 'Dossier_Attachment.pdf'} (PAGE {check.page_number || 1})
              </span>
            </div>
            <div className="p-3 bg-[#F4F5F2] border border-[#D8DCD6] font-mono text-[11px] text-[#17201C] leading-relaxed whitespace-pre-wrap">
              {firstEvidence?.snippet || check.evidence_text || check.reason}
            </div>
          </div>

          {/* Verification Source Tag */}
          <div className="p-3 border border-[#D8DCD6] bg-[#EDEFEA] flex items-center justify-between font-mono text-[11px]">
            <span className="text-[#59625D]">DATA SOURCE IDENTIFIER:</span>
            <span className="font-bold text-[#163C32]">
              {firstEvidence?.verified_source || check.verification_source || 'DEMO / MOCK GOVERNMENT SOURCE'}
            </span>
          </div>

        </div>

        {/* Footer Actions */}
        <div className="bg-[#F4F5F2] px-6 py-3 border-t border-[#D8DCD6] flex items-center justify-between">
          <div className="text-[10px] font-mono text-[#59625D]">
            SECTION 4 GFR LEGAL EVIDENCE CITATION
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-4 py-1.5 border border-[#D8DCD6] text-xs font-mono font-semibold text-[#59625D] hover:bg-white hover:text-[#17201C] transition-colors"
            >
              CLOSE
            </button>
            {onOpenReview && (
              <button
                onClick={() => {
                  onClose();
                  onOpenReview(check);
                }}
                className="px-4 py-1.5 bg-[#163C32] hover:bg-[#0E2922] text-white text-xs font-mono font-bold transition-colors"
              >
                PROCEED TO OFFICER REVIEW &rarr;
              </button>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};
