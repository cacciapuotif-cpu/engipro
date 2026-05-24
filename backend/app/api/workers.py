"""
Worker management API routes.
"""
from fastapi import Path, APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_role
from app.models import User, UserRole, WorkerStatus
from app.schemas.worker import (
    WorkerCreate,
    WorkerUpdate,
    WorkerResponse,
    WorkerListResponse,
)
from app.services.worker import WorkerService

router = APIRouter(prefix="/api/v1/workers", tags=["Workers"])


# ── Routes with fixed path segments MUST come before /{worker_id} wildcard ──

@router.get("/search", response_model=list[WorkerListResponse])
async def search_workers(
    company_id: int = Query(..., ge=1),
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Search workers by name, CF, or mansione."""
    workers = WorkerService.search(db, company_id, q)
    return workers


@router.get("/roles/rspp", response_model=list[WorkerListResponse])
async def get_rspp_list(
    company_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all RSPP workers in company."""
    workers = WorkerService.get_rspp_list(db, company_id)
    return workers


@router.get("/roles/rls", response_model=list[WorkerListResponse])
async def get_rls_list(
    company_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all RLS workers in company."""
    workers = WorkerService.get_rls_list(db, company_id)
    return workers


@router.get("/cf/{codice_fiscale}", response_model=WorkerResponse)
async def get_worker_by_cf(
    codice_fiscale: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get worker by codice fiscale."""
    try:
        worker = WorkerService.get_by_cf(db, codice_fiscale)
        return worker
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/department/{department_id}", response_model=list[WorkerListResponse])
async def get_workers_by_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all workers in a department."""
    workers = WorkerService.get_by_department(db, department_id)
    return workers


@router.get("/location/{location_id}", response_model=list[WorkerListResponse])
async def get_workers_by_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all workers in a location/sede."""
    workers = WorkerService.get_by_location(db, location_id)
    return workers


# ── Generic CRUD endpoints ──

@router.post("", response_model=WorkerResponse, status_code=status.HTTP_201_CREATED)
async def create_worker(
    worker_data: WorkerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.COMPANY_ADMIN, UserRole.HR)),
):
    """Create a new worker."""
    try:
        worker = WorkerService.create(db, worker_data)
        return worker
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("", response_model=list[WorkerListResponse])
async def list_workers(
    company_id: int = Query(None, ge=1),
    status: WorkerStatus = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List workers. Without company_id returns all workers (ADMIN only)."""
    try:
        if company_id is None:
            from app.models import Worker as WorkerModel
            query = db.query(WorkerModel)
            if status:
                query = query.filter(WorkerModel.stato == status)
            return query.offset(skip).limit(limit).all()
        workers = WorkerService.get_all(db, company_id, skip, limit, status)
        return workers
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{worker_id}", response_model=WorkerResponse)
async def get_worker(
    worker_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get worker by ID."""
    try:
        worker = WorkerService.get_by_id(db, worker_id)
        return worker
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/{worker_id}", response_model=WorkerResponse)
async def update_worker(
    worker_id: int,
    worker_data: WorkerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.COMPANY_ADMIN, UserRole.HR, UserRole.MANAGER)),
):
    """Update worker."""
    try:
        worker = WorkerService.update(db, worker_id, worker_data)
        return worker
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{worker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_worker(
    worker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.COMPANY_ADMIN)),
):
    """Soft delete worker."""
    try:
        WorkerService.delete(db, worker_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/{worker_id}/status/{new_status}", response_model=WorkerResponse)
async def change_worker_status(
    worker_id: int,
    new_status: WorkerStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.COMPANY_ADMIN, UserRole.HR)),
):
    """Change worker status."""
    try:
        worker = WorkerService.change_status(db, worker_id, new_status)
        return worker
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
