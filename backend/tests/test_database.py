import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlite3 import Connection as SQLite3Connection
from fastapi.testclient import TestClient

from app.core.database import Base
from app.models.models import (
    User, Tender, Requirement, Bidder, Bid, BidderProject, BidderPersonnel,
    Document, Evidence, ComplianceCheck, AuditLog
)
from app.main import app

# In-memory SQLite for test isolation
TEST_SQLITE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    test_engine = create_engine(
        TEST_SQLITE_URL,
        connect_args={"check_same_thread": False}
    )
    
    @event.listens_for(test_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, SQLite3Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
            
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


def test_1_sqlite_connection_and_foreign_keys_pragma(db_session):
    """Test that SQLite connection is active and foreign keys are enforced via PRAGMA."""
    result = db_session.execute(text("PRAGMA foreign_keys;")).scalar()
    assert result == 1, "PRAGMA foreign_keys must be enabled (1) for SQLite"


def test_2_tender_and_requirements_crud(db_session):
    """Test creating a Tender and associated Tender Requirements."""
    user = User(
        name="Sunil Verma",
        email="sunil.verma@mopng.gov.in",
        username="sverma",
        password_hash="hashed_pw_123",
        role="PROCUREMENT_OFFICER"
    )
    db_session.add(user)
    db_session.commit()

    tender = Tender(
        tender_number="MOPNG/PIPE/TEST/001",
        title="150 KM Natural Gas Pipeline EPC",
        issuing_organization="GAIL (India) Limited",
        ministry="Ministry of Petroleum & Natural Gas",
        created_by=user.id
    )
    db_session.add(tender)
    db_session.commit()

    req1 = Requirement(
        tender_id=tender.id,
        category="TURNOVER",
        description="Minimum average turnover of INR 25 Crore",
        threshold=25.0,
        threshold_unit="CRORE",
        mandatory=True
    )
    req2 = Requirement(
        tender_id=tender.id,
        category="SIMILAR_PIPELINE_EXPERIENCE",
        description="Minimum 100 KM natural gas pipeline",
        required_pipeline_length_km=100.0,
        required_pipeline_type="NATURAL_GAS",
        mandatory=True
    )
    db_session.add_all([req1, req2])
    db_session.commit()

    # Query back and verify relationships
    saved_tender = db_session.query(Tender).filter_by(tender_number="MOPNG/PIPE/TEST/001").first()
    assert saved_tender is not None
    assert len(saved_tender.requirements) == 2
    assert saved_tender.creator.email == "sunil.verma@mopng.gov.in"


def test_3_bidder_projects_personnel_and_documents(db_session):
    """Test Bidder, BidderProject, BidderPersonnel, and Document persistence in SQLite."""
    tender = Tender(
        tender_number="MOPNG/PIPE/TEST/002",
        title="200 KM Cross-Country Crude Pipeline",
        issuing_organization="IOCL"
    )
    db_session.add(tender)
    db_session.commit()

    bidder = Bidder(
        tender_id=tender.id,
        legal_name="PRAVEEN B S ENGINEERING SERVICES",
        trade_name="Praveen Petro-Pipelines",
        pan="BSZPP1234K",
        gstin="29MOCKP1234M1Z5",
        status="SUBMITTED"
    )
    db_session.add(bidder)
    db_session.commit()

    # Add Project
    project = BidderProject(
        bidder_id=bidder.id,
        project_name="GAIL 135 KM Pipeline EPC",
        client_name="GAIL (India) Limited",
        pipeline_length_km=135.0,
        pipeline_diameter="24 inch NB API 5L X70",
        project_value=82.0
    )
    db_session.add(project)

    # Add Personnel
    personnel = BidderPersonnel(
        bidder_id=bidder.id,
        name="Praveen Kumar B S",
        designation="Chief Pipeline Project Manager",
        qualification="B.Tech Mechanical & NDT Level II",
        years_of_experience=12.0
    )
    db_session.add(personnel)

    # Add Document
    doc = Document(
        bidder_id=bidder.id,
        tender_id=tender.id,
        document_name="Pipeline_Completion_Certificate.pdf",
        document_type="EXPERIENCE_CERTIFICATE",
        file_path="uploads/demo.pdf",
        extraction_method="PDF_TEXT"
    )
    db_session.add(doc)
    db_session.commit()

    saved_bidder = db_session.query(Bidder).filter_by(pan="BSZPP1234K").first()
    assert saved_bidder is not None
    assert len(saved_bidder.projects) == 1
    assert saved_bidder.projects[0].pipeline_length_km == 135.0
    assert len(saved_bidder.personnel) == 1
    assert len(saved_bidder.documents) == 1


def test_4_compliance_check_evidence_and_audit_log(db_session):
    """Test ComplianceCheck, Evidence items, and GFR 2017 Audit Log persistence."""
    tender = Tender(tender_number="MOPNG/PIPE/TEST/003", title="Test Tender")
    db_session.add(tender)
    db_session.commit()

    req = Requirement(tender_id=tender.id, category="GST", mandatory=True)
    bidder = Bidder(tender_id=tender.id, legal_name="Praveen Pipelines Ltd", gstin="29MOCKP1234M1Z5")
    db_session.add_all([req, bidder])
    db_session.commit()

    check = ComplianceCheck(
        bidder_id=bidder.id,
        requirement_id=req.id,
        status="PASS",
        confidence=0.98,
        reason="Valid active GSTIN registered to bidder verified via mock portal."
    )
    db_session.add(check)
    db_session.commit()

    evidence = Evidence(
        compliance_check_id=check.id,
        document_name="GST_Registration_Certificate.pdf",
        page_number=1,
        source_text="GSTIN: 29MOCKP1234M1Z5 Status: ACTIVE",
        confidence=0.98
    )
    db_session.add(evidence)

    audit = AuditLog(
        user_name="Rajesh Sharma",
        action="VERIFY_REQUIREMENT",
        entity_type="COMPLIANCE_CHECK",
        entity_id=check.id,
        tender_id=tender.id,
        bidder_id=bidder.id,
        new_state={"status": "PASS", "confidence": 0.98}
    )
    db_session.add(audit)
    db_session.commit()

    saved_check = db_session.query(ComplianceCheck).filter_by(id=check.id).first()
    assert saved_check is not None
    assert len(saved_check.evidence_items) == 1
    assert saved_check.evidence_items[0].page_number == 1

    saved_audit = db_session.query(AuditLog).filter_by(action="VERIFY_REQUIREMENT").first()
    assert saved_audit is not None
    assert saved_audit.user_name == "Rajesh Sharma"


def test_5_api_health_and_endpoints():
    """Test FastAPI endpoints with SQLite backend."""
    client = TestClient(app)
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

    res_tenders = client.get("/api/tenders")
    assert res_tenders.status_code == 200
    assert isinstance(res_tenders.json(), list)
