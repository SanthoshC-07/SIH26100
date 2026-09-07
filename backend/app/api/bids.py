from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Bid, Tender, Bidder, User
from app.schemas.schemas import BidCreate, BidResponse
from app.api.deps import get_current_user, require_role, verify_bid_ownership
from app.audit.audit_service import AuditService

router = APIRouter(prefix="/bids", tags=["Bids"])

@router.get("", response_model=List[BidResponse])
def list_bids(
    tender_id: Optional[str] = None,
    bidder_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Bid)
    
    # Object-level isolation: Bidder can ONLY see their own bids
    if current_user.role == "BIDDER":
        effective_id = current_user.effective_bidder_id
        if not effective_id:
            return []
        query = query.filter(Bid.bidder_id == effective_id)
    else:
        if bidder_id:
            query = query.filter(Bid.bidder_id == bidder_id)

    if tender_id:
        query = query.filter(Bid.tender_id == tender_id)

    return query.order_by(Bid.created_at.desc()).all()

@router.post("", response_model=BidResponse, status_code=status.HTTP_201_CREATED)
def submit_bid(
    bid_in: BidCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("BIDDER"))
):
    # Enforce bidder ownership: bidder can only submit bids for their own registered bidder profile
    effective_id = current_user.effective_bidder_id
    if not effective_id or bid_in.bidder_id != effective_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied."
        )

    tender = db.query(Tender).filter(Tender.id == bid_in.tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    
    bidder = db.query(Bidder).filter(Bidder.id == bid_in.bidder_id).first()
    if not bidder:
        raise HTTPException(status_code=404, detail="Bidder not found")

    bid = Bid(
        tender_id=bid_in.tender_id,
        bidder_id=bid_in.bidder_id,
        bid_reference_number=bid_in.bid_reference_number,
        submission_date=bid_in.submission_date,
        technical_bid_status=bid_in.technical_bid_status,
        financial_bid_amount=bid_in.financial_bid_amount,
        currency=bid_in.currency or "INR",
        remarks=bid_in.remarks
    )
    db.add(bid)
    db.commit()
    db.refresh(bid)

    AuditService.log_event(
        db=db,
        action="BID_SUBMITTED",
        entity_type="BID",
        entity_id=bid.id,
        user_id=current_user.id,
        user_name=current_user.name,
        role=current_user.role,
        tender_id=tender.id,
        bidder_id=bidder.id,
        description=f"Bidder {bidder.legal_name} submitted formal bid {bid.bid_reference_number}"
    )

    return bid

@router.get("/{id}", response_model=BidResponse)
def get_bid(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bid = verify_bid_ownership(id, current_user, db)
    return bid

@router.get("/{id}/documents")
def get_bid_documents(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bid = verify_bid_ownership(id, current_user, db)
    
    from app.models.models import Document
    docs = db.query(Document).filter(Document.bidder_id == bid.bidder_id).all()
    results = []
    for d in docs:
        results.append({
            "id": d.id,
            "bidder_id": d.bidder_id,
            "tender_id": d.tender_id,
            "document_name": d.document_name,
            "original_filename": d.original_filename or d.document_name,
            "document_type": d.document_type,
            "file_size": d.file_size,
            "mime_type": d.mime_type,
            "is_scanned": d.is_scanned,
            "page_count": d.page_count,
            "extraction_method": d.extraction_method or ("TESSERACT_OCR" if d.is_scanned else "PDF_TEXT"),
            "upload_timestamp": d.upload_timestamp or d.created_at,
            "entities_count": len(d.entities) if d.entities else 0
        })
    return results

@router.get("/{id}/requirements")
def get_bid_requirements(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bid = verify_bid_ownership(id, current_user, db)
    
    from app.api.compliance import run_compliance_evaluation
    eval_res = run_compliance_evaluation(bid.id, db)
    reqs = eval_res.get("requirements", [])

    # If caller is BIDDER, do not leak internal notes or raw confidence scores
    if current_user.role == "BIDDER":
        sanitized = []
        for r in reqs:
            sanitized.append({
                "id": r.get("id"),
                "clause_number": r.get("clause_number"),
                "category": r.get("category"),
                "description": r.get("description"),
                "mandatory": r.get("mandatory"),
                "status": r.get("status"),
                "reason": r.get("reason"),
                "evidence": r.get("evidence")
            })
        return sanitized

    return reqs

