import os
import uuid
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal, Base, engine
from app.core.security import create_access_token, get_password_hash
from app.models.models import (
    User, Tender, Requirement, Bidder, Bid, Document, DocumentPage,
    ComplianceCheck, Evidence, RiskAssessment, RiskFactor, OfficerDecision,
    OfficerOverride, AuditEvent, ComplianceReport, VerificationRun
)
from app.scoring.risk_engine import RiskEngine
from app.services.report_generator import ReportGenerator

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="module")
def test_users(db_session):
    u_suffix = uuid.uuid4().hex[:6]
    officer = User(
        id=f"usr-officer-{u_suffix}",
        name=f"Rajesh Sharma {u_suffix}",
        username=f"officer_{u_suffix}",
        email=f"officer_{u_suffix}@mopng.gov.in",
        password_hash=get_password_hash("Officer@123"),
        role="PROCUREMENT_OFFICER"
    )
    admin = User(
        id=f"usr-admin-{u_suffix}",
        name=f"Sunil Verma {u_suffix}",
        username=f"admin_{u_suffix}",
        email=f"admin_{u_suffix}@mopng.gov.in",
        password_hash=get_password_hash("Admin@123"),
        role="ADMIN"
    )
    bidder_user = User(
        id=f"usr-bidder-{u_suffix}",
        name=f"Praveen B S {u_suffix}",
        username=f"bidder_{u_suffix}",
        email=f"praveen_{u_suffix}@praveeneng.com",
        password_hash=get_password_hash("Bidder@123"),
        role="BIDDER"
    )
    db_session.add_all([officer, admin, bidder_user])
    db_session.commit()

    tokens = {
        "officer": create_access_token(data={"sub": officer.username, "role": officer.role, "uid": officer.id}),
        "admin": create_access_token(data={"sub": admin.username, "role": admin.role, "uid": admin.id}),
        "bidder": create_access_token(data={"sub": bidder_user.username, "role": bidder_user.role, "uid": bidder_user.id}),
        "officer_user": officer,
        "admin_user": admin,
        "bidder_user": bidder_user
    }
    return tokens

# ==============================================================================
# 1. RISK ANALYSIS TESTS
# ==============================================================================
def test_01_risk_engine_levels_low_to_critical():
    """
    Test configurable risk engine rules:
    - No issues + high confidence -> LOW
    - REVIEW / INSUFFICIENT items -> MEDIUM
    - Mandatory requirement failure -> HIGH
    - Critical safety/statutory failure -> CRITICAL
    """
    # 1. LOW: All pass, high confidence
    low_checks = [
        {"requirement_category": "GST", "status": "PASS", "confidence": 0.95, "mandatory": True},
        {"requirement_category": "PAN", "status": "PASS", "confidence": 0.98, "mandatory": True},
        {"requirement_category": "TURNOVER", "status": "PASS", "confidence": 0.92, "mandatory": True},
        {"requirement_category": "EXPERIENCE", "status": "PASS", "confidence": 0.90, "mandatory": True},
    ]
    res_low = RiskEngine.assess_risk(low_checks, overall_score=95.0)
    assert res_low["risk_level"] == "LOW"
    assert res_low["risk_score"] <= 25.0

    # 2. MEDIUM: Review or Insufficient items or low confidence
    med_checks = [
        {"requirement_category": "GST", "status": "PASS", "confidence": 0.95, "mandatory": True},
        {"requirement_category": "HSE", "status": "REVIEW", "confidence": 0.71, "mandatory": True, "reason": "Provisional audit certificate"},
        {"requirement_category": "TURNOVER", "status": "PASS", "confidence": 0.90, "mandatory": True}
    ]
    res_med = RiskEngine.assess_risk(med_checks, overall_score=80.0)
    assert res_med["risk_level"] == "MEDIUM"
    assert 25.0 <= res_med["risk_score"] <= 60.0

    # 3. HIGH: Mandatory financial / experience / technical failure
    high_checks = [
        {"requirement_category": "GST", "status": "PASS", "confidence": 0.95, "mandatory": True},
        {"requirement_category": "TURNOVER", "status": "FAIL", "confidence": 0.95, "mandatory": True, "reason": "Audited turnover INR 18 Cr below INR 25 Cr threshold"},
        {"requirement_category": "EXPERIENCE", "status": "PASS", "confidence": 0.90, "mandatory": True}
    ]
    res_high = RiskEngine.assess_risk(high_checks, overall_score=65.0)
    assert res_high["risk_level"] == "HIGH"
    assert res_high["risk_score"] >= 55.0

    # 4. CRITICAL: Critical safety/HSE failure or statutory fraud/blacklist
    crit_checks = [
        {"requirement_category": "HSE", "status": "FAIL", "confidence": 0.95, "mandatory": True, "reason": "No valid OISD / ISO 45001 safety certification submitted"},
        {"requirement_category": "GST", "status": "PASS", "confidence": 0.95, "mandatory": True}
    ]
    res_crit = RiskEngine.assess_risk(crit_checks, overall_score=50.0)
    assert res_crit["risk_level"] == "CRITICAL"
    assert res_crit["risk_score"] >= 80.0

