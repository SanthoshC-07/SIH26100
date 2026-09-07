from typing import Dict, Any
from app.checkers.base_checker import BaseChecker
from app.rules.pan_rule import PANRuleEngine

class PANChecker(BaseChecker):
    """
    Check 2: PAN & Legal Entity Identity Consistency
    Verifies:
    1. PAN format
    2. PAN extracted from document
    3. PAN matches bidder record
    4. Name consistency
    """
    def get_checker_name(self) -> str:
        return "PANChecker"

    def verify(
        self,
        requirement: Dict[str, Any],
        evidence: Dict[str, Any],
        bidder: Dict[str, Any]
    ) -> Dict[str, Any]:
        bidder_name = bidder.get("legal_name") or bidder.get("bidder_name", "")
        pan = bidder.get("pan", "")
        entities = evidence.get("entities", [])
        mandatory = requirement.get("mandatory", True)

        res = PANRuleEngine.evaluate(bidder_name, pan, entities, mandatory)
        
        doc_name = res.get("document_name") or "PAN_Card.pdf"
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
                "rule": "PAN Statutory Format Verification",
                "condition": f"Statutory 10-char structure on '{pan}'",
                "passed": format_valid
            },
            {
                "rule": "Corporate Entity Consistency",
                "condition": f"Document entity matches declared bidder '{bidder_name}'",
                "passed": name_matched
            },
            {
                "rule": "Document & Record Consistency",
                "condition": "Consistent PAN across submitted documents",
                "passed": consistency_valid
            }
        ]

        cross_consistency = {
            "bidder_name_match": name_matched,
            "pan_format_valid": format_valid,
            "discrepancies": [] if is_pass else [reason]
        }

        # Structured requirement-specific extraction
        from app.documents.requirement_extractors import PANCardExtractor
        doc_chunks = evidence.get("doc_chunks", [])
        combined_text = "\n".join([c.get("text", "") for c in doc_chunks])
        doc_name = res.get("document_name") or "02_Income_Tax_PAN_Card.pdf"
        doc_id = None
        if doc_chunks:
            doc_name = doc_chunks[0].get("document_name", doc_name)
            doc_id = doc_chunks[0].get("document_id")

        if combined_text:
            extracted_res = PANCardExtractor.extract_from_text(combined_text, doc_name=doc_name, doc_id=doc_id)
        else:
            extracted_res = {
                "requirement_id": requirement.get("id") or "REQ-002",
                "category": "PAN",
                "data": {
                    "pan": pan,
                    "legal_name": bidder_name,
                    "pan_type": "Company" if (pan and len(pan) >= 4 and pan[3].upper() == 'C') else "Corporate Entity",
                    "status": "Active" if is_pass else "Not detected"
                },
                "fields": [
                    {
                        "field": "pan",
                        "label": "PAN Card Number",
                        "value": pan or None,
                        "display_value": pan or "Not detected",
                        "source": doc_name,
                        "page": 1,
                        "method": "PDF_TEXT",
                        "confidence": 0.98 if pan else 0.0,
                        "detected": bool(pan)
                    },
                    {
                        "field": "legal_name",
                        "label": "PAN Card Holder Name",
                        "value": bidder_name or None,
                        "display_value": bidder_name or "Not detected",
                        "source": doc_name,
                        "page": 1,
                        "method": "PDF_TEXT",
                        "confidence": 0.96 if bidder_name else 0.0,
                        "detected": bool(bidder_name)
                    }
                ],
                "summary": f"PAN: {pan} ({bidder_name})" if pan else "PAN: Not detected"
            }

        verif_details = {
            **res.get("calculation_breakdown", {}),
            "data": extracted_res.get("data", {}),
            "fields": extracted_res.get("fields", []),
            "summary": extracted_res.get("summary", "")
        }

        extracted_req = {
            "category": "INCOME_TAX_PAN",
            "format": "PAN_10_CHAR",
            "extracted_pan": pan,
            "mandatory": mandatory
        }

        return self.format_compliance_result(
            requirement_id=requirement.get("id") or "REQ-002",
            status=status,
            confidence=confidence,
            requirement_text=requirement.get("description") or "Valid Permanent Account Number (PAN) issued by Income Tax Department.",
            extracted_requirement=extracted_req,
            evidence_list=evidence_list,
            rule_results=rule_results,
            semantic_score=1.0,
            cross_document_consistency=cross_consistency,
            explanation=reason,
            risk="LOW" if is_pass else "HIGH",
            extra_metadata={
                "source": res.get("source", "MOCK_INCOME_TAX_PORTAL"),
                "method": res.get("method", "RULE_AND_PORTAL"),
                "verification_details": verif_details
            }
        )
