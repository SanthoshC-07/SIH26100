import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { tenderService, documentService } from '../services';
import { Tender } from '../types';

export const TendersPage: React.FC = () => {
  const navigate = useNavigate();
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [toastMessage, setToastMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Edit Modal State
  const [editingTender, setEditingTender] = useState<Tender | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editOrg, setEditOrg] = useState('');
  const [editStatus, setEditStatus] = useState('');
  const [savingEdit, setSavingEdit] = useState(false);

  // Upload Modal State
  const [uploadTenderId, setUploadTenderId] = useState<string | null>(null);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const fetchTenders = async () => {
    setLoading(true);
    try {
      const data = await tenderService.getTenders({
        status: statusFilter || undefined,
        search: searchTerm || undefined
      });
      setTenders(data);
    } catch (err: any) {
      setToastMessage({ type: 'error', text: err.response?.data?.detail || 'Unable to load tenders list.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTenders();
  }, [statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchTenders();
  };

  const openEditModal = (t: Tender, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingTender(t);
    setEditTitle(t.title);
    setEditOrg(t.organization);
    setEditStatus(t.status);
  };

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingTender) return;
    setSavingEdit(true);
    try {
      await tenderService.updateTender(editingTender.id, {
        title: editTitle,
        organization: editOrg,
        status: editStatus as any
      });
      setToastMessage({ type: 'success', text: `Tender ${editingTender.tender_number} updated successfully.` });
      setEditingTender(null);
      fetchTenders();
    } catch (err: any) {
      setToastMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to update tender.' });
    } finally {
      setSavingEdit(false);
    }
  };

  const openUploadModal = (tenderId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setUploadTenderId(tenderId);
    setUploadFile(null);
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadTenderId || !uploadFile) return;
    setUploading(true);
    try {
      await documentService.uploadTenderDocument(uploadTenderId, uploadFile);
      setToastMessage({ type: 'success', text: 'Tender specification document uploaded and processed successfully.' });
      setUploadTenderId(null);
      fetchTenders();
    } catch (err: any) {
      setToastMessage({ type: 'error', text: err.response?.data?.detail || 'Document upload failed. Invalid file type or size.' });
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (tenderId: string, tenderNum: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm(`Are you sure you want to delete Tender ${tenderNum}?`)) return;
    try {
      await tenderService.deleteTender(tenderId);
      setToastMessage({ type: 'success', text: `Tender ${tenderNum} deleted successfully.` });
      fetchTenders();
    } catch (err: any) {
      setToastMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to delete tender.' });
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Toast Notification */}
      {toastMessage && (
        <div className={`p-3 border text-xs font-mono font-bold flex items-center justify-between ${
          toastMessage.type === 'error' ? 'bg-[#FBEBEB] text-[#7A1C1C] border-[#F1B5B5]' : 'bg-[#E8F3EE] text-[#114B3A] border-[#B4DACB]'
        }`}>
          <span>{toastMessage.text}</span>
          <button onClick={() => setToastMessage(null)} className="ml-4 font-normal text-slate-500">✕</button>
        </div>
      )}

      {/* Header Banner */}
      <div className="border border-[#D8DCD6] bg-white p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="text-[10px] font-mono uppercase tracking-widest text-[#A7833B] font-bold">
            TENDER MANAGEMENT & COMPLIANCE RULES
          </div>
          <h1 className="text-base font-mono font-bold tracking-tight text-[#17201C] mt-0.5 uppercase">
            PROCUREMENT TENDERS DIRECTORY
          </h1>
          <p className="text-xs text-[#59625D] mt-0.5">
            Publish GeM custom bids, inspect extracted requirement matrices, and manage bidder submissions
          </p>
        </div>

        <button
          onClick={() => navigate('/tenders/create')}
          className="px-4 py-2 bg-[#163C32] hover:bg-[#0E2922] text-white font-mono font-bold text-xs uppercase tracking-wider transition-colors shrink-0"
        >
          + PUBLISH NEW TENDER
        </button>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="border border-[#D8DCD6] bg-white p-3.5 flex flex-col md:flex-row gap-3 items-center justify-between font-mono text-xs">
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2.5 w-full md:max-w-md">
          <span className="text-[10px] font-bold text-[#59625D] uppercase">SEARCH:</span>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="TENDER REF, TITLE, OR MINISTRY..."
            className="w-full border border-[#D8DCD6] p-1.5 px-2 bg-white text-[#17201C] outline-none focus:border-[#163C32]"
          />
          <button type="submit" className="px-3 py-1.5 bg-[#101A17] text-white font-bold text-[11px] shrink-0">
            FILTER
          </button>
        </form>

        <div className="flex items-center gap-2.5 w-full md:w-auto justify-end">
          <span className="text-[10px] font-bold text-[#59625D] uppercase">STATUS:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="border border-[#D8DCD6] p-1.5 px-2 bg-white text-[#17201C] outline-none text-xs"
          >
            <option value="">ALL STATUSES</option>
            <option value="ACTIVE">ACTIVE</option>
            <option value="UNDER_REVIEW">UNDER REVIEW</option>
            <option value="DRAFT">DRAFT</option>
            <option value="CLOSED">CLOSED</option>
          </select>
        </div>
      </div>

      {/* Tenders Table */}
      <div className="border border-[#D8DCD6] bg-white">
        {loading ? (
          <div className="p-12 text-center text-[#59625D] font-mono text-xs">
            RETRIEVING PROCUREMENT TENDERS...
          </div>
        ) : tenders.length === 0 ? (
          <div className="p-12 text-center text-[#59625D] font-mono text-xs">
            NO TENDERS FOUND IN DIRECTORY
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="border-b border-[#D8DCD6] bg-[#EDEFEA] text-[#59625D] text-[10px] uppercase tracking-wider">
                <tr>
                  <th className="px-5 py-3">TENDER REFERENCE</th>
                  <th className="px-5 py-3">SCOPE & SPECIFICATION</th>
                  <th className="px-5 py-3">PROCURING MINISTRY / ORG</th>
                  <th className="px-5 py-3">DEADLINE</th>
                  <th className="px-5 py-3 text-center">STATUS</th>
                  <th className="px-5 py-3 text-center">BIDDERS</th>
                  <th className="px-5 py-3 text-right">ACTIONS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#D8DCD6] text-[#17201C]">
                {tenders.map((t) => (
                  <tr
                    key={t.id}
                    onClick={() => navigate(`/tenders/${t.id}`)}
                    className="hover:bg-[#F4F5F2] cursor-pointer transition-colors"
                  >
                    <td className="px-5 py-3.5 font-bold text-[#163C32] whitespace-nowrap">
                      {t.tender_number}
                    </td>
                    <td className="px-5 py-3.5 max-w-sm font-sans">
                      <div className="font-bold text-xs text-[#17201C] line-clamp-1">{t.title}</div>
                      <div className="text-[11px] font-mono text-[#59625D] mt-0.5">
                        ESTIMATED: ₹{(t.estimated_value / 10000000).toFixed(2)} CR
                      </div>
                    </td>
                    <td className="px-5 py-3.5 max-w-xs truncate text-[#59625D] font-sans text-xs">
                      {t.organization}
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap text-[11px] text-[#59625D]">
                      {t.submission_deadline ? new Date(t.submission_deadline).toLocaleDateString() : 'ROLLING'}
                    </td>
                    <td className="px-5 py-3.5 text-center whitespace-nowrap">
                      <span className={`inline-block px-2 py-0.5 border text-[10px] font-bold ${
                        t.status === 'ACTIVE' ? 'bg-[#E8F3EE] text-[#114B3A] border-[#B4DACB]' :
                        (t.status === 'UNDER_REVIEW' ? 'bg-[#FDF5E6] text-[#875200] border-[#F6D59B]' : 'bg-[#ECEFEA] text-[#4E5853] border-[#D0D6CF]')
                      }`}>
                        {t.status}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-center font-bold">
                      <span className="px-2 py-0.5 border border-[#D8DCD6] bg-[#EDEFEA] text-[10px]">
                        {t.bidders_count || 0}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center justify-end gap-1.5 text-[10px]">
                        <button
                          onClick={() => navigate(`/tenders/${t.id}`)}
                          className="px-2 py-1 border border-[#D8DCD6] bg-white hover:bg-[#EDEFEA] font-bold text-[#17201C]"
                        >
                          VIEW
                        </button>
                        <button
                          onClick={(e) => openUploadModal(t.id, e)}
                          className="px-2 py-1 border border-[#D8DCD6] bg-white hover:bg-[#EDEFEA] font-bold text-[#163C32]"
                        >
                          UPLOAD
                        </button>
                        <button
                          onClick={(e) => openEditModal(t, e)}
                          className="px-2 py-1 border border-[#D8DCD6] bg-white hover:bg-[#EDEFEA] font-bold text-[#875200]"
                        >
                          EDIT
                        </button>
                        <button
                          onClick={(e) => handleDelete(t.id, t.tender_number, e)}
                          className="px-2 py-1 border border-[#D8DCD6] bg-white hover:bg-[#FBEBEB] font-bold text-[#7A1C1C]"
                        >
                          DEL
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Edit Tender Modal */}
      {editingTender && (
        <div className="fixed inset-0 z-50 bg-[#101A17]/70 backdrop-blur-none flex items-center justify-center p-4 font-mono">
          <div className="bg-white border border-[#22322C] max-w-lg w-full shadow-2xl">
            <div className="px-6 py-4 bg-[#101A17] text-white flex items-center justify-between border-b border-[#22322C]">
              <h3 className="text-xs font-bold uppercase tracking-wider">EDIT TENDER: {editingTender.tender_number}</h3>
              <button onClick={() => setEditingTender(null)} className="text-[#808B84] hover:text-white">✕</button>
            </div>
            <form onSubmit={handleSaveEdit} className="p-6 space-y-4 text-xs">
              <div>
                <label className="block text-[10px] font-bold text-[#59625D] uppercase mb-1">Tender Title</label>
                <input
                  type="text"
                  required
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  className="w-full border border-[#D8DCD6] p-2 bg-white text-[#17201C] outline-none"
                />
              </div>
              <div>
                <label className="block text-[10px] font-bold text-[#59625D] uppercase mb-1">Procuring Organization</label>
                <input
                  type="text"
                  required
                  value={editOrg}
                  onChange={(e) => setEditOrg(e.target.value)}
                  className="w-full border border-[#D8DCD6] p-2 bg-white text-[#17201C] outline-none"
                />
              </div>
              <div>
                <label className="block text-[10px] font-bold text-[#59625D] uppercase mb-1">Status</label>
                <select
                  value={editStatus}
                  onChange={(e) => setEditStatus(e.target.value)}
                  className="w-full border border-[#D8DCD6] p-2 bg-white text-[#17201C] outline-none"
                >
                  <option value="ACTIVE">ACTIVE</option>
                  <option value="UNDER_REVIEW">UNDER REVIEW</option>
                  <option value="DRAFT">DRAFT</option>
                  <option value="CLOSED">CLOSED</option>
                </select>
              </div>
              <div className="pt-3 border-t border-[#D8DCD6] flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setEditingTender(null)}
                  className="px-4 py-2 border border-[#D8DCD6] text-xs font-semibold text-[#59625D]"
                >
                  CANCEL
                </button>
                <button
                  type="submit"
                  disabled={savingEdit}
                  className="px-5 py-2 bg-[#163C32] hover:bg-[#0E2922] text-white font-bold text-xs uppercase"
                >
                  {savingEdit ? "SAVING..." : "SAVE CHANGES"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Upload Document Modal */}
      {uploadTenderId && (
        <div className="fixed inset-0 z-50 bg-[#101A17]/70 backdrop-blur-none flex items-center justify-center p-4 font-mono">
          <div className="bg-white border border-[#22322C] max-w-md w-full shadow-2xl">
            <div className="px-6 py-4 bg-[#101A17] text-white flex items-center justify-between border-b border-[#22322C]">
              <h3 className="text-xs font-bold uppercase tracking-wider">UPLOAD SPECIFICATION DOCUMENT</h3>
              <button onClick={() => setUploadTenderId(null)} className="text-[#808B84] hover:text-white">✕</button>
            </div>
            <form onSubmit={handleUploadSubmit} className="p-6 space-y-4 text-xs">
              <div className="border border-dashed border-[#D8DCD6] p-6 text-center bg-[#FCFCFA]">
                <input
                  type="file"
                  id="tender-modal-upload"
                  accept=".pdf,.png,.jpg,.jpeg"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      setUploadFile(e.target.files[0]);
                    }
                  }}
                  className="hidden"
                />
                <label htmlFor="tender-modal-upload" className="cursor-pointer block space-y-2">
                  <div className="font-bold text-[#17201C]">
                    {uploadFile ? uploadFile.name : "SELECT SPECIFICATION PDF (MAX 25 MB)"}
                  </div>
                  <div className="text-[10px] text-[#59625D]">PDF, PNG, JPG supported</div>
                </label>
              </div>
              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setUploadTenderId(null)}
                  className="px-4 py-2 border border-[#D8DCD6] text-xs font-semibold text-[#59625D]"
                >
                  CANCEL
                </button>
                <button
                  type="submit"
                  disabled={uploading || !uploadFile}
                  className="px-5 py-2 bg-[#163C32] hover:bg-[#0E2922] text-white font-bold text-xs uppercase disabled:opacity-50"
                >
                  {uploading ? "PARSING CLAUSES..." : "UPLOAD & PARSE"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};