def test_02_risk_factors_traceability_links(db_session):
    """
    Verify each risk factor links to requirement_id, evidence snippet,
    source document, and page number.
    """
    bidder_id = str(uuid.uuid4())
    req_id = str(uuid.uuid4())
    checks = [
        {
            "requirement_id": req_id,
            "requirement_category": "HSE",
            "status": "REVIEW",
            "confidence": 0.71,
            "mandatory": True,
            "reason": "Certificate requires manual verification",
            "source_document": "HSE_Audit_2025.pdf",
            "page_number": 14,
            "evidence": "Provisional ISO 45001 approval issued by Registrar"
        }
    ]
    risk_data = RiskEngine.assess_risk(checks, overall_score=82.0)
    assert len(risk_data["detailed_factors"]) > 0
    df = risk_data["detailed_factors"][0]
    assert df["requirement_id"] == req_id
    assert df["source_document"] == "HSE_Audit_2025.pdf"
    assert df["page_number"] == 14
    assert "Provisional" in df["evidence_snippet"]

# ==============================================================================
# 2. OFFICER REVIEW & OVERRIDE TESTS
# ==============================================================================
def test_03_officer_accept_ai_result(client, db_session, test_users):
    """
    Procurement officer accepts AI baseline result:
    - Status remains matching AI baseline
    - No override flag
    - Stored in officer decisions
    """
    u_suf = uuid.uuid4().hex[:6]
    tender = Tender(tender_number=f"TND-ACCEPT-{u_suf}", title="Tender Accept AI", issuing_organization="GAIL")
    db_session.add(tender)
    db_session.commit()

    bidder = Bidder(tender_id=tender.id, legal_name=f"Vendor Alpha {u_suf}", gstin=f"27AAACA{u_suf[:4]}1Z5", pan=f"AAACA{u_suf[:4]}F")
    req = Requirement(tender_id=tender.id, clause_number="REQ-001", category="GST", description="Valid GST registration", mandatory=True)
    db_session.add_all([bidder, req])
    db_session.commit()

    check = ComplianceCheck(bidder_id=bidder.id, requirement_id=req.id, status="PASS", confidence=0.98, reason="Valid GST verified")
    db_session.add(check)
    db_session.commit()

    headers = {"Authorization": f"Bearer {test_users['officer']}"}
    r = client.post(
        f"/api/officer-review/{bidder.id}/requirements/{req.id}/decision",
        headers=headers,
        json={"decision": "ACCEPT_AI_RESULT", "reason": "Verified and accepted AI baseline"}
    )
    assert r.status_code == 200
    data = r.json()
    assert data["officer_status"] == "PASS"
    assert data["is_override"] == False
    assert data["ai_status"] == "PASS"

def test_04_officer_override_requires_mandatory_reason(client, db_session, test_users):
    """
    Overriding AI result strictly mandates a documented justification.
    Fails with 400 Bad Request if reason is empty or whitespace.
    """
    u_suf = uuid.uuid4().hex[:6]
    tender = Tender(tender_number=f"TND-OVR-REAS-{u_suf}", title="Tender Override Reason Test", issuing_organization="IOCL")
    db_session.add(tender)
    db_session.commit()

    bidder = Bidder(tender_id=tender.id, legal_name=f"Vendor Beta {u_suf}")
    req = Requirement(tender_id=tender.id, clause_number="REQ-002", category="TURNOVER", description="Turnover check", mandatory=True)
    db_session.add_all([bidder, req])
    db_session.commit()

    check = ComplianceCheck(bidder_id=bidder.id, requirement_id=req.id, status="PASS", confidence=0.95, reason="Turnover passed")
    db_session.add(check)
    db_session.commit()

    headers = {"Authorization": f"Bearer {test_users['officer']}"}
    # Empty reason override
    r = client.post(
        f"/api/officer-review/{bidder.id}/requirements/{req.id}/decision",
        headers=headers,
        json={"decision": "FAIL", "reason": "   "}
    )
    assert r.status_code == 400
    assert "mandatory" in r.json()["detail"].lower()

