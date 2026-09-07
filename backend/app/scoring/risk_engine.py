from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class RiskEngine:
    """
    Phase 5: Configurable Multi-Factor Petroleum Bid Risk Analysis Engine
    
    Evaluates:
    - FAIL requirements
    - REVIEW requirements
    - INSUFFICIENT evidence
    - missing mandatory documents
    - conflicting documents
    - low extraction confidence
    - low semantic confidence
    - critical financial failures
    - critical experience failures
    - technical failures
    - HSE/safety failures
    - statutory compliance issues

    Risk Levels:
    - LOW: No failures, high extraction and semantic confidence, complete documentation.
    - MEDIUM: Ambiguous evidence, REVIEW or INSUFFICIENT items, low confidence scores.
    - HIGH: Mandatory requirement failure, financial shortfall, technical deficit, missing key documents.
    - CRITICAL: Statutory fraud/failure, blacklisting, critical safety/HSE failure, severe multi-failures.
    """

    DEFAULT_CONFIG = {
        "confidence_threshold_low": 0.75,
        "semantic_threshold_low": 0.75,
        "critical_categories": ["BLACKLISTING", "DEBARMENT"],
        "statutory_categories": ["GST", "PAN", "STATUTORY", "TAX", "REGISTRATION"],
        "safety_categories": ["HSE", "SAFETY", "ISO_45001", "ISO_14001", "FIRE_SAFETY", "ENVIRONMENTAL_SAFETY"],
        "financial_categories": ["TURNOVER", "FINANCIAL", "NET_WORTH", "SOLVENCY", "FINANCIAL_ELIGIBILITY"],
        "experience_categories": ["EXPERIENCE", "SIMILAR_WORK", "PIPELINE_EXPERIENCE", "OIL_GAS_EXPERIENCE"],
        "technical_categories": ["TECHNICAL", "PIPELINE_SPEC", "EQUIPMENT", "MANPOWER", "TECHNICAL_SPECIFICATION"],
        "severity_penalties": {
            "CRITICAL": 50.0,
            "HIGH": 25.0,
            "MEDIUM": 12.0,
            "LOW": 3.0
        }
    }

    @classmethod
    def assess_risk(
        cls,
        compliance_checks: List[Dict[str, Any]],
        overall_score: float = 100.0,
        cross_document_consistency: Optional[Dict[str, Any]] = None,
        missing_documents: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        rules = cls.DEFAULT_CONFIG.copy()
        if config:
            rules.update(config)

        primary_risk_factors: List[str] = []
        detailed_factors: List[Dict[str, Any]] = []

        has_critical_statutory_fail = False
        has_critical_safety_fail = False
        has_blacklist = False
        mandatory_failures = 0
        review_count = 0
        insufficient_count = 0
        low_confidence_count = 0

        conf_threshold = rules.get("confidence_threshold_low", 0.75)
        sem_threshold = rules.get("semantic_threshold_low", 0.75)

        for check in compliance_checks:
            cat = (check.get("requirement_category") or check.get("category") or "").upper()
            status = (check.get("status") or "").upper()
            mandatory = check.get("requirement_mandatory", check.get("mandatory", True))
            confidence = float(check.get("confidence") or 1.0)
            semantic_score = float(check.get("semantic_score") or 1.0)
            reason = check.get("reason") or check.get("explanation") or ""
            req_id = check.get("requirement_id") or check.get("id")
            check_id = check.get("compliance_check_id") or check.get("id")
            source_doc = check.get("source_document") or check.get("document_name")
            page_num = check.get("page_number")
            evidence_snippet = str(check.get("evidence") or check.get("source_text") or check.get("evidence_text") or "")

            # 1. Critical Blacklisting / Debarment
            if cat in rules["critical_categories"] and status == "FAIL":
                has_blacklist = True
                factor_desc = f"CRITICAL: Vendor identified in Debarred/Blacklisted registry. {reason}"
                primary_risk_factors.append(factor_desc)
                detailed_factors.append({
                    "factor_type": "CRITICAL_BLACKLIST",
                    "severity": "CRITICAL",
                    "description": factor_desc,
                    "requirement_id": req_id,
                    "compliance_check_id": check_id,
                    "evidence_snippet": evidence_snippet,
                    "source_document": source_doc,
                    "page_number": page_num
                })

            # 2. Critical Safety / HSE Failures
            if any(sc in cat for sc in rules["safety_categories"]) and status == "FAIL":
                has_critical_safety_fail = True
                factor_desc = f"CRITICAL: Critical HSE/Safety failure detected in {cat}. {reason}"
                primary_risk_factors.append(factor_desc)
                detailed_factors.append({
                    "factor_type": "CRITICAL_HSE_FAILURE",
                    "severity": "CRITICAL",
                    "description": factor_desc,
                    "requirement_id": req_id,
                    "compliance_check_id": check_id,
                    "evidence_snippet": evidence_snippet,
                    "source_document": source_doc,
                    "page_number": page_num
                })

            # 3. Critical Statutory Compliance Issues (GST / PAN failure)
            if any(sc in cat for sc in rules["statutory_categories"]) and status == "FAIL":
                has_critical_statutory_fail = True
                factor_desc = f"CRITICAL: Statutory identity/tax failure detected in {cat}. {reason}"
                primary_risk_factors.append(factor_desc)
                detailed_factors.append({
                    "factor_type": "CRITICAL_STATUTORY_FAILURE",
                    "severity": "CRITICAL",
                    "description": factor_desc,
                    "requirement_id": req_id,
                    "compliance_check_id": check_id,
                    "evidence_snippet": evidence_snippet,
                    "source_document": source_doc,
                    "page_number": page_num
                })

            # 4. Mandatory Failures (Financial, Experience, Technical)
            if status == "FAIL" and mandatory and not (cat in rules["critical_categories"] or any(sc in cat for sc in rules["safety_categories"]) or any(sc in cat for sc in rules["statutory_categories"])):
                mandatory_failures += 1
                if any(fc in cat for fc in rules["financial_categories"]):
                    ftype = "CRITICAL_FINANCIAL_FAILURE"
                    prefix = "Critical financial failure"
                elif any(ec in cat for ec in rules["experience_categories"]):
                    ftype = "CRITICAL_EXPERIENCE_FAILURE"
                    prefix = "Critical experience failure"
                elif any(tc in cat for tc in rules["technical_categories"]):
                    ftype = "TECHNICAL_FAILURE"
                    prefix = "Technical specification failure"
                else:
                    ftype = "MANDATORY_REQUIREMENT_FAILURE"
                    prefix = f"Mandatory {cat} failure"

                factor_desc = f"{prefix}: {reason}"
                primary_risk_factors.append(factor_desc)
                detailed_factors.append({
                    "factor_type": ftype,
                    "severity": "HIGH",
                    "description": factor_desc,
                    "requirement_id": req_id,
                    "compliance_check_id": check_id,
                    "evidence_snippet": evidence_snippet,
                    "source_document": source_doc,
                    "page_number": page_num
                })

            # 5. Non-Mandatory Failures
            elif status == "FAIL" and not mandatory:
                factor_desc = f"Non-mandatory requirement failure in {cat}: {reason}"
                primary_risk_factors.append(factor_desc)
                detailed_factors.append({
                    "factor_type": "NON_MANDATORY_FAIL",
                    "severity": "MEDIUM",
                    "description": factor_desc,
                    "requirement_id": req_id,
                    "compliance_check_id": check_id,
                    "evidence_snippet": evidence_snippet,
                    "source_document": source_doc,
                    "page_number": page_num
                })

            # 6. REVIEW Requirements
            if status == "REVIEW":
                review_count += 1
                factor_desc = f"Requirement requires manual review ({cat}): {reason}"
                primary_risk_factors.append(factor_desc)
                detailed_factors.append({
                    "factor_type": "REVIEW_REQUIRED",
                    "severity": "MEDIUM",
                    "description": factor_desc,
                    "requirement_id": req_id,
                    "compliance_check_id": check_id,
                    "evidence_snippet": evidence_snippet,
                    "source_document": source_doc,
                    "page_number": page_num
                })

            # 7. INSUFFICIENT Evidence
            if status == "INSUFFICIENT":
                insufficient_count += 1
                factor_desc = f"Insufficient evidence for {cat}: {reason}"
                primary_risk_factors.append(factor_desc)
                detailed_factors.append({
                    "factor_type": "INSUFFICIENT_EVIDENCE",
                    "severity": "MEDIUM",
                    "description": factor_desc,
                    "requirement_id": req_id,
                    "compliance_check_id": check_id,
                    "evidence_snippet": evidence_snippet,
                    "source_document": source_doc,
                    "page_number": page_num
                })

            # 8. Low Extraction / Semantic Confidence
            if status == "PASS" and confidence < conf_threshold:
                low_confidence_count += 1
                factor_desc = f"{cat} evidence confidence = {confidence:.2f} (below {conf_threshold:.2f} threshold)"
                primary_risk_factors.append(factor_desc)
                detailed_factors.append({
                    "factor_type": "LOW_EXTRACTION_CONFIDENCE",
                    "severity": "MEDIUM",
                    "description": factor_desc,
                    "requirement_id": req_id,
                    "compliance_check_id": check_id,
                    "evidence_snippet": evidence_snippet,
                    "source_document": source_doc,
                    "page_number": page_num
                })
            elif status == "PASS" and semantic_score < sem_threshold and semantic_score > 0.0:
                factor_desc = f"{cat} semantic similarity confidence = {semantic_score:.2f} (marginal match)"
                primary_risk_factors.append(factor_desc)
                detailed_factors.append({
                    "factor_type": "LOW_SEMANTIC_CONFIDENCE",
                    "severity": "MEDIUM",
                    "description": factor_desc,
                    "requirement_id": req_id,
                    "compliance_check_id": check_id,
                    "evidence_snippet": evidence_snippet,
                    "source_document": source_doc,
                    "page_number": page_num
                })

        # 9. Cross-Document Inconsistencies
        if cross_document_consistency:
            cdc_status = (cross_document_consistency.get("status") or "").upper()
            issues = cross_document_consistency.get("issues", [])
            discrepancies = cross_document_consistency.get("discrepancies", [])
            all_issues = issues + discrepancies

            if cdc_status == "FAIL":
                for issue in all_issues:
                    factor_desc = f"Conflicting documents detected: {issue}"
                    primary_risk_factors.append(factor_desc)
                    detailed_factors.append({
                        "factor_type": "CONFLICTING_DOCUMENTS",
                        "severity": "HIGH",
                        "description": factor_desc,
                        "requirement_id": None,
                        "compliance_check_id": None,
                        "evidence_snippet": None,
                        "source_document": "Cross-Document Integrity Check",
                        "page_number": None
                    })
            elif cdc_status == "REVIEW" or (all_issues and cdc_status != "PASS"):
                for issue in all_issues:
                    factor_desc = f"Cross-document consistency warning: {issue}"
                    primary_risk_factors.append(factor_desc)
                    detailed_factors.append({
                        "factor_type": "DOCUMENT_DISCREPANCY",
                        "severity": "MEDIUM",
                        "description": factor_desc,
                        "requirement_id": None,
                        "compliance_check_id": None,
                        "evidence_snippet": None,
                        "source_document": "Cross-Document Integrity Check",
                        "page_number": None
                    })

        # 10. Missing Mandatory Documents
        if missing_documents:
            for doc in missing_documents:
                factor_desc = f"Missing mandatory document: {doc}"
                primary_risk_factors.append(factor_desc)
                detailed_factors.append({
                    "factor_type": "MISSING_MANDATORY_DOC",
                    "severity": "HIGH",
                    "description": factor_desc,
                    "requirement_id": None,
                    "compliance_check_id": None,
                    "evidence_snippet": None,
                    "source_document": doc,
                    "page_number": None
                })

        # Determine Overall Risk Level and Risk Score
        # Rules:
        # - Critical safety/statutory failure OR Blacklist OR >=2 mandatory fails -> CRITICAL
        # - Mandatory requirement FAIL OR Missing mandatory doc -> HIGH
        # - Some REVIEW/INSUFFICIENT OR Low confidence OR non-mandatory fail -> MEDIUM
        # - No failures + high confidence -> LOW
        if has_blacklist or has_critical_statutory_fail or has_critical_safety_fail or mandatory_failures >= 2:
            risk_level = "CRITICAL"
            base_score = 88.0
        elif mandatory_failures == 1 or any(df["severity"] == "HIGH" for df in detailed_factors):
            risk_level = "HIGH"
            base_score = 68.0
        elif review_count > 0 or insufficient_count > 0 or any(df["severity"] == "MEDIUM" for df in detailed_factors) or overall_score < 85:
            risk_level = "MEDIUM"
            base_score = 38.0
        else:
            risk_level = "LOW"
            base_score = 10.0

        if detailed_factors:
            risk_score = round(min(100.0, max(10.0, base_score + min(10.0, len(detailed_factors) * 2.0))), 1)
        else:
            risk_score = 10.0
            primary_risk_factors.append("No critical risk factors identified. Bid exhibits robust statutory and tender compliance.")

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "primary_risk_factors": primary_risk_factors,
            "detailed_factors": detailed_factors,
            "assessed_at": datetime.now(timezone.utc).isoformat()
        }

    @classmethod
    def persist_risk_factors(cls, db, bidder_id: str, risk_data: Dict[str, Any]) -> None:
        """
        Synchronizes computed risk assessment and granular risk factors into SQLite.
        """
        from app.models.models import RiskAssessment, RiskFactor

        assessment = db.query(RiskAssessment).filter(RiskAssessment.bidder_id == bidder_id).first()
        if not assessment:
            assessment = RiskAssessment(
                bidder_id=bidder_id,
                risk_level=risk_data["risk_level"],
                risk_score=risk_data["risk_score"],
                primary_risk_factors=risk_data["primary_risk_factors"],
                assessed_at=datetime.now(timezone.utc)
            )
            db.add(assessment)
            db.flush()
        else:
            assessment.risk_level = risk_data["risk_level"]
            assessment.risk_score = risk_data["risk_score"]
            assessment.primary_risk_factors = risk_data["primary_risk_factors"]
            assessment.assessed_at = datetime.now(timezone.utc)

        # Clear existing factors and insert fresh granular factor rows
        db.query(RiskFactor).filter(RiskFactor.bid_id == bidder_id).delete()
        for df in risk_data.get("detailed_factors", []):
            factor = RiskFactor(
                risk_assessment_id=assessment.id,
                bid_id=bidder_id,
                requirement_id=df.get("requirement_id"),
                compliance_check_id=df.get("compliance_check_id"),
                factor_type=df.get("factor_type", "GENERAL_RISK"),
                severity=df.get("severity", "MEDIUM"),
                description=df.get("description", ""),
                evidence_snippet=df.get("evidence_snippet"),
                source_document=df.get("source_document"),
                page_number=df.get("page_number"),
                created_at=datetime.now(timezone.utc)
            )
            db.add(factor)
        db.commit()
