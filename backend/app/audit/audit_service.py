from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.models import AuditLog, AuditEvent, User
from app.core.logging_config import logger

class AuditService:
    """
    Phase 5: Section 4 GFR 2017 Compliant Immutable Audit Service.
    Supports logging and retrieving auditable system actions across the procurement lifecycle.
    """

    @staticmethod
    def log_event(
        db: Session,
        action: str,
        entity_type: str,
        entity_id: str,
        user_id: Optional[str] = None,
        user_name: str = "SYSTEM",
        role: str = "SYSTEM",
        tender_id: Optional[str] = None,
        bidder_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """
        Records an immutable audit event in compliance with GFR 2017.
        """
        try:
            valid_user_id = None
            detected_role = role or "SYSTEM"
            detected_name = user_name or "SYSTEM"

            if user_id and user_id != "system":
                u = db.query(User).filter(User.id == user_id).first()
                if u:
                    valid_user_id = u.id
                    detected_role = u.role or detected_role
                    detected_name = u.name or u.username or detected_name

            event = AuditEvent(
                user_id=valid_user_id,
                user_name=detected_name,
                role=detected_role,
                action=action,
                entity_type=entity_type,
                entity_id=str(entity_id),
                tender_id=tender_id,
                bidder_id=bidder_id,
                description=description or f"{action} executed on {entity_type} {entity_id}",
                metadata_payload=metadata or {},
                timestamp=datetime.now(timezone.utc)
            )
            db.add(event)

            # Dual-write to legacy AuditLog for backward compatibility with existing tests
            legacy_log = AuditLog(
                user_id=valid_user_id,
                user_name=detected_name,
                action=action,
                entity_type=entity_type,
                entity_id=str(entity_id),
                tender_id=tender_id,
                bidder_id=bidder_id,
                previous_state=(metadata or {}).get("previous_state"),
                new_state=(metadata or {}).get("new_state"),
                reason=description or (metadata or {}).get("reason"),
                source="MOPNG_PIPELINE_PORTAL",
                model_version="SIH26100-v2.0",
                rule_version="2.0",
                ip_address="127.0.0.1",
                timestamp=datetime.now(timezone.utc)
            )
            db.add(legacy_log)

            db.commit()
            db.refresh(event)
            logger.info(f"[AUDIT EVENT] {action} on {entity_type} ({entity_id}) by {detected_name} [{detected_role}]")
            return event
        except Exception as e:
            logger.error(f"Failed to record audit event: {e}")
            db.rollback()
            return None

    @classmethod
    def log_action(
        cls,
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
        """
        Legacy entry point for backwards compatibility across existing controllers.
        Also records the immutable AuditEvent automatically.
        """
        meta = {
            "previous_state": previous_state,
            "new_state": new_state,
            "reason": reason,
            "source": source,
            "ip_address": ip_address
        }
        cls.log_event(
            db=db,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            user_name=user_name,
            role="PROCUREMENT_OFFICER" if "OFFICER" in (user_name or "") else "SYSTEM",
            tender_id=tender_id,
            bidder_id=bidder_id,
            description=reason or f"{action} on {entity_type} {entity_id}",
            metadata=meta
        )
        
        # Query and return the corresponding AuditLog entry
        log_entry = db.query(AuditLog).filter(
            AuditLog.entity_id == str(entity_id),
            AuditLog.action == action
        ).order_by(AuditLog.timestamp.desc()).first()
        return log_entry