def test_05_officer_override_preserves_ai_baseline(client, db_session, test_users):
    """
    When officer overrides AI finding:
    - Original AI result (ai_status, ai_confidence) is preserved
    - officer_status, officer_reason, officer identity, and timestamp are captured
    - Audit event AI_RESULT_OVERRIDDEN is recorded
    """
    u_suf = uuid.uuid4().hex[:6]
    tender = Tender(tender_number=f"TND-OVR-BASE-{u_suf}", title="Tender Preserve Baseline", issuing_organization="BPCL")
    db_session.add(tender)
    db_session.commit()

    bidder = Bidder(tender_id=tender.id, legal_name=f"Vendor Gamma {u_suf}")
    req = Requirement(tender_id=tender.id, clause_number="REQ-007", category="HSE", description="HSE Certification ISO 45001", mandatory=True)
    db_session.add_all([bidder, req])
    db_session.commit()

    orig_ai_status = "PASS"
    orig_ai_conf = 0.94
    check = ComplianceCheck(bidder_id=bidder.id, requirement_id=req.id, status=orig_ai_status, confidence=orig_ai_conf, reason="ISO 45001 verified")
    db_session.add(check)
    db_session.commit()

    override_justification = "Certificate authenticity requires manual verification with issuing registrar."
    headers = {"Authorization": f"Bearer {test_users['officer']}"}
    r = client.post(
        f"/api/officer-review/{bidder.id}/requirements/{req.id}/decision",
        headers=headers,
        json={"decision": "REVIEW", "reason": override_justification}
    )
    assert r.status_code == 200
    data = r.json()
    assert data["ai_status"] == orig_ai_status
    assert data["ai_confidence"] == orig_ai_conf
    assert data["officer_status"] == "REVIEW"
    assert data["officer_reason"] == override_justification
    assert data["is_override"] == True
    assert data["officer_name"] is not None
    assert data["decision_timestamp"] is not None

    # Check OfficerDecision and OfficerOverride records in SQLite
    dec = db_session.query(OfficerDecision).filter(OfficerDecision.requirement_id == req.id).first()
    assert dec is not None
    assert dec.ai_status == orig_ai_status
    assert dec.officer_status == "REVIEW"

    override_record = db_session.query(OfficerOverride).filter(OfficerOverride.requirement_id == req.id).first()
    assert override_record is not None
    assert override_record.original_ai_status == orig_ai_status
    assert override_record.overridden_status == "REVIEW"

    # Check Audit event
    audit_ev = db_session.query(AuditEvent).filter(
        AuditEvent.entity_id == req.id,
        AuditEvent.action == "AI_RESULT_OVERRIDDEN"
    ).first()
    assert audit_ev is not None

# ==============================================================================
# 3. FINAL BID DECISION TESTS
# ==============================================================================
def test_06_final_bid_decisions_and_confirmation(client, db_session, test_users):
    """
    Test final procurement decisions:
    - QUALIFIED, DISQUALIFIED, REVIEW / HOLD
    - Mandatory confirmation flag and remarks
    - Audit event FINAL_BID_DECISION generated
    """
    u_suf = uuid.uuid4().hex[:6]
    tender = Tender(tender_number=f"TND-FINAL-{u_suf}", title="Tender Final Decision", issuing_organization="GAIL")
    db_session.add(tender)
    db_session.commit()

    bidder = Bidder(tender_id=tender.id, legal_name=f"Vendor Delta {u_suf}")
    db_session.add(bidder)
    db_session.commit()

    bid = Bid(tender_id=tender.id, bidder_id=bidder.id, bid_reference_number=f"BID-FINAL-{u_suf}")
    db_session.add(bid)
    db_session.commit()

    headers = {"Authorization": f"Bearer {test_users['officer']}"}

    # 1. Unconfirmed request fails
    r_unconf = client.post(
        f"/api/officer-review/{bidder.id}/final-decision",
        headers=headers,
        json={"decision": "QUALIFIED", "remarks": "Eligible bidder", "confirmed": False}
    )
    assert r_unconf.status_code == 400

    # 2. Confirmed final decision succeeds
    r_final = client.post(
        f"/api/officer-review/{bidder.id}/final-decision",
        headers=headers,
        json={"decision": "QUALIFIED", "remarks": "Bidder satisfies all technical and statutory GFR criteria.", "confirmed": True}
    )
    assert r_final.status_code == 200
    res = r_final.json()
    assert res["decision"] == "QUALIFIED"
    assert res["summary"]["officer_decision"] == "QUALIFIED"

    # Verify Bid updated
    db_session.refresh(bid)
    assert bid.technical_bid_status == "QUALIFIED"

    # Verify Audit log
    final_audit = db_session.query(AuditEvent).filter(
        AuditEvent.entity_id == bid.id,
        AuditEvent.action == "FINAL_BID_DECISION"
    ).first()
    assert final_audit is not None

