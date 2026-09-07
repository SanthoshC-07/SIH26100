import React, { useState, useEffect } from 'react';
import {
  FileText,
  Filter,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Search,
  Database,
  Layers,
  Flame,
  Building,
  ShieldAlert,
  SlidersHorizontal,
  ChevronDown,
  ChevronUp,
  Tag,
  Hash
} from 'lucide-react';
import {
  requirementDatasetService,
  RequirementDatasetItem,
  RequirementReviewItem
} from '../services';

export const RequirementReviewPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dataset' | 'review_queue'>('dataset');
  const [items, setItems] = useState<RequirementDatasetItem[]>([]);
  const [reviewItems, setReviewItems] = useState<RequirementReviewItem[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [pipelineRunning, setPipelineRunning] = useState<boolean>(false);
  const [pipelineMessage, setPipelineMessage] = useState<string | null>(null);

  // Filters
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedDomain, setSelectedDomain] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  const categories = [
    'ALL',
    'GST_TAX_COMPLIANCE',
    'MSME_UDYAM_ELIGIBILITY',
    'FINANCIAL_ELIGIBILITY',
    'EXPERIENCE_ELIGIBILITY',
    'OEM_AUTHORIZATION',
    'BLACKLISTING_DEBARMENT',
    'TECHNICAL_SPECIFICATION',
    'INDUSTRY_STANDARD_COMPLIANCE',
    'SAFETY_REGULATORY_COMPLIANCE',
    'MAKE_IN_INDIA_LOCAL_CONTENT'
  ];

  const domainOptions = [
    { label: 'All Domains', value: 'ALL' },
    { label: 'Petroleum Pipeline', value: 'PETROLEUM_PIPELINE' },
    { label: 'Oil & Gas', value: 'OIL_GAS' },
    { label: 'General Govt Procurement', value: 'GENERAL_GOVERNMENT_PROCUREMENT' },
    { label: 'Needs Review', value: 'REVIEW' }
  ];

  const statusOptions = ['ALL', 'PENDING', 'APPROVED', 'REJECTED', 'NEEDS_REVIEW'];

  const fetchData = async () => {
    setLoading(true);
    try {
      const [datasetRes, reviewsRes, statsRes] = await Promise.all([
        requirementDatasetService.getDataset({
          category: selectedCategory !== 'ALL' ? selectedCategory : undefined,
          domain_relevance: selectedDomain !== 'ALL' ? selectedDomain : undefined,
          review_status: selectedStatus !== 'ALL' ? selectedStatus : undefined,
          search: searchTerm ? searchTerm : undefined,
          limit: 150
        }),
        requirementDatasetService.getReviews({
          search: searchTerm ? searchTerm : undefined,
          limit: 150
        }),
        requirementDatasetService.getStats()
      ]);

      setItems(datasetRes.items || []);
      setReviewItems(reviewsRes.items || []);
      setStats(statsRes);
    } catch (err) {
      console.error('Error fetching requirement dataset:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedCategory, selectedDomain, selectedStatus]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchData();
  };

  const handleUpdateStatus = async (reqId: string, newStatus: string) => {
    try {
      await requirementDatasetService.updateReview(reqId, newStatus);
      // Update local state immediately
      setItems((prev) =>
        prev.map((item) =>
          item.requirement_id === reqId ? { ...item, review_status: newStatus as any } : item
        )
      );
      // Re-fetch stats
      requirementDatasetService.getStats().then(setStats);
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  };

  const handleRunPipeline = async () => {
    setPipelineRunning(true);
    setPipelineMessage('Running PyMuPDF & Tesseract OCR extraction and ML classification pipeline...');
    try {
      const res = await requirementDatasetService.runPipeline();
      setPipelineMessage(
        `Pipeline completed successfully! Extracted ${res.dataset_count} clauses across ${res.stats?.total_pages_processed || 0} pages.`
      );
      await fetchData();
    } catch (err: any) {
      setPipelineMessage(`Pipeline error: ${err?.response?.data?.detail || err.message}`);
    } finally {
      setPipelineRunning(false);
    }
  };

  const getDomainBadge = (dom: string) => {
    switch (dom) {
      case 'PETROLEUM_PIPELINE':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#E8F3FF] text-[#0052CC] border border-[#B3D4FF]">
            <Flame className="w-3 h-3 text-[#0052CC]" />
            Petroleum Pipeline
          </span>
        );
      case 'OIL_GAS':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#FFF4E5] text-[#B76E00] border border-[#FFE2B3]">
            <Flame className="w-3 h-3 text-[#D98A16]" />
            Oil & Gas
          </span>
        );
      case 'GENERAL_GOVERNMENT_PROCUREMENT':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#F0F4F8] text-[#4A5568] border border-[#CBD5E1]">
            <Building className="w-3 h-3 text-[#64748B]" />
            General Procurement
          </span>
        );
      case 'REVIEW':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#FFF0F0] text-[#C83B32] border border-[#FFD0D0]">
            <AlertTriangle className="w-3 h-3 text-[#C83B32]" />
            Review Needed
          </span>
        );
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold bg-[#E6F4EA] text-[#137333] border border-[#CEEAD6]">
            <CheckCircle2 className="w-3 h-3" /> Approved
          </span>
        );
      case 'REJECTED':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold bg-[#FCE8E6] text-[#C5221F] border border-[#FAD2CF]">
            <XCircle className="w-3 h-3" /> Rejected
          </span>
        );
      case 'NEEDS_REVIEW':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold bg-[#FEF7E0] text-[#B06000] border border-[#FEEFC3]">
            <AlertTriangle className="w-3 h-3" /> Needs Review
          </span>
        );
      case 'PENDING':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold bg-[#F1F3F4] text-[#5F6368] border border-[#DADCE0]">
            Pending Review
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg border border-[#D9DEE3] p-6 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-[#D98A16] uppercase tracking-wider mb-1">
            <Database className="w-4 h-4" /> Phase 3A — Requirement Intelligence Dataset
          </div>
          <h1 className="font-serif text-2xl font-bold text-[#10283A]">
            Tender PDF → Requirement Dataset Review
          </h1>
          <p className="text-xs text-[#66717C] mt-1 max-w-2xl">
            Audit-traceable requirement extraction pipeline for Ministry of Petroleum &amp; Natural Gas tenders.
            Human-in-the-loop review interface for authorized Procurement Officers and Administrators.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={fetchData}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold bg-[#F4F5F7] hover:bg-[#EAECEF] text-[#10283A] rounded border border-[#D9DEE3] transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>

          <button
            onClick={handleRunPipeline}
            disabled={pipelineRunning}
            className="flex items-center gap-2 px-4 py-2 text-xs font-bold bg-[#10283A] hover:bg-[#18374D] text-white rounded shadow-sm transition-colors"
          >
            <Layers className={`w-4 h-4 ${pipelineRunning ? 'animate-spin' : ''}`} />
            {pipelineRunning ? 'Extracting PDFs...' : 'Run Extraction Pipeline'}
          </button>
        </div>
      </div>

      {pipelineMessage && (
        <div className="p-4 bg-[#EBF5FB] border border-[#A9CCE3] rounded-lg text-xs text-[#1B4F72] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <RefreshCw className={`w-4 h-4 ${pipelineRunning ? 'animate-spin' : ''}`} />
            <span>{pipelineMessage}</span>
          </div>
          <button
            onClick={() => setPipelineMessage(null)}
            className="text-[#5D6D7E] hover:text-[#1B4F72] font-bold"
          >
            &times;
          </button>
        </div>
      )}

      {/* KPI Cards */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          <div className="bg-white border border-[#D9DEE3] rounded-lg p-4 shadow-sm">
            <div className="text-[11px] font-bold uppercase text-[#66717C]">Total Requirements</div>
            <div className="text-2xl font-serif font-bold text-[#10283A] mt-1">
              {stats.total_requirements || 0}
            </div>
            <div className="text-[10px] text-[#8A9BA8] mt-0.5">Extracted from tender PDFs</div>
          </div>

          <div className="bg-white border border-[#B3D4FF] rounded-lg p-4 shadow-sm bg-gradient-to-br from-white to-[#F4F8FF]">
            <div className="text-[11px] font-bold uppercase text-[#0052CC]">Petroleum Pipeline</div>
            <div className="text-2xl font-serif font-bold text-[#0052CC] mt-1">
              {stats.domain_relevance_distribution?.PETROLEUM_PIPELINE || 0}
            </div>
            <div className="text-[10px] text-[#0052CC]/80 mt-0.5">Pipeline laying &amp; specs</div>
          </div>

          <div className="bg-white border border-[#FFE2B3] rounded-lg p-4 shadow-sm bg-gradient-to-br from-white to-[#FFFDF9]">
            <div className="text-[11px] font-bold uppercase text-[#B76E00]">Oil &amp; Gas Domain</div>
            <div className="text-2xl font-serif font-bold text-[#B76E00] mt-1">
              {stats.domain_relevance_distribution?.OIL_GAS || 0}
            </div>
            <div className="text-[10px] text-[#B76E00]/80 mt-0.5">Hydrocarbon sector clauses</div>
          </div>

          <div className="bg-white border border-[#CBD5E1] rounded-lg p-4 shadow-sm">
            <div className="text-[11px] font-bold uppercase text-[#4A5568]">General Procurement</div>
            <div className="text-2xl font-serif font-bold text-[#4A5568] mt-1">
              {stats.domain_relevance_distribution?.GENERAL_GOVERNMENT_PROCUREMENT || 0}
            </div>
            <div className="text-[10px] text-[#66717C] mt-0.5">GST / PAN / MSME / GFR</div>
          </div>

          <div className="bg-white border border-[#FFD0D0] rounded-lg p-4 shadow-sm bg-gradient-to-br from-white to-[#FFF9F9]">
            <div className="text-[11px] font-bold uppercase text-[#C83B32]">Pending Review</div>
            <div className="text-2xl font-serif font-bold text-[#C83B32] mt-1">
              {stats.review_status_distribution?.PENDING || stats.total_needing_review || 0}
            </div>
            <div className="text-[10px] text-[#C83B32]/80 mt-0.5">Awaiting human sign-off</div>
          </div>
        </div>
      )}

      {/* Main Tabs */}
      <div className="flex border-b border-[#D9DEE3] bg-white rounded-t-lg px-4 pt-3 gap-4">
        <button
          onClick={() => setActiveTab('dataset')}
          className={`pb-3 text-xs font-bold flex items-center gap-2 border-b-2 transition-colors ${
            activeTab === 'dataset'
              ? 'border-[#D98A16] text-[#10283A]'
              : 'border-transparent text-[#66717C] hover:text-[#10283A]'
          }`}
        >
          <Database className="w-4 h-4" />
          Master Requirement Dataset ({items.length})
        </button>

        <button
          onClick={() => setActiveTab('review_queue')}
          className={`pb-3 text-xs font-bold flex items-center gap-2 border-b-2 transition-colors ${
            activeTab === 'review_queue'
              ? 'border-[#C83B32] text-[#C83B32]'
              : 'border-transparent text-[#66717C] hover:text-[#10283A]'
          }`}
        >
          <ShieldAlert className="w-4 h-4" />
          Flagged Review Queue ({reviewItems.length})
        </button>
      </div>

      {/* Filters Bar */}
      <div className="bg-white border border-[#D9DEE3] p-4 rounded-b-lg -mt-6 shadow-sm space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <form onSubmit={handleSearch} className="flex items-center gap-2 flex-1 min-w-[280px]">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-[#8A9BA8] absolute left-3 top-2.5" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search requirement text, document name, or ID..."
                className="w-full pl-9 pr-3 py-1.5 text-xs bg-[#F4F5F7] border border-[#D9DEE3] rounded focus:outline-none focus:border-[#10283A]"
              />
            </div>
            <button
              type="submit"
              className="px-3 py-1.5 bg-[#10283A] text-white text-xs font-semibold rounded hover:bg-[#18374D]"
            >
              Search
            </button>
          </form>

          {activeTab === 'dataset' && (
            <div className="flex flex-wrap items-center gap-2 text-xs">
              {/* Category Dropdown */}
              <div className="flex items-center gap-1.5">
                <span className="text-[#66717C] font-semibold">Category:</span>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="px-2.5 py-1.5 bg-[#F4F5F7] border border-[#D9DEE3] rounded text-xs text-[#10283A] font-medium"
                >
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat.replace(/_/g, ' ')}
                    </option>
                  ))}
                </select>
              </div>

              {/* Domain Dropdown */}
              <div className="flex items-center gap-1.5">
                <span className="text-[#66717C] font-semibold">Domain:</span>
                <select
                  value={selectedDomain}
                  onChange={(e) => setSelectedDomain(e.target.value)}
                  className="px-2.5 py-1.5 bg-[#F4F5F7] border border-[#D9DEE3] rounded text-xs text-[#10283A] font-medium"
                >
                  {domainOptions.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Status Dropdown */}
              <div className="flex items-center gap-1.5">
                <span className="text-[#66717C] font-semibold">Status:</span>
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="px-2.5 py-1.5 bg-[#F4F5F7] border border-[#D9DEE3] rounded text-xs text-[#10283A] font-medium"
                >
                  {statusOptions.map((st) => (
                    <option key={st} value={st}>
                      {st}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Dataset Table Tab */}
      {activeTab === 'dataset' && (
        <div className="bg-white border border-[#D9DEE3] rounded-lg shadow-sm overflow-hidden">
          {loading ? (
            <div className="py-16 text-center text-xs text-[#66717C]">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto text-[#10283A] mb-2" />
              Loading requirement dataset...
            </div>
          ) : items.length === 0 ? (
            <div className="py-16 text-center text-xs text-[#66717C]">
              No requirements found matching current filter criteria.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-[#10283A] text-white font-sans text-[11px] uppercase tracking-wider">
                    <th className="py-3 px-3 w-10">#</th>
                    <th className="py-3 px-3 w-32">Req ID &amp; Source</th>
                    <th className="py-3 px-4 min-w-[320px]">Requirement Clause Text</th>
                    <th className="py-3 px-3 w-48">Predicted Category</th>
                    <th className="py-3 px-3 w-40">Domain Relevance</th>
                    <th className="py-3 px-3 w-44">Extracted Parameters</th>
                    <th className="py-3 px-3 w-28">Status</th>
                    <th className="py-3 px-3 w-36 text-center">Officer Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#EAECEF]">
                  {items.map((item, idx) => {
                    const isExpanded = expandedRow === item.requirement_id;
                    return (
                      <React.Fragment key={item.requirement_id}>
                        <tr className="hover:bg-[#F9FBFC] transition-colors">
                          <td className="py-3 px-3 text-[#8A9BA8] font-mono">{idx + 1}</td>

                          <td className="py-3 px-3 font-mono">
                            <div className="font-bold text-[#10283A]">{item.requirement_id}</div>
                            <div className="text-[10px] text-[#66717C] truncate max-w-[140px]" title={item.source_document}>
                              {item.source_document}
                            </div>
                            <div className="text-[10px] text-[#D98A16] font-semibold">
                              Page {item.page_number}
                            </div>
                          </td>

                          <td className="py-3 px-4">
                            <div className="font-medium text-[#10283A] leading-relaxed line-clamp-3">
                              {item.original_text}
                            </div>
                            <button
                              onClick={() => setExpandedRow(isExpanded ? null : item.requirement_id)}
                              className="text-[10px] text-[#0052CC] hover:underline font-semibold mt-1 flex items-center gap-1"
                            >
                              {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                              {isExpanded ? 'Hide Raw Details' : 'View Full Context & Entities'}
                            </button>
                          </td>

                          <td className="py-3 px-3">
                            <div className="font-semibold text-[#10283A] text-[11.5px]">
                              {item.category.replace(/_/g, ' ')}
                            </div>
                            <div className="flex items-center gap-1.5 mt-1">
                              <span className="text-[10px] text-[#66717C]">Conf:</span>
                              <span className="font-mono text-[10px] font-bold text-[#10283A]">
                                {((item.classification_confidence || 0) * 100).toFixed(0)}%
                              </span>
                              <span className="text-[9px] px-1.5 py-0.2 bg-[#F0F4F8] text-[#4A5568] rounded border border-[#D9DEE3]">
                                {item.extraction_method}
                              </span>
                            </div>
                          </td>

                          <td className="py-3 px-3">{getDomainBadge(item.domain_relevance)}</td>

                          <td className="py-3 px-3 font-mono text-[11px]">
                            {item.minimum_value !== null && item.minimum_value !== undefined && (
                              <div className="text-[#10283A]">
                                <span className="text-[#66717C]">Min:</span> {item.minimum_value} {item.unit || ''}
                              </div>
                            )}
                            {item.length_km !== null && item.length_km !== undefined && (
                              <div className="text-[#0052CC]">
                                <span className="text-[#66717C]">Length:</span> {item.length_km} KM
                              </div>
                            )}
                            {item.diameter_inch !== null && item.diameter_inch !== undefined && (
                              <div className="text-[#0052CC]">
                                <span className="text-[#66717C]">Dia:</span> {item.diameter_inch} Inch
                              </div>
                            )}
                            {item.experience_years !== null && item.experience_years !== undefined && (
                              <div className="text-[#B76E00]">
                                <span className="text-[#66717C]">Exp:</span> {item.experience_years} Years
                              </div>
                            )}
                            {item.percentage !== null && item.percentage !== undefined && (
                              <div className="text-[#137333]">
                                <span className="text-[#66717C]">Pct:</span> {item.percentage}%
                              </div>
                            )}
                            {item.count !== null && item.count !== undefined && (
                              <div className="text-[#64748B]">
                                <span className="text-[#66717C]">Count:</span> {item.count}
                              </div>
                            )}
                            {item.minimum_value === null &&
                              item.length_km === null &&
                              item.experience_years === null &&
                              item.percentage === null &&
                              item.count === null && (
                                <span className="text-[#8A9BA8] italic font-sans text-[10px]">
                                  Qualitative requirement
                                </span>
                              )}
                          </td>

                          <td className="py-3 px-3">{getStatusBadge(item.review_status)}</td>

                          <td className="py-3 px-3 text-center">
                            <div className="flex items-center justify-center gap-1">
                              <button
                                onClick={() => handleUpdateStatus(item.requirement_id, 'APPROVED')}
                                title="Approve Clause"
                                className="p-1 rounded bg-[#E6F4EA] hover:bg-[#CEEAD6] text-[#137333] border border-[#CEEAD6]"
                              >
                                <CheckCircle2 className="w-3.5 h-3.5" />
                              </button>
                              <button
                                onClick={() => handleUpdateStatus(item.requirement_id, 'REJECTED')}
                                title="Reject Clause"
                                className="p-1 rounded bg-[#FCE8E6] hover:bg-[#FAD2CF] text-[#C5221F] border border-[#FAD2CF]"
                              >
                                <XCircle className="w-3.5 h-3.5" />
                              </button>
                              <button
                                onClick={() => handleUpdateStatus(item.requirement_id, 'NEEDS_REVIEW')}
                                title="Flag for Review"
                                className="p-1 rounded bg-[#FEF7E0] hover:bg-[#FEEFC3] text-[#B06000] border border-[#FEEFC3]"
                              >
                                <AlertTriangle className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </td>
                        </tr>

                        {isExpanded && (
                          <tr className="bg-[#F8FAFC]">
                            <td colSpan={8} className="p-4 border-t border-b border-[#D9DEE3]">
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                                <div>
                                  <div className="font-bold text-[#10283A] mb-1">Normalized Clause Text:</div>
                                  <div className="p-2 bg-white rounded border border-[#D9DEE3] text-[#4A5568] leading-relaxed">
                                    {item.normalized_text}
                                  </div>
                                </div>

                                <div>
                                  <div className="font-bold text-[#10283A] mb-1">Detected Entities &amp; Standards:</div>
                                  <div className="p-2 bg-white rounded border border-[#D9DEE3] flex flex-wrap gap-1.5 min-h-[40px]">
                                    {item.entities && item.entities.length > 0 ? (
                                      item.entities.map((ent, eIdx) => (
                                        <span
                                          key={eIdx}
                                          className="px-2 py-0.5 rounded text-[10px] bg-[#E8F0FE] text-[#174EA6] border border-[#D2E3FC] font-mono"
                                        >
                                          {ent}
                                        </span>
                                      ))
                                    ) : (
                                      <span className="text-[#8A9BA8] italic text-[11px]">No specific domain entities</span>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Review Queue Tab */}
      {activeTab === 'review_queue' && (
        <div className="bg-white border border-[#D9DEE3] rounded-lg shadow-sm overflow-hidden">
          <div className="p-4 border-b border-[#D9DEE3] bg-[#FFF9F9] flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs text-[#C83B32] font-semibold">
              <ShieldAlert className="w-4 h-4" />
              Requirements Flagged for Manual Verification ({reviewItems.length} items)
            </div>
            <div className="text-[11px] text-[#66717C]">
              Includes low classifier confidence, missing numeric attributes, or ambiguous domain tags.
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-[#10283A] text-white font-sans text-[11px] uppercase tracking-wider">
                  <th className="py-3 px-3 w-12">#</th>
                  <th className="py-3 px-3 w-36">Req ID &amp; Source</th>
                  <th className="py-3 px-4 min-w-[300px]">Clause Text</th>
                  <th className="py-3 px-3 w-44">Predicted Category</th>
                  <th className="py-3 px-3 w-24">Confidence</th>
                  <th className="py-3 px-4 w-60">Review Reason</th>
                  <th className="py-3 px-3 w-36 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#EAECEF]">
                {reviewItems.map((rItem, idx) => (
                  <tr key={rItem.requirement_id} className="hover:bg-[#FFFDFD] transition-colors">
                    <td className="py-3 px-3 text-[#8A9BA8] font-mono">{idx + 1}</td>
                    <td className="py-3 px-3 font-mono">
                      <div className="font-bold text-[#10283A]">{rItem.requirement_id}</div>
                      <div className="text-[10px] text-[#66717C] truncate max-w-[140px]" title={rItem.source_document}>
                        {rItem.source_document}
                      </div>
                      <div className="text-[10px] text-[#D98A16] font-semibold">
                        Page {rItem.page_number}
                      </div>
                    </td>
                    <td className="py-3 px-4 font-medium text-[#10283A] leading-relaxed">
                      {rItem.original_text}
                    </td>
                    <td className="py-3 px-3 font-semibold text-[#10283A]">
                      {rItem.predicted_category.replace(/_/g, ' ')}
                    </td>
                    <td className="py-3 px-3 font-mono text-[11px] font-bold">
                      {((rItem.classification_confidence || 0) * 100).toFixed(0)}%
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-block px-2 py-0.5 rounded text-[10.5px] font-semibold bg-[#FCE8E6] text-[#C5221F] border border-[#FAD2CF]">
                        {rItem.review_reason}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-center">
                      <div className="flex items-center justify-center gap-1.5">
                        <button
                          onClick={() => handleUpdateStatus(rItem.requirement_id, 'APPROVED')}
                          className="px-2.5 py-1 text-[11px] font-bold bg-[#E6F4EA] hover:bg-[#CEEAD6] text-[#137333] rounded border border-[#CEEAD6]"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => handleUpdateStatus(rItem.requirement_id, 'REJECTED')}
                          className="px-2.5 py-1 text-[11px] font-bold bg-[#FCE8E6] hover:bg-[#FAD2CF] text-[#C5221F] rounded border border-[#FAD2CF]"
                        >
                          Reject
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
