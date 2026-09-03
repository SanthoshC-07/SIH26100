import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { tenderService, bidderService } from '../services';
import { Tender, Requirement, Bidder } from '../types';
import { RiskBadge } from '../components/RiskBadge';

export const TenderDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [tender, setTender] = useState<Tender | null>(null);
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [bidders, setBidders] = useState<Bidder[]>([]);
  const [loading, setLoading] = useState(true);

  const [newBidderName, setNewBidderName] = useState('');
  const [newBidderGstin, setNewBidderGstin] = useState('');
  const [creatingBidder, setCreatingBidder] = useState(false);
  const [showAddBidder, setShowAddBidder] = useState(false);

  useEffect(() => {
    if (!id) return;
    Promise.all([
      tenderService.getTenderById(id),
      tenderService.getRequirements(id),
      bidderService.getBidders(id)
    ]).then(([t, r, b]) => {
      setTender(t);
      setRequirements(r);
      setBidders(b);
    }).finally(() => setLoading(false));
  }, [id]);

  const handleCreateBidder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id || !newBidderName.trim()) return;
    setCreatingBidder(true);
    try {
      const created = await bidderService.createBidder({
        tender_id: id,
        bidder_name: newBidderName.trim(),
        gstin: newBidderGstin.trim() || undefined
      });
      setBidders([created, ...bidders]);
      setNewBidderName('');
      setNewBidderGstin('');
      setShowAddBidder(false);
      navigate(`/bidders/${created.id}`);
    } catch (err) {
      console.error(err);
    } finally {
      setCreatingBidder(false);
    }
  };

  if (loading || !tender) {
    return (
      <div className="flex items-center justify-center h-64 text-[#59625D] font-mono text-xs">
        RETRIEVING TENDER SPECIFICATION MATRIX...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      
      {/* Top Breadcrumb */}
      <button
        onClick={() => navigate('/tenders')}
        className="text-xs font-mono font-bold text-[#59625D] hover:text-[#17201C] flex items-center gap-1.5 transition-colors"
      >
        &larr; BACK TO TENDERS DIRECTORY
      </button>

      {/* Tender Header Card */}
      <div className="border border-[#D8DCD6] bg-white p-6 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-4 border-b border-[#D8DCD6] font-mono text-xs">
          <div className="flex items-center gap-2.5">
            <span className="font-bold text-[#163C32] px-2.5 py-1 border border-[#B4DACB] bg-[#E8F3EE]">
              {tender.tender_number}
            </span>
            <span className="px-2 py-1 border border-[#D8DCD6] bg-[#EDEFEA] font-bold text-[#17201C]">
              {tender.status}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[#59625D]">ESTIMATED VALUE:</span>
            <span className="font-bold text-[#17201C]">
              ₹{(tender.estimated_value / 10000000).toFixed(2)} CRORE
            </span>
          </div>
        </div>

        <div>
          <h1 className="text-xl font-bold tracking-tight text-[#17201C]">
            {tender.title}
          </h1>
          <div className="flex flex-wrap items-center gap-3 text-xs font-mono text-[#59625D] mt-1">
            <span>PROCURING ENTITY: <strong className="text-[#17201C]">{tender.organization}</strong></span>
            <span>•</span>
            <span>CATEGORY: <strong className="text-[#17201C]">{tender.category}</strong></span>
          </div>
        </div>
      </div>

      {/* Requirements Matrix & Bidders Split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Requirements Matrix (2 cols) */}
        <div className="lg:col-span-2 border border-[#D8DCD6] bg-white">
          <div className="px-6 py-3.5 border-b border-[#D8DCD6] bg-[#EDEFEA] flex items-center justify-between font-mono">
            <div>
              <h2 className="text-xs font-bold uppercase tracking-wider text-[#17201C]">
                STRUCTURED COMPLIANCE REQUIREMENTS MATRIX ({requirements.length})
              </h2>
              <p className="text-[10px] text-[#59625D]">
                Parsed clause constraints, numerical thresholds, and statutory verification rules
              </p>
            </div>
            <span className="text-[10px] font-bold text-[#163C32]">
              RULE PARSER ACTIVE
            </span>
          </div>

          <div className="divide-y divide-[#D8DCD6]">
            {requirements.map((req) => (
              <div key={req.id} className="p-4 hover:bg-[#F4F5F2] transition-colors space-y-2 font-mono text-xs">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 bg-[#101A17] text-white font-bold text-[10px]">
                      {req.category}
                    </span>
                    {req.clause_number && (
                      <span className="text-[#59625D] font-bold text-[11px]">
                        {req.clause_number}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    {req.mandatory ? (
                      <span className="px-2 py-0.5 bg-[#FBEBEB] text-[#7A1C1C] border border-[#F1B5B5] text-[10px] font-bold">
                        MANDATORY
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 bg-[#ECEFEA] text-[#4E5853] border border-[#D0D6CF] text-[10px] font-bold">
                        OPTIONAL / PREFERENCE
                      </span>
                    )}
                    <span className="text-[10px] text-[#59625D]">
                      {req.verification_method}
                    </span>
                  </div>
                </div>

                <p className="text-xs text-[#17201C] font-sans font-medium leading-relaxed">
                  {req.description}
                </p>

                {req.threshold && (
                  <div className="text-[11px] font-bold text-[#163C32] bg-[#E8F3EE] p-1.5 border border-[#B4DACB] inline-block">
                    THRESHOLD: {req.threshold_unit === "INR" ? `₹${(req.threshold / 10000000).toFixed(2)} CR` : `${req.threshold} ${req.threshold_unit}`} ({req.period || "CURRENT"})
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Submitted Bidders List (1 col) */}
        <div className="border border-[#D8DCD6] bg-white h-fit">
          <div className="px-5 py-3.5 border-b border-[#D8DCD6] bg-[#EDEFEA] flex items-center justify-between font-mono">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-[#17201C]">
                SUBMITTED BIDDERS ({bidders.length})
              </h3>
              <p className="text-[10px] text-[#59625D]">Compliance dossiers</p>
            </div>
            <button
              onClick={() => setShowAddBidder(!showAddBidder)}
              className="px-2 py-1 bg-[#163C32] hover:bg-[#0E2922] text-white text-[10px] font-bold uppercase"
            >
              + ADD BIDDER
            </button>
          </div>

          {showAddBidder && (
            <form onSubmit={handleCreateBidder} className="p-4 border-b border-[#D8DCD6] bg-[#FCFCFA] space-y-3 font-mono text-xs">
              <input
                type="text"
                required
                value={newBidderName}
                onChange={(e) => setNewBidderName(e.target.value)}
                placeholder="LEGAL ENTITY NAME *"
                className="w-full border border-[#D8DCD6] p-2 bg-white text-[#17201C] outline-none"
              />
              <input
                type="text"
                value={newBidderGstin}
                onChange={(e) => setNewBidderGstin(e.target.value)}
                placeholder="GSTIN (OPTIONAL)"
                className="w-full border border-[#D8DCD6] p-2 bg-white text-[#17201C] outline-none"
              />
              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddBidder(false)}
                  className="px-2.5 py-1 text-xs text-[#59625D]"
                >
                  CANCEL
                </button>
                <button
                  type="submit"
                  disabled={creatingBidder}
                  className="px-3 py-1 bg-[#163C32] text-white text-[10px] font-bold uppercase disabled:opacity-50"
                >
                  {creatingBidder ? "ADDING..." : "SAVE BIDDER"}
                </button>
              </div>
            </form>
          )}

          <div className="divide-y divide-[#D8DCD6]">
            {bidders.map((b) => (
              <div
                key={b.id}
                onClick={() => navigate(`/bidders/${b.id}`)}
                className="p-3.5 hover:bg-[#F4F5F2] cursor-pointer transition-colors space-y-1.5 font-mono"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="font-bold text-xs text-[#17201C] font-sans">
                    {b.bidder_name}
                  </div>
                  {b.risk_level && <RiskBadge level={b.risk_level} size="sm" />}
                </div>

                <div className="flex items-center justify-between text-[11px] text-[#59625D]">
                  <span>{b.gstin || "NO GSTIN"}</span>
                  <span className="font-bold text-[#17201C]">
                    SCORE: {b.compliance_score !== null && b.compliance_score !== undefined ? `${b.compliance_score}/100` : "PENDING"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
};
