import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ListFilter,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  Search,
  RefreshCw,
  ExternalLink,
  ShieldCheck,
  UserCheck,
  Check,
  ChevronRight,
  Plus,
  ArrowRight
} from 'lucide-react';
import { bidderService } from '../services';
import { Bidder, ComplianceCheck } from '../types';
import { OfficerReviewModal } from '../components/OfficerReviewModal';

export const ReviewQueuePage: React.FC = () => {
  const navigate = useNavigate();
  const [bidders, setBidders] = useState<Bidder[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedCheckForReview, setSelectedCheckForReview] = useState<ComplianceCheck | null>(null);
  const [selectedBidderName, setSelectedBidderName] = useState('');
  const [showLogModal, setShowLogModal] = useState(false);
  const [logSuccessMessage, setLogSuccessMessage] = useState('');

  const loadData = () => {
    setLoading(true);
    bidderService.getBidders()
      .then((b) => setBidders(b))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const indusBidder = bidders.find(b => b.legal_name.toLowerCase().includes('indus'));
  const bharatBidder = bidders.find(b => b.legal_name.toLowerCase().includes('bharat'));
  const praveenBidder = bidders.find(b => b.legal_name.toLowerCase().includes('praveen'));

  // Items structured exactly per PDF Page 6 Recent Complaints + SIH compliance review items
  const complaintsList = [
    {
      id: 'CPL-0341',
      bidder: 'Nova Petrochem Co.',
      bidderId: bharatBidder?.id || 'b-nova',
      category: 'Bid Document Disputes',
      status: 'Resolved',
      filed: '02 Sep 2026',
      requirement: 'REQ-007 — HSE / SAFETY',
      issue: 'Dispute regarding provisional ISO 45001 certificate; verified with accredited registry.',
      confidence: 92,
      assignedOfficer: 'Alex Rivera'
    },
    {
      id: 'CPL-0340',
      bidder: 'Summit Pipeline Inc.',
      bidderId: indusBidder?.id || 'b-summit',
      category: 'Payment Delays',
      status: 'In Progress',
      filed: '03 Sep 2026',
      requirement: 'REQ-006 — SOLVENCY & EMD',
      issue: 'Bank guarantee e-PBG confirmation pending from State Bank of India treasury branch.',
      confidence: 78,
      assignedOfficer: 'Alex Rivera'
    },
    {
      id: 'CPL-0338',
      bidder: 'Delta Refining Group',
      bidderId: indusBidder?.id || 'b-delta',
      category: 'Verification Errors',
      status: 'Escalated',
      filed: '01 Sep 2026',
      requirement: 'REQ-004 — SIMILAR PIPELINE EXPERIENCE',
      issue: 'Pipeline length shortfall: 60 KM submitted vs 100 KM mandatory threshold; escalated to CPO.',
      confidence: 96,
      assignedOfficer: 'Alex Rivera'
    },
    {
      id: 'CPL-0335',
      bidder: 'Horizon Oilfield Svcs.',
      bidderId: bharatBidder?.id || 'b-horizon',
      category: 'Other',
      status: 'In Progress',
      filed: '29 Aug 2026',
      requirement: 'REQ-001 — STATUTORY GSTIN',
      issue: 'GST legal entity name spelling variance between PAN database and GeM registration.',
      confidence: 84,
      assignedOfficer: 'Alex Rivera'
    },
    {
      id: 'CPL-0329',
      bidder: 'Indus Pipeline Infrastructure',
      bidderId: indusBidder?.id || 'b-indus',
      category: 'Bid Document Disputes',
      status: 'Escalated',
      filed: '28 Aug 2026',
      requirement: 'REQ-003 — FINANCIAL TURNOVER',
      issue: 'Turnover shortfall: 3-year average ₹18.00 Cr vs ₹25.00 Cr mandatory qualification threshold.',
      confidence: 95,
      assignedOfficer: 'Alex Rivera'
    }
  ];

  const filteredComplaints = complaintsList.filter(item => {
    const matchSearch = item.bidder.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.issue.toLowerCase().includes(searchQuery.toLowerCase());
    const matchCategory = selectedCategory === 'ALL' || item.category === selectedCategory;
    return matchSearch && matchCategory;
  });

  const handleOpenReview = (item: any) => {
    setSelectedBidderName(item.bidder);
    setSelectedCheckForReview({
      id: item.id,
      bidder_id: item.bidderId || '',
      requirement_id: item.requirement,
      requirement_category: item.category,
      requirement_description: item.issue,
      requirement_mandatory: true,
      status: item.status === 'Resolved' ? 'PASS' : item.status === 'Escalated' ? 'FAIL' : 'REVIEW',
      confidence: item.confidence / 100,
      reason: item.issue,
      evidence_text: item.issue,
      document_name: 'Complaint_Dossier_' + item.id + '.pdf',
      page_number: 1,
      rule_version: '3.0.0',
      verified_at: new Date().toISOString()
    });
  };

  const getStatusPill = (status: string) => {
    if (status === 'Resolved') {
      return (
        <span className="inline-block px-3.5 py-1 text-[11px] font-semibold text-white bg-[#198754] rounded-md tracking-tight">
          Resolved
        </span>
      );
    }
    if (status === 'In Progress') {
      return (
        <span className="inline-block px-3.5 py-1 text-[11px] font-semibold text-white bg-[#D98A16] rounded-md tracking-tight">
          In Progress
        </span>
      );
    }
    return (
      <span className="inline-block px-3.5 py-1 text-[11px] font-semibold text-white bg-[#C83B32] rounded-md tracking-tight">
        Escalated
      </span>
    );
  };

  return (
    <div className="space-y-6 font-sans">
      
      {/* ── Top Header Section (from PDF Page 6) ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="text-[11px] font-mono tracking-widest text-[#66717C] uppercase font-bold">
            COMPLAINT RECEIVER
          </div>
          <h1 className="text-2xl sm:text-3xl font-serif font-bold text-[#10283A] tracking-tight mt-0.5">
            Complaint Receiver
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowLogModal(true)}
            className="px-5 py-2.5 bg-[#10283A] hover:bg-[#18374D] text-white text-xs font-semibold rounded-md transition-colors shadow-sm inline-flex items-center gap-1.5"
            title="Log New Complaint"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>+ Log Complaint</span>
          </button>

          <button
            onClick={loadData}
            title="Refresh Queue"
            className="p-2.5 bg-[#FFFFFF] hover:bg-[#F4F5F7] border border-[#D9DEE3] text-[#66717C] hover:text-[#10283A] rounded-md transition-colors shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {logSuccessMessage && (
        <div className="p-3.5 bg-[#EAF5F0] border border-[#A8D9C5] text-[#198754] text-xs font-semibold rounded-md flex items-center gap-2">
          <Check className="w-4 h-4" />
          <span>{logSuccessMessage}</span>
        </div>
      )}

      {/* ── Top Two Cards Side-by-Side (from PDF Page 6) ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Left Card: Resolution Progress */}
        <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded-md p-6 shadow-sm space-y-4">
          <h2 className="text-base font-serif font-bold text-[#10283A]">
            Resolution Progress
          </h2>

          <div className="space-y-3.5 text-xs">
            {/* Resolved 72% (green) */}
            <div>
              <div className="flex justify-between font-semibold text-[#17212B] mb-1.5">
                <span>Resolved</span>
                <span className="font-mono font-bold text-[#198754]">72%</span>
              </div>
              <div className="w-full bg-[#F4F5F7] h-2.5 rounded-full overflow-hidden">
                <div className="bg-[#198754] h-full rounded-full" style={{ width: '72%' }} />
              </div>
            </div>

            {/* In Progress 18% (amber) */}
            <div>
              <div className="flex justify-between font-semibold text-[#17212B] mb-1.5">
                <span>In Progress</span>
                <span className="font-mono font-bold text-[#D98A16]">18%</span>
              </div>
              <div className="w-full bg-[#F4F5F7] h-2.5 rounded-full overflow-hidden">
                <div className="bg-[#D98A16] h-full rounded-full" style={{ width: '18%' }} />
              </div>
            </div>

            {/* Escalated 10% (red) */}
            <div>
              <div className="flex justify-between font-semibold text-[#17212B] mb-1.5">
                <span>Escalated</span>
                <span className="font-mono font-bold text-[#C83B32]">10%</span>
              </div>
              <div className="w-full bg-[#F4F5F7] h-2.5 rounded-full overflow-hidden">
                <div className="bg-[#C83B32] h-full rounded-full" style={{ width: '10%' }} />
              </div>
            </div>

            {/* Overall SLA Compliance 88% (navy) */}
            <div className="pt-2 border-t border-[#D9DEE3]">
              <div className="flex justify-between font-semibold text-[#17212B] mb-1.5">
                <span>Overall SLA Compliance</span>
                <span className="font-mono font-bold text-[#10283A]">88%</span>
              </div>
              <div className="w-full bg-[#F4F5F7] h-2.5 rounded-full overflow-hidden">
                <div className="bg-[#10283A] h-full rounded-full" style={{ width: '88%' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Right Card: Complaints by Category */}
        <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded-md p-6 shadow-sm space-y-4">
          <h2 className="text-base font-serif font-bold text-[#10283A]">
            Complaints by Category
          </h2>

          <div className="space-y-3.5 text-xs">
            {/* Bid Document Disputes 45% */}
            <div>
              <div className="flex justify-between font-semibold text-[#17212B] mb-1.5">
                <span>Bid Document Disputes</span>
                <span className="font-mono font-bold text-[#10283A]">45%</span>
              </div>
              <div className="w-full bg-[#F4F5F7] h-2.5 rounded-full overflow-hidden">
                <div className="bg-[#10283A] h-full rounded-full" style={{ width: '45%' }} />
              </div>
            </div>

            {/* Payment Delays 30% */}
            <div>
              <div className="flex justify-between font-semibold text-[#17212B] mb-1.5">
                <span>Payment Delays</span>
                <span className="font-mono font-bold text-[#10283A]">30%</span>
              </div>
              <div className="w-full bg-[#F4F5F7] h-2.5 rounded-full overflow-hidden">
                <div className="bg-[#10283A] h-full rounded-full" style={{ width: '30%' }} />
              </div>
            </div>

            {/* Verification Errors 15% */}
            <div>
              <div className="flex justify-between font-semibold text-[#17212B] mb-1.5">
                <span>Verification Errors</span>
                <span className="font-mono font-bold text-[#10283A]">15%</span>
              </div>
              <div className="w-full bg-[#F4F5F7] h-2.5 rounded-full overflow-hidden">
                <div className="bg-[#10283A] h-full rounded-full" style={{ width: '15%' }} />
              </div>
            </div>

            {/* Other 10% */}
            <div>
              <div className="flex justify-between font-semibold text-[#17212B] mb-1.5">
                <span>Other</span>
                <span className="font-mono font-bold text-[#10283A]">10%</span>
              </div>
              <div className="w-full bg-[#F4F5F7] h-2.5 rounded-full overflow-hidden">
                <div className="bg-[#10283A] h-full rounded-full" style={{ width: '10%' }} />
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* ── Search & Filter Ribbon ── */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 bg-white p-3 rounded-md border border-[#D9DEE3] shadow-sm">
        <div className="relative flex-1 max-w-md">
          <Search className="w-3.5 h-3.5 text-[#66717C] absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search complaint ID, bidder, issue, category..."
            className="w-full pl-8 pr-3 py-1.5 bg-[#FFFFFF] border border-[#D9DEE3] text-xs text-[#17212B] placeholder-[#8C9BA5] rounded focus:outline-none focus:border-[#10283A] transition-colors"
          />
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[11px] font-semibold text-[#66717C] uppercase tracking-wide">
            Category:
          </span>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-1.5 bg-[#FFFFFF] border border-[#D9DEE3] text-xs text-[#17212B] rounded focus:outline-none focus:border-[#10283A]"
          >
            <option value="ALL">All Categories</option>
            <option value="Bid Document Disputes">Bid Document Disputes</option>
            <option value="Payment Delays">Payment Delays</option>
            <option value="Verification Errors">Verification Errors</option>
            <option value="Other">Other</option>
          </select>
        </div>
      </div>

      {/* ── Recent Complaints Card (from PDF Page 6) ── */}
      <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded-md shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-[#D9DEE3] flex items-center justify-between">
          <h2 className="text-base font-serif font-bold text-[#10283A]">
            Recent Complaints
          </h2>
          <span className="text-xs text-[#66717C]">
            Showing {filteredComplaints.length} records
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse font-sans">
            <thead>
              <tr className="border-b border-[#D9DEE3] bg-[#F9FAFB]/60 text-[11px] font-semibold text-[#66717C] uppercase tracking-wider font-mono">
                <th className="py-3 px-6">Complaint ID</th>
                <th className="py-3 px-6">Bidder</th>
                <th className="py-3 px-6">Category</th>
                <th className="py-3 px-6">Status</th>
                <th className="py-3 px-6">Filed</th>
                <th className="py-3 px-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#D9DEE3]/70 font-sans">
              {filteredComplaints.map((c) => (
                <tr
                  key={c.id}
                  onClick={() => handleOpenReview(c)}
                  className="hover:bg-[#F9FAFB] cursor-pointer transition-colors"
                >
                  <td className="py-3.5 px-6 font-mono font-bold text-[#10283A]">
                    {c.id}
                  </td>
                  <td className="py-3.5 px-6 font-semibold text-[#17212B]">
                    <div>{c.bidder}</div>
                    <div className="text-[10px] text-[#66717C] font-normal truncate max-w-sm mt-0.5">
                      {c.issue}
                    </div>
                  </td>
                  <td className="py-3.5 px-6 text-[#17212B]">
                    {c.category}
                  </td>
                  <td className="py-3.5 px-6">
                    {getStatusPill(c.status)}
                  </td>
                  <td className="py-3.5 px-6 font-mono text-[#66717C]">
                    {c.filed}
                  </td>
                  <td className="py-3.5 px-6 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleOpenReview(c);
                      }}
                      className="px-3 py-1 bg-[#10283A] hover:bg-[#18374D] text-white text-[11px] font-semibold rounded transition-colors shadow-sm"
                    >
                      Review
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Officer Review Modal (GFR 2017 Decision Workspace) ── */}
      {selectedCheckForReview && (
        <OfficerReviewModal
          check={selectedCheckForReview}
          bidderName={selectedBidderName}
          onClose={() => setSelectedCheckForReview(null)}
          onSuccess={() => {
            setSelectedCheckForReview(null);
            loadData();
          }}
        />
      )}

      {/* ── Log Complaint Modal ── */}
      {showLogModal && (
        <div className="fixed inset-0 bg-[#10283A]/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white border border-[#D9DEE3] rounded-md shadow-lg max-w-lg w-full p-6 space-y-4 font-sans">
            <h3 className="text-base font-serif font-bold text-[#10283A]">
              Log New Procurement Complaint
            </h3>
            <p className="text-xs text-[#66717C]">
              File an official bidder complaint or technical specification grievance for review.
            </p>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                setShowLogModal(false);
                setLogSuccessMessage('Complaint registered successfully and assigned to Officer Alex Rivera.');
                setTimeout(() => setLogSuccessMessage(''), 4000);
              }}
              className="space-y-3 text-xs"
            >
              <div>
                <label className="font-semibold text-[#17212B] block mb-1">Bidder / Contractor Entity</label>
                <input
                  type="text"
                  defaultValue="Nova Petrochem Co."
                  required
                  className="w-full px-3 py-2 bg-white border border-[#D9DEE3] rounded focus:outline-none focus:border-[#10283A]"
                />
              </div>

              <div>
                <label className="font-semibold text-[#17212B] block mb-1">Grievance Category</label>
                <select className="w-full px-3 py-2 bg-white border border-[#D9DEE3] rounded focus:outline-none focus:border-[#10283A]">
                  <option>Bid Document Disputes</option>
                  <option>Payment Delays</option>
                  <option>Verification Errors</option>
                  <option>Other</option>
                </select>
              </div>

              <div>
                <label className="font-semibold text-[#17212B] block mb-1">Detailed Description of Issue</label>
                <textarea
                  rows={3}
                  placeholder="State specific tender clause number, discrepancy details, and impact..."
                  required
                  className="w-full px-3 py-2 bg-white border border-[#D9DEE3] rounded focus:outline-none focus:border-[#10283A]"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowLogModal(false)}
                  className="px-4 py-2 border border-[#D9DEE3] text-[#66717C] hover:text-[#17212B] rounded text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-[#10283A] text-white hover:bg-[#18374D] rounded text-xs font-semibold shadow-sm"
                >
                  Submit Complaint
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};

export default ReviewQueuePage;
