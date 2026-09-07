from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.core.domain_vocabulary import ComplianceResultStatus

class BaseChecker(ABC):
    """
    Abstract contract for all modular compliance checkers in the Petroleum & Natural Gas domain.
    
    Phase 4 Standardized Interface:
    verify(requirement, evidence, bidder) -> {
        "requirement_id": "",
        "status": "PASS | FAIL | REVIEW | INSUFFICIENT | NOT_APPLICABLE",
        "confidence": 0.0,
        "requirement": "",
        "extracted_requirement": {},
        "evidence": [],
        "rule_results": [],
        "semantic_score": null,
        "cross_document_consistency": null,
        "explanation": "",
        "risk": "LOW | MEDIUM | HIGH | CRITICAL"
    }
    """

    @abstractmethod
    def get_checker_name(self) -> str:
        """Returns unique identifier name for the checker."""
        pass

    @abstractmethod
    def verify(
        self,
        requirement: Dict[str, Any],
        evidence: Dict[str, Any],
        bidder: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes domain verification logic.
        Args:
            requirement: Structured requirement dictionary (threshold, category, mandatory, etc.)
            evidence: Extracted evidence context (entities, document chunks, raw text, citations)
            bidder: Bidder entity dictionary (legal_name, pan, gstin, projects, personnel)
        Returns:
            Structured verification result payload.
        """
        pass

    @classmethod
    def format_compliance_result(
        cls,
        requirement_id: str,
        status: str,
        confidence: float,
        requirement_text: str,
        extracted_requirement: Dict[str, Any],
        evidence_list: List[Dict[str, Any]],
        rule_results: List[Dict[str, Any]],
        semantic_score: Optional[float],
        cross_document_consistency: Optional[Dict[str, Any]],
        explanation: str,
        risk: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Helper to guarantee consistent Phase 4 result structure across all checkers."""
        if not risk:
            if status == "FAIL":
                risk = "HIGH" if extracted_requirement.get("mandatory", True) else "MEDIUM"
            elif status in ["REVIEW", "INSUFFICIENT"]:
                risk = "MEDIUM"
            else:
                risk = "LOW"

        # Backwards compatible first-evidence values
        first_ev = evidence_list[0] if evidence_list else {}
        doc_name = first_ev.get("document_name") or "Evidence_Document.pdf"
        page_num = first_ev.get("page_number", 1)
        source_txt = first_ev.get("text") or first_ev.get("source_text") or explanation

        payload = {
            "requirement_id": requirement_id or "",
            "status": status,
            "confidence": round(confidence, 2),
            "requirement": requirement_text or "",
            "extracted_requirement": extracted_requirement or {},
            "evidence": evidence_list,
            "rule_results": rule_results,
            "semantic_score": round(semantic_score, 2) if semantic_score is not None else None,
            "cross_document_consistency": cross_document_consistency,
            "explanation": explanation,
            "risk": risk,

            # Backwards compatibility fields for existing UI/API consumers
            "source_document": doc_name,
            "document_name": doc_name,
            "document_id": first_ev.get("document_id"),
            "page_number": page_num,
            "source_text": source_txt,
            "extracted_entities": first_ev.get("extracted_entities") or extracted_requirement,
            "rule_result": rule_results[0] if rule_results and len(rule_results) == 1 else rule_results,
            "reason": explanation,
            "source": extra_metadata.get("source", "COMPLIANCE_ENGINE") if extra_metadata else "COMPLIANCE_ENGINE",
            "method": extra_metadata.get("method", "HYBRID_RULE_AND_NLP") if extra_metadata else "HYBRID_RULE_AND_NLP",
            "verification_details": extra_metadata.get("verification_details", {}) if extra_metadata else {}
        }
        return payload
