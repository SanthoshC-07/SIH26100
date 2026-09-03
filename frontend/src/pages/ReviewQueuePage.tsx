import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { complianceService } from '../services';
import { ComplianceCheck } from '../types';
import { ComplianceBadge } from '../components/ComplianceBadge';
import { OfficerReviewModal } from '../components/OfficerReviewModal';
import { EvidenceModal } from '../components/EvidenceModal';

export const ReviewQueuePage: React.FC = () => {
  const navigate = useNavigate();
  const [pendingChecks, setPendingChecks] = useState<ComplianceCheck[]>([]);
  const [loading, setLoading] = useState(true);

  const [selectedForReview, setSelectedForReview] = useState<ComplianceCheck | null>(null);
  const [selectedForEvidence, setSelectedForEvidence] = useState<ComplianceCheck | null>(null);

  const loadPending = async () => {
    setLoading(true);
    try {
      const data = await complianceService.getPendingReviews();
      setPendingChecks(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPending();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-[#59625D] font-mono text-xs">
        RETRIEVING OFFICER REVIEW QUEUE...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="border border-[#D8DCD6] bg-white p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 font-mono">
        <div>
          <div className="text-[10px] uppercase tracking-widest text-[#A7833B] font-bold">
            HUMAN-IN-THE-LOOP GOVERNANCE WORKBENCH
          </div>
          <h1 className="text-base font-bold tracking-tight text-[#17201C] mt-0.5 uppercase">
            REVIEW QUEUE ({pendingChecks.length} ITEMS REQUIRE ATTENTION)
          </h1>
          <p className="text-xs text-[#59625D] font-sans mt-0.5">
            Requirements where AI detected marginal confidence, discrepancy, or requires discretionary determination
          </p>
        </div>
        <div className="px-3 py-1 bg-[#FDF5E6] border border-[#F6D59B] text-[#875200] text-xs font-bold">
          SECTION 4 GFR ACTION REQUIRED
        </div>
      </div>

      {pendingChecks.length === 0 ? (
        <div className="border border-[#D8DCD6] bg-white p-12 text-center space-y-2 font-mono">
          <div className="text-xs font-bold text-[#114B3A] uppercase">
            ZERO PENDING DISCRETIONARY REVIEWS
          </div>
          <p className="text-xs text-[#59625D]">
            All bidder verification checks have been processed.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {pendingChecks.map((check) => (
            <div
              key={check.id}
              className="border border-[#D8DCD6] bg-white p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 font-mono"
            >
              <div className="space-y-2 max-w-2xl text-xs">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="px-2 py-0.5 bg-[#101A17] text-white font-bold text-[10px]">
                    {check.requirement_category}
                  </span>
                  <ComplianceBadge status={check.status} size="sm" />
                  <span className="text-[#875200] font-bold">
                    CONFIDENCE: {(check.confidence * 100).toFixed(0)}%
                  </span>
                  <span className="text-[#808B84] text-[10px]">
                    SOURCE: {check.verification_source}
                  </span>
                </div>

                <h2 className="text-xs font-bold text-[#17201C] font-sans">
                  {check.requirement_description || check.reason}
                </h2>

                <div className="text-xs text-[#17201C] bg-[#FCFCFA] p-3 border border-[#D8DCD6] font-sans">
                  <strong>Verification Note:</strong> {check.reason}
                </div>

                <div className="text-[10px] text-[#59625D]">
                  ATTACHMENT: <strong>{check.document_name || "Dossier_Attachment.pdf"}</strong> (PAGE {check.page_number || 1})
                </div>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={() => setSelectedForEvidence(check)}
                  className="px-3 py-1.5 border border-[#D8DCD6] bg-white hover:bg-[#EDEFEA] text-[11px] font-bold text-[#17201C]"
                >
                  VIEW EVIDENCE
                </button>
                <button
                  onClick={() => setSelectedForReview(check)}
                  className="px-3.5 py-1.5 bg-[#163C32] hover:bg-[#0E2922] text-white text-[11px] font-bold uppercase"
                >
                  REVIEW & OVERRIDE
                </button>
                <button
                  onClick={() => navigate(`/bidders/${check.bidder_id}`)}
                  className="px-3 py-1.5 border border-[#101A17] bg-[#101A17] text-white text-[11px] font-bold"
                >
                  DOSSIER &rarr;
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modals */}
      <EvidenceModal
        check={selectedForEvidence}
        onClose={() => setSelectedForEvidence(null)}
        onOpenReview={(c) => setSelectedForReview(c)}
      />

      <OfficerReviewModal
        check={selectedForReview}
        onClose={() => setSelectedForReview(null)}
        onSuccess={() => loadPending()}
      />

    </div>
  );
};
