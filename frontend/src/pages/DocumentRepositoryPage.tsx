import React, { useState, useEffect } from 'react';
import {
  FileSearch,
  Search,
  RefreshCw,
  FileText,
  Eye,
  Building,
  CheckCircle2,
  Clock,
  Layers,
  Sparkles,
  ExternalLink,
  ChevronRight,
  Filter,
  Check,
  UploadCloud,
  Cpu,
  Database,
  Hash,
  Award,
  AlertCircle,
  FileCheck
} from 'lucide-react';
import { evidenceService, documentService } from '../services';

interface DocumentItem {
  id: string;
  bidder_id?: string;
  bidder_name?: string;
  tender_id?: string;
  tender_title?: string;
  document_name: string;
  original_filename?: string;
  document_type: string;
  file_size: number;
  mime_type: string;
  is_scanned: boolean;
  page_count: number;
  extraction_method: string;
  upload_timestamp: string;
  entities_count: number;
  entities: Array<{
    id: string;
    entity_type: string;
    entity_value: string;
    normalized_value?: string;
    confidence: number;
    page_number: number;
    context_snippet?: string;
  }>;
  extracted_text_snippet?: string;
}

interface ExtractedEntityItem {
  id: string;
  document_id: string;
  document_name: string;
  bidder_id?: string;
  bidder_name?: string;
  entity_type: string;
  entity_value: string;
  normalized_value?: string;
  confidence: number;
  page_number: number;
  context_snippet?: string;
  created_at?: string;
}

