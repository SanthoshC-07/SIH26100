from typing import Dict, Any, List
from app.government_adapters import adapters
from app.documents.entity_extractor import EntityExtractor

class GSTRuleEngine:
    @staticmethod
    def evaluate(
        bidder_name: str,
        claimed_gstin: str,
        extracted_entities: List[Dict[str, Any]],
        mandatory: bool = True
    ) -> Dict[str, Any]:
        # Identify GSTIN from entities or bidder record
        gstin = claimed_gstin
        found_entity = None
        for ent in extracted_entities:
            if ent.get("entity_type") == "GSTIN":
                gstin = ent.get("entity_value")
                found_entity = ent
                break

        if not gstin:
            return {
                "status": "FAIL" if mandatory else "NOT_APPLICABLE",
                "confidence": 0.98,
                "reason": "Missing mandatory GSTIN certificate or declaration.",
                "evidence": "No GSTIN found in submitted bidder documents.",
                "document_id": None,
                "document_name": None,
                "page_number": 1,
                "source": "RULE_ENGINE",
                "method": "STATUTORY_CHECK"
            }

        # Query Government Adapter
        portal_res = adapters.gst.verify_identity(gstin, bidder_name)
        if not portal_res["is_valid"]:
            return {
                "status": "FAIL",
                "confidence": 0.95,
                "reason": f"GST Portal returned non-compliant status: {portal_res.get('message')}",
                "evidence": f"Queried GSTIN: {gstin}. Status: {portal_res.get('status')}",
                "document_id": found_entity.get("document_id") if found_entity else None,
                "document_name": found_entity.get("document_name") if found_entity else "GST_Certificate.pdf",
                "page_number": found_entity.get("page_number", 1) if found_entity else 1,
                "source": "MOCK_GST_PORTAL",
                "method": "PORTAL_AND_RULE"
            }

        portal_data = portal_res["data"]
        legal_name = portal_data.get("legal_name", "")
        
        # Cross check legal name normalization
        norm_bidder = EntityExtractor.normalize_company_name(bidder_name)
        norm_portal = EntityExtractor.normalize_company_name(legal_name)
        
        name_match = (norm_bidder == norm_portal) or (norm_bidder in norm_portal) or (norm_portal in norm_bidder)
        
        if not name_match and bidder_name:
            return {
                "status": "REVIEW",
                "confidence": 0.85,
                "reason": f"GSTIN is ACTIVE, but registered legal name ('{legal_name}') does not exactly match bidder entity ('{bidder_name}').",
                "evidence": f"GSTIN: {gstin} | Registered Name: {legal_name} | Return Status: {portal_data.get('return_filing_status')}",
                "document_id": found_entity.get("document_id") if found_entity else None,
                "document_name": found_entity.get("document_name") if found_entity else "GST_Certificate.pdf",
                "page_number": found_entity.get("page_number", 1) if found_entity else 1,
                "source": "MOCK_GST_PORTAL",
                "method": "PORTAL_AND_RULE"
            }

        return {
            "status": "PASS",
            "confidence": 0.98,
            "reason": f"GSTIN {gstin} is ACTIVE and return filing is COMPLIANT ({portal_data.get('filing_frequency', 'Monthly')}). Name match verified.",
            "evidence": f"GSTIN: {gstin} | Legal Name: {legal_name} | Status: {portal_data.get('status')} | Return Filing: {portal_data.get('return_filing_status')}",
            "document_id": found_entity.get("document_id") if found_entity else None,
            "document_name": found_entity.get("document_name") if found_entity else "GST_Certificate.pdf",
            "page_number": found_entity.get("page_number", 1) if found_entity else 1,
            "source": "MOCK_GST_PORTAL",
            "method": "PORTAL_AND_RULE"
        }
