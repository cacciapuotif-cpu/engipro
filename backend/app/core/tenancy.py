"""Request-local tenant filtering, shared by all domain routers.

The ORM listener belongs only to the request Session and also filters counts,
relationship loads and indirect resources. No process-global tenant state exists.
"""
from collections.abc import AsyncIterator
from typing import Any
from fastapi import Depends, HTTPException, Request
from sqlalchemy import event, select
from sqlalchemy.orm import ORMExecuteState, Session, with_loader_criteria
from app.core.database import get_db
from app.core.dependencies import get_company_scope
from app.models import (
    Company, Worker, Location, Department, Deadline, Document, HealthProtocol,
    MedicalVisit, Course, CourseEdition, CourseParticipation, DPIItem,
    DPIAssignment, Timbratura, AttendanceRecord,
)

DIRECT = (Worker, Location, Department, Deadline, Document, HealthProtocol,
          MedicalVisit, Course, DPIItem, DPIAssignment, Timbratura, AttendanceRecord)
REFERENCES: dict[str, Any] = {
    'company_id': Company, 'worker_id': Worker, 'responsabile_id': Worker,
    'assegnato_a': Worker, 'location_id': Location, 'department_id': Department,
    'deadline_id': Deadline, 'document_id': Document, 'documento_padre_id': Document,
    'protocol_id': HealthProtocol, 'visit_id': MedicalVisit, 'course_id': Course,
    'edition_id': CourseEdition, 'participation_id': CourseParticipation,
    'item_id': DPIItem, 'dpi_item_id': DPIItem, 'assignment_id': DPIAssignment,
    'record_id': AttendanceRecord,
}


async def enforce_company_scope(
    request: Request,
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
) -> AsyncIterator[None]:
    if scope is None:
        yield
        return

    def filter_queries(state: ORMExecuteState) -> None:
        if state.is_select or state.is_update or state.is_delete:
            options = [with_loader_criteria(model, model.company_id == scope, include_aliases=True) for model in DIRECT]
            options.extend([
                with_loader_criteria(Company, (Company.id == scope) & Company.is_active.is_(True), include_aliases=True),
                with_loader_criteria(CourseEdition, CourseEdition.course_id.in_(select(Course.id).where(Course.company_id == scope)), include_aliases=True),
                with_loader_criteria(CourseParticipation,
                    CourseParticipation.worker_id.in_(select(Worker.id).where(Worker.company_id == scope))
                    & CourseParticipation.edition_id.in_(select(CourseEdition.id).join(Course).where(Course.company_id == scope)), include_aliases=True),
            ])
            state.statement = state.statement.options(*options)

    event.listen(db, 'do_orm_execute', filter_queries)
    try:
        if db.query(Company).filter(Company.id == scope).first() is None:
            raise HTTPException(status_code=403, detail='Azienda non attiva')
        # Check referenced resources even on subresource lists (404, never existence leaks).
        for name, value in request.path_params.items():
            model = REFERENCES.get(name)
            if model is not None and db.query(model).filter(model.id == value).first() is None:
                raise HTTPException(status_code=404, detail='Risorsa non trovata')
        if request.method in ('POST', 'PUT', 'PATCH'):
            content_type = request.headers.get('content-type', '')
            data: Any = {}
            if 'application/json' in content_type:
                try:
                    data = await request.json()
                except ValueError:
                    data = {}
            elif 'multipart/form-data' in content_type:
                data = dict(await request.form())
            if isinstance(data, dict):
                if data.get('company_id') is not None and str(data['company_id']) != str(scope):
                    raise HTTPException(status_code=403, detail='Azienda non autorizzata')
                for name, value in data.items():
                    model = REFERENCES.get(name)
                    if model is not None and value is not None and db.query(model).filter(model.id == value).first() is None:
                        raise HTTPException(status_code=403, detail='Riferimento non autorizzato')
        yield
    finally:
        event.remove(db, 'do_orm_execute', filter_queries)
