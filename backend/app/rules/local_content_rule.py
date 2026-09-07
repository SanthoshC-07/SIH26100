from typing import Dict, Any, List

class LocalContentRuleEngine:
    @staticmethod
    def evaluate(
        required_percentage: float,
        extracted_entities: List[Dict[str, Any]],
        mandatory: bool = True
    ) -> Dict[str, Any]:
        req_pct = required_percentage or 50.0
        
        local_content_items = [
            e for e in extracted_entities 
            if e.get("entity_type") in ["LOCAL_CONTENT_PERCENT", "LOCAL_CONTENT_DECLARATION", "LOCAL_CONTENT"]
        ]
        
        if not local_content_items:
            return {
                "status": "FAIL" if mandatory else "REVIEW",
                "confidence": 0.92,
                "reason": "Make in India (MII) / Local Content declaration certificate not found.",
                "evidence": "No local content percentage declaration found in bidder submission.",
                "document_id": None,
                "document_name": None,
                "page_number": 1,
                "source": "RULE_ENGINE",
                "method": "STATUTORY_CHECK"
            }

        first_item = local_content_items[0]
        declared_pct = 0.0
        if first_item.get("normalized_value") is not None:
            try:
                declared_pct = float(first_item.get("normalized_value"))
            except ValueError:
                declared_pct = 0.0
        else:
            val_str = str(first_item.get("entity_value", ""))
            import re
            m = re.search(r"(\d+(?:\.\d+)?)", val_str)
            if m:
                declared_pct = float(m.group(1))


        passed = declared_pct >= req_pct
        classification = "Class-I Local Supplier" if declared_pct >= 50 else ("Class-II Local Supplier" if declared_pct >= 20 else "Non-Local Supplier")

        if passed:
            return {
                "status": "PASS",
                "confidence": 0.98,
                "reason": f"Declared local content of {declared_pct:.1f}% meets/exceeds the tender requirement of {req_pct:.1f}% ({classification}).",
                "evidence": f"Declared Local Content: {declared_pct:.1f}% | Classification: {classification} | Required: {req_pct:.1f}%",
                "document_id": first_item.get("document_id"),
                "document_name": first_item.get("document_name", "Local_Content_Declaration.pdf"),
                "page_number": first_item.get("page_number", 1),
                "source": "RULE_ENGINE",
                "method": "ARITHMETIC_VERIFICATION"
            }
        else:
            return {
                "status": "FAIL",
                "confidence": 0.98,
                "reason": f"Declared local content of {declared_pct:.1f}% is below the required threshold of {req_pct:.1f}% ({classification}).",
                "evidence": f"Declared: {declared_pct:.1f}% < Required: {req_pct:.1f}%",
                "document_id": first_item.get("document_id"),
                "document_name": first_item.get("document_name", "Local_Content_Declaration.pdf"),
                "page_number": first_item.get("page_number", 1),
                "source": "RULE_ENGINE",
                "method": "ARITHMETIC_VERIFICATION"
            }
