"""Explicit ownership checks shared by domain endpoints."""
from typing import Any
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import (Company, Worker, Location, Department, Deadline, Document,
                        HealthProtocol, MedicalVisit, Course, CourseEdition,
                        CourseParticipation, DPIItem, DPIAssignment, AttendanceRecord)

RESOURCES: dict[str, type] = {
    "company_id": Company, "worker_id": Worker, "responsabile_id": Worker, "assegnato_a": Worker,
    "location_id": Location, "department_id": Department, "deadline_id": Deadline,
    "document_id": Document, "documento_padre_id": Document,
    "protocol_id": HealthProtocol, "visit_id": MedicalVisit, "course_id": Course,
    "edition_id": CourseEdition, "participation_id": CourseParticipation,
    "item_id": DPIItem, "dpi_item_id": DPIItem, "assignment_id": DPIAssignment,
    "record_id": AttendanceRecord,
}


def owner_id(db: Session, resource: Any) -> int:
    if isinstance(resource, Company):
        return resource.id
    if isinstance(resource, CourseEdition):
        return require_resource(db, "course_id", resource.course_id, None).company_id
    if isinstance(resource, CourseParticipation):
        return owner_id(db, require_resource(db, "edition_id", resource.edition_id, None))
    return resource.company_id


def require_resource(db: Session, field: str, resource_id: int, scope: int | None) -> Any:
    resource = db.query(RESOURCES[field]).filter(RESOURCES[field].id == resource_id).first()
    if resource is None or (scope is not None and owner_id(db, resource) != scope):
        raise HTTPException(404, "Risorsa non trovata")
    return resource


def validate_write(db: Session, values: dict[str, Any], scope: int | None,
                   existing_company: int | None = None) -> None:
    company = values.get("company_id", existing_company)
    if existing_company is not None and company != existing_company:
        raise HTTPException(403, "Trasferimento tra aziende non consentito")
    if scope is not None and company is not None and company != scope:
        raise HTTPException(403, "Azienda non autorizzata")
    if company is not None:
        require_resource(db, "company_id", company, scope)
    for field, value in values.items():
        if field in RESOURCES and field != "company_id" and value is not None:
            linked = require_resource(db, field, value, scope)
            linked_company = owner_id(db, linked)
            if company is None:
                company = linked_company
            if company != linked_company:
                raise HTTPException(403, "Risorse appartenenti ad aziende diverse")
    key = values.get("storage_key")
    if key and company is not None and not key.startswith(f"companies/{company}/documents/"):
        raise HTTPException(403, "Chiave documento non autorizzata")
