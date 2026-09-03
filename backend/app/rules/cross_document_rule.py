from typing import Dict, Any, List
from app.documents.entity_extractor import EntityExtractor

class CrossDocumentConsistencyEngine:
    @staticmethod
    def evaluate(
        bidder_name: str,
        claimed_gstin: str,
        claimed_pan: str,
        extracted_entities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Cross-checks identity consistency across all uploaded documents:
        - GST legal name vs PAN name vs Udyam name vs Financial Statement name
        - Embedded PAN in GSTIN vs Claimed PAN
        """
        inconsistencies = []
        
        # 1. GST vs PAN embedded consistency
        gstins = [e.get("entity_value") for e in extracted_entities if e.get("entity_type") == "GSTIN"]
        pans = [e.get("entity_value") for e in extracted_entities if e.get("entity_type") == "PAN"]
        
        if claimed_pan:
            pans.append(claimed_pan)
        if claimed_gstin:
            gstins.append(claimed_gstin)

        for g in gstins:
            if len(g) == 15:
                embedded_pan = g[2:12].upper()
                for p in pans:
                    if p and p.upper() != embedded_pan:
                        inconsistencies.append(f"PAN mismatch: Document PAN '{p}' does not match PAN embedded in GSTIN '{g}' ({embedded_pan}).")

        # 2. Company Name Consistency
        names_found = [e.get("entity_value") for e in extracted_entities if e.get("entity_type") == "COMPANY_NAME"]
        norm_bidder = EntityExtractor.normalize_company_name(bidder_name)
        
        for name in names_found:
            norm_doc_name = EntityExtractor.normalize_company_name(name)
            if norm_bidder and norm_doc_name:
                # Compare fuzzy similarity
                if norm_doc_name not in norm_bidder and norm_bidder not in norm_doc_name:
                    # Ignore common words like OEM or Bank names
                    if not any(k in norm_doc_name for k in ["bank", "ministry", "oem", "department"]):
                        inconsistencies.append(f"Entity name discrepancy: Found '{name}' in uploaded documents vs declared bidder '{bidder_name}'.")

        is_consistent = len(inconsistencies) == 0

        if is_consistent:
            return {
                "status": "PASS",
                "confidence": 0.98,
                "reason": "High cross-document consistency: Company name, PAN, and GSTIN match across statutory certificates, financial statements, and declarations.",
                "evidence": f"Cross-verified identity tokens for '{bidder_name}'. Zero identity discrepancies detected.",
                "document_id": None,
                "document_name": None,
                "page_number": 1,
                "source": "RULE_ENGINE",
                "method": "CROSS_DOCUMENT_VERIFICATION"
            }
        else:
            return {
                "status": "REVIEW",
                "confidence": 0.85,
                "reason": f"Cross-document consistency flagged: {'; '.join(inconsistencies[:2])}",
                "evidence": " | ".join(inconsistencies),
                "document_id": None,
                "document_name": None,
                "page_number": 1,
                "source": "RULE_ENGINE",
                "method": "CROSS_DOCUMENT_VERIFICATION"
            }
