import csv
import io
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.core.database import get_db
from app.models.models import AuditEvent, AuditLog, User
from app.schemas.schemas import AuditEventResponse, AuditLogResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/audit", tags=["Audit Trail"])

@router.get("", response_model=List[AuditEventResponse])
def get_audit_events(
    tender_id: Optional[str] = None,
    bidder_id: Optional[str] = None,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    role: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Returns auditable events per Section 4 GFR 2017.
    Procurement Officers and Admins can query full audit log.
    Bidders can only view public events related to their own bids.
    """
    # RBAC protection: Bidders must not view audit trail
    if current_user and current_user.role == "BIDDER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied."
        )

    query = db.query(AuditEvent)

    if tender_id:
        query = query.filter(AuditEvent.tender_id == tender_id)
    if bidder_id:
        query = query.filter(AuditEvent.bidder_id == bidder_id)
    if user_id:
        query = query.filter(AuditEvent.user_id == user_id)
    if action:
        query = query.filter(AuditEvent.action == action)
    if role:
        query = query.filter(AuditEvent.role == role)

    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                AuditEvent.description.ilike(search_fmt),
                AuditEvent.action.ilike(search_fmt),
                AuditEvent.user_name.ilike(search_fmt),
                AuditEvent.entity_type.ilike(search_fmt)
            )
        )

    if start_date:
        try:
            sd = datetime.fromisoformat(start_date)
            query = query.filter(AuditEvent.timestamp >= sd)
        except ValueError:
            pass

    if end_date:
        try:
            ed = datetime.fromisoformat(end_date)
            query = query.filter(AuditEvent.timestamp <= ed)
        except ValueError:
            pass

    # If bidder user, filter out internal officer notes or override reasons
    if current_user and current_user.role == "BIDDER":
        query = query.filter(
            AuditEvent.action.notin_(["AI_RESULT_OVERRIDDEN", "OFFICER_REVIEWED", "LOGIN", "LOGOUT"])
        )

    # Ensure limit and offset are integers even if invoked directly
    limit_val = int(getattr(limit, "default", limit) if not isinstance(limit, int) else limit)
    offset_val = int(getattr(offset, "default", offset) if not isinstance(offset, int) else offset)

    events = query.order_by(AuditEvent.timestamp.desc()).offset(offset_val).limit(limit_val).all()
    return events

@router.get("/{bid_id}", response_model=List[AuditEventResponse])
def get_bid_audit_events(
    bid_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Retrieves complete lifecycle audit records for a specific bid submission.
    """
    return get_audit_events(bidder_id=bid_id, limit=500, offset=0, db=db, current_user=current_user)

@router.get("/export/csv")
def export_audit_csv(
    tender_id: Optional[str] = None,
    bidder_id: Optional[str] = None,
    action: Optional[str] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Exports filtered immutable audit trail as CSV for official oversight archiving.
    """
    if current_user and current_user.role == "BIDDER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bidders do not have authorization to export system audit records."
        )

    events = get_audit_events(
        tender_id=tender_id,
        bidder_id=bidder_id,
        action=action,
        role=role,
        limit=500,
        offset=0,
        db=db,
        current_user=current_user
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Event ID", "Timestamp (UTC)", "User Name", "Role", "Action", "Entity Type", "Entity ID", "Description"])

    for ev in events:
        writer.writerow([
            ev.event_id,
            ev.timestamp.isoformat() if ev.timestamp else "",
            ev.user_name,
            ev.role,
            ev.action,
            ev.entity_type,
            ev.entity_id,
            ev.description
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=GeM_Procurement_Audit_Trail.csv"}
    )

# ----------------- BACKWARD COMPATIBILITY -----------------
@router.get("/logs", response_model=List[AuditLogResponse])
def get_legacy_audit_logs(
    tender_id: Optional[str] = None,
    bidder_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    if tender_id:
        query = query.filter(AuditLog.tender_id == tender_id)
    if bidder_id:
        query = query.filter(AuditLog.bidder_id == bidder_id)
    if action:
        query = query.filter(AuditLog.action == action)
        
    logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return logs
