import React, { useState } from 'react';
import {
  FolderOpen,
  Search,
  Filter,
  Upload,
  FileText,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Download,
  ShieldCheck,
  Eye,
  FileCheck2,
  ChevronRight
} from 'lucide-react';

export const DocumentRepositoryPage: React.FC = () => {
  const [selectedDoc, setSelectedDoc] = useState<any>({
    name: 'Praveen_BS_Mock_Petroleum_Compliance_Evidence_Pack.pdf',
    code: 'DOC-8821',
    status: 'Verified',
    bidRef: 'BID-2026-001',
    uploadedBy: 'Alex Rivera',
    date: '2026-09-03 14:30',
    size: '4.2 MB',
    type: 'PDF',
    digitalSig: 'PASS',
    templateMatch: 'PASS',
    entityCheck: 'PASS'
  });

  const [activeDetailTab, setActiveDetailTab] = useState<'METADATA' | 'AUDIT'>('METADATA');

  const mockDocs = [
    {
      name: 'Praveen_BS_Mock_Petroleum_Compliance_Evidence_Pack.pdf',
      code: 'DOC-8821',
      status: 'Verified',
      bidRef: 'BID-2026-001',
      uploadedBy: 'Alex Rivera',
      date: '2026-09-03 14:30',
      size: '4.2 MB',
      type: 'PDF',
      digitalSig: 'PASS',
      templateMatch: 'PASS',
      entityCheck: 'PASS'
    },
    {
      name: 'L&T_Compliance_Certificates_Bundle.pdf',
      code: 'DOC-8822',
      status: 'Processing',
      bidRef: 'BID-2026-002',
      uploadedBy: 'Marcus Thorne',
      date: '2026-09-03 12:15',
      size: '12.8 MB',
      type: 'PDF',
      digitalSig: 'PASS',
      templateMatch: 'PASS',
      entityCheck: 'REVIEW'
    },
    {
      name: 'Indus_Financial_Audit_2023_Q4.pdf',
      code: 'DOC-8823',
      status: 'Verified',
      bidRef: 'BID-2026-003',
      uploadedBy: 'Sarah Jenkins',
      date: '2026-09-02 09:45',
      size: '3.1 MB',
      type: 'PDF',
      digitalSig: 'PASS',
      templateMatch: 'PASS',
      entityCheck: 'PASS'
    },
    {
      name: 'PetroCon_Subcontractor_Agreements.pdf',
      code: 'DOC-8824',
      status: 'Flagged',
      bidRef: 'BID-2026-004',
      uploadedBy: 'David Miller',
      date: '2026-09-01 11:20',
      size: '850 KB',
      type: 'PDF',
      digitalSig: 'FAIL',
      templateMatch: 'REVIEW',
      entityCheck: 'FAIL'
    }
  ];

  return (
    <div className="space-y-6">
      
      {/* 1. Header & Actions (Matching Page 7 from PDF) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">
            Document Repository
          </h1>
          <p className="text-xs text-slate-500">
            Secure vault of parsed tender specifications, bidder evidence dossiers, and OCR text caches.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search within repository..."
              className="w-full pl-9 pr-3 py-2 bg-white border border-slate-200 rounded-lg text-xs focus:outline-none focus:border-blue-500 shadow-2xs"
            />
          </div>
          <button className="px-3.5 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-2xs">
            <Filter className="w-3.5 h-3.5 text-slate-500" /> Filter
          </button>
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold flex items-center gap-1.5 shadow-sm">
            <Upload className="w-4 h-4" /> Upload
          </button>
        </div>
      </div>

      {/* 2. Main Grid: Document List (2 cols) & Detail Drawer (1 col) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Document Table (2 cols) */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-500 font-semibold uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="py-3 px-5">Name</th>
                  <th className="py-3 px-5 text-center">Status</th>
                  <th className="py-3 px-5">Bid Ref</th>
                  <th className="py-3 px-5">Uploaded By</th>
                  <th className="py-3 px-5 text-right">Size</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 text-slate-700">
                {mockDocs.map((doc) => {
                  const isSelected = selectedDoc?.code === doc.code;
                  const statusBg = doc.status === 'Verified' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : doc.status === 'Processing' ? 'bg-blue-50 text-blue-700 border-blue-200' : 'bg-rose-50 text-rose-700 border-rose-200';
                  
                  return (
                    <tr
                      key={doc.code}
                      onClick={() => setSelectedDoc(doc)}
                      className={`hover:bg-slate-50 cursor-pointer transition-colors ${
                        isSelected ? 'bg-blue-50/40' : ''
                      }`}
                    >
                      <td className="py-3.5 px-5">
                        <div className="flex items-center gap-2.5">
                          <FileText className="w-4 h-4 text-blue-600 shrink-0" />
                          <div>
                            <div className="font-bold text-slate-900">{doc.name}</div>
                            <div className="text-[10px] text-slate-400 font-mono">{doc.type} • {doc.code}</div>
                          </div>
                        </div>
                      </td>
                      <td className="py-3.5 px-5 text-center">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold border ${statusBg}`}>
                          {doc.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-5 font-mono text-[11px] font-medium text-slate-600">
                        {doc.bidRef}
                      </td>
                      <td className="py-3.5 px-5">
                        <div className="font-medium text-slate-800">{doc.uploadedBy}</div>
                        <div className="text-[10px] text-slate-400 font-mono">{doc.date}</div>
                      </td>
                      <td className="py-3.5 px-5 text-right font-mono text-[11px] text-slate-600">
                        {doc.size}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Detail / Preview Panel (Matching Page 7 from PDF) */}
        {selectedDoc && (
          <div className="bg-white rounded-xl border border-slate-200 shadow-card p-5 space-y-5 flex flex-col justify-between">
            <div className="space-y-4">
              {/* Top Title & Close */}
              <div className="flex items-start justify-between gap-2 border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <FileCheck2 className="w-5 h-5 text-blue-600 shrink-0" />
                  <div>
                    <h3 className="font-bold text-xs text-slate-900 line-clamp-1">{selectedDoc.name}</h3>
                    <p className="text-[10px] text-slate-500">Detailed Analysis & Preview</p>
                  </div>
                </div>
              </div>

              {/* Thumbnail Container */}
              <div className="w-full h-36 rounded-lg bg-gradient-to-tr from-slate-900 to-slate-800 flex flex-col items-center justify-center text-white relative overflow-hidden group shadow-inner">
                <FileText className="w-10 h-10 text-blue-400 mb-2 opacity-80" />
                <span className="text-xs font-mono font-bold">{selectedDoc.name}</span>
                <span className="text-[10px] text-slate-400 font-mono mt-1">PyMuPDF / OCR Verified</span>
                
                <button className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-1.5 text-xs font-bold text-white">
                  <Eye className="w-4 h-4" /> Full Preview
                </button>
              </div>

              {/* Tabs: Metadata vs Audit History */}
              <div className="flex border-b border-slate-200 text-xs">
                <button
                  onClick={() => setActiveDetailTab('METADATA')}
                  className={`flex-1 py-2 font-semibold border-b-2 transition-all ${
                    activeDetailTab === 'METADATA' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Metadata
                </button>
                <button
                  onClick={() => setActiveDetailTab('AUDIT')}
                  className={`flex-1 py-2 font-semibold border-b-2 transition-all ${
                    activeDetailTab === 'AUDIT' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Audit History
                </button>
              </div>

              {/* Metadata Fields */}
              {activeDetailTab === 'METADATA' ? (
                <div className="space-y-3 text-xs">
                  <div className="grid grid-cols-2 gap-2 text-slate-600">
                    <div>
                      <span className="text-[10px] text-slate-400 block uppercase font-bold">STATUS</span>
                      <span className="font-bold text-emerald-600 font-mono">● {selectedDoc.status}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 block uppercase font-bold">FILE SIZE</span>
                      <span className="font-bold text-slate-800 font-mono">{selectedDoc.size}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 block uppercase font-bold">UPLOADER</span>
                      <span className="font-bold text-slate-800">{selectedDoc.uploadedBy}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 block uppercase font-bold">UPLOAD DATE</span>
                      <span className="font-bold text-slate-800 font-mono">{selectedDoc.date}</span>
                    </div>
                  </div>

                  {/* AI Verification Summary Box */}
                  <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-2">
                    <div className="text-[10px] font-bold uppercase text-slate-500 tracking-wider">
                      AI Verification Summary
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-700">Digital Signature Verified</span>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded font-mono">
                        PASS
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-700">Template Matching</span>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded font-mono">
                        PASS
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-700">Entity Consistency Check</span>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded font-mono">
                        PASS
                      </span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-xs space-y-2 text-slate-600">
                  <div className="p-2 border border-slate-100 rounded">
                    <span className="font-bold text-slate-800 block">OCR Extraction Succeeded</span>
                    <span className="text-[10px] text-slate-400 font-mono">2026-09-03 14:31:02</span>
                  </div>
                  <div className="p-2 border border-slate-100 rounded">
                    <span className="font-bold text-slate-800 block">Uploaded to MoPNG Pipeline Vault</span>
                    <span className="text-[10px] text-slate-400 font-mono">2026-09-03 14:30:15</span>
                  </div>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2 pt-3 border-t border-slate-100">
              <button className="flex-1 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors">
                <Download className="w-3.5 h-3.5" /> Download
              </button>
              <button className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold transition-colors">
                Verify Manually
              </button>
            </div>

          </div>
        )}

      </div>

    </div>
  );
};
