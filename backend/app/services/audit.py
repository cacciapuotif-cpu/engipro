"""Isolated, best-effort audit writer and filterable queries."""
import logging
from datetime import datetime
from sqlalchemy.orm import Session, Query
from app.core.database import SessionLocal
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    @staticmethod
    def log(*, user_id: int | None, action: str, resource_type: str,
            resource_id: int | None, path: str, ip_address: str,
            user_agent: str, status_code: int) -> None:
        try:
            with SessionLocal() as db:
                db.add(AuditLog(user_id=user_id, action=action, resource_type=resource_type,
                                resource_id=resource_id, path=path[:2048], ip_address=ip_address[:45],
                                user_agent=user_agent[:512], status_code=status_code))
                db.commit()
        except Exception:
            logger.error('Impossibile scrivere il registro audit', exc_info=True)

    @staticmethod
    def query(db: Session, user_id: int | None = None, resource_type: str | None = None,
              from_date: datetime | None = None, to_date: datetime | None = None) -> Query[AuditLog]:
        query = db.query(AuditLog)
        if user_id is not None:
            query = query.filter(AuditLog.user_id == user_id)
        if resource_type is not None:
            query = query.filter(AuditLog.resource_type == resource_type)
        if from_date is not None:
            query = query.filter(AuditLog.timestamp >= from_date)
        if to_date is not None:
            query = query.filter(AuditLog.timestamp <= to_date)
        return query.order_by(AuditLog.timestamp.desc(), AuditLog.id.desc())
