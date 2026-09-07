"""
SIH26100 — Tender PDF to Requirement Dataset Pipeline
------------------------------------------------------
Automated, auditable pipeline that ingests tender PDFs (IOCL, MoPNG, ONGC, etc.),
extracts text via PyMuPDF/Tesseract, segments into clauses, identifies bidder requirements,
classifies into the 10 locked taxonomy classes, tags domain relevance, extracts structured
numerical/entity constraints, deduplicates, and outputs:
  1. ml/datasets/requirement_dataset.csv (reviewable requirement dataset, review_status=PENDING)
  2. ml/datasets/requirement_review.csv  (human verification queue with review reasons)

Authoritative Path:
    ml/scripts/tender_pdf_pipeline.py
"""
import os
import sys
import csv
import json
import re
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Set

# Ensure project root is on sys.path
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ML_DIR = os.path.dirname(_THIS_DIR)
PROJECT_ROOT = os.path.dirname(_ML_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if os.path.join(PROJECT_ROOT, "backend") not in sys.path:
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))

from backend.app.documents.extractor import DocumentExtractor
from backend.app.nlp.text_normalizer import TextNormalizer
from backend.app.nlp.clause_segmenter import ClauseSegmenter
from backend.app.nlp.requirement_detector import RequirementDetector
from ml.scripts.requirement_classifier import requirement_classifier, REQUIREMENT_CLASSES
from ml.services.requirement_extractor import unified_requirement_extractor
from ml.services.requirement_regex import regex_requirement_extractor

# Default paths
DATASETS_DIR = os.path.join(_ML_DIR, "datasets")
REQUIREMENT_DATASET_CSV = os.path.join(DATASETS_DIR, "requirement_dataset.csv")
REQUIREMENT_REVIEW_CSV = os.path.join(DATASETS_DIR, "requirement_review.csv")
PETROLEUM_TERMS_JSON = os.path.join(DATASETS_DIR, "petroleum_terms.json")

# Standard CSV Columns as required by Phase 3A specifications
DATASET_COLUMNS = [
    "requirement_id",
    "source_document",
    "page_number",
    "original_text",
    "normalized_text",
    "category",
    "domain_relevance",
    "minimum_value",
    "maximum_value",
    "unit",
    "currency",
    "percentage",
    "count",
    "length_km",
    "diameter_inch",
    "experience_years",
    "time_period_years",
    "date",
    "project_type",
    "sector",
    "role",
    "qualification",
    "scope",
    "entities",
    "extraction_method",
    "classification_confidence",
    "review_status"
]

REVIEW_COLUMNS = [
    "requirement_id",
    "source_document",
    "page_number",
    "original_text",
    "predicted_category",
    "classification_confidence",
    "extraction_method",
    "review_reason"
]

# Petroleum Pipeline domain keywords & regexes
PETROLEUM_PIPELINE_KEYWORDS = [
    "pipeline", "cross-country pipeline", "cross country pipeline", "transmission pipeline",
    "gas pipeline", "oil pipeline", "pipeline construction", "pipeline laying", "epc",
    "api 5l", "api 6d", "api 1104", "asme b31.8", "asme b31.4", "oisd-141", "oisd 141",
    "welding engineer", "lead pipeline engineer", "pipeline engineer", "hydrotesting",
    "golden tie-in", "cased crossing", "sv station", "pigging station", "metering station",
    "line pipe", "ball valve", "plug valve", "3lpe", "cathodic protection", "hdd"
]

OIL_GAS_KEYWORDS = [
    "natural gas", "petroleum", "crude oil", "lpg", "lng", "hydrocarbon", "hydrocarbons",
    "refinery", "terminal", "petroleum products", "oil and gas", "oil & gas", "cgd",
    "city gas distribution", "png", "cng", "petrochemical", "upstream", "midstream", "downstream"
]

NON_REQUIREMENT_PATTERNS = [
    r"^table of contents",
    r"^contents\b",
    r"^page\s+\d+\s+of\s+\d+",
    r"^tender no\.?:\s*$",
    r"^signature of bidder",
    r"^authorized signatory",
    r"^date:\s*place:\s*$",
    r"^annexure\s+[a-z0-9]+\s*$",
    r"^section\s+[0-9ivx]+\s*$",
    r"^bidding document for\s*$"
]


