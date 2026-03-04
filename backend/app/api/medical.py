"""
Medical API routes - protocolli sanitari e visite mediche.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models import User
from app.models.medical import VisitType, VisitStatus, VisitOutcome
from app.schemas.medical import (
    HealthProtocolCreate, HealthProtocolUpdate, HealthProtocolResponse,
    MedicalVisitCreate, MedicalVisitUpdate, MedicalVisitResponse,
)
from app.services.medical import HealthProtocolService, MedicalVisitService
from pydantic import BaseModel
from datetime import date

router = APIRouter(prefix="/api/v1/medical", tags=["Medical"])


# --- Protocolli Sanitari ---

@router.post("/protocols", response_model=HealthProtocolResponse, status_code=status.HTTP_201_CREATED)
async def create_protocol(
    data: HealthProtocolCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Crea protocollo sanitario."""
    return HealthProtocolService.create(db, data)


@router.get("/protocols", response_model=list[HealthProtocolResponse])
async def list_protocols(
    company_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista protocolli sanitari."""
    return HealthProtocolService.get_all(db, company_id, skip, limit)


@router.get("/protocols/{protocol_id}", response_model=HealthProtocolResponse)
async def get_protocol(
    protocol_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ottieni protocollo per ID."""
    try:
        return HealthProtocolService.get_by_id(db, protocol_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/protocols/{protocol_id}", response_model=HealthProtocolResponse)
async def update_protocol(
    protocol_id: int,
    data: HealthProtocolUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Aggiorna protocollo sanitario."""
    try:
        return HealthProtocolService.update(db, protocol_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/protocols/{protocol_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_protocol(
    protocol_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Elimina protocollo (soft delete)."""
    try:
        HealthProtocolService.delete(db, protocol_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Visite Mediche ---

@router.post("/visits", response_model=MedicalVisitResponse, status_code=status.HTTP_201_CREATED)
async def create_visit(
    data: MedicalVisitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Pianifica visita medica."""
    return MedicalVisitService.create(db, data)


@router.get("/visits", response_model=list[MedicalVisitResponse])
async def list_visits(
    company_id: Optional[int] = Query(None),
    worker_id: Optional[int] = Query(None),
    tipo: Optional[VisitType] = Query(None),
    stato: Optional[VisitStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista visite mediche con filtri."""
    return MedicalVisitService.get_all(db, company_id, worker_id, tipo, stato, skip, limit)


@router.get("/visits/{visit_id}", response_model=MedicalVisitResponse)
async def get_visit(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ottieni visita per ID."""
    try:
        return MedicalVisitService.get_by_id(db, visit_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/visits/{visit_id}", response_model=MedicalVisitResponse)
async def update_visit(
    visit_id: int,
    data: MedicalVisitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Aggiorna visita medica."""
    try:
        return MedicalVisitService.update(db, visit_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


class CompleteVisitRequest(BaseModel):
    esito: VisitOutcome
    data_prossima_visita: Optional[date] = None


@router.post("/visits/{visit_id}/complete", response_model=MedicalVisitResponse)
async def complete_visit(
    visit_id: int,
    data: CompleteVisitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Registra esito visita medica."""
    try:
        return MedicalVisitService.complete(db, visit_id, data.esito, data.data_prossima_visita)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/visits/{visit_id}/cancel", response_model=MedicalVisitResponse)
async def cancel_visit(
    visit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Annulla visita medica."""
    try:
        return MedicalVisitService.cancel(db, visit_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
