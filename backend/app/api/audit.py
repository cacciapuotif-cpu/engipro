"""Administrator-only audit queries and streamed CSV export."""
import csv
import io
from collections.abc import Iterator
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_role
from app.models import UserRole
from app.services.audit import AuditService

router = APIRouter(prefix="/api/v1/audit", tags=["Audit"],
                   dependencies=[Depends(require_role(UserRole.ADMIN))])


class AuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int | None
    action: str
    resource_type: str
    resource_id: int | None
    path: str
    ip_address: str | None
    user_agent: str | None
    status_code: int
    timestamp: datetime


@router.get("/logs", response_model=list[AuditResponse])
def list_logs(user_id: int | None = None, resource_type: str | None = None,
              from_date: datetime | None = None, to_date: datetime | None = None,
              skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000),
              db: Session = Depends(get_db)) -> list:
    return AuditService.query(db, user_id, resource_type, from_date, to_date, skip, limit).all()


@router.get("/logs/export")
def export_logs(user_id: int | None = None, resource_type: str | None = None,
                from_date: datetime | None = None, to_date: datetime | None = None,
                db: Session = Depends(get_db)) -> StreamingResponse:
    def rows() -> Iterator[str]:
        fields = list(AuditResponse.model_fields)
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(fields)
        yield buffer.getvalue()
        for row in AuditService.query(db, user_id, resource_type, from_date, to_date, limit=None).yield_per(500):
            buffer.seek(0)
            buffer.truncate(0)
            values = [getattr(row, field) for field in fields]
            values = [("'" + value) if isinstance(value, str) and value.startswith(("=", "+", "-", "@", "\t", "\r")) else value for value in values]
            writer.writerow(values)
            yield buffer.getvalue()
    return StreamingResponse(rows(), media_type="text/csv",
                             headers={"Content-Disposition": 'attachment; filename="audit.csv"'})
