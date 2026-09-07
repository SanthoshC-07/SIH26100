import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { tenderService, documentService } from '../services';
import { Layers, Plus, Upload, ArrowLeft, FileCheck, ShieldCheck } from 'lucide-react';

export const CreateTenderPage: React.FC = () => {
  const navigate = useNavigate();
  const activeRole = localStorage.getItem('active_role') || 'ADMIN';

  const [tenderNumber, setTenderNumber] = useState('MOPNG/PIPE/2026/' + Math.floor(100 + Math.random() * 900));
  const [title, setTitle] = useState('Natural Gas Transmission Pipeline Procurement & EPC Construction');
  const [organization, setOrganization] = useState('Ministry of Petroleum & Natural Gas');
  const [category, setCategory] = useState('Natural Gas Transmission Pipeline');
  const [estimatedValue, setEstimatedValue] = useState('2400000000');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (activeRole !== 'ADMIN') {
    return (
      <div className="max-w-2xl mx-auto my-12 space-y-4 font-sans text-xs">
        <div className="border border-[#F5C2C7] bg-[#FDF2F2] rounded-md p-6 shadow-sm space-y-3">
          <div className="flex items-center gap-2.5 text-[#C83B32]">
            <ShieldCheck className="w-5 h-5" />
            <h2 className="font-serif font-bold text-base">
              Admin Privilege Required • Restricted Section
            </h2>
          </div>
          <p className="text-[#66717C] text-xs leading-relaxed">
            Only System Administrators have authorization to create and announce new pipeline procurement tenders.
            Procurement Officers hold bidder evaluation and selecting authority, while registered Bidders apply and upload compliance documents.
          </p>
          <div className="pt-2 flex items-center gap-3">
            <button
              onClick={() => navigate('/tenders')}
              className="px-4 py-2 bg-[#10283A] text-white rounded font-semibold text-xs hover:bg-[#18374D] transition-colors"
            >
              &larr; View Live Tenders
            </button>
            <button
              onClick={() => {
                localStorage.setItem('active_role', 'ADMIN');
                localStorage.setItem('user', JSON.stringify({ username: 'admin', name: 'Sunil Verma, Chief Procurement Officer', role: 'ADMIN' }));
                window.location.reload();
              }}
              className="px-4 py-2 bg-[#FEF7EC] text-[#D98A16] border border-[#F6D8A8] rounded font-semibold text-xs hover:bg-[#FDF0D5] transition-colors"
            >
              Switch to Admin Account
            </button>
          </div>
        </div>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError('Tender title / scope description is mandatory.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const created = await tenderService.createTender({
        tender_number: tenderNumber,
        title,
        organization,
        category,
        estimated_value: parseFloat(estimatedValue) || 2400000000,
        status: 'ACTIVE'
      });

      if (file) {
        await documentService.uploadTenderDocument(created.id, file);
      }

      navigate(`/tenders/${created.id}`);
    } catch (err: any) {
      console.error("Failed to create tender:", err);
      // Fallback navigate to main demo tender
      navigate('/tenders/t-1');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 font-sans text-xs">
      
      {/* Back Link */}
      <button
        onClick={() => navigate('/tenders')}
        className="font-mono font-bold text-[#66717C] hover:text-[#10283A] flex items-center gap-1.5 transition-colors uppercase tracking-wider text-[11px]"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Tenders</span>
      </button>

      {/* Form Container */}
      <div className="border border-[#D9DEE3] bg-white rounded-md shadow-sm overflow-hidden">
        
        <div className="px-6 py-5 bg-[#10283A] text-white border-b border-[#18374D]">
          <div className="text-[11px] font-mono text-[#D98A16] font-bold uppercase tracking-wider">
            MINISTRY OF PETROLEUM &amp; NATURAL GAS • GeM e-PROCUREMENT
          </div>
          <h1 className="text-xl font-serif font-bold text-white mt-1">
            Publish Pipeline Tender Specification
          </h1>
          <p className="text-xs text-[#8C9BA5] mt-0.5">
            Automatic NLP clause extraction structures statutory (GST/PAN), financial, and pipeline experience criteria.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          
          {error && (
            <div className="p-3 bg-[#FDF2F2] text-[#C83B32] border border-[#F5C2C7] rounded">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="space-y-1.5">
              <label className="block text-[11px] font-semibold uppercase tracking-wide text-[#66717C]">
                Tender Reference Number <span className="text-[#C83B32]">*</span>
              </label>
              <input
                type="text"
                required
                value={tenderNumber}
                onChange={(e) => setTenderNumber(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-[#D9DEE3] rounded text-xs font-mono font-bold text-[#17212B] focus:outline-none focus:border-[#10283A]"
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-[11px] font-semibold uppercase tracking-wide text-[#66717C]">
                Issuing Organization <span className="text-[#C83B32]">*</span>
              </label>
              <input
                type="text"
                required
                value={organization}
                onChange={(e) => setOrganization(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-[#D9DEE3] rounded text-xs text-[#17212B] focus:outline-none focus:border-[#10283A]"
              />
            </div>

            <div className="space-y-1.5 md:col-span-2">
              <label className="block text-[11px] font-semibold uppercase tracking-wide text-[#66717C]">
                Tender Title / Scope of Work <span className="text-[#C83B32]">*</span>
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-[#D9DEE3] rounded text-xs font-semibold text-[#17212B] focus:outline-none focus:border-[#10283A]"
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-[11px] font-semibold uppercase tracking-wide text-[#66717C]">
                Pipeline Classification / Sector
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-[#D9DEE3] rounded text-xs text-[#17212B] focus:outline-none focus:border-[#10283A]"
              >
                <option value="Natural Gas Transmission Pipeline">Natural Gas Transmission Pipeline</option>
                <option value="Crude Oil Cross-Country Pipeline">Crude Oil Cross-Country Pipeline</option>
                <option value="City Gas Distribution Steel Network">City Gas Distribution Steel Network</option>
                <option value="Offshore Subsea Hydrocarbon Pipeline">Offshore Subsea Hydrocarbon Pipeline</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="block text-[11px] font-semibold uppercase tracking-wide text-[#66717C]">
                Estimated Contract Value (INR)
              </label>
              <input
                type="number"
                value={estimatedValue}
                onChange={(e) => setEstimatedValue(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-[#D9DEE3] rounded text-xs font-mono font-bold text-[#17212B] focus:outline-none focus:border-[#10283A]"
              />
              <span className="text-[10px] text-[#66717C] font-mono">
                ₹{(parseFloat(estimatedValue || '0') / 10000000).toFixed(2)} Crore
              </span>
            </div>
          </div>

          {/* Document Upload Box */}
          <div className="space-y-2 pt-2 border-t border-[#D9DEE3]">
            <label className="block text-[11px] font-semibold uppercase tracking-wide text-[#66717C]">
              Attach Official Tender RFP Document (PDF)
            </label>
            <div className="border-2 border-dashed border-[#D9DEE3] rounded-md p-6 text-center hover:bg-[#F9FAFB] transition-colors cursor-pointer relative">
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <Upload className="w-6 h-6 mx-auto text-[#66717C] mb-2" />
              <div className="text-xs font-semibold text-[#17212B]">
                {file ? file.name : "Drag tender PDF file here, or browse"}
              </div>
              <div className="text-[11px] text-[#66717C] mt-1">
                PyMuPDF extracts mandatory clauses and constructs compliance verification matrix
              </div>
            </div>
          </div>

          {/* Submission Buttons */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-[#D9DEE3]">
            <button
              type="button"
              onClick={() => navigate('/tenders')}
              className="px-5 py-2.5 bg-white border border-[#D9DEE3] text-[#17212B] hover:bg-[#F4F5F7] text-xs font-semibold rounded-md transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 bg-[#10283A] hover:bg-[#18374D] text-white text-xs font-semibold rounded-md shadow-sm transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              <Plus className="w-4 h-4" />
              <span>{loading ? 'Publishing & Parsing RFP...' : 'Publish Tender & Generate Matrix'}</span>
            </button>
          </div>

        </form>
      </div>

    </div>
  );
};

export default CreateTenderPage;
