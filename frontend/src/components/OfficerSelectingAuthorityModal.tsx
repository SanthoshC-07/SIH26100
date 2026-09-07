import React, { useState } from 'react';
import { ShieldCheck, CheckCircle2, XCircle, AlertTriangle, Scale, Award, Info, Lock } from 'lucide-react';
import { bidderService } from '../services';

interface OfficerSelectingAuthorityModalProps {
  bidderId: string;
  bidderName: string;
  tenderNumber?: string;
  currentStatus?: string;
  complianceScore?: number;
  riskLevel?: string;
  onClose: () => void;
  onSuccess: (updatedStatus: string) => void;
}

export const OfficerSelectingAuthorityModal: React.FC<OfficerSelectingAuthorityModalProps> = ({
  bidderId,
  bidderName,
  tenderNumber = 'MOPNG/PIPE/2026/017',
  currentStatus = 'UNDER_EVALUATION',
  complianceScore = 100,
  riskLevel = 'LOW',
  onClose,
  onSuccess
}) => {
  const [decision, setDecision] = useState<'ELIGIBLE' | 'INELIGIBLE' | 'SHORTLISTED' | 'QUALIFIED' | 'DISQUALIFIED'>('ELIGIBLE');
  const [statutoryRule, setStatutoryRule] = useState('GFR 2017 Rule 173 - Technical & Financial Competency');
  const [remarks, setRemarks] = useState(
    'Bidder satisfies all statutory tax compliance (GST & PAN), meets 3-year turnover threshold, and possesses proven ≥ 100 KM 24-inch natural gas pipeline execution experience.'
  );
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const rulesList = [
    'GFR 2017 Rule 173 - Technical & Financial Competency',
    'MoPNG Section 4.2 - Pipeline EPC Contractor Eligibility',
    'Public Procurement (Preference to Make in India) Class-I Local Supplier',
    'GFR 2017 Rule 151 - Debarment & Integrity Verification Clear',
    'Manual Review Override - Tender Evaluation Committee Resolution'
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!remarks.trim()) {
      setError('A comprehensive officer evaluation justification is strictly required.');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      await bidderService.recordSelectingAuthorityDecision(bidderId, {
        decision,
        remarks: remarks.trim(),
        statutory_rule: statutoryRule,
        technical_score: complianceScore,
        financial_cleared: decision === 'ELIGIBLE' || decision === 'QUALIFIED' || decision === 'SHORTLISTED'
      });

      onSuccess(decision);
      onClose();
    } catch (err: any) {
      console.error('Selecting authority error:', err);
      setError(err?.response?.data?.detail?.message || err?.response?.data?.detail || 'Failed to record decision. Ensure you have Procurement Officer privileges.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4 backdrop-blur-xs font-sans">
      <div className="bg-[#FFFFFF] border border-[#BAC4CE] rounded-lg shadow-2xl max-w-2xl w-full overflow-hidden text-xs">
        
        {/* Header */}
        <div className="px-6 py-4 bg-[#10283A] text-white flex items-center justify-between border-b border-[#18374D]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded bg-[#D98A16] text-[#10283A] flex items-center justify-center font-bold">
              <Scale className="w-4 h-4 text-[#10283A]" />
            </div>
            <div>
              <div className="text-[10px] font-mono text-[#D98A16] font-bold uppercase tracking-wider">
                PROCUREMENT OFFICER SELECTING AUTHORITY
              </div>
              <h2 className="text-base font-serif font-bold text-white leading-tight">
                Determine Bidder Eligibility for Tender Award
              </h2>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="text-[#8A9BA8] hover:text-white text-lg font-bold p-1 rounded"
          >
            ✕
          </button>
        </div>

        {/* Content Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          
          {/* Bidder Context Summary Card */}
          <div className="p-3.5 bg-[#F4F6F8] border border-[#D9DEE3] rounded grid grid-cols-2 sm:grid-cols-4 gap-3 text-[11px]">
            <div>
              <span className="text-[#66717C] uppercase font-semibold text-[9px] block">Bidder Legal Entity</span>
              <span className="font-bold text-[#10283A] block truncate">{bidderName}</span>
            </div>
            <div>
              <span className="text-[#66717C] uppercase font-semibold text-[9px] block">Tender Number</span>
              <span className="font-mono text-[#10283A] block font-semibold">{tenderNumber}</span>
            </div>
            <div>
              <span className="text-[#66717C] uppercase font-semibold text-[9px] block">AI Compliance Score</span>
              <span className="font-mono font-bold text-[#0F6B38] block">{complianceScore}%</span>
            </div>
            <div>
              <span className="text-[#66717C] uppercase font-semibold text-[9px] block">Current Status</span>
              <span className="font-mono font-bold text-[#D98A16] block">{currentStatus}</span>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-[#FDF2F2] text-[#C83B32] border border-[#F5C2C7] rounded text-xs">
              {error}
            </div>
          )}

          {/* Decision Selection Grid */}
          <div>
            <label className="block text-[11px] font-bold text-[#10283A] uppercase tracking-wider mb-2 font-mono">
              Select Official Eligibility Determination <span className="text-[#C83B32]">*</span>
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
              
              {/* 1. ELIGIBLE / QUALIFIED */}
              <button
                type="button"
                onClick={() => {
                  setDecision('ELIGIBLE');
                  setRemarks('Bidder meets all mandatory statutory, technical pipeline experience, and financial net worth criteria. Qualified for technical award round.');
                }}
                className={`p-3 rounded border text-left transition-all flex flex-col justify-between ${
                  decision === 'ELIGIBLE' || decision === 'QUALIFIED'
                    ? 'bg-[#E8F8EE] border-[#0F6B38] ring-2 ring-[#0F6B38]/30 shadow-sm'
                    : 'bg-[#FFFFFF] border-[#D9DEE3] hover:bg-[#F9FAFB]'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-[#0F6B38] font-mono">ELIGIBLE / QUALIFIED</span>
                  <CheckCircle2 className="w-4 h-4 text-[#0F6B38]" />
                </div>
                <p className="text-[10.5px] text-[#556270] mt-1.5 leading-snug">
                  Bidder meets all tender specifications &amp; passes GFR 2017 thresholds.
                </p>
              </button>

              {/* 2. SHORTLISTED */}
              <button
                type="button"
                onClick={() => {
                  setDecision('SHORTLISTED');
                  setRemarks('Bidder cleared preliminary compliance checks and is shortlisted for technical presentation and commercial price opening.');
                }}
                className={`p-3 rounded border text-left transition-all flex flex-col justify-between ${
                  decision === 'SHORTLISTED'
                    ? 'bg-[#FFF4E0] border-[#D98A16] ring-2 ring-[#D98A16]/30 shadow-sm'
                    : 'bg-[#FFFFFF] border-[#D9DEE3] hover:bg-[#F9FAFB]'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-[#8A5000] font-mono">SHORTLISTED</span>
                  <Award className="w-4 h-4 text-[#D98A16]" />
                </div>
                <p className="text-[10.5px] text-[#556270] mt-1.5 leading-snug">
                  Shortlisted for final technical presentation and commercial opening.
                </p>
              </button>

              {/* 3. INELIGIBLE / DISQUALIFIED */}
              <button
                type="button"
                onClick={() => {
                  setDecision('INELIGIBLE');
                  setRemarks('Bidder fails mandatory tender criteria (insufficient experience / turnover threshold / statutory non-compliance). Disqualified.');
                }}
                className={`p-3 rounded border text-left transition-all flex flex-col justify-between ${
                  decision === 'INELIGIBLE' || decision === 'DISQUALIFIED'
                    ? 'bg-[#FDECEC] border-[#9C211B] ring-2 ring-[#9C211B]/30 shadow-sm'
                    : 'bg-[#FFFFFF] border-[#D9DEE3] hover:bg-[#F9FAFB]'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-[#9C211B] font-mono">INELIGIBLE</span>
                  <XCircle className="w-4 h-4 text-[#9C211B]" />
                </div>
                <p className="text-[10.5px] text-[#556270] mt-1.5 leading-snug">
                  Disqualify bidder due to mandatory criteria failure or threshold gap.
                </p>
              </button>

            </div>
          </div>

          {/* Statutory Reference Rule */}
          <div className="space-y-1.5">
            <label className="block text-[11px] font-bold text-[#66717C] uppercase font-mono">
              Statutory Procurement Standard / GFR Rule
            </label>
            <select
              value={statutoryRule}
              onChange={(e) => setStatutoryRule(e.target.value)}
              className="w-full px-3 py-2 bg-white border border-[#D9DEE3] rounded text-xs font-sans text-[#17212B] focus:outline-none focus:border-[#10283A]"
            >
              {rulesList.map((r, i) => (
                <option key={i} value={r}>{r}</option>
              ))}
            </select>
          </div>

          {/* Officer Remarks / Written Justification */}
          <div className="space-y-1.5">
            <label className="block text-[11px] font-bold text-[#66717C] uppercase font-mono">
              Officer Determination Justification &amp; Findings <span className="text-[#C83B32]">*</span>
            </label>
            <textarea
              rows={3}
              required
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
              placeholder="Enter comprehensive findings, verified document references, and evaluation committee determination..."
              className="w-full p-2.5 bg-white border border-[#D9DEE3] rounded text-xs text-[#17212B] focus:outline-none focus:border-[#10283A] leading-relaxed font-sans"
            />
            <div className="text-[10.5px] text-[#66717C] flex items-center gap-1">
              <Lock className="w-3 h-3 text-[#10283A]" />
              <span>This decision is permanently recorded in the immutable GFR 2017 Audit Trail with officer timestamp.</span>
            </div>
          </div>

          {/* Action Footer */}
          <div className="flex items-center justify-between pt-3 border-t border-[#D9DEE3]">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-white border border-[#BAC4CE] hover:bg-[#F4F6F8] text-[#10283A] font-semibold rounded text-xs transition-colors"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={submitting}
              className={`px-5 py-2 font-bold text-xs rounded shadow transition-colors flex items-center gap-1.5 text-white ${
                decision === 'ELIGIBLE' || decision === 'QUALIFIED'
                  ? 'bg-[#0F6B38] hover:bg-[#0D5C30]'
                  : decision === 'SHORTLISTED'
                  ? 'bg-[#D98A16] hover:bg-[#C0770E]'
                  : 'bg-[#9C211B] hover:bg-[#801B16]'
              }`}
            >
              <Scale className="w-3.5 h-3.5" />
              <span>
                {submitting ? 'Recording Decision...' : `Confirm Official Decision: ${decision}`}
              </span>
            </button>
          </div>

        </form>

      </div>
    </div>
  );
};
