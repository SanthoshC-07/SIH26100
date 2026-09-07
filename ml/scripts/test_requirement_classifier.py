"""
SIH26100 — 6/6 ML Test Suite for Requirement Classifier
-------------------------------------------------------
Authoritative ML test suite validating:
1. Model loading & pipeline integrity
2. 10 locked requirement classes classification
3. Confidence scoring & probability distributions
4. Batch classification
5. Requirement extraction with threshold & evidence mapping
6. Edge cases, empty inputs & fallback heuristics

Usage:
    pytest ml/scripts/test_requirement_classifier.py -v
"""
import os
import sys
import pytest

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ML_DIR = os.path.dirname(_THIS_DIR)
PROJECT_ROOT = os.path.dirname(_ML_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if _ML_DIR not in sys.path:
    sys.path.insert(0, _ML_DIR)
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from ml.scripts.requirement_classifier import (
    RequirementClassifier,
    requirement_classifier,
    REQUIREMENT_CLASSES,
)
from ml.scripts.requirement_extractor import (
    RequirementExtractor,
    requirement_extractor,
)


# ==============================================================================
# TEST 1: Model Loading & Pipeline Integrity
# ==============================================================================
def test_1_model_loading():
    """Verify authoritative model file exists and loads as a valid scikit-learn pipeline."""
    clf = RequirementClassifier.get_instance()
    assert clf.is_ready is True, "RequirementClassifier failed to load authoritative model"
    
    info = clf.get_info()
    assert info["ready"] is True
    assert info["num_classes"] == 10
    assert len(info["classes"]) == 10
    assert set(info["classes"]) == set(REQUIREMENT_CLASSES)


# ==============================================================================
# TEST 2: 10 Locked Requirement Classes Classification
# ==============================================================================
def test_2_ten_locked_classes():
    """Verify high-accuracy prediction across all 10 locked petroleum procurement classes."""
    test_cases = [
        ("The bidder must possess a valid GSTIN registration certificate.", "GST_TAX_COMPLIANCE"),
        ("Bidder must be registered under Udyam / MSME portal.", "MSME_UDYAM_ELIGIBILITY"),
        ("Minimum average annual turnover of INR 25 Crore over last 3 fiscal years.", "FINANCIAL_ELIGIBILITY"),
        ("Bidder must have completed natural gas transmission pipeline construction of 100 KM.", "EXPERIENCE_ELIGIBILITY"),
        ("Manufacturer Authorization Form (MAF) from line pipe OEM is mandatory.", "OEM_AUTHORIZATION"),
        ("Affidavit on stamp paper confirming non-blacklisting and no debarment by PSUs.", "BLACKLISTING_DEBARMENT"),
        ("Pipeline outer diameter shall be 24-inch API 5L Grade X70 with 100 bar design pressure.", "TECHNICAL_SPECIFICATION"),
        ("Valves must strictly comply with API 6D and ASME B16.34 standards.", "INDUSTRY_STANDARD_COMPLIANCE"),
        ("Contractor must maintain ISO 45001 Occupational Health and Safety certification.", "SAFETY_REGULATORY_COMPLIANCE"),
        ("Minimum 50 percent local content required under Make in India policy.", "MAKE_IN_INDIA_LOCAL_CONTENT"),
    ]

    for clause, expected_class in test_cases:
        res = requirement_classifier.classify(clause)
        predicted = res.get("predicted_class")
        confidence = res.get("confidence", 0.0)
        assert predicted == expected_class, (
            f"Classification failed for: '{clause}'. Expected {expected_class}, got {predicted} (conf: {confidence:.2f})"
        )
        assert confidence >= 0.40, f"Confidence too low ({confidence:.2f}) for '{clause}'"


# ==============================================================================
# TEST 3: Confidence Scoring & Probability Distributions
# ==============================================================================
def test_3_confidence_scoring_and_distribution():
    """Verify confidence values, probability distributions, and normalization."""
    res = requirement_classifier.classify("Bidder must submit CA certified turnover statements exceeding INR 50 Crore.")
    
    assert "confidence" in res
    assert 0.0 <= res["confidence"] <= 1.0
    assert res["predicted_class"] == "FINANCIAL_ELIGIBILITY"
    
    all_scores = res.get("all_scores", {})
    assert len(all_scores) == 10, f"Expected 10 class probabilities, got {len(all_scores)}"
    for cls_name in REQUIREMENT_CLASSES:
        assert cls_name in all_scores
        assert 0.0 <= all_scores[cls_name] <= 1.0

    total_prob = sum(all_scores.values())
    assert 0.98 <= total_prob <= 1.02, f"Probabilities do not sum to ~1.0: {total_prob}"


# ==============================================================================
# TEST 4: Batch Classification
# ==============================================================================
def test_4_batch_classification():
    """Verify efficient batch classification endpoint and ordering retention."""
    clauses = [
        "Valid GST registration in State of execution is mandatory.",
        "Udyam registration certificate required for MSME exemption.",
        "API Spec 5L line pipe shall be used for cross-country laying."
    ]
    results = requirement_classifier.classify_batch(clauses)
    assert len(results) == 3
    assert results[0]["predicted_class"] == "GST_TAX_COMPLIANCE"
    assert results[1]["predicted_class"] == "MSME_UDYAM_ELIGIBILITY"
    assert results[2]["predicted_class"] in ["INDUSTRY_STANDARD_COMPLIANCE", "TECHNICAL_SPECIFICATION"]

    # Test empty batch
    empty_res = requirement_classifier.classify_batch([])
    assert empty_res == []


# ==============================================================================
# TEST 5: Requirement Extractor Integration (Thresholds & Evidence)
# ==============================================================================
def test_5_requirement_extractor_integration():
    """Verify extraction of numerical thresholds, mandatory flags, and required evidence."""
    clause = "The bidder shall have minimum average turnover of INR 50 Crore over last 3 years."
    extracted = requirement_extractor.extract_from_clause(clause, "REQ-001")
    
    assert extracted["clause_id"] == "REQ-001"
    assert extracted["category"] == "FINANCIAL_ELIGIBILITY"
    assert extracted["mandatory"] is True
    assert extracted["threshold"] == 500000000.0
    assert extracted["threshold_unit"] == "INR"
    assert "AUDITED_BALANCE_SHEET" in extracted["evidence_types"]


# ==============================================================================
# TEST 6: Edge Cases, Empty Inputs & Fallback Heuristics
# ==============================================================================
def test_6_edge_cases_and_fallbacks():
    """Verify graceful handling of empty inputs, whitespace, and fallback behavior."""
    # 1. Empty string
    res_empty = requirement_classifier.classify("")
    assert res_empty["confidence"] == 0.0
    assert "error" in res_empty

    # 2. Whitespace
    res_ws = requirement_classifier.classify("   \n\t  ")
    assert res_ws["confidence"] == 0.0

    # 3. Fallback heuristic verification
    fallback_class, fallback_conf = requirement_classifier._rule_based_fallback("GSTIN verification required")
    assert fallback_class == "GST_TAX_COMPLIANCE"
    assert fallback_conf >= 0.85
