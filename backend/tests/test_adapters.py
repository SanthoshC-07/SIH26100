import pytest
from app.government_adapters import adapters

def test_gst_adapter_valid_format():
    assert adapters.gst.validate_gstin_format("27AABCA1234F1Z5") is True
    assert adapters.gst.validate_gstin_format("INVALID_GST") is False
    assert adapters.gst.validate_gstin_format("") is False

def test_gst_adapter_verification():
    res = adapters.gst.verify_identity("27AABCA1234F1Z5", "Apex Infotech Solutions Private Limited")
    assert res["is_valid"] is True
    assert res["status"] == "ACTIVE"
    assert res["data"]["return_filing_status"] == "COMPLIANT"
    assert "DEMO / MOCK GOVERNMENT SOURCE" in res["source_type"]

def test_pan_adapter():
    assert adapters.pan.validate_pan_format("AABCA1234F") is True
    assert adapters.pan.validate_pan_format("INVALID") is False
    assert adapters.pan.get_pan_entity_type("AABCA1234F") == "COMPANY"
    assert adapters.pan.get_pan_entity_type("AABFB5678G") == "PARTNERSHIP_OR_LLP"
    
    res = adapters.pan.verify_identity("AABCA1234F", "Apex Infotech")
    assert res["is_valid"] is True
    assert res["data"]["status"] == "VALID_ACTIVE"

def test_udyam_adapter():
    assert adapters.udyam.validate_udyam_format("UDYAM-MH-01-0012345") is True
    assert adapters.udyam.validate_udyam_format("UDYAM-12345") is False
    
    res = adapters.udyam.verify_identity("UDYAM-MH-01-0012345", "Apex Infotech")
    assert res["is_valid"] is True
    assert res["data"]["enterprise_type"] == "MEDIUM"

def test_blacklist_adapter():
    # Clear entity
    clear_res = adapters.blacklist.check_entity("Apex Infotech Solutions Private Limited", "AABCA1234F")
    assert clear_res["is_valid"] is True
    assert clear_res["status"] == "CLEAR"

    # Flagged entity
    flagged_res = adapters.blacklist.check_entity("Fraudulent Tech Solutions Ltd", "AABCF9999Z")
    assert flagged_res["is_valid"] is False
    assert flagged_res["status"] == "FLAGGED"
    assert "DEBARRED" in flagged_res["message"]
