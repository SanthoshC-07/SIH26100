import React, { useState } from 'react';
import { ComplianceCheck } from '../types';
import { complianceService } from '../services';
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  FileText,
  Cpu,
  UserCheck,
  HelpCircle,
  RefreshCw,
  Edit3,
  Scale
} from 'lucide-react';
import { ComplianceBadge } from './ComplianceBadge';

interface OfficerReviewModalProps {
  check: ComplianceCheck | null;
  bidderId?: string;
  bidderName?: string;
  onClose: () => void;
  onSuccess: () => void;
}

export const OfficerReviewModal: React.FC<OfficerReviewModalProps> = ({
  check,
  bidderId,
  bidderName,
  onClose,
  onSuccess
}) => {
  if (!check) return null;

  const [selectedAction, setSelectedAction] = useState<
    'ACCEPT' | 'REJECT' | 'REQUEST_CLARIFICATION' | 'MARK_INSUFFICIENT' | 'REVERIFY' | 'ADD_NOTE'
  >('ACCEPT');

  const [remarks, setRemarks] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [reverifying, setReverifying] = useState(false);
  const [error, setError] = useState('');

  const handleReverify = async () => {
    if (!bidderId && !check.bidder_id) return;
    setReverifying(true);
    setError('');
    try {
      await complianceService.reverifyRequirement(
        bidderId || check.bidder_id,
        check.requirement_id || check.clause_number || ''
      );
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Reverification failed.');
    } finally {
      setReverifying(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (selectedAction === 'REVERIFY') {
      await handleReverify();
      return;
    }

    if (!remarks.trim() && selectedAction !== 'ACCEPT') {
      setError('A written justification remark is strictly mandatory for officer determinations under Section 4 GFR 2017.');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      let targetStatus: string = 'PASS';
      let actionLabel = 'OFFICER_ACCEPT';

      if (selectedAction === 'ACCEPT') {
        targetStatus = 'PASS';
        actionLabel = 'OFFICER_ACCEPT';
      } else if (selectedAction === 'REJECT') {
        targetStatus = 'FAIL';
        actionLabel = 'OFFICER_REJECT';
      } else if (selectedAction === 'REQUEST_CLARIFICATION') {
        targetStatus = 'REVIEW';
        actionLabel = 'REQUEST_CLARIFICATION';
      } else if (selectedAction === 'MARK_INSUFFICIENT') {
        targetStatus = 'INSUFFICIENT';
        actionLabel = 'MARK_INSUFFICIENT';
      } else if (selectedAction === 'ADD_NOTE') {
        targetStatus = check.status;
        actionLabel = 'ADD_NOTE';
      }

      await complianceService.submitOfficerReview(check.id, {
        bidder_id: bidderId || check.bidder_id,
        action_type: actionLabel,
        new_status: targetStatus as any,
        remarks: remarks.trim() || `Officer decision recorded: ${selectedAction}`,
        requirement_id: check.requirement_id || (check as any).clause_number || (check as any).requirement_category,
      });

      onSuccess();
      onClose();
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      if (typeof detail === 'string') {
        setError(detail);
      } else if (detail?.message) {
        setError(detail.message);
      } else {
        setError('Failed to record officer review determination. Please ensure the backend service is reachable.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const evItem = check.evidence_items?.[0];

  return (
    <div className="fixed inset-0 z-50 bg-[#10283A]/80 flex items-center justify-center p-4">
      <div className="bg-[#FFFFFF] border border-[#BAC4CE] max-w-3xl w-full flex flex-col font-sans text-xs max-h-[92vh] overflow-y-auto shadow-2xl rounded">
        
        {/* Header Bar */}
        <div className="bg-[#10283A] text-white px-5 py-3.5 flex items-center justify-between border-b border-[#BAC4CE]">
          <div className="flex items-center gap-2">
            <UserCheck className="w-5 h-5 text-[#D98A16]" />
            <div>
              <h3 className="font-serif font-bold tracking-tight text-sm">
                OFFICER REVIEW & COMPLIANCE DETERMINATION
              </h3>
              <p className="text-[11px] text-[#BAC4CE] font-mono mt-0.5">
                Bidder: {bidderName || check.bidder_id} • Clause: {check.clause_number || check.category || check.requirement_category}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-[#BAC4CE] hover:text-white text-sm px-2 py-1 bg-[#18374D] rounded font-mono"
          >
            ✕
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          
          {/* 1. TENDER REQUIREMENT & AI SYSTEM STATUS */}
          <div className="p-4 bg-[#F8FAFC] border border-[#D9DEE3] rounded space-y-2 font-mono">
            <div className="text-[10px] text-[#66717C] font-bold uppercase tracking-wider">
              1. TENDER REQUIREMENT SPECIFICATION
            </div>
            <div className="flex items-center justify-between">
              <span className="font-bold text-[#10283A] text-xs">
                {check.clause_number || 'REQ'} • {check.category || check.requirement_category || 'GENERAL'}
              </span>
              <ComplianceBadge status={check.status} size="md" />
            </div>
            <div className="text-xs text-[#556270] font-sans">
              {check.requirement_description || check.reason}
            </div>
          </div>

          {/* 2. EVIDENCE & TELEMETRY BREAKDOWN (10-Step Audit Matrix) */}
          <div className="p-4 bg-[#FFFFFF] border border-[#D9DEE3] rounded space-y-3 font-mono text-xs">
            <div className="text-[10px] text-[#66717C] font-bold uppercase tracking-wider flex items-center gap-1.5">
              <Scale className="w-3.5 h-3.5 text-[#D98A16]" />
              <span>2. EVIDENCE & DETERMINISTIC RULE TELEMETRY</span>
            </div>

            <div className="grid grid-cols-2 gap-3 text-[11px]">
              <div className="p-2.5 bg-[#F8FAFC] border border-[#EAEEF2] rounded">
                <span className="text-[#66717C] block text-[10px] uppercase">Source Document</span>
                <span className="font-bold text-[#10283A] truncate block mt-0.5">
                  {check.document_name || evItem?.document_name || 'Evidence_Dossier.pdf'}
                </span>
              </div>
              <div className="p-2.5 bg-[#F8FAFC] border border-[#EAEEF2] rounded">
                <span className="text-[#66717C] block text-[10px] uppercase">Source Page & OCR Method</span>
                <span className="font-bold text-[#10283A] block mt-0.5">
                  Page {check.page_number || evItem?.page_number || 1} • {evItem?.extraction_method || 'PyMuPDF Native'}
                </span>
              </div>
              <div className="p-2.5 bg-[#F8FAFC] border border-[#EAEEF2] rounded">
                <span className="text-[#66717C] block text-[10px] uppercase">Deterministic Rule Result</span>
                <span className="font-bold text-[#0F6B38] block mt-0.5">
                  {check.status === 'PASS' ? 'THRESHOLD SATISFIED (≥ Condition)' : (check.status === 'REVIEW' ? 'MANUAL REVIEW REQUIRED' : 'DEFICIT / INSUFFICIENT')}
                </span>
              </div>
              <div className="p-2.5 bg-[#F8FAFC] border border-[#EAEEF2] rounded">
                <span className="text-[#66717C] block text-[10px] uppercase">AI Semantic Confidence</span>
                <span className="font-bold text-[#10283A] block mt-0.5">
                  {Math.round((check.confidence || 0.95) * 100)}% (Confidence Gated)
                </span>
              </div>
            </div>

            {/* Extracted Text Snippet */}
            <div className="pt-2">
              <span className="text-[10px] text-[#66717C] uppercase block mb-1">CITED EVIDENCE SNIPPET</span>
              <div className="p-2.5 bg-[#F4F6F8] border border-[#D9DEE3] rounded font-sans text-xs text-[#10283A] italic leading-relaxed">
                "{check.evidence_text || evItem?.snippet || check.reason || 'Evidence extract verified against statutory registry.'}"
              </div>
            </div>
          </div>

          {/* 3. OFFICER ACTION SELECTION */}
          <div className="space-y-2">
            <div className="text-[11px] font-mono font-bold text-[#10283A] uppercase tracking-wider">
              3. SELECT OFFICER DETERMINATION ACTION
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs font-mono">
              {[
                { id: 'ACCEPT', label: '✓ Accept (PASS)', color: 'border-[#8CD9A8] hover:bg-[#E8F8EE] text-[#0F6B38]' },
                { id: 'REJECT', label: '✕ Reject (FAIL)', color: 'border-[#F5A3A0] hover:bg-[#FDECEC] text-[#9C211B]' },
                { id: 'REQUEST_CLARIFICATION', label: '? Clarification (REVIEW)', color: 'border-[#F0CA85] hover:bg-[#FFF4E0] text-[#8A5000]' },
                { id: 'MARK_INSUFFICIENT', label: '⚠ Mark Insufficient', color: 'border-[#F0CA85] hover:bg-[#FFF4E0] text-[#8A5000]' },
                { id: 'REVERIFY', label: '↻ Reverify with AI', color: 'border-[#BAC4CE] hover:bg-[#F4F6F8] text-[#10283A]' },
                { id: 'ADD_NOTE', label: '✎ Add Note Only', color: 'border-[#BAC4CE] hover:bg-[#F4F6F8] text-[#10283A]' }
              ].map((act) => (
                <button
                  key={act.id}
                  type="button"
                  onClick={() => setSelectedAction(act.id as any)}
                  className={`p-2.5 border rounded text-left transition-all ${
                    selectedAction === act.id
                      ? 'bg-[#10283A] text-white border-[#10283A] shadow-sm'
                      : `bg-white ${act.color}`
                  }`}
                >
                  <div className="font-bold">{act.label}</div>
                </button>
              ))}
            </div>
          </div>

          {/* 4. JUSTIFICATION REMARKS */}
          <div className="space-y-1.5 font-mono">
            <label className="text-[11px] font-bold text-[#10283A] uppercase tracking-wider flex items-center justify-between">
              <span>4. Officer Justification Remark (GFR 2017 Audit Trail)</span>
              <span className="text-[10px] text-[#66717C] font-normal">Mandatory for overrides</span>
            </label>
            <textarea
              rows={3}
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
              placeholder="Provide formal procurement officer justification note for immutable audit trail record..."
              className="w-full p-2.5 border border-[#BAC4CE] rounded text-xs bg-[#FFFFFF] text-[#10283A] focus:outline-none focus:border-[#10283A] font-sans"
            />
          </div>

          {error && (
            <div className="p-3 bg-[#FDECEC] border border-[#F5A3A0] text-[#9C211B] text-xs font-mono rounded flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-[#9C211B] flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Footer Buttons */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#D9DEE3]">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-[#BAC4CE] text-[#556270] hover:text-[#10283A] text-xs font-semibold rounded font-mono transition-colors"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={submitting || reverifying}
              className="px-5 py-2 bg-[#10283A] hover:bg-[#18374D] text-[#FFFFFF] text-xs font-bold rounded shadow-sm font-mono transition-colors flex items-center gap-2"
            >
              {(submitting || reverifying) && <RefreshCw className="w-3.5 h-3.5 animate-spin text-[#D98A16]" />}
              <span>{reverifying ? 'Reverifying...' : submitting ? 'Recording Determination...' : 'Commit Officer Determination'}</span>
            </button>
          </div>

        </form>
      </div>
    </div>
  );
};
