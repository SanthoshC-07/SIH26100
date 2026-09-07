"""
Clause Segmentation Engine
Ministry of Petroleum & Natural Gas - Petroleum & Natural Gas Pipeline Procurement
"""
import re
from typing import List, Dict, Any
from app.nlp.text_normalizer import TextNormalizer

class ClauseSegmenter:
    """
    Segments tender documents into individual clauses, sub-clauses,
    and eligibility criteria with page numbers and normalized text.
    """

    # Clause heading patterns
    CLAUSE_PATTERN = re.compile(
        r"(?:^|\n)(?P<heading>(?:Clause|Section|Cl\.?|Item|Article)?\s*(?:\d+(?:\.\d+)*|[A-Z]\.|\([a-z0-9]+\))\s*[:\.\-]?\s+)",
        re.IGNORECASE
    )

    BULLET_PATTERN = re.compile(
        r"(?:^|\n)(?P<bullet>(?:[-*•–—]|\([iIvVxX0-9a-zA-Z]+\)|[a-z]\))\s+)"
    )

    @classmethod
    def segment_text_into_clauses(cls, full_text: str, page_map: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Segments raw or page-mapped text into structured clause objects.
        """
        clauses = []
        
        # If page_map is provided (from DocumentExtractor), parse page by page
        if page_map:
            clause_global_idx = 1
            for p in page_map:
                p_num = p.get("page_number", 1)
                p_text = p.get("text", "")
                page_clauses = cls._segment_single_block(p_text, p_num, clause_global_idx)
                for c in page_clauses:
                    clauses.append(c)
                    clause_global_idx += 1
            if clauses:
                return clauses

        # Fallback to whole text segmentation
        return cls._segment_single_block(full_text, 1, 1)

    @classmethod
    def _segment_single_block(cls, text: str, page_number: int, start_idx: int) -> List[Dict[str, Any]]:
        """
        Segments a continuous text block into discrete clauses.
        """
        if not text or not text.strip():
            return []

        lines = [l.strip() for l in text.split("\n") if l.strip()]
        paragraphs = []
        curr_lines = []
        curr_clause_label = None

        for line in lines:
            # Check for clause header start
            m_clause = re.match(r"^(?:(?:Clause|Section|Cl\.?|Item)\s+)?([0-9]+(?:\.[0-9]+)*|[A-Z]\.|\([a-zA-Z0-9]+\))(?:\s*[:\.\-]\s*|\s+)", line, re.IGNORECASE)
            m_bullet = re.match(r"^(?:[-*•–—]|\([iIvVxX0-9a-zA-Z]+\)|[a-z]\))\s+", line)

            if m_clause or m_bullet:
                if curr_lines:
                    paragraphs.append({
                        "label": curr_clause_label,
                        "text": " ".join(curr_lines)
                    })
                    curr_lines = []
                curr_clause_label = m_clause.group(1) if m_clause else None

            curr_lines.append(line)

        if curr_lines:
            paragraphs.append({
                "label": curr_clause_label,
                "text": " ".join(curr_lines)
            })

        results = []
        idx = start_idx
        for p in paragraphs:
            raw_c_text = p["text"].strip()
            if len(raw_c_text) < 15:  # Skip tiny fragments
                continue

            normalized_c_text = TextNormalizer.normalize_text(raw_c_text)
            clause_num = p["label"] or f"Cl-{idx}"
            if not clause_num.startswith("Cl-") and not re.match(r"^\d", clause_num):
                clause_num = f"Cl-{idx} ({clause_num})"

            results.append({
                "clause_number": clause_num,
                "page_number": page_number,
                "original_text": raw_c_text,
                "normalized_text": normalized_c_text
            })
            idx += 1

        return results
