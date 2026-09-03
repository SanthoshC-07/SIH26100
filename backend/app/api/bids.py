from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Bid, Tender, Bidder, User
from app.schemas.schemas import BidCreate, BidResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/bids", tags=["Bids"])

@router.get("", response_model=List[BidResponse])
def list_bids(
    tender_id: Optional[str] = None,
    bidder_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Bid)
    if tender_id:
        query = query.filter(Bid.tender_id == tender_id)
    if bidder_id:
        query = query.filter(Bid.bidder_id == bidder_id)
    return query.order_by(Bid.created_at.desc()).all()

@router.post("", response_model=BidResponse)
def submit_bid(
    bid_in: BidCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
    return bid

@router.get("/{id}", response_model=BidResponse)
def get_bid(id: str, db: Session = Depends(get_db)):
    bid = db.query(Bid).filter(Bid.id == id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    return bid
