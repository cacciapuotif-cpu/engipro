"""
Deadlines API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models import User
from app.models.deadline import DeadlineStatus
from app.schemas.deadline import DeadlineCreate, DeadlineUpdate, DeadlineResponse
from app.services.deadline import DeadlineService

router = APIRouter(prefix="/api/v1/deadlines", tags=["Deadlines"])


@router.post("", response_model=DeadlineResponse, status_code=status.HTTP_201_CREATED)
async def create_deadline(
    data: DeadlineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Crea una nuova scadenza."""
    return DeadlineService.create(db, data)


@router.get("", response_model=list[DeadlineResponse])
async def list_deadlines(
    company_id: Optional[int] = Query(None),
    worker_id: Optional[int] = Query(None),
    stato: Optional[DeadlineStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista scadenze con filtri opzionali."""
    return DeadlineService.get_all(db, company_id, worker_id, stato, skip, limit)


@router.get("/{deadline_id}", response_model=DeadlineResponse)
async def get_deadline(
    deadline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ottieni scadenza per ID."""
    try:
        return DeadlineService.get_by_id(db, deadline_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{deadline_id}", response_model=DeadlineResponse)
async def update_deadline(
    deadline_id: int,
    data: DeadlineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Aggiorna scadenza."""
    try:
        return DeadlineService.update(db, deadline_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{deadline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deadline(
    deadline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Elimina scadenza."""
    try:
        DeadlineService.delete(db, deadline_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{deadline_id}/complete", response_model=DeadlineResponse)
async def complete_deadline(
    deadline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Segna scadenza come completata."""
    try:
        return DeadlineService.complete(db, deadline_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
