from typing import Dict, Any, List
from app.government_adapters import adapters
from app.documents.entity_extractor import EntityExtractor

class PANRuleEngine:
    @staticmethod
    def evaluate(
        bidder_name: str,
        claimed_pan: str,
        extracted_entities: List[Dict[str, Any]],
        mandatory: bool = True
    ) -> Dict[str, Any]:
        pan = claimed_pan
        found_entity = None
        for ent in extracted_entities:
            if ent.get("entity_type") == "PAN":
                pan = ent.get("entity_value")
                found_entity = ent
                break

        if not pan:
            # Check if PAN is embedded in GSTIN
            for ent in extracted_entities:
                if ent.get("entity_type") == "GSTIN" and len(ent.get("entity_value", "")) == 15:
                    pan = ent.get("entity_value")[2:12]
                    found_entity = ent
                    break

        if not pan:
            return {
                "status": "FAIL" if mandatory else "NOT_APPLICABLE",
                "confidence": 0.98,
                "reason": "Missing mandatory PAN Card / Income Tax submission.",
                "evidence": "No PAN record found in submitted documents.",
                "document_id": None,
                "document_name": None,
                "page_number": 1,
                "source": "RULE_ENGINE",
                "method": "STATUTORY_CHECK"
            }

        portal_res = adapters.pan.verify_identity(pan, bidder_name)
        if not portal_res["is_valid"]:
            return {
                "status": "FAIL",
                "confidence": 0.95,
                "reason": f"PAN validation failed: {portal_res.get('message')}",
                "evidence": f"Queried PAN: {pan}. Error: {portal_res.get('data', {}).get('error')}",
                "document_id": found_entity.get("document_id") if found_entity else None,
                "document_name": found_entity.get("document_name") if found_entity else "PAN_Card.pdf",
                "page_number": found_entity.get("page_number", 1) if found_entity else 1,
                "source": "MOCK_PAN_PORTAL",
                "method": "PORTAL_AND_RULE"
            }

        portal_data = portal_res["data"]
        return {
            "status": "PASS",
            "confidence": 0.98,
            "reason": f"PAN {pan} verified ACTIVE ({portal_data.get('entity_type', 'COMPANY')}). Income Tax return filing compliant.",
            "evidence": f"PAN: {pan} | Entity: {portal_data.get('entity_name')} | Status: {portal_data.get('status')} | ITR Filed 3 Yrs: {portal_data.get('itr_filed_last_3_years')}",
            "document_id": found_entity.get("document_id") if found_entity else None,
            "document_name": found_entity.get("document_name") if found_entity else "PAN_Card.pdf",
            "page_number": found_entity.get("page_number", 1) if found_entity else 1,
            "source": "MOCK_PAN_PORTAL",
            "method": "PORTAL_AND_RULE"
        }


class UdyamRuleEngine:
    @staticmethod
    def evaluate(
        bidder_name: str,
        claimed_udyam: str,
        extracted_entities: List[Dict[str, Any]],
        mandatory: bool = False
    ) -> Dict[str, Any]:
        udyam = claimed_udyam
        found_entity = None
        for ent in extracted_entities:
            if ent.get("entity_type") == "UDYAM_NUMBER":
                udyam = ent.get("entity_value")
                found_entity = ent
                break

        if not udyam:
            return {
                "status": "NOT_APPLICABLE" if not mandatory else "REVIEW",
                "confidence": 0.95,
                "reason": "Bidder has not submitted an Udyam/MSME certificate (MSME exemptions/preference will not apply).",
                "evidence": "No Udyam registration number declared.",
                "document_id": None,
                "document_name": None,
                "page_number": 1,
                "source": "RULE_ENGINE",
                "method": "APPLICABILITY_CHECK"
            }

        portal_res = adapters.udyam.verify_identity(udyam, bidder_name)
        if not portal_res["is_valid"]:
            return {
                "status": "FAIL" if mandatory else "REVIEW",
                "confidence": 0.95,
                "reason": f"Udyam registration check failed: {portal_res.get('message')}",
                "evidence": f"Queried Udyam: {udyam}",
                "document_id": found_entity.get("document_id") if found_entity else None,
                "document_name": found_entity.get("document_name") if found_entity else "Udyam_Certificate.pdf",
                "page_number": found_entity.get("page_number", 1) if found_entity else 1,
                "source": "MOCK_UDYAM_PORTAL",
                "method": "PORTAL_AND_RULE"
            }

        portal_data = portal_res["data"]
        return {
            "status": "PASS",
            "confidence": 0.98,
            "reason": f"Valid Udyam Registration ({portal_data.get('enterprise_type', 'MSME')}) confirmed with Ministry of MSME.",
            "evidence": f"Udyam: {udyam} | Enterprise: {portal_data.get('enterprise_name')} | Type: {portal_data.get('enterprise_type')} | Status: {portal_data.get('status')}",
            "document_id": found_entity.get("document_id") if found_entity else None,
            "document_name": found_entity.get("document_name") if found_entity else "Udyam_Certificate.pdf",
            "page_number": found_entity.get("page_number", 1) if found_entity else 1,
            "source": "MOCK_UDYAM_PORTAL",
            "method": "PORTAL_AND_RULE"
        }
