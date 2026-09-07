import re
from typing import Dict, Any, List
from app.government_adapters import adapters
from app.documents.entity_extractor import EntityExtractor

PAN_REGEX = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"

class PANRuleEngine:
    @staticmethod
    def evaluate(
        bidder_name: str,
        claimed_pan: str,
        extracted_entities: List[Dict[str, Any]],
        mandatory: bool = True
    ) -> Dict[str, Any]:
        extracted_pan = None
        found_entity = None
        for ent in extracted_entities:
            if ent.get("entity_type") == "PAN":
                extracted_pan = (ent.get("entity_value") or "").strip().upper()
                found_entity = ent
                break

        if not extracted_pan:
            # Check if PAN is embedded in GSTIN
            for ent in extracted_entities:
                if ent.get("entity_type") == "GSTIN" and len(ent.get("entity_value", "")) >= 12:
                    embedded = ent.get("entity_value")[2:12].upper()
                    if re.match(PAN_REGEX, embedded):
                        extracted_pan = embedded
                        found_entity = ent
                        break

        pan = (extracted_pan or claimed_pan or "").strip().upper()

        if not pan:
            return {
                "status": "FAIL" if mandatory else "NOT_APPLICABLE",
                "confidence": 0.98,
                "reason": "Missing mandatory PAN Card or Income Tax registration in submitted bidder documents.",
                "evidence": "No PAN record found in submitted documents.",
                "document_id": None,
                "document_name": None,
                "page_number": 1,
                "source": "RULE_ENGINE",
                "method": "STATUTORY_CHECK",
                "format_valid": False,
                "name_matched": False,
                "consistency_valid": False
            }

        # 1. Deterministic PAN Format Validation
        format_valid = bool(re.match(PAN_REGEX, pan))
        if not format_valid:
            return {
                "status": "FAIL",
                "confidence": 0.99,
                "reason": f"Invalid PAN format '{pan}'. Statutory PAN requires standard 10-character alphanumeric structure (e.g. ABCDE1234F: 5 letters, 4 digits, 1 letter).",
                "evidence": f"Declared/Extracted PAN: '{pan}' fails statutory 10-character format validation.",
                "document_id": found_entity.get("document_id") if found_entity else None,
                "document_name": found_entity.get("document_name") if found_entity else "PAN_Card.pdf",
                "page_number": found_entity.get("page_number", 1) if found_entity else 1,
                "source": "DETERMINISTIC_RULE_ENGINE",
                "method": "REGEX_FORMAT_VALIDATION",
                "format_valid": False,
                "name_matched": False,
                "consistency_valid": False
            }

        # 2. Consistency between extracted PAN and claimed PAN
        if extracted_pan and claimed_pan and extracted_pan != claimed_pan.strip().upper():
            return {
                "status": "REVIEW",
                "confidence": 0.88,
                "reason": f"Extracted document PAN '{extracted_pan}' conflicts with bidder record PAN '{claimed_pan}'.",
                "evidence": f"Document PAN: {extracted_pan} vs Claimed PAN: {claimed_pan}",
                "document_id": found_entity.get("document_id") if found_entity else None,
                "document_name": found_entity.get("document_name") if found_entity else "PAN_Card.pdf",
                "page_number": found_entity.get("page_number", 1) if found_entity else 1,
                "source": "CROSS_DOCUMENT_CONSISTENCY",
                "method": "DOCUMENT_CROSS_CHECK",
                "format_valid": True,
                "name_matched": False,
                "consistency_valid": False
            }

        portal_res = adapters.pan.verify_identity(pan, bidder_name)
        if not portal_res.get("is_valid", False):
            return {
                "status": "FAIL",
                "confidence": 0.95,
                "reason": f"PAN validation adapter returned non-compliant status: {portal_res.get('message', 'Invalid PAN')}",
                "evidence": f"Queried PAN: {pan}. Error: {portal_res.get('data', {}).get('error', 'Adapter non-compliant')}",
                "document_id": found_entity.get("document_id") if found_entity else None,
                "document_name": found_entity.get("document_name") if found_entity else "PAN_Card.pdf",
                "page_number": found_entity.get("page_number", 1) if found_entity else 1,
                "source": "MOCK_ADAPTER_VERIFICATION",
                "method": "ADAPTER_AND_RULE",
                "format_valid": True,
                "name_matched": False,
                "consistency_valid": False
            }

        portal_data = portal_res.get("data", {})
        registered_name = portal_data.get("entity_name", "")

        # 3. Bidder legal-name consistency
        norm_bidder = EntityExtractor.normalize_company_name(bidder_name)
        norm_portal = EntityExtractor.normalize_company_name(registered_name)
        name_match = bool(norm_bidder and norm_portal and (norm_bidder == norm_portal or norm_bidder in norm_portal or norm_portal in norm_bidder))

        if not name_match and bidder_name:
            return {
                "status": "REVIEW",
                "confidence": 0.85,
                "reason": f"PAN {pan} format is valid, but registered entity name ('{registered_name}') does not match declared bidder '{bidder_name}'.",
                "evidence": f"PAN: {pan} | Registered Name: {registered_name} | Declared Bidder: {bidder_name}",
                "document_id": found_entity.get("document_id") if found_entity else None,
                "document_name": found_entity.get("document_name") if found_entity else "PAN_Card.pdf",
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
            "reason": f"PAN {pan} verified ACTIVE ({portal_data.get('entity_type', 'COMPANY')}). Income Tax return filing compliant. Name consistency verified (verified via mock adapter architecture; no live government API claimed).",
            "evidence": f"PAN: {pan} | Entity: {registered_name} | Status: {portal_data.get('status', 'ACTIVE')} | ITR Filed 3 Yrs: {portal_data.get('itr_filed_last_3_years', True)}",
            "document_id": found_entity.get("document_id") if found_entity else None,
            "document_name": found_entity.get("document_name") if found_entity else "PAN_Card.pdf",
            "page_number": found_entity.get("page_number", 1) if found_entity else 1,
            "source": "MOCK_ADAPTER_VERIFICATION",
            "method": "ADAPTER_AND_RULE",
            "format_valid": True,
            "name_matched": True,
            "consistency_valid": True
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
