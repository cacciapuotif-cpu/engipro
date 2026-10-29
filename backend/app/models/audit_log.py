"""Append-only access trail; request bodies and credentials are never stored."""
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, event
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    action = Column(String(10), nullable=False)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(Integer, nullable=True)
    path = Column(String(2048), nullable=False)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(512), nullable=False)
    status_code = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, default=lambda: datetime.now(timezone.utc))


@event.listens_for(AuditLog, 'before_update')
@event.listens_for(AuditLog, 'before_delete')
def reject_audit_mutation(mapper: Any, connection: Any, target: AuditLog) -> None:
    raise ValueError('Il registro audit è immutabile')
