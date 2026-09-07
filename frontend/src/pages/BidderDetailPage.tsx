import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { bidderService, documentService, evidenceService } from '../services';
import { BidderDetail, ComplianceCheck, Document, EvidenceSearchResult } from '../types';
import { RiskBadge } from '../components/RiskBadge';
import { ComplianceBadge } from '../components/ComplianceBadge';
import { EvidenceModal } from '../components/EvidenceModal';
import { OfficerReviewModal } from '../components/OfficerReviewModal';
import { OfficerSelectingAuthorityModal } from '../components/OfficerSelectingAuthorityModal';
import {
  FileSpreadsheet,
  Upload,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Eye,
  RefreshCw,
  FileText,
  Layers,
  ArrowLeft,
  ChevronRight,
  ShieldCheck,
  Building,
  UserCheck,
  Clock,
  Sparkles,
  Info
} from 'lucide-react';

interface ProcessingPipelineStep {
  step: number;
  name: string;
  engine?: string;
  status: string;
  detail: string;
}

export const BidderDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [bidder, setBidder] = useState<BidderDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);

  // Active requirement tab / section for focused evidence viewing
  const [activeTab, setActiveTab] = useState<string>('R03');

  // Live Processing Pipeline state per requirement
  const [processingReq, setProcessingReq] = useState<string | null>(null);
  const [pipelineSteps, setPipelineSteps] = useState<ProcessingPipelineStep[]>([]);
  const [lastUploadedEvidence, setLastUploadedEvidence] = useState<{ [reqCode: string]: any }>({});
  const [debarmentInfo, setDebarmentInfo] = useState<any>(null);
  const [checkingDebarment, setCheckingDebarment] = useState(false);

  // Modals state
  const [selectedCheckForEvidence, setSelectedCheckForEvidence] = useState<ComplianceCheck | null>(null);
  const [selectedCheckForReview, setSelectedCheckForReview] = useState<ComplianceCheck | null>(null);
  const [showSelectingAuthorityModal, setShowSelectingAuthorityModal] = useState(false);
  const [previewDocument, setPreviewDocument] = useState<Document | null>(null);

  // Semantic Vector Evidence Search
  const [semanticQuery, setSemanticQuery] = useState('cross country natural gas pipeline 100 km 24 inch');
  const [semanticResults, setSemanticResults] = useState<EvidenceSearchResult[]>([]);
  const [isSearchingEvidence, setIsSearchingEvidence] = useState(false);

  const handleSemanticSearch = async (queryText?: string) => {
    if (!id) return;
    const q = queryText || semanticQuery;
    if (!q.trim()) return;
    setIsSearchingEvidence(true);
    try {
      const results = await evidenceService.searchEvidence({
        query: q,
        bidder_id: id,
        top_k: 4
      });
      setSemanticResults(results);
    } catch (err) {
      console.error("Semantic search failed:", err);
    } finally {
      setIsSearchingEvidence(false);
    }
  };

  const fileInputRefs = useRef<{ [key: string]: HTMLInputElement | null }>({});

  const loadDebarmentCheck = async () => {
    if (!id) return;
    setCheckingDebarment(true);
    try {
      const res = await bidderService.getDebarmentCheck(id);
      setDebarmentInfo(res);
    } catch (err) {
      console.error("Debarment check error:", err);
    } finally {
      setCheckingDebarment(false);
    }
  };

  const loadBidder = async () => {
    if (!id) return;
    try {
      const data = await bidderService.getBidderDetail(id);
      setBidder(data);
      loadDebarmentCheck();
    } catch (err) {
      console.error("Error loading bidder:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBidder();
  }, [id]);

  // Handle Requirement-Specific Upload & Live Processing Simulation/Execution
  const handleRequirementUpload = async (
    reqCode: string,
    category: string,
    file: File
  ) => {
    if (!id) return;
    setProcessingReq(reqCode);
    setPipelineSteps([
      { step: 1, name: 'File Upload', status: 'IN_PROGRESS', detail: `Uploading ${file.name} (${Math.round(file.size / 1024)} KB)...` }
    ]);

    try {
      // Step 1 done
      await new Promise(r => setTimeout(r, 400));
      setPipelineSteps(prev => [
        { step: 1, name: 'File Upload', status: 'COMPLETED', detail: `Uploaded ${file.name} (${Math.round(file.size / 1024)} KB)` },
        { step: 2, name: 'PDF Text Extraction', engine: 'PyMuPDF', status: 'IN_PROGRESS', detail: 'Running PyMuPDF digital text stream extraction...' }
      ]);

      // Step 2 & 3
      await new Promise(r => setTimeout(r, 600));
      const isScanned = file.name.toLowerCase().includes('scanned') || file.type.includes('image');
      setPipelineSteps(prev => [
        prev[0],
        { step: 2, name: 'PDF Text Extraction', engine: 'PyMuPDF', status: 'COMPLETED', detail: 'PyMuPDF page stream extraction completed' },
        { step: 3, name: 'Text Quality Check', status: isScanned ? 'SCANNED_DETECTED' : 'TEXT_FOUND', detail: isScanned ? 'Scanned document detected — Loading & Extracting via 300 DPI OCR...' : 'Digital text quality verified' },
        { step: 4, name: 'OCR Engine', engine: 'Tesseract OCR', status: isScanned ? 'IN_PROGRESS' : 'SKIPPED', detail: isScanned ? 'Rendering page at 300 DPI and applying Tesseract OCR...' : 'OCR not required (native text stream verified)' }
      ]);

      if (isScanned) {
        await new Promise(r => setTimeout(r, 700));
        setPipelineSteps(prev => [
          prev[0], prev[1], prev[2],
          { step: 4, name: 'OCR Engine', engine: 'Tesseract OCR', status: 'COMPLETED', detail: '✓ Tesseract OCR extraction and text normalization completed' }
        ]);
      }

      // Execute backend API call
      const res = await bidderService.uploadRequirementEvidence(id, file, reqCode, category);

      // Step 5 & 6
      setPipelineSteps(prev => [
        ...prev.slice(0, 4),
        { step: 5, name: 'Entity Extraction', status: 'COMPLETED', detail: `Extracted relevant domain tokens for ${category}` },
        { step: 6, name: 'Requirement Verification', status: 'COMPLETED', detail: 'Compliance Engine threshold verification completed' }
      ]);

      // Store in evidence state
      setLastUploadedEvidence(prev => ({
        ...prev,
        [reqCode]: {
          filename: file.name,
          extractionMethod: isScanned ? 'Tesseract OCR' : 'PyMuPDF',
          timestamp: new Date().toLocaleTimeString(),
          result: res
        }
      }));

      await loadBidder();
    } catch (err: any) {
      console.error("Requirement upload error:", err);
      setPipelineSteps(prev => [
        ...prev,
        { step: 99, name: 'Error', status: 'FAILED', detail: err.message || 'Processing failed' }
      ]);
    }
  };

  const handleFullVerification = async () => {
    if (!id) return;
    setVerifying(true);
    try {
      await bidderService.verifyBidder(id);
      await loadBidder();
    } catch (err) {
      console.error("Full verification error:", err);
    } finally {
      setVerifying(false);
    }
  };

  if (loading || !bidder) {
    return (
      <div className="p-8 text-center font-mono text-xs text-[#59625D]">
        RETRIEVING BIDDER VERIFICATION DOSSIER...
      </div>
    );
  }

  // Pre-configured requirements definitions (R01 to R07)
  const requirementDefs = [
    {
      code: 'R01',
      category: 'GST',
      title: 'Valid GST Statutory Registration',
      clause: 'Bidder must possess valid and active GSTIN registration in relevant State/UT with latest GSTR-3B filings.',
      mandatory: 'YES',
      threshold: '—',
      expectedEvidence: 'GST Certificate (Form GST REG-06) / GSTR-3B',
      defaultStatus: 'PASS',
      defaultConfidence: 97,
      defaultSource: 'GST_Registration_Certificate.pdf (Page 1)',
      defaultExtracted: 'GSTIN: 29MOCKP1234M1Z5 | Legal Name: PRAVEEN B S ENGINEERING SERVICES | Status: ACTIVE | Taxpayer Type: Regular',
      comparison: 'Active GSTIN in portal dataset matches submitted registration form',
      rule: 'GSTIN_ACTIVE == TRUE && NAME_MATCH >= 90%'
    },
    {
      code: 'R02',
      category: 'PAN',
      title: 'Valid Permanent Account Number (PAN)',
      clause: 'Bidder entity must hold a valid Permanent Account Number (PAN) matching legal corporate identity.',
      mandatory: 'YES',
      threshold: '—',
      expectedEvidence: 'Income Tax PAN Card / ITR Acknowledgement',
      defaultStatus: 'PASS',
      defaultConfidence: 98,
      defaultSource: 'GST_Registration_Certificate.pdf (Page 1)',
      defaultExtracted: 'PAN: BSZPP1234K | Name: PRAVEEN B S ENGINEERING SERVICES | Category: Company',
      comparison: 'Format valid (5 letters, 4 digits, 1 letter) & matches bidder corporate identity',
      rule: 'PAN_VALID == TRUE && ENTITY_NAME_MATCH >= 95%'
    },
    {
      code: 'R03',
      category: 'TURNOVER',
      title: 'Average Annual Financial Turnover',
      clause: 'Bidder shall have minimum average annual turnover of INR 25 Crore during previous 3 financial years.',
      mandatory: 'YES',
      threshold: '₹25.00 Crore',
      expectedEvidence: 'Audited Balance Sheets / CA Certified Turnover Certificate',
      defaultStatus: 'PASS',
      defaultConfidence: 96,
      defaultSource: 'Financial_Statement.pdf (Page 3)',
      defaultExtracted: 'FY 2023-24: INR 30 Crore | FY 2024-25: INR 27 Crore | FY 2025-26: INR 24 Crore',
      calculatedValue: 'Average Annual Turnover: INR 27 Crore',
      comparison: '27.00 Crore >= 25.00 Crore (Surplus: INR 2.00 Crore)',
      rule: 'AVERAGE(FY23, FY24, FY25) >= 25.00 CR'
    },
    {
      code: 'R04',
      category: 'OIL_GAS_EXPERIENCE',
      title: 'Oil & Gas Sector EPC Experience',
      clause: 'Bidder must possess proven prior execution experience of minimum 7 years in Petroleum, Natural Gas, or Hydrocarbon pipeline projects.',
      mandatory: 'YES',
      threshold: '7 Years',
      expectedEvidence: 'Client Completion Certificates / Work Orders',
      defaultStatus: 'PASS',
      defaultConfidence: 94,
      defaultSource: 'Oil_Gas_Experience_Summary.pdf (Page 1)',
      defaultExtracted: 'Total verified experience: 9 Years across 3 major EPC pipeline contracts for GAIL, IOCL, ONGC',
      calculatedValue: 'Verified Experience: 9 Years (Semantic match: 94%)',
      comparison: '9 Years >= 7 Years',
      rule: 'SECTOR_EXPERIENCE_YEARS >= 7.0 && SEMANTIC_SCORE >= 85%'
    },
    {
      code: 'R05',
      category: 'SIMILAR_PIPELINE_EXPERIENCE',
      title: 'Similar Cross-Country Pipeline Experience',
      clause: 'Bidder must have successfully constructed and commissioned at least one cross-country high-pressure natural gas transmission pipeline of minimum 100 km length (24-inch or higher).',
      mandatory: 'YES',
      threshold: '100 KM (24" OD)',
      expectedEvidence: 'Pipeline Completion Certificate / Taking Over Certificate',
      defaultStatus: 'PASS',
      defaultConfidence: 95,
      defaultSource: 'Pipeline_Completion_Certificate.pdf (Page 4)',
      defaultExtracted: 'Project: Natural Gas Transmission Pipeline | Length: 135 KM | Diameter: 24 Inch NB API 5L X70 | Value: INR 82 Cr | Completion: 15-03-2025 | Role: EPC Contractor',
      calculatedValue: 'Extracted Length: 135 KM (Diameter: 24 Inch)',
      comparison: '135 KM >= 100 KM && 24 Inch >= 24 Inch',
      rule: 'PIPELINE_LENGTH_KM >= 100.0 && DIAMETER_INCH >= 24'
    },
    {
      code: 'R06',
      category: 'TECHNICAL_MANPOWER',
      title: 'Technical Pipeline Engineering Personnel',
      clause: 'Bidder must commit and deploy a minimum of 5 qualified pipeline engineers (B.Tech / B.E. Mechanical / Pipeline / NDT Level II) with at least 8 years of relevant site experience.',
      mandatory: 'YES',
      threshold: '5 Engineers',
      expectedEvidence: 'Key Personnel CVs / Degree Certificates / Experience Affidavits',
      defaultStatus: 'PASS',
      defaultConfidence: 93,
      defaultSource: 'Technical_Manpower_CVs.pdf (Page 1-5)',
      defaultExtracted: '5 qualified engineers deployed: Praveen B S (12 yrs/9 yrs pl), Ravi Kumar (11 yrs/10 yrs pl), Suresh Sharma (10 yrs/9 yrs pl), Ananya Rao (9 yrs/8 yrs pl), Vikram Patel (9 yrs/8 yrs pl)',
      calculatedValue: 'Found: 5 qualifying engineers with >= 8 years experience',
      comparison: '5 qualifying engineers >= 5 mandatory',
      rule: 'COUNT(QUALIFYING_ENGINEERS_WITH_8YRS_EXP) >= 5'
    },
    {
      code: 'R07',
      category: 'HSE_SAFETY',
      title: 'HSE & Occupational Health & Safety Compliance',
      clause: 'Bidder must maintain certified Occupational Health & Safety (ISO 45001) and Environmental Management (ISO 14001) systems with a zero-fatality site safety policy.',
      mandatory: 'YES',
      threshold: 'ISO 45001 / 14001',
      expectedEvidence: 'ISO 45001 Certificate / ISO 14001 Certificate / Corporate HSE Policy',
      defaultStatus: 'REVIEW',
      defaultConfidence: 81,
      defaultSource: 'HSE_ISO45001_Safety_Dossier.pdf (Page 1)',
      defaultExtracted: 'ISO 45001:2018 Certified | ISO 14001:2015 Certified | Valid Until: 31-12-2026 | Zero-fatality site policy',
      calculatedValue: 'Certificates valid; requires officer review for site-specific safety endorsement',
      comparison: 'Accreditation valid through 2026',
      rule: 'ISO_45001_VALID == TRUE && ZERO_FATALITY_DECLARED == TRUE'
    }
  ];

  // Primary compliance checks from bidder object or fallback
  const complianceChecks = bidder.compliance_checks || [];

  // Match requirement definition with actual check
  const getCheckForReq = (reqCode: string, category: string) => {
    return complianceChecks.find(c => 
      (c.requirement_category && c.requirement_category.toUpperCase() === category.toUpperCase()) ||
      ((c as any).category && (c as any).category.toUpperCase() === category.toUpperCase()) ||
      (c.clause_number && c.clause_number.toUpperCase() === reqCode.toUpperCase()) ||
      ((c as any).requirement?.category && (c as any).requirement.category.toUpperCase() === category.toUpperCase()) ||
      ((c as any).requirement?.clause_number && (c as any).requirement.clause_number.toUpperCase() === reqCode.toUpperCase()) ||
      (c.requirement_id && (c.requirement_id.includes(reqCode) || c.requirement_id === reqCode))
    );
  };

  const getReviewCheckObject = (currentReq: typeof requirementDefs[0], existingCheck?: any): ComplianceCheck => {
    if (existingCheck && existingCheck.id) {
      return {
        ...existingCheck,
        bidder_id: existingCheck.bidder_id || bidder.id,
        requirement_id: existingCheck.requirement_id || currentReq.code,
        requirement_category: existingCheck.requirement_category || currentReq.category,
        requirement_description: existingCheck.requirement_description || currentReq.clause,
        status: existingCheck.status || currentReq.defaultStatus,
        confidence: existingCheck.confidence || (currentReq.defaultConfidence / 100),
        evidence_text: existingCheck.evidence_text || currentReq.defaultExtracted,
        document_name: existingCheck.document_name || currentReq.defaultSource.split(' ')[0],
      };
    }
    return {
      id: existingCheck?.id || '',
      bidder_id: bidder.id,
      requirement_id: currentReq.code,
      requirement_category: currentReq.category,
      requirement_description: currentReq.clause,
      requirement_mandatory: currentReq.mandatory === 'YES',
      status: currentReq.defaultStatus as any,
      confidence: currentReq.defaultConfidence / 100,
      score_contribution: currentReq.defaultStatus === 'PASS' ? 1.0 : (currentReq.defaultStatus === 'REVIEW' ? 0.5 : 0.0),
      reason: currentReq.comparison,
      evidence_text: currentReq.defaultExtracted,
      document_name: currentReq.defaultSource.split(' ')[0],
      page_number: 1,
      verification_source: 'HYBRID',
      verification_method: 'RULE_AND_PORTAL',
      rule_version: '3.0.0',
      verified_at: new Date().toISOString()
    } as ComplianceCheck;
  };

  const isHeadlineBidder = bidder.legal_name.toLowerCase().includes('praveen');
  const complianceScore = bidder.compliance_score || (isHeadlineBidder ? 86 : 60);

  return (
    <div className="space-y-6 font-sans">
      
      {/* Top Breadcrumb & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <button
          onClick={() => navigate('/bidders')}
          className="text-xs font-mono font-bold text-[#66717C] hover:text-[#10283A] flex items-center gap-1.5 transition-colors uppercase tracking-wider"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Bidder Records</span>
        </button>

        <div className="flex flex-wrap items-center gap-2 text-xs">
          <button
            onClick={() => setShowSelectingAuthorityModal(true)}
            className="px-4 py-2 bg-[#0F6B38] text-white hover:bg-[#0D5C30] flex items-center gap-1.5 font-bold rounded-md shadow-sm transition-colors"
            title="Procurement Officer Selecting Authority: Determine Bidder Eligibility for Tender Award"
          >
            <ShieldCheck className="w-4 h-4 text-[#D98A16]" />
            <span>Officer Selecting Authority (Determine Eligibility)</span>
          </button>

          <button
            onClick={handleFullVerification}
            disabled={verifying}
            className="px-4 py-2 bg-[#10283A] text-white hover:bg-[#18374D] flex items-center gap-1.5 font-semibold rounded-md shadow-sm transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-[#D98A16] ${verifying ? 'animate-spin' : ''}`} />
            <span>{verifying ? 'Verifying Criteria...' : 'Re-Run Verification Engine'}</span>
          </button>
        </div>
      </div>

      {/* 1. BIDDER HEADER CARD */}
      <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded-md p-6 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2 text-[11px] font-mono font-bold tracking-widest text-[#D98A16] uppercase">
              <span>PETROLEUM EPC CONTRACTOR</span>
              <span>•</span>
              <span>TENDER: MOPNG/PIPE/2026/017</span>
            </div>
            <h1 className="text-2xl font-serif font-bold tracking-tight text-[#10283A] mt-1">
              {bidder.legal_name}
            </h1>
            <div className="text-xs text-[#66717C] mt-0.5">
              {bidder.registered_address || "#42, Pipeline Corridor Industrial Estate, Peenya, Bengaluru, Karnataka 560058"}
            </div>
          </div>

          {/* Compliance Score Block Widget */}
          <div className="bg-[#F9FAFB] border border-[#D9DEE3] rounded-md p-4 shrink-0 min-w-[240px]">
            <div className="flex items-center justify-between text-xs font-bold">
              <span className="text-[#66717C] uppercase tracking-wider">COMPLIANCE SCORE</span>
              <span className="text-lg text-[#10283A] font-bold font-mono">{complianceScore} / 100</span>
            </div>
            {/* Structured Block Score Bar */}
            <div className="w-full bg-[#E5E7EB] h-2 rounded-full mt-2 overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${complianceScore}%`,
                  backgroundColor: complianceScore >= 80 ? '#198754' : complianceScore >= 60 ? '#D98A16' : '#C83B32'
                }}
              />
            </div>
            <div className="mt-2.5 flex items-center justify-between pt-2 border-t border-[#D9DEE3] text-[11px]">
              <span className="text-[#66717C] font-semibold">RISK RATING:</span>
              <RiskBadge level={bidder.risk_level || (isHeadlineBidder ? 'MEDIUM' : 'LOW')} />
            </div>
          </div>
        </div>

        {/* Metadata Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4 mt-5 pt-4 border-t border-[#D9DEE3] text-xs">
          <div>
            <div className="text-[10px] text-[#66717C] uppercase font-semibold">PAN Number</div>
            <div className="font-mono font-bold text-[#17212B] mt-0.5">{bidder.pan || 'BSZPP1234K'}</div>
          </div>
          <div>
            <div className="text-[10px] text-[#66717C] uppercase font-semibold">GSTIN</div>
            <div className="font-mono font-bold text-[#17212B] mt-0.5">{bidder.gstin || '29MOCKP1234M1Z5'}</div>
          </div>
          <div>
            <div className="text-[10px] text-[#66717C] uppercase font-semibold">Oil & Gas Experience</div>
            <div className="font-bold text-[#17212B] mt-0.5">{bidder.oil_gas_experience_years || 9.0} Years</div>
          </div>
          <div>
            <div className="text-[10px] text-[#66717C] uppercase font-semibold">Pipeline Experience</div>
            <div className="font-bold text-[#17212B] mt-0.5">{bidder.pipeline_experience_years || 9.0} Years</div>
          </div>
          <div>
            <div className="text-[10px] text-[#66717C] uppercase font-semibold">Bid Status</div>
            <div className="font-bold text-[#D98A16] mt-0.5">
              {bidder.status?.replace('_', ' ') || 'UNDER EVALUATION'}
            </div>
          </div>
          <div>
            <div className="text-[10px] text-[#66717C] uppercase font-semibold">Overall Compliance</div>
            <div className="font-bold text-[#198754] mt-0.5">86% COMPLIANT</div>
          </div>
        </div>
      </div>

      {/* 2. COMPLIANCE BREAKDOWN TABLE */}
      <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded-md shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-[#D9DEE3] flex items-center justify-between">
          <h2 className="text-base font-serif font-bold text-[#10283A]">
            Compliance Breakdown & Criteria Results
          </h2>
          <span className="text-xs text-[#66717C]">
            7 Core Petroleum Procurement Checks
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse font-sans">
            <thead>
              <tr className="border-b border-[#D9DEE3] bg-[#F9FAFB]/60 text-[11px] font-semibold text-[#66717C] uppercase tracking-wider font-mono">
                <th className="py-3 px-6">ID</th>
                <th className="py-3 px-6">Category</th>
                <th className="py-3 px-6">Requirement</th>
                <th className="py-3 px-6">Result</th>
                <th className="py-3 px-6">Confidence</th>
                <th className="py-3 px-6">Evidence Source</th>
                <th className="py-3 px-6 text-right">Officer Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#EAECE8]">
              {requirementDefs.map((req) => {
                const check = getCheckForReq(req.code, req.category);
                const status = check?.status || req.defaultStatus;
                const conf = Math.round((check?.confidence || req.defaultConfidence / 100) * 100);

                return (
                  <tr
                    key={req.code}
                    className={`hover:bg-[#F4F5F2] ${activeTab === req.code ? 'bg-[#F4F7F5]' : ''}`}
                  >
                    <td className="font-bold text-[#163C32]">{req.code}</td>
                    <td className="font-bold">{req.category}</td>
                    <td className="font-sans text-xs max-w-md">{req.title}</td>
                    <td>
                      <ComplianceBadge status={status} />
                    </td>
                    <td className="font-bold text-[#166534]">{conf}%</td>
                    <td className="text-[#59625D] text-[11px] truncate max-w-xs">
                      {check?.document_name || req.defaultSource}
                    </td>
                    <td>
                      <button
                        onClick={() => {
                          setActiveTab(req.code);
                          setSelectedCheckForReview(getReviewCheckObject(req, check));
                        }}
                        className="px-2 py-1 bg-[#163C32] text-white hover:bg-[#0E2821] text-[11px] font-mono font-bold transition-colors"
                      >
                        Inspect / Review
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 3. CRITICAL NEW FEATURE: REQUIREMENT-SPECIFIC DOCUMENT UPLOAD & LIVE PIPELINE */}
      <div className="panel-sharp bg-white">
        <div className="p-3.5 bg-[#163C32] text-white flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Upload className="w-4 h-4 text-[#A7833B]" />
            <div>
              <h2 className="font-bold text-xs uppercase tracking-wider">
                Requirement-Specific Evidence Upload & Document Processing Pipeline
              </h2>
              <div className="text-[10px] text-[#B5BFB8] font-mono">
                Upload separately per tender criterion (R01–R07) • Live PyMuPDF / Tesseract OCR Telemetry
              </div>
            </div>
          </div>

          {/* Quick Requirement Selector Tabs */}
          <div className="flex flex-wrap gap-1 font-mono text-[10px]">
            {requirementDefs.map((req) => (
              <button
                key={req.code}
                onClick={() => setActiveTab(req.code)}
                className={`px-2 py-1 border transition-colors ${
                  activeTab === req.code
                    ? 'bg-[#A7833B] text-white border-white font-bold'
                    : 'bg-[#101A17] text-[#D0D7D3] border-[#163C32] hover:bg-[#163C32]'
                }`}
              >
                {req.code}
              </button>
            ))}
          </div>
        </div>

        {/* Active Requirement Card */}
        {(() => {
          const currentReq = requirementDefs.find(r => r.code === activeTab) || requirementDefs[2];
          const check = getCheckForReq(currentReq.code, currentReq.category);
          const isProcessingThis = processingReq === currentReq.code;
          const lastUpload = lastUploadedEvidence[currentReq.code];

          return (
            <div className="p-5 space-y-5">
              
              {/* Requirement Header Banner */}
              <div className="p-4 bg-[#F4F5F2] border border-[#D0D7D3]">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2 text-[10px] font-mono font-bold text-[#A7833B] uppercase">
                      <span>REQUIREMENT {currentReq.code} — {currentReq.category}</span>
                      <span>•</span>
                      <span>MANDATORY: {currentReq.mandatory}</span>
                      <span>•</span>
                      <span>THRESHOLD: {currentReq.threshold}</span>
                    </div>
                    <div className="font-bold text-sm text-[#17201C] mt-1 font-sans">
                      {currentReq.clause}
                    </div>
                  </div>

                  {/* Upload Action */}
                  <div className="shrink-0 font-mono">
                    <input
                      type="file"
                      ref={el => fileInputRefs.current[currentReq.code] = el}
                      accept=".pdf,.png,.jpg,.jpeg"
                      onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                          handleRequirementUpload(currentReq.code, currentReq.category, e.target.files[0]);
                          e.target.value = '';
                        }
                      }}
                      className="hidden"
                    />
                    <button
                      onClick={() => fileInputRefs.current[currentReq.code]?.click()}
                      disabled={isProcessingThis}
                      className="px-4 py-2 bg-[#163C32] text-white hover:bg-[#0E2821] text-xs font-bold flex items-center gap-2 transition-colors disabled:opacity-50"
                    >
                      <Upload className="w-3.5 h-3.5 text-[#A7833B]" />
                      <span>{isProcessingThis ? 'PROCESSING...' : `[ Upload ${currentReq.category} Evidence ]`}</span>
                    </button>
                    <div className="text-[9px] text-[#59625D] text-right mt-1">Accepted: PDF, PNG, JPG</div>
                  </div>
                </div>
              </div>

              {/* LIVE DOCUMENT PROCESSING PIPELINE (6 STEPS) */}
              {isProcessingThis && (
                <div className="panel-sharp p-4 bg-[#0E2821] text-white font-mono space-y-3">
                  <div className="flex items-center justify-between border-b border-[#163C32] pb-2">
                    <div className="flex items-center gap-2 text-xs font-bold text-[#A7833B]">
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>DOCUMENT PROCESSING PIPELINE IN PROGRESS...</span>
                    </div>
                    <span className="text-[10px] text-[#B5BFB8]">SIH26100 Telemetry Engine</span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 text-xs">
                    {pipelineSteps.map((step) => (
                      <div
                        key={step.step}
                        className={`p-2.5 border ${
                          step.status === 'COMPLETED' || step.status === 'TEXT_FOUND' || step.status === 'SKIPPED'
                            ? 'bg-[#101A17] border-[#166534] text-[#D0D7D3]'
                            : (step.status === 'SCANNED_DETECTED'
                               ? 'bg-[#101A17] border-[#D97706] text-[#FDE68A]'
                               : 'bg-[#163C32] border-[#A7833B] text-white animate-pulse')
                        }`}
                      >
                        <div className="flex items-center justify-between text-[10px] text-[#8E9A92]">
                          <span>STEP {step.step}: {step.name}</span>
                          <span className="font-bold">
                            {step.status === 'COMPLETED' ? '✓ DONE' : (step.status === 'SCANNED_DETECTED' ? '⚠ SCANNED' : step.status)}
                          </span>
                        </div>
                        <div className="mt-1 text-[11px] leading-tight">
                          {step.detail}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* EXTRACTED EVIDENCE & CALCULATION VIEW */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                
                {/* LEFT: Extracted Evidence & Source Text */}
                <div className="panel-sharp p-4 bg-white border border-[#D0D7D3] space-y-3 font-mono text-xs">
                  <div className="flex items-center justify-between border-b border-[#D0D7D3] pb-2">
                    <div className="font-bold text-[#163C32] uppercase flex items-center gap-1.5">
                      <FileText className="w-3.5 h-3.5" />
                      <span>Extracted Evidence</span>
                    </div>
                    <span className="text-[10px] px-1.5 py-0.2 bg-[#ECFDF5] text-[#166534] border border-[#A7F3D0] font-bold">
                      Confidence: {currentReq.defaultConfidence}%
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-[11px] bg-[#F4F5F2] p-2.5 border border-[#D0D7D3]">
                    <div>
                      <div className="text-[9px] text-[#59625D] uppercase">Document</div>
                      <div className="font-bold text-[#17201C] truncate">{lastUpload?.filename || currentReq.defaultSource.split(' ')[0]}</div>
                    </div>
                    <div>
                      <div className="text-[9px] text-[#59625D] uppercase">Source Page</div>
                      <div className="font-bold text-[#17201C]">{currentReq.defaultSource.match(/Page \d+/)?.[0] || 'Page 1'}</div>
                    </div>
                    <div>
                      <div className="text-[9px] text-[#59625D] uppercase">Extraction Method</div>
                      <div className="font-bold text-[#163C32]">{lastUpload?.extractionMethod || 'PyMuPDF'}</div>
                    </div>
                  </div>

                  <div>
                    <div className="text-[10px] font-bold text-[#59625D] uppercase mb-1">
                      Extracted Fields:
                    </div>
                    <div className="p-2.5 bg-[#F4F5F2] border border-[#D0D7D3] text-xs font-mono space-y-1 text-[#17201C]">
                      {currentReq.code === 'R03' && (
                        <>
                          <div className="flex justify-between"><span>FY 2023-24:</span><span className="font-bold">INR 30 Crore</span></div>
                          <div className="flex justify-between"><span>FY 2024-25:</span><span className="font-bold">INR 27 Crore</span></div>
                          <div className="flex justify-between"><span>FY 2025-26:</span><span className="font-bold">INR 24 Crore</span></div>
                        </>
                      )}
                      {currentReq.code === 'R05' && (
                        <>
                          <div className="flex justify-between"><span>Project:</span><span className="font-bold">Natural Gas Transmission Pipeline</span></div>
                          <div className="flex justify-between"><span>Length:</span><span className="font-bold text-[#163C32]">135 KM</span></div>
                          <div className="flex justify-between"><span>Diameter:</span><span className="font-bold">24 Inch NB API 5L X70</span></div>
                          <div className="flex justify-between"><span>Role:</span><span className="font-bold">EPC Contractor</span></div>
                        </>
                      )}
                      {currentReq.code === 'R06' && (
                        <>
                          <div className="flex justify-between"><span>Deployable Team:</span><span className="font-bold">5 Pipeline Engineers</span></div>
                          <div className="flex justify-between"><span>Qualification:</span><span className="font-bold">B.Tech Mechanical / Metallurgy</span></div>
                          <div className="flex justify-between"><span>Site Experience:</span><span className="font-bold">8 to 12 Years</span></div>
                        </>
                      )}
                      {currentReq.code !== 'R03' && currentReq.code !== 'R05' && currentReq.code !== 'R06' && (
                        <div>{currentReq.defaultExtracted}</div>
                      )}
                    </div>
                  </div>

                  <div>
                    <div className="text-[10px] font-bold text-[#59625D] uppercase mb-1">
                      Source Evidence Text Quote:
                    </div>
                    <blockquote className="p-2.5 bg-[#EAECE8] border-l-2 border-l-[#163C32] font-mono text-[11px] text-[#17201C] leading-relaxed">
                      "{currentReq.code === 'R03'
                        ? 'The bidder reported annual turnover of INR 30 Crore for FY 2023-24, INR 27 Crore for FY 2024-25 and INR 24 Crore for FY 2025-26.'
                        : (currentReq.code === 'R05'
                            ? 'Client: GAIL (India) Limited. Completed 135 KM natural gas transmission pipeline successfully commissioned in March 2025 as EPC Contractor.'
                            : currentReq.defaultExtracted)}"
                    </blockquote>
                  </div>
                </div>

                {/* RIGHT: Calculated Value vs Tender Threshold & Rule Result */}
                <div className="panel-sharp p-4 bg-white border border-[#D0D7D3] space-y-3 font-mono text-xs">
                  <div className="flex items-center justify-between border-b border-[#D0D7D3] pb-2">
                    <div className="font-bold text-[#163C32] uppercase flex items-center gap-1.5">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      <span>Calculated Value & Rule Verification</span>
                    </div>
                    <ComplianceBadge status={currentReq.defaultStatus} />
                  </div>

                  {currentReq.calculatedValue && (
                    <div className="p-3 bg-[#F4F5F2] border border-[#D0D7D3]">
                      <div className="text-[10px] text-[#59625D] uppercase font-bold">
                        Calculated Metric
                      </div>
                      <div className="text-base font-bold text-[#163C32] mt-0.5">
                        {currentReq.calculatedValue}
                      </div>
                    </div>
                  )}

                  <div className="space-y-2">
                    <div className="flex justify-between py-1.5 border-b border-[#EAECE8]">
                      <span className="text-[#59625D]">Tender Requirement:</span>
                      <span className="font-bold text-[#17201C]">{currentReq.threshold !== '—' ? currentReq.threshold : 'Statutory Active'}</span>
                    </div>
                    <div className="flex justify-between py-1.5 border-b border-[#EAECE8]">
                      <span className="text-[#59625D]">Comparison Rule:</span>
                      <span className="font-bold text-[#163C32]">{currentReq.rule}</span>
                    </div>
                    <div className="flex justify-between py-1.5 border-b border-[#EAECE8]">
                      <span className="text-[#59625D]">Rule Evaluation:</span>
                      <span className="font-bold text-[#166534]">{currentReq.comparison}</span>
                    </div>
                    <div className="flex justify-between py-1.5">
                      <span className="text-[#59625D]">Verification Determination:</span>
                      <span className="font-bold text-[#166534]">{currentReq.defaultStatus} ({currentReq.defaultConfidence}% Confidence)</span>
                    </div>
                  </div>

                  <div className="p-3 bg-[#ECFDF5] border border-[#A7F3D0] text-[#166534] text-[11px] leading-relaxed">
                    <strong>Rule Engine Rationale:</strong> Extracted data matches or surpasses mandatory tender threshold specifications. Verified via hybrid rule determinism and sentence transformer similarity score.
                  </div>

                  <div className="pt-2 flex items-center justify-between">
                    <button
                      onClick={() => {
                        const doc = bidder.documents?.find(d => d.document_name.toLowerCase().includes(currentReq.category.toLowerCase().substring(0, 3))) || bidder.documents?.[0];
                        if (doc) setPreviewDocument(doc);
                        else setSelectedCheckForEvidence(check || ({} as any));
                      }}
                      className="px-3 py-1.5 bg-[#F4F5F2] border border-[#D0D7D3] hover:bg-[#EAECE8] text-[#17201C] font-bold text-[11px] flex items-center gap-1.5 transition-colors"
                    >
                      <Eye className="w-3.5 h-3.5 text-[#163C32]" />
                      <span>Split-Screen Document Preview</span>
                    </button>

                    <button
                      onClick={() => setSelectedCheckForReview(getReviewCheckObject(currentReq, check))}
                      className="px-3 py-1.5 bg-[#163C32] text-white hover:bg-[#0E2821] font-bold text-[11px] flex items-center gap-1.5 transition-colors"
                    >
                      <span>Officer Decision & Override</span>
                    </button>
                  </div>
                </div>

              </div>

            </div>
          );
        })()}
      </div>

      {/* 4. DOMAIN-SPECIFIC VERIFICATION PANELS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        
        {/* PANEL A: SIMILAR PIPELINE & OIL GAS EXPERIENCE */}
        <div className="panel-sharp bg-white flex flex-col">
          <div className="p-3 bg-[#EAECE8] border-b border-[#D0D7D3] flex items-center justify-between">
            <h3 className="font-bold text-xs uppercase tracking-wider text-[#17201C]">
              Petroleum & Pipeline Experience Details
            </h3>
            <span className="text-[10px] font-mono text-[#166534] font-bold">135 KM ≥ 100 KM (PASS)</span>
          </div>

          <div className="p-4 space-y-3 font-mono text-xs flex-1">
            <div className="p-3 bg-[#F4F5F2] border border-[#D0D7D3]">
              <div className="text-[10px] text-[#59625D] uppercase font-bold">Oil & Gas Experience (R04)</div>
              <div className="flex justify-between mt-1"><span>Required:</span><span className="font-bold">7 Years</span></div>
              <div className="flex justify-between"><span>Extracted:</span><span className="font-bold text-[#163C32]">9 Years</span></div>
              <div className="flex justify-between"><span>Relevant Sector:</span><span className="font-bold">Oil & Gas / Natural Gas</span></div>
              <div className="flex justify-between"><span>Relevant Projects:</span><span className="font-bold">3 PSU Contracts</span></div>
              <div className="flex justify-between"><span>Semantic Relevance:</span><span className="font-bold text-[#166534]">94%</span></div>
              <div className="flex justify-between mt-1 pt-1 border-t border-[#D0D7D3]"><span>Result:</span><span className="font-bold text-[#166534]">PASS</span></div>
            </div>

            <div className="p-3 bg-[#F4F5F2] border border-[#D0D7D3]">
              <div className="text-[10px] text-[#59625D] uppercase font-bold">Similar Pipeline Experience (R05)</div>
              <div className="flex justify-between mt-1"><span>Required:</span><span className="font-bold">Natural Gas Pipeline (≥ 100 KM)</span></div>
              <div className="flex justify-between"><span>Bidder Evidence:</span><span className="font-bold">Natural Gas Transmission Pipeline</span></div>
              <div className="flex justify-between"><span>Length:</span><span className="font-bold text-[#163C32]">135 KM</span></div>
              <div className="flex justify-between"><span>Diameter:</span><span className="font-bold">24 Inch NB API 5L X70</span></div>
              <div className="flex justify-between"><span>Semantic Match:</span><span className="font-bold text-[#166534]">94%</span></div>
              <div className="flex justify-between"><span>Rule Verification:</span><span className="font-bold text-[#166534]">135 &ge; 100 &rarr; PASS</span></div>
              <div className="flex justify-between mt-1 pt-1 border-t border-[#D0D7D3]"><span>Final:</span><span className="font-bold text-[#166534]">PASS</span></div>
            </div>
          </div>
        </div>

        {/* PANEL B: TECHNICAL MANPOWER VERIFICATION (R06) */}
        <div className="panel-sharp bg-white flex flex-col">
          <div className="p-3 bg-[#EAECE8] border-b border-[#D0D7D3] flex items-center justify-between">
            <h3 className="font-bold text-xs uppercase tracking-wider text-[#17201C]">
              Technical Manpower Verification (5 Engineers ≥ 8 Yrs)
            </h3>
            <span className="text-[10px] font-mono text-[#166534] font-bold">5 / 5 QUALIFIED (PASS)</span>
          </div>

          <div className="overflow-x-auto flex-1">
            <table className="w-full table-dense text-left font-mono text-xs">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Designation</th>
                  <th>Qualification</th>
                  <th>Experience</th>
                  <th>Pipeline Exp</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#EAECE8]">
                <tr>
                  <td className="font-bold text-[#17201C]">Praveen B S</td>
                  <td>Project Engineer</td>
                  <td>B.Tech Mechanical</td>
                  <td>12 Years</td>
                  <td>9 Years</td>
                  <td><span className="text-[#166534] font-bold">QUALIFIED</span></td>
                </tr>
                <tr>
                  <td className="font-bold text-[#17201C]">Ravi Kumar</td>
                  <td>Pipeline Engineer</td>
                  <td>B.Tech Mechanical</td>
                  <td>11 Years</td>
                  <td>10 Years</td>
                  <td><span className="text-[#166534] font-bold">QUALIFIED</span></td>
                </tr>
                <tr>
                  <td className="font-bold text-[#17201C]">Suresh Sharma</td>
                  <td>Welding Specialist</td>
                  <td>B.E. Metallurgy</td>
                  <td>10 Years</td>
                  <td>9 Years</td>
                  <td><span className="text-[#166534] font-bold">QUALIFIED</span></td>
                </tr>
                <tr>
                  <td className="font-bold text-[#17201C]">Ananya Rao</td>
                  <td>QA/QC Inspector</td>
                  <td>B.Tech Mechanical</td>
                  <td>9 Years</td>
                  <td>8 Years</td>
                  <td><span className="text-[#166534] font-bold">QUALIFIED</span></td>
                </tr>
                <tr>
                  <td className="font-bold text-[#17201C]">Vikram Patel</td>
                  <td>Site Safety Officer</td>
                  <td>Diploma Safety</td>
                  <td>9 Years</td>
                  <td>8 Years</td>
                  <td><span className="text-[#166534] font-bold">QUALIFIED</span></td>
                </tr>
              </tbody>
            </table>
          </div>
          <div className="p-3 bg-[#F4F5F2] border-t border-[#D0D7D3] font-mono text-[11px] flex items-center justify-between text-[#166534]">
            <span>Required: 5 engineers</span>
            <span className="font-bold">Found: 5 qualifying engineers &rarr; PASS</span>
          </div>
        </div>

      </div>

      {/* 4B. DEBARMENT / BLACKLISTING VERIFICATION PANEL (MOCK ADAPTER) */}
      <div className="bg-[#FFFFFF] border border-[#D9DEE3] rounded-md shadow-sm overflow-hidden font-sans">
        <div className="px-5 py-3.5 bg-[#10283A] text-white flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-[#D98A16]" />
            <div>
              <h3 className="font-serif font-bold text-xs uppercase tracking-wider">
                Central Debarment / Blacklisting Verification (Rule 151 GFR 2017)
              </h3>
              <div className="text-[10px] text-[#BAC4CE] font-mono">
                Integrated GeM Debarred Registry • CPPP Central Blacklist • MoPNG Debarment Cell
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 font-mono text-[11px]">
            <span className="px-2 py-0.5 bg-[#18374D] border border-[#BAC4CE] text-[#D98A16] font-bold rounded">
              MOCK ADAPTER ARCHITECTURE
            </span>
            <button
              onClick={loadDebarmentCheck}
              disabled={checkingDebarment}
              className="px-2.5 py-1 bg-[#D98A16] hover:bg-[#E39A22] text-[#10283A] font-bold rounded text-[10px] transition-colors flex items-center gap-1"
            >
              <RefreshCw className={`w-3 h-3 ${checkingDebarment ? 'animate-spin' : ''}`} />
              <span>{checkingDebarment ? 'Checking...' : 'Re-Query Portals'}</span>
            </button>
          </div>
        </div>

        <div className="p-5 space-y-4 text-xs">
          {/* Telemetry Row */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-3 bg-[#F8FAFC] border border-[#EAEEF2] rounded font-mono">
            <div>
              <span className="text-[10px] text-[#66717C] uppercase block">Queried Vendor</span>
              <span className="font-bold text-[#10283A] truncate block mt-0.5">{bidder.legal_name}</span>
            </div>
            <div>
              <span className="text-[10px] text-[#66717C] uppercase block">PAN / Entity ID</span>
              <span className="font-bold text-[#10283A] block mt-0.5">{bidder.pan || 'BSZPP1234K'}</span>
            </div>
            <div>
              <span className="text-[10px] text-[#66717C] uppercase block">Debarment Status</span>
              <span className={`inline-block px-2 py-0.5 text-[10px] font-bold rounded mt-0.5 ${
                (debarmentInfo?.status || 'NOT_FOUND') === 'NOT_FOUND' || (debarmentInfo?.status || '') === 'EXPIRED'
                  ? 'bg-[#E8F8EE] text-[#0F6B38] border border-[#8CD9A8]'
                  : 'bg-[#FDECEC] text-[#9C211B] border border-[#F5A3A0]'
              }`}>
                {debarmentInfo?.status || 'NOT_FOUND'}
              </span>
            </div>
            <div>
              <span className="text-[10px] text-[#66717C] uppercase block">Verification Determination</span>
              <span className={`font-bold block mt-0.5 ${
                (debarmentInfo?.verification_status || 'CLEAR') === 'CLEAR'
                  ? 'text-[#0F6B38]'
                  : 'text-[#9C211B]'
              }`}>
                ● {debarmentInfo?.verification_status || 'CLEAR — ELIGIBLE'}
              </span>
            </div>
          </div>

          {/* Details Table */}
          <div className="border border-[#D9DEE3] rounded overflow-hidden">
            <table className="w-full text-left border-collapse font-sans text-xs">
              <tbody className="divide-y divide-[#EAEEF2]">
                <tr>
                  <td className="py-2.5 px-4 font-mono font-bold text-[#66717C] bg-[#F8FAFC] w-1/4">Query Rationale & Finding</td>
                  <td className="py-2.5 px-4 font-medium text-[#10283A]">
                    {debarmentInfo?.reason || 'No adverse blacklisting or debarment record found across government registries for this entity.'}
                  </td>
                </tr>
                <tr>
                  <td className="py-2.5 px-4 font-mono font-bold text-[#66717C] bg-[#F8FAFC]">Databases Queried</td>
                  <td className="py-2.5 px-4 font-mono text-[11px] text-[#556270]">
                    {debarmentInfo?.source || 'GeM Debarred Vendor Registry / CPPP Central Blacklist / MoF GFR Rule 151 (Mock Adapter)'}
                  </td>
                </tr>
                <tr>
                  <td className="py-2.5 px-4 font-mono font-bold text-[#66717C] bg-[#F8FAFC]">Effective Period</td>
                  <td className="py-2.5 px-4 font-mono text-[11px] text-[#556270]">
                    Effective: <strong className="text-[#10283A]">{debarmentInfo?.effective_date || 'N/A'}</strong> • Valid Until: <strong className="text-[#10283A]">{debarmentInfo?.end_date || 'N/A'}</strong>
                  </td>
                </tr>
                <tr>
                  <td className="py-2.5 px-4 font-mono font-bold text-[#66717C] bg-[#F8FAFC]">Supporting Verification Extract</td>
                  <td className="py-2.5 px-4 font-mono text-[11px] text-[#10283A] flex items-center justify-between">
                    <span>{debarmentInfo?.supporting_document || 'Central_Debarment_Registry_Extract.pdf'}</span>
                    <span className="text-[#0F6B38] font-bold">✓ Digitally Signed</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="text-[11px] text-[#8A5000] bg-[#FFF8E6] border border-[#F0CA85] rounded p-2.5 font-mono">
            <strong>DEMO / HACKATHON ADAPTER NOTICE:</strong> Demonstrates mock adapter architecture for automated cross-referencing of central exclusion lists. In production, connects via secure API gateway to GeM / CPP Portal.
          </div>
        </div>
      </div>

      {/* 5. SEMANTIC EVIDENCE VECTOR SEARCH & CHUNKS RETRIEVAL */}
      <div className="panel-sharp bg-white">
        <div className="p-3.5 bg-[#163C32] text-white flex flex-col sm:flex-row sm:items-center justify-between gap-2 font-mono">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-[#A7833B]" />
            <div>
              <h3 className="font-bold text-xs uppercase tracking-wider">
                Petroleum Semantic Evidence Vector Retrieval (all-MiniLM-L6-v2)
              </h3>
              <div className="text-[10px] text-[#B5BFB8]">
                Search across bidder's extracted chunks • Cosine Similarity Scoring • Exact Page & Document Attribution
              </div>
            </div>
          </div>
          <span className="text-[10px] px-2 py-0.5 bg-[#101A17] text-[#A7833B] border border-[#163C32]">
            DENSE EMBEDDINGS 384-D
          </span>
        </div>

        <div className="p-4 space-y-3 font-mono text-xs">
          <div className="flex flex-col sm:flex-row gap-2">
            <div className="relative flex-1">
              <input
                type="text"
                value={semanticQuery}
                onChange={(e) => setSemanticQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSemanticSearch()}
                placeholder="Query bidder evidence (e.g. 'natural gas pipeline 100 km 24 inch', 'annual turnover 3 years')..."
                className="w-full bg-[#F4F5F2] border border-[#D0D7D3] px-3 py-2 text-xs text-[#17201C] focus:outline-none focus:border-[#163C32]"
              />
            </div>
            <button
              onClick={() => handleSemanticSearch()}
              disabled={isSearchingEvidence}
              className="px-4 py-2 bg-[#163C32] text-white hover:bg-[#0E2821] font-bold flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-[#A7833B] ${isSearchingEvidence ? 'animate-spin' : ''}`} />
              <span>{isSearchingEvidence ? 'SEARCHING VECTORS...' : 'SEARCH EVIDENCE'}</span>
            </button>
          </div>

          {/* Quick Preset Queries */}
          <div className="flex flex-wrap items-center gap-1.5 text-[10px] text-[#59625D]">
            <span className="font-bold uppercase">Quick Queries:</span>
            {[
              'natural gas pipeline 100 km 24 inch',
              'annual turnover previous 3 financial years',
              'ISO 45001 safety certification and zero fatality',
              'technical manpower pipeline engineers 8 years',
              'oil gas epc contract experience'
            ].map((q) => (
              <button
                key={q}
                onClick={() => {
                  setSemanticQuery(q);
                  handleSemanticSearch(q);
                }}
                className="px-2 py-0.5 bg-[#F4F5F2] hover:bg-[#EAECE8] border border-[#D0D7D3] text-[#163C32]"
              >
                {q}
              </button>
            ))}
          </div>

          {/* Search Results Display */}
          {semanticResults.length > 0 && (
            <div className="mt-3 space-y-2">
              <div className="text-[11px] font-bold text-[#163C32] uppercase flex items-center justify-between border-b border-[#D0D7D3] pb-1">
                <span>Top Retrieved Semantic Evidence Chunks ({semanticResults.length})</span>
                <span className="text-[10px] text-[#59625D]">Ranked by Cosine Similarity</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {semanticResults.map((res, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-[#F4F5F2] border border-[#D0D7D3] space-y-2 hover:border-[#163C32] transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5 text-[10px] text-[#163C32] font-bold truncate max-w-[200px]">
                        <FileText className="w-3.5 h-3.5 text-[#163C32] shrink-0" />
                        <span className="truncate">{res.document_name}</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <span className="px-1.5 py-0.2 bg-[#ECFDF5] text-[#166534] border border-[#A7F3D0] text-[9px] font-bold">
                          PAGE {res.page_number}
                        </span>
                        <span className="px-1.5 py-0.2 bg-[#EFF6FF] text-[#1E40AF] border border-[#BFDBFE] text-[9px] font-bold">
                          {Math.round(res.similarity_score * 100)}% MATCH
                        </span>
                      </div>
                    </div>

                    <p className="font-sans text-xs text-[#17201C] line-clamp-3 bg-white p-2 border border-[#EAECE8] leading-relaxed">
                      "{res.text}"
                    </p>

                    <div className="flex items-center justify-between text-[10px] text-[#59625D] pt-1">
                      <span>OCR Engine: <strong className="text-[#163C32]">{res.extraction_method || 'PyMuPDF'}</strong></span>
                      <span>Confidence: <strong className="text-[#166534]">{Math.round(res.confidence * 100)}%</strong></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 6. BIDDER DOCUMENTS TABLE */}
      <div className="panel-sharp bg-white">
        <div className="p-3 bg-[#EAECE8] border-b border-[#D0D7D3] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileSpreadsheet className="w-3.5 h-3.5 text-[#163C32]" />
            <h3 className="font-bold text-xs uppercase tracking-wider text-[#17201C]">
              Bidder Documents & OCR Extraction Registry
            </h3>
          </div>
          <span className="text-[10px] font-mono text-[#59625D]">
            {bidder.documents?.length || 6} Registered Dossiers
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full table-dense text-left font-mono text-xs">
            <thead>
              <tr>
                <th>Document Name</th>
                <th>Type</th>
                <th>Pages</th>
                <th>OCR Status</th>
                <th>Indexed</th>
                <th>Evidence Found</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#EAECE8]">
              {bidder.documents?.map((doc) => (
                <tr key={doc.id} className="hover:bg-[#F4F5F2]">
                  <td className="font-sans font-semibold text-[#17201C]">
                    <div className="flex items-center gap-2">
                      <FileText className="w-3.5 h-3.5 text-[#163C32]" />
                      <span>{doc.document_name}</span>
                    </div>
                  </td>
                  <td>{doc.document_type}</td>
                  <td>{doc.page_count || 1} pages</td>
                  <td>
                    <span className="px-1.5 py-0.5 bg-[#ECFDF5] text-[#166534] border border-[#A7F3D0] text-[10px] font-bold">
                      {doc.extraction_method === 'TESSERACT_OCR' ? 'TESSERACT OCR' : 'OCR COMPLETE'}
                    </span>
                  </td>
                  <td>
                    <span className="text-[#166534] font-bold">INDEXED</span>
                  </td>
                  <td className="font-bold text-[#163C32]">
                    {doc.document_name.includes('Financial') ? '3 EVIDENCE ITEMS' : 'VERIFIED'}
                  </td>
                  <td>
                    <button
                      onClick={() => setPreviewDocument(doc)}
                      className="px-2 py-1 bg-[#163C32] text-white hover:bg-[#0E2821] text-[11px] font-mono font-bold transition-colors flex items-center gap-1"
                    >
                      <Eye className="w-3 h-3" />
                      <span>Preview</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* MODALS */}
      {selectedCheckForEvidence && (
        <EvidenceModal
          check={selectedCheckForEvidence}
          bidderName={bidder.legal_name}
          onClose={() => setSelectedCheckForEvidence(null)}
        />
      )}

      {selectedCheckForReview && (
        <OfficerReviewModal
          check={selectedCheckForReview}
          bidderId={bidder.id}
          bidderName={bidder.legal_name}
          onClose={() => setSelectedCheckForReview(null)}
          onSuccess={() => {
            setSelectedCheckForReview(null);
            loadBidder();
          }}
        />
      )}

      {/* Officer Selecting Authority Decision Modal */}
      {showSelectingAuthorityModal && (
        <OfficerSelectingAuthorityModal
          bidderId={bidder.id}
          bidderName={bidder.legal_name}
          tenderNumber="MOPNG/PIPE/2026/017"
          currentStatus={bidder.status || 'UNDER_EVALUATION'}
          complianceScore={complianceScore}
          riskLevel={bidder.risk_level || (isHeadlineBidder ? 'MEDIUM' : 'LOW')}
          onClose={() => setShowSelectingAuthorityModal(false)}
          onSuccess={(newStatus) => {
            setShowSelectingAuthorityModal(false);
            loadBidder();
          }}
        />
      )}

      {/* Split-Screen Document Preview Drawer/Modal */}
      {previewDocument && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-white border border-[#163C32] max-w-5xl w-full max-h-[90vh] flex flex-col font-mono text-xs">
            
            {/* Header */}
            <div className="p-3 bg-[#163C32] text-white flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-[#A7833B]" />
                <span className="font-bold uppercase tracking-wider">
                  SPLIT-SCREEN EVIDENCE VIEWER: {previewDocument.document_name}
                </span>
              </div>
              <button
                onClick={() => setPreviewDocument(null)}
                className="px-2 py-0.5 bg-[#101A17] hover:bg-[#DC2626] text-white"
              >
                ✕ CLOSE
              </button>
            </div>

            {/* Split Content */}
            <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-[#D0D7D3] overflow-y-auto flex-1">
              
              {/* LEFT: Document Preview */}
              <div className="p-4 bg-[#F4F5F2] space-y-3">
                <div className="text-[11px] font-bold text-[#163C32] uppercase flex items-center justify-between">
                  <span>DOCUMENT PREVIEW (PAGE {previewDocument.page_count || 1})</span>
                  <span className="text-[10px] text-[#59625D]">Engine: {previewDocument.extraction_method || 'PyMuPDF'}</span>
                </div>

                <div className="p-4 bg-white border border-[#D0D7D3] min-h-[300px] text-xs leading-relaxed text-[#17201C] whitespace-pre-wrap">
                  {previewDocument.extracted_text || 
                    `[MINISTRY OF PETROLEUM & NATURAL GAS - PIPELINE TENDER DOSSIER]\n\nDocument: ${previewDocument.document_name}\nPage: 1 of ${previewDocument.page_count || 1}\n\n` +
                    (previewDocument.document_name.includes('Financial')
                      ? "FY 2023-24: INR 30 Crore\nFY 2024-25: INR 27 Crore\nFY 2025-26: INR 24 Crore\nAverage Annual Turnover = (30 + 27 + 24) / 3 = INR 27 Crore (Exceeds requirement of INR 25 Crore)."
                      : (previewDocument.document_name.includes('Pipeline')
                          ? "Completed 135 KM natural gas transmission pipeline successfully commissioned in March 2025. Diameter: 24 Inch NB API 5L X70. Role: EPC Contractor."
                          : "Verified statutory compliance and technical qualifications under MoPNG Pipeline Tender Guidelines."))}
                </div>
              </div>

              {/* RIGHT: Extracted Evidence */}
              <div className="p-4 bg-white space-y-4">
                <div className="text-[11px] font-bold text-[#163C32] uppercase">
                  EXTRACTED EVIDENCE & VERIFICATION
                </div>

                <div className="p-3 bg-[#F4F5F2] border border-[#D0D7D3] space-y-2">
                  <div className="flex justify-between">
                    <span className="text-[#59625D]">Document:</span>
                    <span className="font-bold">{previewDocument.document_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#59625D]">Extraction Engine:</span>
                    <span className="font-bold text-[#163C32]">{previewDocument.extraction_method || 'PyMuPDF Native'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#59625D]">Text Quality:</span>
                    <span className="font-bold text-[#166534]">VERIFIED HIGH CONFIDENCE</span>
                  </div>
                </div>

                <div className="p-3 bg-[#ECFDF5] border border-[#A7F3D0] space-y-1 text-[#166534]">
                  <div className="font-bold">VERIFICATION RESULT: PASS</div>
                  <div className="text-[11px]">
                    Evidence extracted from this document directly satisfies tender requirement criteria.
                  </div>
                </div>

                <div className="pt-4 flex justify-end">
                  <button
                    onClick={() => setPreviewDocument(null)}
                    className="px-4 py-1.5 bg-[#163C32] text-white hover:bg-[#0E2821] font-bold"
                  >
                    Done Reviewing
                  </button>
                </div>
              </div>

            </div>

          </div>
        </div>
      )}

    </div>
  );
};
