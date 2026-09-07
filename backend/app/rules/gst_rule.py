from typing import Dict, Any, List
import re
from app.government_adapters import adapters
from app.documents.entity_extractor import EntityExtractor

GSTIN_REGEX = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"

class GSTRuleEngine:
    @staticmethod
    def evaluate(
        bidder_name: str,
        claimed_gstin: str,
        extracted_entities: List[Dict[str, Any]],
        mandatory: bool = True
    ) -> Dict[str, Any]:
        # Identify GSTIN from entities or bidder record
        extracted_gstin = None
        found_entity = None
        for ent in extracted_entities:
            if ent.get("entity_type") == "GSTIN":
                extracted_gstin = (ent.get("entity_value") or "").strip().upper()
                found_entity = ent
                break

        gstin = (extracted_gstin or claimed_gstin or "").strip().upper()

        if not gstin:
            return {
                "status": "FAIL" if mandatory else "NOT_APPLICABLE",
                "confidence": 0.98,
                "reason": "Missing mandatory GSTIN certificate or declaration in submitted documents.",
                "evidence": "No GSTIN found in submitted bidder documents.",
                "document_id": None,
                "document_name": None,
                "page_number": 1,
                "source": "RULE_ENGINE",
                "method": "STATUTORY_CHECK",
                "format_valid": False,
                "name_matched": False,
                "consistency_valid": False
            }

        # 1. Deterministic GSTIN Format Validation
        format_valid = bool(re.match(GSTIN_REGEX, gstin))
        if not format_valid:
            return {
                "status": "FAIL",
                "confidence": 0.99,
                "reason": f"Invalid GSTIN format '{gstin}'. Statutory GSTIN requires standard 15-character alphanumeric format (e.g. 29ABCDE1234F1Z5).",
                "evidence": f"Declared/Extracted GSTIN: '{gstin}' fails statutory 15-character format validation.",
                "document_id": found_entity.get("document_id") if found_entity else None,
                "document_name": found_entity.get("document_name") if found_entity else "GST_Certificate.pdf",
                "page_number": found_entity.get("page_number", 1) if found_entity else 1,
                "source": "DETERMINISTIC_RULE_ENGINE",
                "method": "REGEX_FORMAT_VALIDATION",
                "format_valid": False,
                "name_matched": False,
                "consistency_valid": False
            }

        # 2. Consistency between extracted GSTIN and claimed GSTIN
        if extracted_gstin and claimed_gstin and extracted_gstin != claimed_gstin.strip().upper():
            return {
                "status": "REVIEW",
                "confidence": 0.88,
                "reason": f"Extracted GSTIN '{extracted_gstin}' conflicts with bidder record GSTIN '{claimed_gstin}'.",
                "evidence": f"Document GSTIN: {extracted_gstin} vs Claimed GSTIN: {claimed_gstin}",
                "document_id": found_entity.get("document_id") if found_entity else None,
                "document_name": found_entity.get("document_name") if found_entity else "GST_Certificate.pdf",
                "page_number": found_entity.get("page_number", 1) if found_entity else 1,
                "source": "CROSS_DOCUMENT_CONSISTENCY",
                "method": "DOCUMENT_CROSS_CHECK",
                "format_valid": True,
                "name_matched": False,
                "consistency_valid": False
            }

        # 3. Verify via external adapter (mock / authorized external adapter architecture)
        # Note: Do NOT claim live government verified; state clearly adapter/mock verification.
        portal_res = adapters.gst.verify_identity(gstin, bidder_name)
        if not portal_res.get("is_valid", False):
            return {
                "status": "FAIL",
                "confidence": 0.95,
                "reason": f"GST verification adapter returned non-compliant status: {portal_res.get('message', 'Inactive/Invalid GSTIN')}",
                "evidence": f"Queried GSTIN: {gstin}. Adapter Status: {portal_res.get('status')}",
                "document_id": found_entity.get("document_id") if found_entity else None,
                "document_name": found_entity.get("document_name") if found_entity else "GST_Certificate.pdf",
                "page_number": found_entity.get("page_number", 1) if found_entity else 1,
                "source": "MOCK_ADAPTER_VERIFICATION",
                "method": "ADAPTER_AND_RULE",
                "format_valid": True,
                "name_matched": False,
                "consistency_valid": False
            }

        portal_data = portal_res.get("data", {})
        legal_name = portal_data.get("legal_name", "")

        # 4. Bidder legal-name consistency
        norm_bidder = EntityExtractor.normalize_company_name(bidder_name)
        norm_portal = EntityExtractor.normalize_company_name(legal_name)

        name_match = bool(norm_bidder and norm_portal and (norm_bidder == norm_portal or norm_bidder in norm_portal or norm_portal in norm_bidder))

        if not name_match and bidder_name:
            return {
                "status": "REVIEW",
                "confidence": 0.85,
                "reason": f"GSTIN {gstin} format is valid, but registered legal name ('{legal_name}') does not match declared bidder entity ('{bidder_name}').",
                "evidence": f"GSTIN: {gstin} | Registered Entity: {legal_name} | Declared Bidder: {bidder_name}",
                "document_id": found_entity.get("document_id") if found_entity else None,
                "document_name": found_entity.get("document_name") if found_entity else "GST_Certificate.pdf",
                "page_number": found_entity.get("page_number", 1) if found_entity else 1,
                "source": "MOCK_ADAPTER_VERIFICATION",
                "method": "ADAPTER_AND_RULE",
                "format_valid": True,
                "name_matched": False,
                "consistency_valid": True
            }

        return {
            "status": "PASS",
            "confidence": 0.98,
            "reason": f"GSTIN {gstin} format verified. Document evidence consistent with '{bidder_name}'. Filing status active (verified via mock adapter architecture; no live government API claimed).",
            "evidence": f"GSTIN: {gstin} | Legal Name: {legal_name} | Status: {portal_data.get('status', 'ACTIVE')} | Return Filing: {portal_data.get('return_filing_status', 'COMPLIANT')}",
            "document_id": found_entity.get("document_id") if found_entity else None,
            "document_name": found_entity.get("document_name") if found_entity else "GST_Certificate.pdf",
            "page_number": found_entity.get("page_number", 1) if found_entity else 1,
            "source": "MOCK_ADAPTER_VERIFICATION",
            "method": "ADAPTER_AND_RULE",
            "format_valid": True,
            "name_matched": True,
            "consistency_valid": True
        }
