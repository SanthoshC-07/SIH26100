import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  Upload,
  CheckCircle2,
  Clock,
  Building,
  ShieldCheck,
  FileSpreadsheet,
  ArrowRight,
  AlertCircle,
  FileCheck,
  Briefcase
} from 'lucide-react';
import { bidderService, tenderService, authService } from '../services';
import { Tender, Bidder } from '../types';

export const BidderDashboardPage: React.FC = () => {
  const [activeTenders, setActiveTenders] = useState<Tender[]>([]);
  const [myBids, setMyBids] = useState<any[]>([]);
  const [myBidderProfile, setMyBidderProfile] = useState<Bidder | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const currentUser = authService.getUserFromStorage();

  useEffect(() => {
    const loadBidderData = async () => {
      setLoading(true);
      setError('');
      try {
        const [tendersRes, bidsRes, biddersRes] = await Promise.all([
          tenderService.getTenders().catch(() => []),
          bidderService.getBids().catch(() => []),
          bidderService.getBidders().catch(() => [])
        ]);

        // Filter active tenders
        const openTenders = (tendersRes || []).filter(
          (t: Tender) => t.status === 'ACTIVE' || t.status === 'OPEN' || t.status === 'PUBLISHED'
        );
        setActiveTenders(openTenders);
        setMyBids(bidsRes || []);

        // Bidder's own profile
        if (biddersRes && biddersRes.length > 0) {
          setMyBidderProfile(biddersRes[0]);
        }
      } catch (err: any) {
        setError('Failed to load contractor portal information.');
      } finally {
        setLoading(false);
      }
    };

    loadBidderData();
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 font-sans">
      {/* Top Welcome Banner */}
      <div className="bg-[#10283A] text-white rounded-2xl p-6 shadow-md relative overflow-hidden">
        <div
          className="absolute right-0 top-0 bottom-0 w-1/3 bg-cover bg-right opacity-15 pointer-events-none"
          style={{ backgroundImage: 'url(/images/refinery_nav.jpg)' }}
        />
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 bg-white/10 rounded-full text-[11px] text-[#D98A16] font-semibold mb-3">
            <Building className="w-3.5 h-3.5" />
            <span>Ministry of Petroleum &amp; Natural Gas — Registered Bidder Portal</span>
          </div>
          <h1 className="text-2xl font-serif font-bold text-white tracking-tight">
            Welcome, {myBidderProfile?.legal_name || currentUser?.name || 'Contractor'}
          </h1>
          <p className="text-xs text-[#B0C0D0] mt-1 leading-relaxed">
            Manage your pipeline procurement bids, track technical qualification compliance, and upload verified statutory evidence.
          </p>

          <div className="mt-4 flex flex-wrap gap-4 text-xs text-[#E2E8F0] font-mono">
            {myBidderProfile?.pan && (
              <span className="bg-white/10 px-2.5 py-1 rounded">
                PAN: <span className="text-white font-bold">{myBidderProfile.pan}</span>
              </span>
            )}
            {myBidderProfile?.gstin && (
              <span className="bg-white/10 px-2.5 py-1 rounded">
                GSTIN: <span className="text-white font-bold">{myBidderProfile.gstin}</span>
              </span>
            )}
            <span className="bg-[#198754]/30 border border-[#198754]/40 px-2.5 py-1 rounded text-[#4ADE80] font-semibold font-sans">
              Status: {myBidderProfile?.status || 'REGISTERED'}
            </span>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-[#FEF2F2] border border-[#FCA5A5] text-[#991B1B] text-xs rounded-lg flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-white border border-[#D9DEE3] rounded-xl p-4 shadow-sm">
          <div className="text-xs text-[#66717C] font-semibold uppercase flex items-center justify-between">
            <span>Active Tenders</span>
            <FileSpreadsheet className="w-4 h-4 text-[#10283A]" />
          </div>
          <div className="text-2xl font-bold text-[#10283A] mt-1">{activeTenders.length}</div>
          <div className="text-[11px] text-[#198754] font-medium mt-0.5">Open for bidding</div>
        </div>

        <div className="bg-white border border-[#D9DEE3] rounded-xl p-4 shadow-sm">
          <div className="text-xs text-[#66717C] font-semibold uppercase flex items-center justify-between">
            <span>My Submitted Bids</span>
            <Briefcase className="w-4 h-4 text-[#D98A16]" />
          </div>
          <div className="text-2xl font-bold text-[#D98A16] mt-1">{myBids.length}</div>
          <div className="text-[11px] text-[#66717C] mt-0.5">Under evaluation</div>
        </div>

        <div className="bg-white border border-[#D9DEE3] rounded-xl p-4 shadow-sm">
          <div className="text-xs text-[#66717C] font-semibold uppercase flex items-center justify-between">
            <span>Compliance Status</span>
            <ShieldCheck className="w-4 h-4 text-[#198754]" />
          </div>
          <div className="text-2xl font-bold text-[#198754] mt-1">
            {myBidderProfile?.status === 'VERIFIED' ? 'Verified' : 'Under Review'}
          </div>
          <div className="text-[11px] text-[#66717C] mt-0.5">GFR 2017 &amp; CVC Rules</div>
        </div>

        <div className="bg-white border border-[#D9DEE3] rounded-xl p-4 shadow-sm flex flex-col justify-between">
          <div>
            <div className="text-xs text-[#66717C] font-semibold uppercase">Quick Action</div>
            <div className="text-xs font-semibold text-[#10283A] mt-1">Submit Application</div>
          </div>
          <Link
            to="/tenders"
            className="inline-flex items-center justify-center gap-1.5 w-full py-1.5 mt-2 bg-[#10283A] hover:bg-[#18374D] text-white text-xs font-semibold rounded transition-colors"
          >
            <span>Browse Tenders</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Active Tenders Open for Bidding */}
        <div className="lg:col-span-2 bg-white border border-[#D9DEE3] rounded-xl shadow-sm p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-[#E2E8F0] pb-3">
            <div>
              <h2 className="font-serif font-bold text-base text-[#10283A]">
                Available Petroleum &amp; Pipeline Tenders
              </h2>
              <p className="text-xs text-[#66717C]">
                Review tender requirements and submit your technical bid dossier
              </p>
            </div>
            <Link
              to="/tenders"
              className="text-xs text-[#D98A16] font-semibold hover:underline flex items-center gap-1"
            >
              View all ({activeTenders.length}) <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="divide-y divide-[#E2E8F0]">
            {loading ? (
              <div className="py-8 text-center text-xs text-[#66717C]">Loading active tenders...</div>
            ) : activeTenders.length === 0 ? (
              <div className="py-8 text-center text-xs text-[#66717C]">
                No active tenders currently available for application.
              </div>
            ) : (
              activeTenders.slice(0, 4).map((t) => (
                <div key={t.id} className="py-3.5 flex items-center justify-between gap-4">
                  <div className="min-w-0">
                    <div className="font-semibold text-xs text-[#10283A] truncate">
                      {t.title}
                    </div>
                    <div className="text-[11px] text-[#66717C] flex items-center gap-3 mt-1">
                      <span className="font-mono text-[#10283A]">{t.tender_number}</span>
                      <span>·</span>
                      <span>{t.organization}</span>
                      <span>·</span>
                      <span className="text-[#198754] font-medium">OPEN</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <Link
                      to={`/tenders/${t.id}`}
                      className="px-3 py-1.5 border border-[#D9DEE3] text-[#4B5563] text-xs font-semibold rounded hover:bg-[#F3F4F6] transition-colors"
                    >
                      View Specs
                    </Link>
                    <Link
                      to={`/tenders/${t.id}/apply`}
                      className="px-3 py-1.5 bg-[#10283A] text-white text-xs font-semibold rounded hover:bg-[#18374D] transition-colors flex items-center gap-1.5"
                    >
                      <Upload className="w-3.5 h-3.5" />
                      Apply
                    </Link>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right 1 Col: My Submissions & Quick Navigation */}
        <div className="bg-white border border-[#D9DEE3] rounded-xl shadow-sm p-5 space-y-4">
          <div className="border-b border-[#E2E8F0] pb-3">
            <h2 className="font-serif font-bold text-base text-[#10283A]">
              My Submissions
            </h2>
            <p className="text-xs text-[#66717C]">Your submitted bids &amp; application dossiers</p>
          </div>

          <div className="space-y-3">
            {myBids.length === 0 ? (
              <div className="py-6 text-center text-xs text-[#66717C]">
                No bids submitted yet. Select a tender above to begin your application.
              </div>
            ) : (
              myBids.map((b) => (
                <div key={b.id} className="p-3 bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-[#10283A]">
                      Bid ID: {b.id?.slice(0, 8)}...
                    </span>
                    <span className="px-2 py-0.5 bg-[#ECFDF5] text-[#065F46] rounded text-[10px] font-bold">
                      {b.status || 'SUBMITTED'}
                    </span>
                  </div>
                  <div className="text-[11px] text-[#66717C] mt-1.5">
                    Tender Reference: <span className="font-mono text-[#10283A]">{b.tender_id?.slice(0, 8)}...</span>
                  </div>
                  <div className="text-[10px] text-[#8C9BA5] mt-1">
                    Submitted: {new Date(b.created_at || Date.now()).toLocaleDateString()}
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="pt-3 border-t border-[#E2E8F0] space-y-2">
            <div className="text-[11px] font-semibold text-[#66717C] uppercase">Contractor Quick Links</div>
            <Link
              to="/bidders"
              className="flex items-center justify-between p-2 rounded-md hover:bg-[#F3F4F6] text-xs text-[#10283A] transition-colors"
            >
              <span>My Profile &amp; Entity Information</span>
              <ArrowRight className="w-3.5 h-3.5 text-[#8C9BA5]" />
            </Link>
            <Link
              to="/evidence-center"
              className="flex items-center justify-between p-2 rounded-md hover:bg-[#F3F4F6] text-xs text-[#10283A] transition-colors"
            >
              <span>Upload Verification Documents</span>
              <ArrowRight className="w-3.5 h-3.5 text-[#8C9BA5]" />
            </Link>
            <Link
              to="/reports"
              className="flex items-center justify-between p-2 rounded-md hover:bg-[#F3F4F6] text-xs text-[#10283A] transition-colors"
            >
              <span>My Compliance Reports</span>
              <ArrowRight className="w-3.5 h-3.5 text-[#8C9BA5]" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
