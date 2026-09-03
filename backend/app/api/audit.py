from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import AuditLog
from app.schemas.schemas import AuditLogResponse

router = APIRouter(prefix="/audit", tags=["Audit Trail"])

@router.get("", response_model=List[AuditLogResponse])
def get_audit_logs(
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
