"""Audit writes use an independent transaction and never fail the request."""
import logging
from datetime import datetime
from typing import Any
from sqlalchemy.orm import Session, Query
from app.core.database import SessionLocal
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    @staticmethod
    def log(**values: Any) -> None:
        try:
            with SessionLocal() as db:
                db.add(AuditLog(**values))
                db.commit()
        except Exception:
            # Do not include values or SQL parameters containing personal data.
            logger.error("Scrittura audit fallita")

    @staticmethod
    def query(db: Session, user_id: int | None = None, resource_type: str | None = None,
              from_date: datetime | None = None, to_date: datetime | None = None,
              skip: int = 0, limit: int | None = 100) -> Query:
        query = db.query(AuditLog)
        if user_id is not None:
            query = query.filter(AuditLog.user_id == user_id)
        if resource_type is not None:
            query = query.filter(AuditLog.resource_type == resource_type)
        if from_date is not None:
            query = query.filter(AuditLog.timestamp >= from_date)
        if to_date is not None:
            query = query.filter(AuditLog.timestamp <= to_date)
        query = query.order_by(AuditLog.timestamp.desc(), AuditLog.id.desc()).offset(skip)
        return query.limit(limit) if limit is not None else query