export const DocumentRepositoryPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dossiers' | 'matrix' | 'inspector'>('dossiers');
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [entities, setEntities] = useState<ExtractedEntityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [selectedEntityType, setSelectedEntityType] = useState<string>('ALL');

  // Live Inspector State
  const [inspecting, setInspecting] = useState(false);
  const [inspectResult, setInspectResult] = useState<any>(null);
  const [dragActive, setDragActive] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [docsData, entsData] = await Promise.all([
        evidenceService.getAllDocuments(),
        evidenceService.getExtractedEntities()
      ]);
      setDocuments(docsData || []);
      setEntities(entsData || []);
      if (docsData && docsData.length > 0 && !selectedDocId) {
        setSelectedDocId(docsData[0].id);
      }
    } catch (err) {
      console.error('Error fetching document evidence:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    await processInspectorFile(file);
  };

  const processInspectorFile = async (file: File) => {
    setInspecting(true);
    try {
      const result = await documentService.inspectDocument(file);
      setInspectResult(result);
      setActiveTab('inspector');
    } catch (err) {
      console.error('Error inspecting file:', err);
    } finally {
      setInspecting(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processInspectorFile(e.dataTransfer.files[0]);
    }
  };

  const activeDoc = documents.find(d => d.id === selectedDocId) || documents[0];

  const filteredDocs = documents.filter(d => {
    const q = searchQuery.toLowerCase();
    const matchSearch =
      d.document_name?.toLowerCase().includes(q) ||
      (d.bidder_name && d.bidder_name.toLowerCase().includes(q)) ||
      d.document_type?.toLowerCase().includes(q);
    return matchSearch;
  });

  const filteredEntities = entities.filter(e => {
    const matchType = selectedEntityType === 'ALL' || e.entity_type === selectedEntityType;
    const q = searchQuery.toLowerCase();
    const matchSearch =
      !q ||
      e.entity_value.toLowerCase().includes(q) ||
      e.entity_type.toLowerCase().includes(q) ||
      (e.bidder_name && e.bidder_name.toLowerCase().includes(q)) ||
      (e.document_name && e.document_name.toLowerCase().includes(q));
    return matchType && matchSearch;
  });

  const entityTypes = [
    'ALL',
    'GSTIN',
    'PAN',
    'COMPANY_NAME',
    'FINANCIAL_TURNOVER',
    'PIPELINE_LENGTH_KM',
    'OIL_GAS_PROJECT',
    'OIL_GAS_EXPERIENCE_YEARS',
    'MANPOWER_RECORD',
    'HSE_CERTIFICATION'
  ];

  const totalPages = documents.reduce((acc, d) => acc + (d.page_count || 1), 0);
  const scannedDocs = documents.filter(d => d.is_scanned).length;
  const digitalDocs = documents.length - scannedDocs;
  const totalEntities = entities.length;

  return (
    <div className="space-y-6 font-sans">
      
      {/* ── Top Header Section ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="text-[11px] font-mono tracking-widest text-[#66717C] uppercase font-bold flex items-center gap-2">
            <Cpu className="w-3.5 h-3.5 text-[#163C32]" />
            <span>NLP & OCR Extraction Intelligence</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-serif font-bold text-[#10283A] tracking-tight mt-0.5">
            Extracted Entities & Document Repository
          </h1>
          <p className="text-xs text-[#66717C] mt-0.5">
            Live multi-document intelligence engine with PyMuPDF native parsing, Tesseract OCR 300 DPI, and FAISS vector evidence retrieval.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={fetchData}
            disabled={loading}
            className="px-3.5 py-1.5 bg-[#FFFFFF] border border-[#D9DEE3] hover:bg-[#F8FAFC] text-[#10283A] text-xs font-semibold rounded shadow-sm flex items-center gap-1.5 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Extractions</span>
          </button>
        </div>
      </div>

      {/* ── Top Summary KPI Cards ── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded-md p-4 shadow-sm space-y-1">
          <div className="text-[11px] font-mono font-semibold text-[#66717C] uppercase tracking-wider">
            Total Documents
          </div>
          <div className="text-2xl font-serif font-bold text-[#10283A] font-mono">
            {documents.length}
          </div>
          <div className="text-xs text-[#66717C]">{totalPages} Total Indexed Pages</div>
        </div>

        <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded-md p-4 shadow-sm space-y-1">
          <div className="text-[11px] font-mono font-semibold text-[#66717C] uppercase tracking-wider">
            PyMuPDF Streams
          </div>
          <div className="text-2xl font-serif font-bold text-[#198754] font-mono">
            {digitalDocs}
          </div>
          <div className="text-xs text-[#198754]">Native PDF Parsed</div>
        </div>

        <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded-md p-4 shadow-sm space-y-1">
          <div className="text-[11px] font-mono font-semibold text-[#66717C] uppercase tracking-wider">
            Tesseract OCR (300 DPI)
          </div>
          <div className="text-2xl font-serif font-bold text-[#D98A16] font-mono">
            {scannedDocs}
          </div>
          <div className="text-xs text-[#D98A16]">Scanned & Deskewed</div>
        </div>

        <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded-md p-4 shadow-sm space-y-1">
          <div className="text-[11px] font-mono font-semibold text-[#66717C] uppercase tracking-wider">
            Extracted Entities
          </div>
          <div className="text-2xl font-serif font-bold text-[#163C32] font-mono">
            {totalEntities}
          </div>
          <div className="text-xs text-[#163C32]">Domain Tokens Extracted</div>
        </div>
      </div>

      {/* ── Navigation Tabs ── */}
      <div className="flex border-b border-[#D9DEE3] bg-[#FFFFFF] px-3 pt-2 rounded-t-md">
        <button
          onClick={() => setActiveTab('dossiers')}
          className={`px-4 py-2.5 font-sans font-semibold text-xs border-b-2 flex items-center gap-2 transition-colors ${
            activeTab === 'dossiers'
              ? 'border-[#163C32] text-[#163C32]'
              : 'border-transparent text-[#66717C] hover:text-[#10283A]'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          <span>Document Evidence Dossiers ({documents.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('matrix')}
          className={`px-4 py-2.5 font-sans font-semibold text-xs border-b-2 flex items-center gap-2 transition-colors ${
            activeTab === 'matrix'
              ? 'border-[#163C32] text-[#163C32]'
              : 'border-transparent text-[#66717C] hover:text-[#10283A]'
          }`}
        >
          <Database className="w-3.5 h-3.5" />
          <span>Extracted Entities Matrix ({entities.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('inspector')}
          className={`px-4 py-2.5 font-sans font-semibold text-xs border-b-2 flex items-center gap-2 transition-colors ${
            activeTab === 'inspector'
              ? 'border-[#163C32] text-[#163C32]'
              : 'border-transparent text-[#66717C] hover:text-[#10283A]'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5 text-[#D98A16]" />
          <span>Live OCR & NLP Inspector</span>
        </button>
      </div>

      {/* ── TAB 1: DOCUMENT EVIDENCE DOSSIERS ── */}
      {activeTab === 'dossiers' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          
          {/* Left Column: Dossier List */}
          <div className="lg:col-span-5 bg-[#FFFFFF] border border-[#D9DEE3] rounded-md shadow-sm overflow-hidden flex flex-col">
            <div className="p-3.5 border-b border-[#EAEEF2] bg-[#F8FAFC]">
              <div className="relative">
                <Search className="w-4 h-4 text-[#66717C] absolute left-3 top-2.5" />
                <input
                  type="text"
                  placeholder="Search documents, bidders, or categories..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 bg-[#FFFFFF] border border-[#D9DEE3] rounded text-xs focus:outline-none focus:border-[#163C32]"
                />
              </div>
            </div>

            <div className="divide-y divide-[#EAEEF2] overflow-y-auto max-h-[620px]">
              {filteredDocs.length === 0 ? (
                <div className="p-8 text-center text-xs text-[#66717C]">
                  No documents found matching the search criteria.
                </div>
              ) : (
                filteredDocs.map(doc => {
                  const isSelected = doc.id === (activeDoc?.id || '');
                  return (
                    <div
                      key={doc.id}
                      onClick={() => setSelectedDocId(doc.id)}
                      className={`p-3.5 cursor-pointer transition-colors ${
                        isSelected
                          ? 'bg-[#EBF3EF] border-l-4 border-[#163C32]'
                          : 'hover:bg-[#F8FAFC]'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <FileText className={`w-4 h-4 ${isSelected ? 'text-[#163C32]' : 'text-[#66717C]'}`} />
                          <span className="font-semibold text-xs text-[#10283A] truncate max-w-[210px]">
                            {doc.document_name || doc.original_filename}
                          </span>
                        </div>
                        <span className={`px-1.5 py-0.5 text-[9px] font-mono font-bold rounded ${
                          doc.is_scanned
                            ? 'bg-[#FEF3C7] text-[#92400E] border border-[#FDE68A]'
                            : 'bg-[#DCFCE7] text-[#166534] border border-[#BBF7D0]'
                        }`}>
                          {doc.extraction_method}
                        </span>
                      </div>

                      <div className="mt-1.5 flex items-center justify-between text-[11px] text-[#66717C]">
                        <span className="font-medium text-[#10283A]">
                          {doc.bidder_name || 'Petroleum Bidder Evidence'}
                        </span>
                        <span className="font-mono text-[10px]">
                          {doc.page_count || 1} pg • {doc.entities_count || doc.entities?.length || 0} entities
                        </span>
                      </div>

                      {doc.extracted_text_snippet && (
                        <p className="mt-1.5 text-[11px] text-[#59625D] line-clamp-2 italic font-mono bg-[#FFFFFF] p-1.5 rounded border border-[#EAEEF2]">
                          "{doc.extracted_text_snippet}"
                        </p>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Right Column: Active Dossier Deep Inspector */}
          <div className="lg:col-span-7 bg-[#FFFFFF] border border-[#D9DEE3] rounded-md shadow-sm overflow-hidden flex flex-col">
            {activeDoc ? (
              <div>
                <div className="px-5 py-3.5 bg-[#10283A] text-white flex items-center justify-between">
                  <div>
                    <h2 className="font-serif font-bold text-sm">
                      {activeDoc.document_name || activeDoc.original_filename}
                    </h2>
                    <div className="text-[11px] text-[#BAC4CE] font-mono mt-0.5">
                      Bidder: {activeDoc.bidder_name || 'General Evidence'} • {activeDoc.document_type}
                    </div>
                  </div>
                  <span className="px-2 py-0.5 bg-[#18374D] border border-[#BAC4CE] text-[#D98A16] font-mono text-[10px] font-bold rounded">
                    {activeDoc.is_scanned ? 'OCR INGESTION' : 'DIGITAL INGESTION'}
                  </span>
                </div>

                <div className="p-5 space-y-5">
                  {/* Metadata Chips */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs p-3 bg-[#F8FAFC] border border-[#EAEEF2] rounded">
                    <div>
                      <span className="text-[10px] text-[#66717C] uppercase block">Engine</span>
                      <span className="font-bold text-[#10283A]">{activeDoc.extraction_method}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-[#66717C] uppercase block">Pages</span>
                      <span className="font-bold text-[#10283A]">{activeDoc.page_count || 1}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-[#66717C] uppercase block">File Size</span>
                      <span className="font-bold text-[#10283A]">{Math.round((activeDoc.file_size || 150000) / 1024)} KB</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-[#66717C] uppercase block">Tokens Extracted</span>
                      <span className="font-bold text-[#163C32]">{activeDoc.entities?.length || 0} Domain Entities</span>
                    </div>
                  </div>

                  {/* Extracted Domain Entities Cards */}
                  <div>
                    <h3 className="font-mono text-xs uppercase font-bold text-[#10283A] mb-2 flex items-center gap-1.5">
                      <Award className="w-3.5 h-3.5 text-[#163C32]" />
                      <span>Extracted Domain Entities & Provenance</span>
                    </h3>

                    {activeDoc.entities && activeDoc.entities.length > 0 ? (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                        {activeDoc.entities.map((ent, idx) => (
                          <div key={idx} className="p-3 bg-[#F4F5F2] border border-[#D0D7D3] rounded space-y-1 font-mono text-xs">
                            <div className="flex items-center justify-between text-[10px]">
                              <span className="font-bold text-[#163C32] bg-[#E2E8F0] px-1.5 py-0.2 rounded">
                                {ent.entity_type}
                              </span>
                              <span className="text-[#166534] font-bold">
                                {Math.round((ent.confidence || 0.95) * 100)}% Conf
                              </span>
                            </div>
                            <div className="font-bold text-xs text-[#17201C] pt-0.5">
                              {ent.entity_value}
                            </div>
                            {ent.context_snippet && (
                              <div className="text-[10px] text-[#59625D] italic truncate">
                                Context: "{ent.context_snippet}"
                              </div>
                            )}
                            <div className="text-[9px] text-[#66717C]">
                              Page: {ent.page_number}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="p-4 bg-[#F8FAFC] border border-dashed border-[#D9DEE3] text-center text-xs text-[#66717C] rounded">
                        No individual entity tokens isolated for this document yet.
                      </div>
                    )}
                  </div>

                  {/* Raw Extracted Snippet Preview */}
                  {activeDoc.extracted_text_snippet && (
                    <div>
                      <h3 className="font-mono text-xs uppercase font-bold text-[#10283A] mb-2 flex items-center gap-1.5">
                        <FileSearch className="w-3.5 h-3.5 text-[#163C32]" />
                        <span>OCR & Extracted Stream Preview</span>
                      </h3>
                      <div className="p-3.5 bg-[#17201C] text-[#EAECE8] font-mono text-xs rounded leading-relaxed whitespace-pre-wrap max-h-[160px] overflow-y-auto">
                        {activeDoc.extracted_text_snippet}
                      </div>
                    </div>
                  )}

                </div>
              </div>
            ) : (
              <div className="p-12 text-center text-xs text-[#66717C]">
                Select a document to inspect extraction details.
              </div>
            )}
          </div>

        </div>
      )}

      {/* ── TAB 2: EXTRACTED ENTITIES MATRIX ── */}
      {activeTab === 'matrix' && (
        <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded-md shadow-sm overflow-hidden space-y-4 p-4">
          
          {/* Filter Bar */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-[#EAEEF2]">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-mono font-bold text-[#66717C] uppercase flex items-center gap-1">
                <Filter className="w-3.5 h-3.5" /> Filter Type:
              </span>
              {entityTypes.map(t => (
                <button
                  key={t}
                  onClick={() => setSelectedEntityType(t)}
                  className={`px-2 py-1 rounded text-[10px] font-mono font-bold transition-colors ${
                    selectedEntityType === t
                      ? 'bg-[#163C32] text-white'
                      : 'bg-[#F1F5F9] text-[#475569] hover:bg-[#E2E8F0]'
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>

            <div className="relative w-full sm:w-64">
              <Search className="w-3.5 h-3.5 text-[#66717C] absolute left-2.5 top-2.5" />
              <input
                type="text"
                placeholder="Filter extracted tokens..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 bg-[#FFFFFF] border border-[#D9DEE3] rounded text-xs focus:outline-none focus:border-[#163C32]"
              />
            </div>
          </div>

          {/* Matrix Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse font-sans text-xs">
              <thead>
                <tr className="bg-[#F8FAFC] border-b border-[#D9DEE3] font-mono text-[11px] text-[#66717C] uppercase">
                  <th className="py-2.5 px-3">Entity Type</th>
                  <th className="py-2.5 px-3">Extracted Value</th>
                  <th className="py-2.5 px-3">Bidder / Organization</th>
                  <th className="py-2.5 px-3">Document Source</th>
                  <th className="py-2.5 px-3">Page</th>
                  <th className="py-2.5 px-3 text-right">Confidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#EAEEF2] font-mono">
                {filteredEntities.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-xs text-[#66717C] font-sans">
                      No extracted domain entities found matching criteria.
                    </td>
                  </tr>
                ) : (
                  filteredEntities.map((ent, i) => (
                    <tr key={ent.id || i} className="hover:bg-[#F8FAFC] transition-colors">
                      <td className="py-2.5 px-3">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#E2E8F0] text-[#1E293B]">
                          {ent.entity_type}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 font-bold text-[#10283A]">
                        {ent.entity_value}
                      </td>
                      <td className="py-2.5 px-3 text-[#334155] font-sans">
                        {ent.bidder_name || 'Petroleum Bidder'}
                      </td>
                      <td className="py-2.5 px-3 text-[#64748B] text-[11px] truncate max-w-[160px]">
                        {ent.document_name}
                      </td>
                      <td className="py-2.5 px-3 text-[#64748B]">
                        Pg {ent.page_number || 1}
                      </td>
                      <td className="py-2.5 px-3 text-right font-bold text-[#166534]">
                        {Math.round((ent.confidence || 0.95) * 100)}%
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

        </div>
      )}

      {/* ── TAB 3: LIVE OCR & NLP INSPECTOR ── */}
      {activeTab === 'inspector' && (
        <div className="space-y-6">
          <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded-md shadow-sm p-6">
            <div className="max-w-2xl mx-auto text-center space-y-4">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-[#EBF3EF] text-[#163C32]">
                <UploadCloud className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-lg font-serif font-bold text-[#10283A]">
                  Test Live OCR & Structured Entity Extraction
                </h3>
                <p className="text-xs text-[#66717C] mt-1">
                  Upload any petroleum bid certificate, audited balance sheet, or GST/PAN PDF to execute live extraction through PyMuPDF and Tesseract OCR.
                </p>
              </div>

              <div
                onDragOver={e => { e.preventDefault(); setDragActive(true); }}
                onDragLeave={() => setDragActive(false)}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-lg p-8 transition-colors ${
                  dragActive ? 'border-[#163C32] bg-[#F0FDF4]' : 'border-[#D9DEE3] bg-[#F8FAFC]'
                }`}
              >
                <input
                  type="file"
                  id="inspector-upload"
                  onChange={handleFileUpload}
                  className="hidden"
                  accept=".pdf,.png,.jpg,.jpeg"
                />
                <label
                  htmlFor="inspector-upload"
                  className="cursor-pointer inline-flex items-center gap-2 px-4 py-2 bg-[#163C32] hover:bg-[#0E2821] text-white rounded text-xs font-bold shadow-sm transition-colors"
                >
                  <FileText className="w-4 h-4" />
                  <span>Choose PDF / Image to Inspect</span>
                </label>
                <div className="text-[11px] text-[#66717C] mt-2">
                  Supports Digital PDF, Scanned PDF, TIFF, PNG, JPEG
                </div>
              </div>

              {inspecting && (
                <div className="p-4 bg-[#EBF3EF] border border-[#BBD5C9] rounded text-xs font-mono text-[#163C32] flex items-center justify-center gap-2">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Running OCR Deskewing, Entity Extraction & Regex Matchers...</span>
                </div>
              )}
            </div>
          </div>

          {/* Inspection Results Section */}
          {inspectResult && (
            <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded-md shadow-sm overflow-hidden">
              <div className="px-5 py-3.5 bg-[#10283A] text-white flex items-center justify-between">
                <div>
                  <h3 className="font-serif font-bold text-sm">
                    Inspection Result: {inspectResult.filename}
                  </h3>
                  <div className="text-[11px] text-[#BAC4CE] font-mono">
                    Engine: {inspectResult.extraction_engine} • Pages: {inspectResult.page_count} • Scanned: {inspectResult.is_scanned ? 'YES' : 'NO'}
                  </div>
                </div>
                <span className="px-2.5 py-0.5 bg-[#166534] text-white text-[10px] font-mono font-bold rounded">
                  SUCCESSFULLY PARSED
                </span>
              </div>

              <div className="p-5 space-y-4">
                {/* Summary Row */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs p-3 bg-[#F8FAFC] border border-[#EAEEF2] rounded">
                  <div>
                    <span className="text-[10px] text-[#66717C] uppercase block">Legal Name</span>
                    <span className="font-bold text-[#10283A]">{inspectResult.legal_name || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-[#66717C] uppercase block">GSTIN</span>
                    <span className="font-bold text-[#10283A]">{inspectResult.gstin || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-[#66717C] uppercase block">PAN</span>
                    <span className="font-bold text-[#10283A]">{inspectResult.pan || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-[#66717C] uppercase block">Udyam Registration</span>
                    <span className="font-bold text-[#10283A]">{inspectResult.udyam_number || 'N/A'}</span>
                  </div>
                </div>

                {/* Extracted Text */}
                <div>
                  <h4 className="font-mono text-xs uppercase font-bold text-[#10283A] mb-1.5">
                    Extracted Text Snippet
                  </h4>
                  <div className="p-3 bg-[#17201C] text-[#EAECE8] font-mono text-xs rounded leading-relaxed whitespace-pre-wrap max-h-[160px] overflow-y-auto">
                    {inspectResult.extracted_text || 'No text extracted.'}
                  </div>
                </div>

                {/* Structured Entities */}
                {inspectResult.entities && inspectResult.entities.length > 0 && (
                  <div>
                    <h4 className="font-mono text-xs uppercase font-bold text-[#10283A] mb-1.5">
                      Structured Tokens Found ({inspectResult.entities.length})
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 font-mono text-xs">
                      {inspectResult.entities.map((e: any, idx: number) => (
                        <div key={idx} className="p-2.5 bg-[#F4F5F2] border border-[#D0D7D3] rounded">
                          <span className="text-[10px] font-bold text-[#163C32] uppercase block">
                            {e.entity_type}
                          </span>
                          <span className="font-bold text-xs text-[#17201C]">{e.entity_value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

    </div>
  );
};
