from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.models import AuditLog
from app.core.logging_config import logger

class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        action: str,
        entity_type: str,
        entity_id: str,
        user_id: Optional[str] = None,
        user_name: str = "PROCUREMENT_OFFICER",
        tender_id: Optional[str] = None,
        bidder_id: Optional[str] = None,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
        source: str = "PROCUREMENT_PORTAL",
        ip_address: str = "127.0.0.1"
    ) -> AuditLog:
        try:
            log_entry = AuditLog(
                user_id=user_id,
                user_name=user_name,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                tender_id=tender_id,
                bidder_id=bidder_id,
                previous_state=previous_state,
                new_state=new_state,
                reason=reason,
                source=source,
                model_version="SIH26100-v1.0",
                rule_version="1.0",
                ip_address=ip_address,
                timestamp=datetime.now(timezone.utc)
            )
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
            logger.info(f"[AUDIT] {action} on {entity_type} {entity_id} by {user_name}")
            return log_entry
        except Exception as e:
            logger.error(f"Failed to record audit log: {e}")
            db.rollback()
            return None
