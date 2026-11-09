"""
Attendance API routes - timbrature e presenze.
"""
from fastapi import Path, APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.core.database import get_db
from app.core.dependencies import get_company_scope
from app.core.tenancy import require_resource, validate_write, owner_id
from app.core.dependencies import get_current_active_user
from app.models import User
from app.models.attendance import AttendanceStatus
from app.schemas.attendance import (
    TimbratureCreate, TimbratureResponse,
    AttendanceRecordCreate, AttendanceRecordUpdate, AttendanceRecordResponse,
)
from app.services.attendance import TimbratureService, AttendanceRecordService

router = APIRouter(prefix="/api/v1/attendance", tags=["Attendance"])


# --- Timbrature ---

@router.post("/timbrature", response_model=TimbratureResponse, status_code=status.HTTP_201_CREATED)
async def create_timbratura(
    data: TimbratureCreate,
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Registra timbratura entrata/uscita."""
    validate_write(db, data.model_dump(exclude_unset=True), scope, None)
    return TimbratureService.create(db, data)


@router.get("/timbrature/worker/{worker_id}", response_model=list[TimbratureResponse])
async def list_timbrature_by_worker(
    worker_id: int,
    data_inizio: Optional[date] = Query(None),
    data_fine: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista timbrature lavoratore con filtro date."""
    resource = require_resource(db, "worker_id", worker_id, scope)
    return TimbratureService.get_by_worker(db, worker_id, data_inizio, data_fine, skip, limit)


@router.get("/timbrature/company/{company_id}", response_model=list[TimbratureResponse])
async def list_timbrature_by_company(
    company_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista timbrature azienda."""
    resource = require_resource(db, "company_id", company_id, scope)
    return TimbratureService.get_by_company(db, company_id, skip, limit)


# --- Record Presenze ---

@router.post("/records", response_model=AttendanceRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_attendance_record(
    data: AttendanceRecordCreate,
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Crea record presenze manuale."""
    validate_write(db, data.model_dump(exclude_unset=True), scope, None)
    return AttendanceRecordService.create(db, data)


@router.get("/records", response_model=list[AttendanceRecordResponse])
async def list_attendance_records(
    company_id: Optional[int] = Query(None),
    worker_id: Optional[int] = Query(None),
    data_inizio: Optional[date] = Query(None),
    data_fine: Optional[date] = Query(None),
    stato: Optional[AttendanceStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista record presenze con filtri."""
    company_id = scope if scope is not None else company_id
    return AttendanceRecordService.get_all(db, company_id, worker_id, data_inizio, data_fine, stato, skip, limit)


@router.get("/records/{record_id}", response_model=AttendanceRecordResponse)
async def get_attendance_record(
    record_id: int,
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ottieni record presenze per ID."""
    resource = require_resource(db, "record_id", record_id, scope)
    try:
        return AttendanceRecordService.get_by_id(db, record_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/records/{record_id}", response_model=AttendanceRecordResponse)
async def update_attendance_record(
    record_id: int,
    data: AttendanceRecordUpdate,
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Aggiorna record presenze."""
    resource = require_resource(db, "record_id", record_id, scope)
    validate_write(db, data.model_dump(exclude_unset=True), scope, owner_id(db, resource))
    try:
        return AttendanceRecordService.update(db, record_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/records/{record_id}/approve", response_model=AttendanceRecordResponse)
async def approve_attendance_record(
    record_id: int,
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Approva record presenze."""
    resource = require_resource(db, "record_id", record_id, scope)
    try:
        return AttendanceRecordService.approve(db, record_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
