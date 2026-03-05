"""
DPI API routes - catalogo, assegnazioni e verbali.
"""
from fastapi import Path, APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models import User
from app.models.dpi import DPICategory, DPIStatus
from app.schemas.dpi import (
    DPIItemCreate, DPIItemUpdate, DPIItemResponse,
    DPIAssignmentCreate, DPIAssignmentUpdate, DPIAssignmentResponse,
)
from app.services.dpi import DPIItemService, DPIAssignmentService

router = APIRouter(prefix="/api/v1/dpi", tags=["DPI"])


# --- Catalogo DPI ---

@router.post("/items", response_model=DPIItemResponse, status_code=status.HTTP_201_CREATED)
async def create_dpi_item(
    data: DPIItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Crea nuovo DPI nel catalogo."""
    return DPIItemService.create(db, data)


@router.get("/items", response_model=list[DPIItemResponse])
async def list_dpi_items(
    company_id: Optional[int] = Query(None),
    categoria: Optional[DPICategory] = Query(None),
    stato: Optional[DPIStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista DPI con filtri."""
    return DPIItemService.get_all(db, company_id, categoria, stato, skip, limit)


@router.get("/items/{item_id}", response_model=DPIItemResponse)
async def get_dpi_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ottieni DPI per ID."""
    try:
        return DPIItemService.get_by_id(db, item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/items/{item_id}", response_model=DPIItemResponse)
async def update_dpi_item(
    item_id: int,
    data: DPIItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Aggiorna DPI."""
    try:
        return DPIItemService.update(db, item_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dpi_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Elimina DPI (soft delete)."""
    try:
        DPIItemService.delete(db, item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Assegnazioni ---

@router.post("/assignments", response_model=DPIAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    data: DPIAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Assegna DPI a lavoratore."""
    return DPIAssignmentService.create(db, data)


@router.get("/assignments", response_model=list[DPIAssignmentResponse])
async def list_assignments_by_company(
    company_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista assegnazioni azienda."""
    return DPIAssignmentService.get_by_company(db, company_id, skip, limit)


@router.get("/workers/{worker_id}/assignments", response_model=list[DPIAssignmentResponse])
async def list_assignments_by_worker(
    worker_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista DPI assegnati a un lavoratore."""
    return DPIAssignmentService.get_by_worker(db, worker_id, skip, limit)


@router.get("/assignments/{assignment_id}", response_model=DPIAssignmentResponse)
async def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ottieni assegnazione per ID."""
    try:
        return DPIAssignmentService.get_by_id(db, assignment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/assignments/{assignment_id}", response_model=DPIAssignmentResponse)
async def update_assignment(
    assignment_id: int,
    data: DPIAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Aggiorna assegnazione DPI."""
    try:
        return DPIAssignmentService.update(db, assignment_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/assignments/{assignment_id}/return", response_model=DPIAssignmentResponse)
async def return_dpi(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Registra restituzione DPI."""
    try:
        return DPIAssignmentService.return_dpi(db, assignment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