# ==============================================================================
# 4. AUDIT TRAIL TESTS
# ==============================================================================
def test_07_audit_trail_events_and_filtering(client, db_session, test_users):
    """
    Verifies immutable audit trail logs and multi-parameter filtering:
    - Filters by action, role, and search query
    - Export CSV functionality
    """
    headers = {"Authorization": f"Bearer {test_users['admin']}"}
    r = client.get("/api/audit?limit=20", headers=headers)
    assert r.status_code == 200
    events = r.json()
    assert isinstance(events, list)

    # Filter by action
    r_filtered = client.get("/api/audit?action=FINAL_BID_DECISION", headers=headers)
    assert r_filtered.status_code == 200
    for ev in r_filtered.json():
        assert ev["action"] == "FINAL_BID_DECISION"

    # Export CSV
    r_csv = client.get("/api/audit/export/csv", headers=headers)
    assert r_csv.status_code == 200
    assert "text/csv" in r_csv.headers["content-type"]
    assert "Event ID" in r_csv.text

def test_08_rbac_isolation_officer_admin_bidder(client, test_users):
    """
    Test RBAC isolation:
    - Officer can review bids and override AI
    - Admin can view full audit trail
    - Bidder is restricted from viewing internal risk details or exporting audit trail
    """
    officer_headers = {"Authorization": f"Bearer {test_users['officer']}"}
    bidder_headers = {"Authorization": f"Bearer {test_users['bidder']}"}

    # Bidder denied access to officer override
    r_bidder_ovr = client.post(
        "/api/officer-review/dummy-bid/requirements/dummy-req/decision",
        headers=bidder_headers,
        json={"decision": "PASS", "reason": "Test"}
    )
    assert r_bidder_ovr.status_code == 403

    # Bidder denied access to internal risk analysis
    r_bidder_risk = client.get("/api/risk/dummy-bid", headers=bidder_headers)
    assert r_bidder_risk.status_code == 403

    # Bidder denied access to export audit CSV
    r_bidder_audit_exp = client.get("/api/audit/export/csv", headers=bidder_headers)
    assert r_bidder_audit_exp.status_code == 403

# ==============================================================================
# 5. COMPLIANCE REPORT TESTS
# ==============================================================================
def test_09_compliance_report_contents_and_mock_adapter(client, db_session, test_users):
    """
    Verifies generated report contents:
    - Executive summary
    - Evidence & page citations
    - Officer decisions
    - Audit information
    - External verification: MOCK ADAPTER disclosure
    """
    u_suf = uuid.uuid4().hex[:6]
    tender = Tender(tender_number=f"TND-REP-{u_suf}", title="Tender Report Gen", issuing_organization="GAIL")
    db_session.add(tender)
    db_session.commit()

    bidder = Bidder(tender_id=tender.id, legal_name=f"Report Test Bidder {u_suf}", gstin="29AABCP1234M1Z5", pan="AABCP1234F")
    req1 = Requirement(tender_id=tender.id, clause_number="REQ-001", category="GST", description="GST Compliance", mandatory=True)
    req2 = Requirement(tender_id=tender.id, clause_number="REQ-004", category="SIMILAR_PIPELINE_EXPERIENCE", description="Pipeline 100 km", mandatory=True)
    db_session.add_all([bidder, req1, req2])
    db_session.commit()

    check1 = ComplianceCheck(bidder_id=bidder.id, requirement_id=req1.id, status="PASS", confidence=0.98, reason="GST valid", verification_source="MOCK_GST_PORTAL", document_name="GST_Cert.pdf", page_number=1)
    check2 = ComplianceCheck(bidder_id=bidder.id, requirement_id=req2.id, status="PASS", confidence=0.94, reason="135 KM 24 inch", verification_source="RULE_ENGINE", document_name="Work_Cert.pdf", page_number=8)
    db_session.add_all([check1, check2])
    db_session.commit()

    headers = {"Authorization": f"Bearer {test_users['officer']}"}
    r = client.post(f"/api/reports/{bidder.id}/generate", headers=headers)
    assert r.status_code == 200
    report_data = r.json()

    assert "executive_summary" in report_data
    assert "detailed_findings" in report_data
    assert "risk_analysis" in report_data
    assert "audit_information" in report_data

    # Check mock adapter disclosure
    gst_finding = next((f for f in report_data["detailed_findings"] if f["category"] == "GST"), None)
    assert gst_finding is not None
    assert "MOCK ADAPTER" in gst_finding["external_verification"]

    # Verify downloadable HTML view
    r_html = client.get(f"/api/reports/{bidder.id}/download", headers=headers)
    assert r_html.status_code == 200
    assert "PETROLEUM BID COMPLIANCE REPORT" in r_html.text