class TenderPDFRequirementPipeline:
    """
    Automated pipeline that converts tender PDFs into structured, reviewable requirements.
    """

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or DATASETS_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        self.classifier = requirement_classifier
        self.extractor = unified_requirement_extractor
        self._load_petroleum_terms()

    def _load_petroleum_terms(self):
        self.petroleum_terms = {}
        if os.path.exists(PETROLEUM_TERMS_JSON):
            try:
                with open(PETROLEUM_TERMS_JSON, "r", encoding="utf-8") as f:
                    self.petroleum_terms = json.load(f)
            except Exception:
                pass

    def evaluate_domain_relevance(self, text: str, category: str) -> Tuple[str, float]:
        """
        Determines domain relevance:
        - PETROLEUM_PIPELINE
        - OIL_GAS
        - GENERAL_GOVERNMENT_PROCUREMENT
        - NOT_RELEVANT
        - REVIEW
        """
        lower = text.lower()

        # Check for petroleum pipeline specifics first
        pipeline_hits = sum(1 for kw in PETROLEUM_PIPELINE_KEYWORDS if kw in lower)
        oil_gas_hits = sum(1 for kw in OIL_GAS_KEYWORDS if kw in lower)

        if pipeline_hits >= 1:
            return "PETROLEUM_PIPELINE", 0.95
        
        if oil_gas_hits >= 1:
            return "OIL_GAS", 0.90

        # Statutory / GFR requirements common to general government procurement
        if category in [
            "GST_TAX_COMPLIANCE", "MSME_UDYAM_ELIGIBILITY", "BLACKLISTING_DEBARMENT"
        ]:
            return "GENERAL_GOVERNMENT_PROCUREMENT", 0.90

        if category == "FINANCIAL_ELIGIBILITY":
            if oil_gas_hits > 0 or pipeline_hits > 0:
                return "OIL_GAS", 0.85
            return "GENERAL_GOVERNMENT_PROCUREMENT", 0.80

        if category == "MAKE_IN_INDIA_LOCAL_CONTENT":
            return "GENERAL_GOVERNMENT_PROCUREMENT", 0.85

        if category in ["TECHNICAL_SPECIFICATION", "INDUSTRY_STANDARD_COMPLIANCE", "SAFETY_REGULATORY_COMPLIANCE"]:
            if any(std in lower for std in ["iso 45001", "iso 14001", "iso 9001", "hse", "safety"]):
                return "OIL_GAS", 0.80
            return "REVIEW", 0.60

        return "GENERAL_GOVERNMENT_PROCUREMENT", 0.70

    def is_boilerplate_or_non_requirement(self, text: str) -> bool:
        """Filters out non-actionable headers, footers, TOC, and signature blocks."""
        cleaned = text.strip()
        if len(cleaned) < 25:
            return True

        lower = cleaned.lower()
        for pat in NON_REQUIREMENT_PATTERNS:
            if re.search(pat, lower):
                return True

        # Pure address or contact info check
        if lower.startswith("address:") or lower.startswith("email:") or lower.startswith("tel:") or lower.startswith("pin code"):
            return True

        # If it's only a title with no modal verb or requirement keyword
        has_requirement_signal = any(
            sig in lower for sig in [
                "shall", "must", "required", "minimum", "at least", "eligible", "eligibility",
                "should have", "submit", "submission", "possess", "completed", "executed",
                "valid", "not less than", "turnover", "crore", "lakh", "experience", "gst", "pan",
                "udyam", "msme", "blacklist", "affidavit", "oem", "local content", "api", "asme",
                "oisd", "iso", "diameter", "km", "engineers", "certificate"
            ]
        )
        if not has_requirement_signal:
            return True

        return False

    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extracts and structures requirements from a single PDF document.
        """
        filename = os.path.basename(pdf_path)
        if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) < 100:
            return {
                "filename": filename,
                "page_count": 0,
                "pymupdf_pages": 0,
                "tesseract_pages": 0,
                "raw_clause_count": 0,
                "candidate_requirements": []
            }

        doc_res = DocumentExtractor.extract_document(pdf_path)
        page_count = doc_res.get("page_count", 0)
        pages = doc_res.get("pages", [])
        extracted_clauses = []
        raw_clause_count = 0
        pymupdf_pages = 0
        tesseract_pages = 0

        for p in pages:
            p_num = p.get("page_number", 1)
            p_text = p.get("text", "").strip()
            p_method = p.get("extraction_method", "PDF_TEXT")
            p_ocr = p.get("ocr_applied", False)

            if p_ocr or p_method == "TESSERACT_OCR":
                tesseract_pages += 1
            else:
                pymupdf_pages += 1

            if not p_text:
                continue

            # Segment page into candidate clauses
            segmented = ClauseSegmenter._segment_single_block(p_text, p_num, start_idx=len(extracted_clauses) + 1)
            raw_clause_count += len(segmented)

            for item in segmented:
                clause_text = item.get("original_text", "").strip()
                if self.is_boilerplate_or_non_requirement(clause_text):
                    continue

                # Requirement Detection Check
                clause_type, det_conf = RequirementDetector.detect_clause_type(clause_text)
                if clause_type in ["OTHER", "INFORMATIONAL"] and det_conf < 0.65:
                    continue

                extracted_clauses.append({
                    "source_document": filename,
                    "page_number": p_num,
                    "original_text": clause_text,
                    "normalized_text": item.get("normalized_text", TextNormalizer.normalize_text(clause_text)),
                    "pdf_extraction_method": p_method,
                    "pdf_confidence": p.get("confidence", 0.95),
                    "detector_type": clause_type,
                    "detector_confidence": det_conf
                })

        return {
            "filename": filename,
            "page_count": page_count,
            "pymupdf_pages": pymupdf_pages,
            "tesseract_pages": tesseract_pages,
            "raw_clause_count": raw_clause_count,
            "candidate_requirements": extracted_clauses
        }

    def process_directory(
        self,
        input_dirs: Any,
        preserve_existing: bool = True
    ) -> Dict[str, Any]:
        """
        Scans directories of PDF documents, deduplicates, and produces full dataset & review queue.
        """
        if isinstance(input_dirs, str):
            input_dirs = [input_dirs]

        pdf_files = []
        for d in input_dirs:
            if os.path.exists(d):
                for f in os.listdir(d):
                    if f.lower().endswith(".pdf"):
                        full_p = os.path.join(d, f)
                        if os.path.getsize(full_p) >= 100:
                            pdf_files.append(full_p)

        # Unique pdf paths
        pdf_files = sorted(list(set(pdf_files)))

        stats = {
            "total_pdfs_scanned": len(pdf_files),
            "total_pages_processed": 0,
            "pages_using_pymupdf": 0,
            "pages_requiring_tesseract": 0,
            "total_clauses_extracted": 0,
            "relevant_requirements": 0,
            "petroleum_relevant_requirements": 0,
            "oil_gas_requirements": 0,
            "general_procurement_requirements": 0,
            "review_requirements": 0,
            "duplicate_clauses_detected": 0,
            "requirements_with_numeric_thresholds": 0,
            "requirements_with_entities": 0,
            "category_distribution": {cat: 0 for cat in REQUIREMENT_CLASSES}
        }

        all_records: List[Dict[str, Any]] = []
        review_records: List[Dict[str, Any]] = []

        # Deduplication tracking: (source_doc, page_num, norm_text_hash)
        exact_provenance_seen: Set[str] = set()
        text_hash_seen: Dict[str, str] = {}  # text_hash -> req_id
        req_counter = 1

        # Load existing valid records if preserve_existing is requested
        if preserve_existing and os.path.exists(REQUIREMENT_DATASET_CSV):
            try:
                with open(REQUIREMENT_DATASET_CSV, "r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        src_doc = row.get("source_document", "")
                        p_num = str(row.get("page_number", "1"))
                        norm_t = row.get("normalized_text", "")
                        if not norm_t:
                            continue

                        prov_key = f"{src_doc}:::p{p_num}:::{norm_t}"
                        exact_provenance_seen.add(prov_key)
                        t_hash = hashlib.sha256(norm_t.lower().encode("utf-8")).hexdigest()
                        text_hash_seen[t_hash] = row.get("requirement_id", f"REQ-PDF-{req_counter:04d}")

                        all_records.append(dict(row))
                        req_counter += 1
            except Exception as e:
                print(f"[Warning] Could not preload existing records: {e}")

        # Process all discovered PDF files
        for pdf_path in pdf_files:
            try:
                pdf_res = self.process_pdf(pdf_path)
                stats["total_pages_processed"] += pdf_res["page_count"]
                stats["pages_using_pymupdf"] += pdf_res["pymupdf_pages"]
                stats["pages_requiring_tesseract"] += pdf_res["tesseract_pages"]
                stats["total_clauses_extracted"] += pdf_res["raw_clause_count"]

                for item in pdf_res["candidate_requirements"]:
                    raw_text = item["original_text"]
                    norm_text = item["normalized_text"]
                    page_num = item["page_number"]
                    src_doc = item["source_document"]

                    prov_key = f"{src_doc}:::p{page_num}:::{norm_text}"
                    if prov_key in exact_provenance_seen:
                        # Exact duplicate record from exact same page & document
                        stats["duplicate_clauses_detected"] += 1
                        continue

                    exact_provenance_seen.add(prov_key)

                    # Text hash near-duplicate / duplicate across pages
                    text_hash = hashlib.sha256(norm_text.lower().encode("utf-8")).hexdigest()
                    is_near_duplicate = False
                    if text_hash in text_hash_seen:
                        stats["duplicate_clauses_detected"] += 1
                        is_near_duplicate = True
                    else:
                        text_hash_seen[text_hash] = f"REQ-PDF-{req_counter:04d}"

                    req_id = f"REQ-PDF-{req_counter:04d}"

                    # 1. Taxonomy classification
                    clf_res = self.classifier.classify(raw_text)
                    pred_category = clf_res.get("predicted_class", "TECHNICAL_SPECIFICATION")
                    clf_conf = clf_res.get("confidence", 0.75)

                    # 2. Domain Relevance Assessment
                    domain_rel, rel_conf = self.evaluate_domain_relevance(raw_text, pred_category)

                    # 3. Structured Extraction (LLM + Regex Fallback)
                    struct_res = self.extractor.extract(raw_text)
                    ext_method = struct_res.get("extraction_method", item["pdf_extraction_method"])

                    # 4. Review Reasons
                    review_reasons = []
                    if clf_conf < 0.60:
                        review_reasons.append("LOW_CLASSIFICATION_CONFIDENCE")
                    if ext_method in ["REGEX_FALLBACK", "LLM_WITH_REGEX_FALLBACK"]:
                        review_reasons.append("REGEX_FALLBACK_USED")
                    if domain_rel == "REVIEW":
                        review_reasons.append("DOMAIN_RELEVANCE_UNCLEAR")
                    if is_near_duplicate:
                        review_reasons.append("POSSIBLE_DUPLICATE")
                    if pred_category == "FINANCIAL_ELIGIBILITY" and not struct_res.get("minimum_value") and not struct_res.get("threshold"):
                        review_reasons.append("MISSING_CRITICAL_VALUE")
                    if pred_category == "EXPERIENCE_ELIGIBILITY" and not struct_res.get("experience_years") and not struct_res.get("length_km"):
                        review_reasons.append("MISSING_CRITICAL_VALUE")

                    needs_review = len(review_reasons) > 0
                    if needs_review:
                        review_records.append({
                            "requirement_id": req_id,
                            "source_document": src_doc,
                            "page_number": page_num,
                            "original_text": raw_text,
                            "predicted_category": pred_category,
                            "classification_confidence": round(clf_conf, 3),
                            "extraction_method": ext_method,
                            "review_reason": "; ".join(review_reasons)
                        })

                    # Canonical dataset row
                    dataset_row = {
                        "requirement_id": req_id,
                        "source_document": src_doc,
                        "page_number": page_num,
                        "original_text": raw_text,
                        "normalized_text": norm_text,
                        "category": pred_category,
                        "domain_relevance": domain_rel,
                        "minimum_value": struct_res.get("minimum_value"),
                        "maximum_value": struct_res.get("maximum_value"),
                        "unit": struct_res.get("unit"),
                        "currency": struct_res.get("currency"),
                        "percentage": struct_res.get("percentage"),
                        "count": struct_res.get("count") or struct_res.get("required_count"),
                        "length_km": struct_res.get("length_km"),
                        "diameter_inch": struct_res.get("diameter_inch"),
                        "experience_years": struct_res.get("experience_years"),
                        "time_period_years": struct_res.get("time_period_years"),
                        "date": struct_res.get("date"),
                        "project_type": struct_res.get("project_type"),
                        "sector": struct_res.get("sector"),
                        "role": struct_res.get("role"),
                        "qualification": struct_res.get("qualification"),
                        "scope": struct_res.get("scope"),
                        "entities": json.dumps(struct_res.get("entities", [])),
                        "extraction_method": ext_method,
                        "classification_confidence": round(clf_conf, 3),
                        "review_status": "PENDING"
                    }

                    all_records.append(dataset_row)
                    req_counter += 1

            except Exception as e:
                print(f"[Pipeline Warning] Error processing {pdf_path}: {e}")

        # Recalculate full summary stats across final records
        for r in all_records:
            stats["relevant_requirements"] += 1
            dom = r.get("domain_relevance", "")
            if dom == "PETROLEUM_PIPELINE":
                stats["petroleum_relevant_requirements"] += 1
            elif dom == "OIL_GAS":
                stats["oil_gas_requirements"] += 1
            elif dom == "GENERAL_GOVERNMENT_PROCUREMENT":
                stats["general_procurement_requirements"] += 1
            else:
                stats["review_requirements"] += 1

            cat = r.get("category", "TECHNICAL_SPECIFICATION")
            if cat in stats["category_distribution"]:
                stats["category_distribution"][cat] += 1

            # Check numeric thresholds
            has_numeric = bool(
                r.get("minimum_value") not in [None, "", "null"] or
                r.get("maximum_value") not in [None, "", "null"] or
                r.get("length_km") not in [None, "", "null"] or
                r.get("diameter_inch") not in [None, "", "null"] or
                r.get("experience_years") not in [None, "", "null"] or
                r.get("time_period_years") not in [None, "", "null"] or
                r.get("percentage") not in [None, "", "null"] or
                r.get("count") not in [None, "", "null"]
            )
            if has_numeric:
                stats["requirements_with_numeric_thresholds"] += 1

            # Check entities
            ents_raw = r.get("entities", "[]")
            try:
                ents_list = json.loads(ents_raw) if isinstance(ents_raw, str) else ents_raw
            except Exception:
                ents_list = []
            if len(ents_list) > 0 or dom in ["PETROLEUM_PIPELINE", "OIL_GAS"]:
                stats["requirements_with_entities"] += 1

        # Save to CSV files
        self.save_dataset_csv(all_records)
        self.save_review_csv(review_records)

        return {
            "stats": stats,
            "dataset_rows": all_records,
            "review_rows": review_records,
            "dataset_file": REQUIREMENT_DATASET_CSV,
            "review_file": REQUIREMENT_REVIEW_CSV
        }

    def save_dataset_csv(self, records: List[Dict[str, Any]], target_path: Optional[str] = None):
        """Saves records to ml/datasets/requirement_dataset.csv with exact standard headers."""
        path = target_path or REQUIREMENT_DATASET_CSV
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=DATASET_COLUMNS)
            writer.writeheader()
            for r in records:
                row = {k: r.get(k, None) for k in DATASET_COLUMNS}
                writer.writerow(row)

    def save_review_csv(self, records: List[Dict[str, Any]], target_path: Optional[str] = None):
        """Saves review items to ml/datasets/requirement_review.csv."""
        path = target_path or REQUIREMENT_REVIEW_CSV
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=REVIEW_COLUMNS)
            writer.writeheader()
            for r in records:
                row = {k: r.get(k, None) for k in REVIEW_COLUMNS}
                writer.writerow(row)


def run_pipeline(input_dirs: Optional[List[str]] = None) -> Dict[str, Any]:
    """CLI & programmatic entry point for Tender PDF Requirement Pipeline."""
    target_dirs = input_dirs or [
        os.path.join(PROJECT_ROOT, "data", "tenders"),
        os.path.join(PROJECT_ROOT, "backend", "uploads")
    ]

    pipeline = TenderPDFRequirementPipeline()
    print("=" * 70)
    print("SIH26100 — PHASE 3A: TENDER PDF -> REQUIREMENT DATASET PIPELINE")
    print("=" * 70)
    print(f"Input Directories: {target_dirs}")
    print(f"Output Dataset   : {REQUIREMENT_DATASET_CSV}")
    print(f"Output Review    : {REQUIREMENT_REVIEW_CSV}")

    result = pipeline.process_directory(target_dirs, preserve_existing=True)
    stats = result["stats"]

    print("\n--- Pipeline Execution Summary ---")
    print(f"1. Total PDFs Scanned                   : {stats['total_pdfs_scanned']}")
    print(f"2. Total Pages Processed                : {stats['total_pages_processed']}")
    print(f"3. Total Candidate Clauses Extracted    : {stats['total_clauses_extracted']}")
    print(f"4. Useful Requirements Identified       : {stats['relevant_requirements']}")
    print(f"5. PETROLEUM_PIPELINE Requirements      : {stats['petroleum_relevant_requirements']}")
    print(f"6. OIL_GAS Requirements                 : {stats['oil_gas_requirements']}")
    print(f"7. GENERAL_GOVERNMENT_PROCUREMENT Reqs  : {stats['general_procurement_requirements']}")
    print(f"8. REVIEW Requirements                  : {stats['review_requirements']}")
    print(f"9. Duplicate/Near-Duplicate Clauses     : {stats['duplicate_clauses_detected']}")
    print(f"11. Requirements with Numeric Thresholds: {stats['requirements_with_numeric_thresholds']}")
    print(f"12. Requirements with Petroleum Entities: {stats['requirements_with_entities']}")

    print("\n10. Count for each of the 10 Requirement Classes:")
    for cat, count in stats["category_distribution"].items():
        print(f"    {cat:<34} : {count}")

    print("\n" + "=" * 70)
    print("PIPELINE EXECUTION COMPLETE")
    print("=" * 70)

    return result


if __name__ == "__main__":
    dirs = [sys.argv[1]] if len(sys.argv) > 1 else None
    run_pipeline(dirs)
