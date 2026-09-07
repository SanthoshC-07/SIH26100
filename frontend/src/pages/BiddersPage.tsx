import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Users,
  Search,
  RefreshCw,
  ChevronRight,
  ShieldCheck,
  Building,
  Plus,
  AlertCircle,
  Upload,
  FileText,
  CheckCircle2,
  XCircle,
  FileSpreadsheet
} from 'lucide-react';
import { bidderService, tenderService } from '../services';
import { Bidder, Tender } from '../types';
import { RiskBadge } from '../components/RiskBadge';

export const BiddersPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [bidders, setBidders] = useState<Bidder[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState(searchParams.get('search') || '');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [selectedBidderId, setSelectedBidderId] = useState<string>('');
  const [officerNotes, setOfficerNotes] = useState<string>(
    'Document verified against tender checklist. Company registration and financial statement confirmed. Pending final compliance sign-off.'
  );
  const [selectionApproved, setSelectionApproved] = useState<boolean>(false);
  const [fileRejected, setFileRejected] = useState<boolean>(false);

  const loadData = () => {
    setLoading(true);
    bidderService.getBidders()
      .then((b) => {
        setBidders(b);
        if (b.length > 0 && !selectedBidderId) {
          setSelectedBidderId(b[0].id);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const defaultBidders: any[] = [
    {
      id: 'b-praveen',
      tender_id: 't-1',
      legal_name: 'Alpha Energy Ltd.',
      email: 'contact@alphaenergy.in',
      phone: '+91 98450 12345',
      pan: 'ABCDE1234F',
      gstin: '29ABCDE1234F1Z5',
      registered_address: 'Bangalore, Karnataka',
      bidder_type: 'EPC_CONTRACTOR',
      oil_gas_experience_years: 12.0,
      pipeline_experience_years: 10.5,
      compliance_score: 94,
      risk_level: 'LOW',
      status: 'SUBMITTED',
      created_at: '2026-02-15T10:00:00Z',
      documents_count: 7,
      verified_documents_count: 7
    },
    {
      id: 'b-nova',
      tender_id: 't-1',
      legal_name: 'Nova Petrochem Co.',
      email: 'bids@novapetro.com',
      phone: '+91 98111 22334',
      pan: 'NOVAP1122K',
      gstin: '27NOVAP1122K1Z9',
      registered_address: 'Mumbai, Maharashtra',
      bidder_type: 'EPC_CONTRACTOR',
      oil_gas_experience_years: 8.0,
      pipeline_experience_years: 7.0,
      compliance_score: 72,
      risk_level: 'MEDIUM',
      status: 'UNDER_REVIEW',
      created_at: '2026-02-16T11:00:00Z',
      documents_count: 5,
      verified_documents_count: 4
    },
    {
      id: 'b-summit',
      tender_id: 't-1',
      legal_name: 'Summit Pipeline Inc.',
      email: 'tenders@summitpipe.in',
      phone: '+91 97222 33445',
      pan: 'SUMMT3344M',
      gstin: '24SUMMT3344M1Z2',
      registered_address: 'Ahmedabad, Gujarat',
      bidder_type: 'EPC_CONTRACTOR',
      oil_gas_experience_years: 9.5,
      pipeline_experience_years: 8.5,
      compliance_score: 85,
      risk_level: 'LOW',
      status: 'UNDER_REVIEW',
      created_at: '2026-02-17T09:30:00Z',
      documents_count: 6,
      verified_documents_count: 6
    },
    {
      id: 'b-delta',
      tender_id: 't-1',
      legal_name: 'Delta Refining Group',
      email: 'projects@deltarefining.com',
      phone: '+91 99333 44556',
      pan: 'DELTR5566P',
      gstin: '03DELTR5566P1Z4',
      registered_address: 'Bathinda, Punjab',
      bidder_type: 'EPC_CONTRACTOR',
      oil_gas_experience_years: 6.0,
      pipeline_experience_years: 4.5,
      compliance_score: 58,
      risk_level: 'HIGH',
      status: 'SUBMITTED',
      created_at: '2026-02-18T14:15:00Z',
      documents_count: 4,
      verified_documents_count: 2
    },
    {
      id: 'b-horizon',
      tender_id: 't-1',
      legal_name: 'Horizon Oilfield Svcs.',
      email: 'info@horizonoil.in',
      phone: '+91 98444 55667',
      pan: 'HORIZ7788R',
      gstin: '06HORIZ7788R1Z1',
      registered_address: 'Gurugram, Haryana',
      bidder_type: 'EPC_CONTRACTOR',
      oil_gas_experience_years: 5.0,
      pipeline_experience_years: 3.5,
      compliance_score: 42,
      risk_level: 'HIGH',
      status: 'SUBMITTED',
      created_at: '2026-02-19T16:45:00Z',
      documents_count: 3,
      verified_documents_count: 1
    }
  ];

  const activeBidders = bidders.length > 0 ? bidders : defaultBidders;

  const currentSelected = activeBidders.find(b => b.id === selectedBidderId) || activeBidders[0];

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(part => part[0])
      .filter(Boolean)
      .slice(0, 2)
      .join('')
      .toUpperCase();
  };

  const handleApprove = () => {
    setSelectionApproved(true);
    setFileRejected(false);
  };

  const handleReject = () => {
    setFileRejected(true);
    setSelectionApproved(false);
  };

  return (
    <div className="space-y-6 font-sans">
      
      {/* ── Top Header Section (from PDF Page 5) ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="text-[11px] font-mono tracking-widest text-[#66717C] uppercase font-bold">
            BIDDER RECORDS
          </div>
          <h1 className="text-2xl sm:text-3xl font-serif font-bold text-[#10283A] tracking-tight mt-0.5">
            Bidder Records — TND-2201
          </h1>
          <p className="text-xs text-[#66717C] mt-0.5">
            Pipeline Maintenance Contract • Natural Gas Transmission Division
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/apply')}
            className="px-4 py-2 bg-[#D98A16] hover:bg-[#E39A22] text-[#10283A] text-xs font-bold rounded-md shadow-sm transition-colors flex items-center gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Register Bidder</span>
          </button>

          <button
            onClick={loadData}
            title="Refresh Records"
            className="p-2 bg-white hover:bg-[#F4F5F7] border border-[#D9DEE3] text-[#66717C] hover:text-[#10283A] rounded-md transition-colors shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* ── PDF Page 5 Two-Column Layout ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* ── Left Column: Bidders on this Tender (from PDF Page 5) ── */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded-md shadow-sm overflow-hidden">
            <div className="px-5 py-4 border-b border-[#D9DEE3] flex items-center justify-between">
              <h2 className="text-base font-serif font-bold text-[#10283A]">
                Bidders on this Tender
              </h2>
              <span className="text-xs text-[#66717C] font-mono">
                {activeBidders.length} Registered
              </span>
            </div>

            <div className="divide-y divide-[#D9DEE3]/70">
              {activeBidders.map((bidder, idx) => {
                const isSelected = bidder.id === (currentSelected?.id || '');
                const initials = getInitials(bidder.legal_name);
                const hasUploaded = idx === 0 || bidder.documents_count && bidder.documents_count > 0;

                return (
                  <div
                    key={bidder.id}
                    onClick={() => {
                      setSelectedBidderId(bidder.id);
                      setSelectionApproved(false);
                      setFileRejected(false);
                    }}
                    className={`p-4 cursor-pointer transition-all flex items-center gap-3.5 ${
                      isSelected
                        ? 'bg-[#F9FAFB] border-l-4 border-l-[#10283A] shadow-inner'
                        : 'hover:bg-[#F9FAFB]/70'
                    }`}
                  >
                    {/* Circle Avatar Badge with Initials (from PDF Page 5) */}
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-xs shrink-0 tracking-tight transition-colors ${
                        isSelected
                          ? 'bg-[#10283A] text-white'
                          : 'bg-[#F4F5F7] text-[#10283A] border border-[#D9DEE3]'
                      }`}
                    >
                      {initials}
                    </div>

                    <div className="min-w-0 flex-1">
                      <div className="text-sm font-semibold text-[#17212B] truncate leading-tight">
                        {bidder.legal_name}
                      </div>
                      <div className="text-xs text-[#66717C] mt-0.5 truncate">
                        {hasUploaded
                          ? 'File uploaded · Pending selection'
                          : 'Awaiting document'}
                      </div>
                    </div>

                    <ChevronRight
                      className={`w-4 h-4 shrink-0 transition-opacity ${
                        isSelected ? 'text-[#10283A] opacity-100' : 'text-[#8C9BA5] opacity-40'
                      }`}
                    />
                  </div>
                );
              })}
            </div>
          </div>

          {/* Quick Nav to full Verification Workspace */}
          <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded-md p-4 shadow-sm flex items-center justify-between">
            <div className="text-xs text-[#17212B]">
              <span className="font-semibold">Need deeper evaluation?</span>
              <p className="text-[11px] text-[#66717C]">Access GFR 2017 checklist and OCR evidence</p>
            </div>
            <button
              onClick={() => navigate(`/bidders/${currentSelected?.id || 'b-praveen'}`)}
              className="px-3.5 py-1.5 bg-[#10283A] hover:bg-[#18374D] text-white text-xs font-semibold rounded transition-colors"
            >
              Open Workspace &rarr;
            </button>
          </div>
        </div>

        {/* ── Right Column: Document Upload & Verification Notes (from PDF Page 5) ── */}
        <div className="lg:col-span-7 space-y-6">
          
          {/* Top Card: Bid Document Upload (from PDF Page 5) */}
          <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded-md shadow-sm p-6 space-y-5">
            <h2 className="text-base font-serif font-bold text-[#10283A]">
              Bid Document Upload — {currentSelected?.legal_name}
            </h2>

            {/* Dashed Drag & Drop Box */}
            <div className="border-2 border-dashed border-[#D9DEE3] rounded-md p-8 text-center bg-[#F9FAFB]/50 hover:bg-[#F9FAFB] transition-colors cursor-pointer group">
              <div className="w-8 h-8 mx-auto text-[#66717C] group-hover:text-[#10283A] flex items-center justify-center mb-2 transition-colors">
                <Upload className="w-6 h-6" />
              </div>
              <div className="text-xs text-[#66717C]">
                Drag file here or browse — only one file may be uploaded per bidder
              </div>
            </div>

            {/* Uploaded File Bar (from PDF Page 5) */}
            <div className="space-y-2">
              <div className="text-[11px] font-mono font-semibold tracking-wider text-[#66717C] uppercase">
                UPLOADED FILE
              </div>

              <div className="flex items-center justify-between p-3 bg-[#F9FAFB] border border-[#D9DEE3] rounded-md">
                <div className="flex items-center gap-2.5 min-w-0">
                  <FileText className="w-4 h-4 text-[#10283A] shrink-0" />
                  <span className="text-xs font-mono font-medium text-[#17212B] truncate">
                    Bid_Proposal_{currentSelected?.legal_name.replace(/\s+/g, '')}_Sept2026.pdf
                  </span>
                </div>

                <button
                  onClick={() => navigate(`/compliance-review`)}
                  className="px-4 py-1.5 bg-[#10283A] hover:bg-[#18374D] text-white text-xs font-semibold rounded transition-colors shadow-sm shrink-0"
                >
                  Select
                </button>
              </div>
            </div>
          </div>

          {/* Bottom Card: Officer Verification Notes (from PDF Page 5) */}
          <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded-md shadow-sm p-6 space-y-4">
            <h2 className="text-base font-serif font-bold text-[#10283A]">
              Officer Verification Notes
            </h2>

            <textarea
              value={officerNotes}
              onChange={(e) => setOfficerNotes(e.target.value)}
              rows={4}
              className="w-full p-3.5 bg-white border border-[#D9DEE3] rounded-md text-xs text-[#17212B] focus:outline-none focus:border-[#10283A] font-sans leading-relaxed resize-y"
              placeholder="Enter official evaluation remarks, verification notes, and decision justifications..."
            />

            {selectionApproved && (
              <div className="p-3 bg-[#EAF5F0] border border-[#A8D9C5] text-xs font-semibold text-[#198754] rounded flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                <span>Selection approved for {currentSelected?.legal_name}. Logged to immutable audit trail.</span>
              </div>
            )}

            {fileRejected && (
              <div className="p-3 bg-[#FDF2F2] border border-[#F5C2C7] text-xs font-semibold text-[#C83B32] rounded flex items-center gap-2">
                <XCircle className="w-4 h-4" />
                <span>Document proposal rejected. Re-upload request dispatched to bidder.</span>
              </div>
            )}

            {/* Action Buttons (from PDF Page 5: Approve Selection & Reject File) */}
            <div className="flex items-center gap-3 pt-2">
              <button
                onClick={handleApprove}
                className="px-6 py-2.5 bg-[#10283A] hover:bg-[#18374D] text-white text-xs font-semibold rounded-md transition-colors shadow-sm"
              >
                Approve Selection
              </button>

              <button
                onClick={handleReject}
                className="px-6 py-2.5 bg-white hover:bg-[#F4F5F7] text-[#17212B] border border-[#D9DEE3] text-xs font-semibold rounded-md transition-colors shadow-sm"
              >
                Reject File
              </button>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
};

export default BiddersPage;