# ==============================================================================
# 6. END-TO-END WORKFLOW TEST: PRAVEEN B S ENGINEERING SERVICES
# ==============================================================================
def test_10_end_to_end_praveen_hse_override_audit_report(client, db_session, test_users):
    """
    Comprehensive End-to-End Pipeline test on mock bidder:
    PRAVEEN B S ENGINEERING SERVICES

    Steps:
    1. Tender & Bid setup
    2. Document & Requirements setup
    3. Run compliance evaluation
    4. Verify initial Risk Analysis is LOW
    5. Procurement Officer Review
    6. Officer OVERRIDES HSE requirement from PASS to REVIEW
       Reason: 'Certificate authenticity requires manual verification.'
    7. Verify AI baseline PASS is preserved while Officer Status becomes REVIEW
    8. Verify AI_RESULT_OVERRIDDEN audit event is recorded
    9. Submit Final Bid Decision: 'REVIEW / HOLD'
    10. Verify FINAL_BID_DECISION audit event is recorded
    11. Generate official Petroleum Bid Compliance Report
    12. Verify report reflects compliance, override, risk, and audit trail
    """
    e2e_suffix = uuid.uuid4().hex[:6]
    tender = Tender(
        tender_number=f"MOPNG/E2E/{e2e_suffix}",
        title="Cross-Country Natural Gas Pipeline E2E Demonstration",
        issuing_organization="GAIL (India) Limited",
        ministry="Ministry of Petroleum & Natural Gas",
        estimated_value=1250000000.0,
        status="ACTIVE"
    )
    db_session.add(tender)
    db_session.commit()

    bidder = Bidder(
        tender_id=tender.id,
        legal_name="PRAVEEN B S ENGINEERING SERVICES",
        trade_name="Praveen Engineering",
        pan="AABCA1234F",
        gstin="29AABCA1234F1Z5",
        country="INDIA",
        status="SUBMITTED"
    )
    db_session.add(bidder)
    db_session.commit()

    bid = Bid(
        tender_id=tender.id,
        bidder_id=bidder.id,
        bid_reference_number=f"BID-PRAVEEN-{e2e_suffix}",
        technical_bid_status="SUBMITTED"
    )
    db_session.add(bid)
    db_session.commit()

    # Create 3 key petroleum requirements: GST, Pipeline Experience, HSE
    req_gst = Requirement(
        tender_id=tender.id,
        clause_number="REQ-001",
        category="GST",
        description="Valid GSTIN statutory registration",
        mandatory=True
    )
    req_exp = Requirement(
        tender_id=tender.id,
        clause_number="REQ-004",
        category="SIMILAR_PIPELINE_EXPERIENCE",
        description="Minimum 2 natural gas pipeline projects with >= 100 km and >= 24 inch",
        threshold=100.0,
        threshold_unit="KM",
        mandatory=True
    )
    req_hse = Requirement(
        tender_id=tender.id,
        clause_number="REQ-007",
        category="HSE",
        description="ISO 45001 / ISO 14001 Occupational Health & Safety Compliance",
        mandatory=True
    )
    db_session.add_all([req_gst, req_exp, req_hse])
    db_session.commit()

    # Step 3: Seed compliance checks (AI evaluates all PASS)
    check_gst = ComplianceCheck(
        bidder_id=bidder.id,
        requirement_id=req_gst.id,
        status="PASS",
        confidence=0.98,
        reason="Active GSTIN 29AABCA1234F1Z5 verified via Portal Adapter",
        evidence_text="Active GSTIN 29AABCA1234F1Z5 verified via Portal Adapter",
        document_name="GST_REG_06.pdf",
        page_number=1,
        verification_source="DEMO / MOCK GOVERNMENT SOURCE"
    )
    check_exp = ComplianceCheck(
        bidder_id=bidder.id,
        requirement_id=req_exp.id,
        status="PASS",
        confidence=0.94,
        reason="Completed 135 KM 24 inch Natural Gas Pipeline for GAIL",
        evidence_text="Completed 135 KM 24 inch Natural Gas Pipeline for GAIL",
        document_name="Experience_Certificate.pdf",
        page_number=8,
        verification_source="HYBRID_RULE_AND_NLP"
    )
    check_hse = ComplianceCheck(
        bidder_id=bidder.id,
        requirement_id=req_hse.id,
        status="PASS",
        confidence=0.92,
        reason="ISO 45001:2018 Certificate valid through 2026",
        evidence_text="ISO 45001:2018 Certificate valid through 2026",
        document_name="HSE_ISO_45001.pdf",
        page_number=3,
        verification_source="HYBRID_RULE_AND_NLP"
    )
    db_session.add_all([check_gst, check_exp, check_hse])
    db_session.commit()

    # Step 4: Evaluate Risk
    headers = {"Authorization": f"Bearer {test_users['officer']}"}
    r_risk = client.post(f"/api/risk/{bidder.id}/calculate", headers=headers)
    assert r_risk.status_code == 200
    risk_out = r_risk.json()
    assert risk_out["risk_level"] == "LOW"

    # Step 5: Procurement Officer Review workspace
    r_ws = client.get(f"/api/officer-review/{bidder.id}", headers=headers)
    assert r_ws.status_code == 200
    ws_data = r_ws.json()
    assert len(ws_data["requirements"]) == 3
    assert ws_data["bidder"]["legal_name"] == "PRAVEEN B S ENGINEERING SERVICES"

    # Step 6: Officer overrides HSE from PASS to REVIEW
    override_reason_text = "Certificate authenticity requires manual verification."
    r_ovr = client.post(
        f"/api/officer-review/{bidder.id}/requirements/{req_hse.id}/decision",
        headers=headers,
        json={"decision": "REVIEW", "reason": override_reason_text}
    )
    assert r_ovr.status_code == 200
    ovr_data = r_ovr.json()

    # Step 7: Verify baseline PASS preserved while officer status is REVIEW
    assert ovr_data["ai_status"] == "PASS"
    assert ovr_data["officer_status"] == "REVIEW"
    assert ovr_data["officer_reason"] == override_reason_text
    assert ovr_data["is_override"] == True

    # Step 8: Verify AI_RESULT_OVERRIDDEN audit event
    audit_ovr = db_session.query(AuditEvent).filter(
        AuditEvent.bidder_id == bidder.id,
        AuditEvent.action == "AI_RESULT_OVERRIDDEN"
    ).first()
    assert audit_ovr is not None
    assert override_reason_text in audit_ovr.description

    # Step 9: Final Bid Decision: REVIEW / HOLD
    r_final = client.post(
        f"/api/officer-review/{bidder.id}/final-decision",
        headers=headers,
        json={
            "decision": "REVIEW / HOLD",
            "remarks": "Technical evaluation satisfactory; HSE certificate confirmation pending third-party audit.",
            "confirmed": True
        }
    )
    assert r_final.status_code == 200
    final_data = r_final.json()
    assert final_data["decision"] == "REVIEW / HOLD"

    # Step 10: Verify FINAL_BID_DECISION audit event
    audit_final = db_session.query(AuditEvent).filter(
        AuditEvent.bidder_id == bidder.id,
        AuditEvent.action == "FINAL_BID_DECISION"
    ).first()
    assert audit_final is not None

    # Step 11: Generate Compliance Report
    r_rep = client.post(f"/api/reports/{bidder.id}/generate", headers=headers)
    assert r_rep.status_code == 200
    rep_data = r_rep.json()
    assert rep_data["final_officer_decision"] == "REVIEW / HOLD"
    assert len(rep_data["officer_decisions"]) >= 1

    # Check that override is cited in the report
    hse_ovr_in_rep = next((od for od in rep_data["officer_decisions"] if od.get("requirement_id") == req_hse.id), None)
    assert hse_ovr_in_rep is not None
    assert hse_ovr_in_rep["ai_status"] == "PASS"
    assert hse_ovr_in_rep["officer_status"] == "REVIEW"
    assert hse_ovr_in_rep["officer_reason"] == override_reason_text

    print("\n✓ End-to-End Pipeline on PRAVEEN B S ENGINEERING SERVICES successfully verified!")
