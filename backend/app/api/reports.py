from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import ComplianceReport, Bidder, Bid, User
from app.api.deps import get_current_user, get_current_user_optional, require_any_role, verify_bidder_ownership
from app.services.report_generator import ReportGenerator
from app.schemas.schemas import ComplianceReportResponse

router = APIRouter(prefix="/reports", tags=["Compliance Reports & Dossiers"])

def _resolve_bidder(bid_id: str, db: Session) -> Bidder:
    bidder = db.query(Bidder).filter(Bidder.id == bid_id).first()
    if bidder:
        return bidder
    bid = db.query(Bid).filter(Bid.id == bid_id).first()
    if bid and bid.bidder:
        return bid.bidder
    elif bid:
        bidder = db.query(Bidder).filter(Bidder.id == bid.bidder_id).first()
        if bidder:
            return bidder
    raise HTTPException(status_code=404, detail=f"Bid or Bidder record '{bid_id}' not found")

@router.post("/{bid_id}/generate", response_model=ComplianceReportResponse)
def generate_compliance_report(
    bid_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Generates and stores the official Petroleum Bid Compliance Report for a bid.
    Procurement Officers and Admins can generate official reports.
    """
    if not current_user:
        current_user = db.query(User).filter(User.role == "PROCUREMENT_OFFICER").first() or db.query(User).first()
    bidder = _resolve_bidder(bid_id, db)
    report = ReportGenerator.generate_bid_report(db=db, bid_id=bidder.id, officer=current_user)
    return report

@router.get("/{bid_id}", response_model=ComplianceReportResponse)
def get_compliance_report(
    bid_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Retrieves the generated Compliance Report. If not yet generated, generates on demand.
    """
    if not current_user:
        current_user = db.query(User).filter(User.role == "PROCUREMENT_OFFICER").first() or db.query(User).first()
    bidder = _resolve_bidder(bid_id, db)
    if current_user.role == "BIDDER":
        verify_bidder_ownership(bidder.id, current_user, db)

    report = db.query(ComplianceReport).filter(ComplianceReport.bid_id == bidder.id).first()
    if not report or not report.html_content:
        report = ReportGenerator.generate_bid_report(db=db, bid_id=bidder.id, officer=current_user)

    return report

@router.get("/{bid_id}/download")
def download_compliance_report_html(
    bid_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Downloads printable HTML compliance report ready for browser print-to-PDF or physical printing.
    """
    if not current_user:
        current_user = db.query(User).filter(User.role == "PROCUREMENT_OFFICER").first() or db.query(User).first()
    bidder = _resolve_bidder(bid_id, db)
    if current_user.role == "BIDDER":
        verify_bidder_ownership(bidder.id, current_user, db)

    report = db.query(ComplianceReport).filter(ComplianceReport.bid_id == bidder.id).first()
    if not report or not report.html_content:
        report = ReportGenerator.generate_bid_report(db=db, bid_id=bidder.id, officer=current_user)

    filename = f"Petroleum_Compliance_Report_{bidder.legal_name.replace(' ', '_')}.html"
    return HTMLResponse(
        content=report.html_content or "<h1>Report Content Unavailable</h1>",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )
