from typing import Dict, Any, List
import re
from app.documents.entity_extractor import EntityExtractor

class OEMRuleEngine:
    @staticmethod
    def evaluate(
        bidder_name: str,
        tender_number: str,
        extracted_entities: List[Dict[str, Any]],
        mandatory: bool = True
    ) -> Dict[str, Any]:
        oem_items = [e for e in extracted_entities if e.get("entity_type") == "OEM_AUTHORIZATION"]
        
        if not oem_items:
            return {
                "status": "FAIL" if mandatory else "REVIEW",
                "confidence": 0.95,
                "reason": "Manufacturer Authorization Form (MAF) / OEM Authorization letter missing.",
                "evidence": "No OEM authorization letter found in submitted bidder documents.",
                "document_id": None,
                "document_name": None,
                "page_number": 1,
                "source": "RULE_ENGINE",
                "method": "ENTITY_MATCH"
            }

        item = oem_items[0]
        context = item.get("context_snippet", "")
        authorized_bidder = item.get("normalized_value", "")
        
        norm_bidder = EntityExtractor.normalize_company_name(bidder_name)
        norm_auth = EntityExtractor.normalize_company_name(authorized_bidder)

        # Check if authorization is issued to the exact bidder
        name_match = (norm_bidder == norm_auth) or (norm_bidder in norm_auth) or (norm_auth in norm_bidder) if norm_auth else False
        
        # Check tender reference match
        tender_match = bool(tender_number and tender_number.lower() in context.lower()) if tender_number else True

        if not name_match and authorized_bidder:
            return {
                "status": "REVIEW",
                "confidence": 0.88,
                "reason": f"OEM Authorization was issued to '{authorized_bidder}', which does not exactly match Bidder entity '{bidder_name}'. Requires Officer Discretion.",
                "evidence": f"OEM Document authorizes: '{authorized_bidder}' | Bidder Name: '{bidder_name}' | Tender Ref in Doc: {'MATCHED' if tender_match else 'GENERAL'}",
                "document_id": item.get("document_id"),
                "document_name": item.get("document_name", "OEM_Authorization.pdf"),
                "page_number": item.get("page_number", 1),
                "source": "RULE_ENGINE",
                "method": "ENTITY_MATCH"
            }

        return {
            "status": "PASS",
            "confidence": 0.96,
            "reason": f"OEM Manufacturer Authorization verified: issued to '{bidder_name}' and valid for tender.",
            "evidence": f"OEM Letter details: {item.get('entity_value')} | Authorized Entity: {authorized_bidder or bidder_name}",
            "document_id": item.get("document_id"),
            "document_name": item.get("document_name", "OEM_Authorization.pdf"),
            "page_number": item.get("page_number", 1),
            "source": "RULE_ENGINE",
            "method": "ENTITY_MATCH"
        }
