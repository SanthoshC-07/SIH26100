import React, { useState } from 'react';
import { ComplianceCheck } from '../types';
import { complianceService } from '../services';

interface OfficerReviewModalProps {
  check: ComplianceCheck | null;
  onClose: () => void;
  onSuccess: () => void;
}

export const OfficerReviewModal: React.FC<OfficerReviewModalProps> = ({ check, onClose, onSuccess }) => {
  if (!check) return null;

  const [actionType, setActionType] = useState('OFFICER_OVERRIDE');
  const [newStatus, setNewStatus] = useState<'PASS' | 'FAIL' | 'REVIEW'>(check.status === 'PASS' ? 'REVIEW' : 'PASS');
  const [remarks, setRemarks] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!remarks.trim()) {
      setError('A written justification / remark is mandatory under Section 4 GFR audit standards.');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      await complianceService.submitOfficerReview(check.id, {
        action_type: actionType,
        new_status: newStatus,
        remarks: remarks.trim(),
        requirement_id: check.requirement_id,
      });
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to record officer override determination.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-[#101A17]/70 backdrop-blur-none flex items-center justify-center p-4">
      <div className="bg-white border border-[#22322C] max-w-xl w-full shadow-2xl flex flex-col">
        
        {/* Header Bar */}
        <div className="bg-[#101A17] text-white px-6 py-4 flex items-center justify-between border-b border-[#22322C]">
          <div className="space-y-0.5">
            <h3 className="text-xs font-mono font-bold tracking-wider uppercase text-[#EDEFEA]">
              PROCUREMENT OFFICER DECISION DISCRETION
            </h3>
            <p className="text-[10px] text-[#808B84] font-mono">
              SECTION 4 GFR HUMAN-IN-THE-LOOP GOVERNANCE
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-[#808B84] hover:text-white font-mono text-sm"
          >
            ✕
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5 text-xs">
          
          {/* Target Clause Context */}
          <div className="p-3 border border-[#D8DCD6] bg-[#FCFCFA] space-y-1.5 font-mono">
            <div className="text-[10px] text-[#59625D] font-bold uppercase tracking-wider">
              EVALUATED REQUIREMENT CLAUSE:
            </div>
            <div className="text-xs font-bold text-[#17201C]">
              {check.requirement_category} — {check.requirement_description || check.reason}
            </div>
            <div className="pt-1.5 border-t border-[#D8DCD6] flex items-center justify-between text-[11px] text-[#59625D]">
              <span>CURRENT STATE: <strong className="text-[#17201C]">{check.status}</strong></span>
              <span>AI CONFIDENCE: <strong className="text-[#163C32]">{(check.confidence * 100).toFixed(0)}%</strong></span>
            </div>
          </div>

          {/* Action Selector */}
          <div className="space-y-1.5">
            <label className="block text-[10px] font-mono font-bold text-[#59625D] uppercase tracking-wider">
              REVIEW ACTION CLASSIFICATION
            </label>
            <select
              value={actionType}
              onChange={(e) => setActionType(e.target.value)}
              className="w-full text-xs font-mono rounded-none border border-[#D8DCD6] p-2.5 bg-white text-[#17201C] focus:border-[#163C32] outline-none"
            >
              <option value="OFFICER_OVERRIDE">OFFICER DISCRETIONARY OVERRIDE</option>
              <option value="OFFICER_ACCEPT">ACCEPT AI RECOMMENDATION</option>
              <option value="REQUEST_CLARIFICATION">REQUEST BIDDER CLARIFICATION / ATTACHMENT</option>
              <option value="DISQUALIFY_BIDDER">MANDATORY DISQUALIFICATION</option>
            </select>
          </div>

          {/* Determined Status Selector (Sharp Buttons) */}
          <div className="space-y-1.5">
            <label className="block text-[10px] font-mono font-bold text-[#59625D] uppercase tracking-wider">
              NEW COMPLIANCE DETERMINATION
            </label>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setNewStatus('PASS')}
                className={`py-2 text-xs font-mono font-bold border transition-colors ${
                  newStatus === 'PASS'
                    ? 'bg-[#163C32] text-white border-[#163C32]'
                    : 'bg-white text-[#17201C] border-[#D8DCD6] hover:bg-[#F4F5F2]'
                }`}
              >
                PASS
              </button>
              <button
                type="button"
                onClick={() => setNewStatus('FAIL')}
                className={`py-2 text-xs font-mono font-bold border transition-colors ${
                  newStatus === 'FAIL'
                    ? 'bg-[#7A1C1C] text-white border-[#7A1C1C]'
                    : 'bg-white text-[#17201C] border-[#D8DCD6] hover:bg-[#F4F5F2]'
                }`}
              >
                FAIL
              </button>
              <button
                type="button"
                onClick={() => setNewStatus('REVIEW')}
                className={`py-2 text-xs font-mono font-bold border transition-colors ${
                  newStatus === 'REVIEW'
                    ? 'bg-[#875200] text-white border-[#875200]'
                    : 'bg-white text-[#17201C] border-[#D8DCD6] hover:bg-[#F4F5F2]'
                }`}
              >
                REVIEW
              </button>
            </div>
          </div>

          {/* Justification Textarea */}
          <div className="space-y-1.5">
            <label className="block text-[10px] font-mono font-bold text-[#59625D] uppercase tracking-wider">
              OFFICER AUDIT REMARKS & JUSTIFICATION <span className="text-[#7A1C1C]">*</span>
            </label>
            <textarea
              required
              rows={3}
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
              placeholder="Record definitive rationale. This explanation is committed to the immutable audit trail."
              className="w-full text-xs font-mono border border-[#D8DCD6] p-2.5 bg-white text-[#17201C] focus:border-[#163C32] outline-none"
            />
          </div>

          {error && (
            <div className="p-2.5 bg-[#FBEBEB] text-[#7A1C1C] border border-[#F1B5B5] font-mono text-xs">
              {error}
            </div>
          )}

          {/* Footer Actions */}
          <div className="pt-3 border-t border-[#D8DCD6] flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-[#D8DCD6] font-mono text-xs font-semibold text-[#59625D] hover:bg-[#F4F5F2] hover:text-[#17201C] transition-colors"
            >
              CANCEL
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 bg-[#163C32] hover:bg-[#0E2922] text-white font-mono text-xs font-bold transition-colors disabled:opacity-50"
            >
              {submitting ? 'COMMITTING AUDIT...' : 'COMMIT DETERMINATION'}
            </button>
          </div>

        </form>

      </div>
    </div>
  );
};
