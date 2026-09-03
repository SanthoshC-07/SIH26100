import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { tenderService, documentService } from '../services';

export const CreateTenderPage: React.FC = () => {
  const navigate = useNavigate();
  const [tenderNumber, setTenderNumber] = useState('GeM/2026/B/' + Math.floor(100000 + Math.random() * 900000));
  const [title, setTitle] = useState('');
  const [organization, setOrganization] = useState('Ministry of Electronics & Information Technology');
  const [category, setCategory] = useState('IT Hardware & Infrastructure');
  const [estimatedValue, setEstimatedValue] = useState('150000000');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

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
        estimated_value: parseFloat(estimatedValue) || 10000000,
        status: 'ACTIVE'
      });

      if (file) {
        await documentService.uploadTenderDocument(created.id, file);
      }

      navigate(`/tenders/${created.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to publish tender.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 font-mono text-xs">
      
      {/* Back Link */}
      <button
        onClick={() => navigate('/tenders')}
        className="font-bold text-[#59625D] hover:text-[#17201C] flex items-center gap-1.5 transition-colors"
      >
        &larr; BACK TO TENDERS DIRECTORY
      </button>

      {/* Form Container */}
      <div className="border border-[#D8DCD6] bg-white">
        
        <div className="px-6 py-4 bg-[#101A17] text-white border-b border-[#22322C]">
          <h2 className="text-sm font-bold uppercase tracking-wider">PUBLISH TENDER SPECIFICATION & EXTRACT CLAUSES</h2>
          <p className="text-[11px] text-[#9DAAA2]">
            Deterministic NLP rule extraction automatically structures statutory, financial, and technical criteria.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          
          {error && (
            <div className="p-3 bg-[#FBEBEB] text-[#7A1C1C] border border-[#F1B5B5]">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="space-y-1.5">
              <label className="block text-[10px] font-bold uppercase tracking-wider text-[#59625D]">
                GeM TENDER REFERENCE NUMBER <span className="text-[#7A1C1C]">*</span>
              </label>
              <input
                type="text"
                required
                value={tenderNumber}
                onChange={(e) => setTenderNumber(e.target.value)}
                className="w-full border border-[#D8DCD6] p-2.5 bg-white text-[#17201C] outline-none focus:border-[#163C32]"
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-[10px] font-bold uppercase tracking-wider text-[#59625D]">
                PROCURING MINISTRY / ORG <span className="text-[#7A1C1C]">*</span>
              </label>
              <input
                type="text"
                required
                value={organization}
                onChange={(e) => setOrganization(e.target.value)}
                className="w-full border border-[#D8DCD6] p-2.5 bg-white text-[#17201C] outline-none focus:border-[#163C32]"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="block text-[10px] font-bold uppercase tracking-wider text-[#59625D]">
              TENDER SCOPE & SPECIFICATION TITLE <span className="text-[#7A1C1C]">*</span>
            </label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Supply and Implementation of High-Density Data Center Cloud Infrastructure"
              className="w-full border border-[#D8DCD6] p-2.5 bg-white text-[#17201C] outline-none focus:border-[#163C32] font-sans text-xs"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="space-y-1.5">
              <label className="block text-[10px] font-bold uppercase tracking-wider text-[#59625D]">
                ESTIMATED VALUE (INR)
              </label>
              <input
                type="number"
                value={estimatedValue}
                onChange={(e) => setEstimatedValue(e.target.value)}
                className="w-full border border-[#D8DCD6] p-2.5 bg-white text-[#17201C] outline-none focus:border-[#163C32]"
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-[10px] font-bold uppercase tracking-wider text-[#59625D]">
                CATEGORY
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full border border-[#D8DCD6] p-2.5 bg-white text-[#17201C] outline-none focus:border-[#163C32]"
              >
                <option value="IT Hardware & Infrastructure">IT Hardware & Infrastructure</option>
                <option value="Cloud & Networking Services">Cloud & Networking Services</option>
                <option value="Industrial Equipment">Industrial Equipment</option>
                <option value="Consulting & Technical Services">Consulting & Technical Services</option>
              </select>
            </div>
          </div>

          {/* Tender PDF Upload Box */}
          <div className="p-6 border border-dashed border-[#D8DCD6] bg-[#FCFCFA] text-center space-y-1.5">
            <input
              type="file"
              id="tender-pdf"
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  setFile(e.target.files[0]);
                }
              }}
              className="hidden"
            />
            <label htmlFor="tender-pdf" className="cursor-pointer block">
              <div className="text-xs font-bold text-[#17201C]">
                {file ? file.name : "ATTACH TENDER SPECIFICATION DOCUMENT (PDF)"}
              </div>
              <p className="text-[10px] text-[#59625D] mt-1">
                PyMuPDF parser automatically identifies financial turnover, statutory compliance, and OEM requirements.
              </p>
            </label>
          </div>

          <div className="pt-3 border-t border-[#D8DCD6] flex items-center justify-between">
            <button
              type="button"
              onClick={() => navigate('/tenders')}
              className="px-4 py-2 border border-[#D8DCD6] font-semibold text-[#59625D]"
            >
              CANCEL
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 bg-[#163C32] hover:bg-[#0E2922] text-white font-bold text-xs uppercase disabled:opacity-50"
            >
              {loading ? "EXTRACTING CLAUSES..." : "PUBLISH TENDER & EXTRACT MATRIX"}
            </button>
          </div>

        </form>

      </div>

    </div>
  );
};
