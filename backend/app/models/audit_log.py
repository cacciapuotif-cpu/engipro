"""Append-only record of access to personal data."""
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import String, DateTime, ForeignKey, event
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    action: Mapped[str] = mapped_column(String(10))
    resource_type: Mapped[str] = mapped_column(String(100), index=True)
    resource_id: Mapped[int | None]
    path: Mapped[str] = mapped_column(String(2048))
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(512))
    status_code: Mapped[int]
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True,
        default=lambda: datetime.now(timezone.utc))


@event.listens_for(AuditLog, "before_update")
@event.listens_for(AuditLog, "before_delete")
def prevent_mutation(mapper: Any, connection: Any, target: AuditLog) -> None:
    raise ValueError("Il registro audit è immutabile")
