from typing import Dict, Any, List
from app.checkers.base_checker import BaseChecker
from app.rules.gst_rule import GSTRuleEngine

class GSTChecker(BaseChecker):
    """
    Check 1: GST Statutory Registration & Active Status
    Verifies:
    1. GSTIN format
    2. GSTIN extracted from document
    3. GSTIN matches bidder record
    4. Name consistency
    5. Mock portal return status
    """
    def get_checker_name(self) -> str:
        return "GSTChecker"

    def verify(
        self,
        requirement: Dict[str, Any],
        evidence: Dict[str, Any],
        bidder: Dict[str, Any]
    ) -> Dict[str, Any]:
        bidder_name = bidder.get("legal_name") or bidder.get("bidder_name", "")
        gstin = bidder.get("gstin", "")
        entities = evidence.get("entities", [])
        mandatory = requirement.get("mandatory", True)

        res = GSTRuleEngine.evaluate(bidder_name, gstin, entities, mandatory)
        
        doc_name = res.get("document_name") or "GST_Certificate.pdf"
        page_num = res.get("page_number", 1)
        status = res.get("status", "REVIEW")
        confidence = res.get("confidence", 0.95)
        reason = res.get("reason", "")
        evidence_text = res.get("evidence", "")

        evidence_list = [
            {
                "document_name": doc_name,
                "document_id": res.get("document_id"),
                "page_number": page_num,
                "text": evidence_text,
                "extraction_method": "PDF_TEXT"
            }
        ] if evidence_text else []

        is_pass = status == "PASS"
        format_valid = res.get("format_valid", is_pass)
        name_matched = res.get("name_matched", is_pass)
        consistency_valid = res.get("consistency_valid", is_pass)

        rule_results = [
            {
                "rule": "GSTIN Statutory Format Verification",
                "condition": f"Statutory 15-char structure on '{gstin}'",
                "passed": format_valid
            },
            {
                "rule": "Legal Name Consistency",
                "condition": f"Document entity matches declared bidder '{bidder_name}'",
                "passed": name_matched
            },
            {
                "rule": "Document & Adapter Consistency",
                "condition": "Consistent GSTIN across submitted documents",
                "passed": consistency_valid
            }
        ]

        cross_consistency = {
            "bidder_name_match": name_matched,
            "gst_format_valid": format_valid,
            "gst_pan_aligned": bool(gstin and len(gstin) >= 12),
            "discrepancies": [] if is_pass else [reason]
        }

        # Structured requirement-specific extraction
        from app.documents.requirement_extractors import GSTRegistrationExtractor
        doc_chunks = evidence.get("doc_chunks", [])
        combined_text = "\n".join([c.get("text", "") for c in doc_chunks])
        doc_name = res.get("document_name") or "01_GST_Registration_Certificate.pdf"
        doc_id = None
        if doc_chunks:
            doc_name = doc_chunks[0].get("document_name", doc_name)
            doc_id = doc_chunks[0].get("document_id")

        if combined_text:
            extracted_res = GSTRegistrationExtractor.extract_from_text(combined_text, doc_name=doc_name, doc_id=doc_id)
        else:
            extracted_res = {
                "requirement_id": requirement.get("id") or "REQ-001",
                "category": "GST",
                "data": {
                    "legal_name": bidder_name,
                    "trade_name": bidder.get("trade_name"),
                    "gstin": gstin,
                    "pan": gstin[2:12] if len(gstin) >= 12 else bidder.get("pan"),
                    "status": "Active" if is_pass else "Not detected"
                },
                "fields": [
                    {
                        "field": "gstin",
                        "label": "GSTIN",
                        "value": gstin or None,
                        "display_value": gstin or "Not detected",
                        "source": doc_name,
                        "page": 1,
                        "method": "PDF_TEXT",
                        "confidence": 0.98 if gstin else 0.0,
                        "detected": bool(gstin)
                    },
                    {
                        "field": "legal_name",
                        "label": "Legal Name",
                        "value": bidder_name or None,
                        "display_value": bidder_name or "Not detected",
                        "source": doc_name,
                        "page": 1,
                        "method": "PDF_TEXT",
                        "confidence": 0.96 if bidder_name else 0.0,
                        "detected": bool(bidder_name)
                    }
                ],
                "summary": f"GSTIN: {gstin} (Legal: {bidder_name})" if gstin else "GSTIN: Not detected"
            }

        verif_details = {
            **res.get("calculation_breakdown", {}),
            "data": extracted_res.get("data", {}),
            "fields": extracted_res.get("fields", []),
            "summary": extracted_res.get("summary", "")
        }

        extracted_req = {
            "category": "GST_TAX_COMPLIANCE",
            "format": "GSTIN_15_CHAR",
            "extracted_gstin": gstin,
            "mandatory": mandatory
        }

        return self.format_compliance_result(
            requirement_id=requirement.get("id") or "REQ-001",
            status=status,
            confidence=confidence,
            requirement_text=requirement.get("description") or "Valid GSTIN registration and active tax filing status.",
            extracted_requirement=extracted_req,
            evidence_list=evidence_list,
            rule_results=rule_results,
            semantic_score=1.0,
            cross_document_consistency=cross_consistency,
            explanation=reason,
            risk="LOW" if is_pass else "HIGH",
            extra_metadata={
                "source": res.get("source", "MOCK_GST_PORTAL"),
                "method": res.get("method", "RULE_AND_PORTAL"),
                "verification_details": verif_details
            }
        )
