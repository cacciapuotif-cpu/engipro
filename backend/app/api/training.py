"""
Training API routes - corsi, edizioni, partecipazioni.
"""
from fastapi import Path, APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_company_scope
from app.core.tenancy import require_resource, validate_write, owner_id
from app.core.dependencies import get_current_active_user
from app.models import User
from app.schemas.training import (
    CourseCreate, CourseUpdate, CourseResponse,
    EditionCreate, EditionUpdate, EditionResponse,
    ParticipationCreate, ParticipationUpdate, ParticipationResponse,
)
from app.services.training import CourseService, EditionService, ParticipationService

router = APIRouter(prefix="/api/v1/training", tags=["Training"])


# --- Corsi ---

@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    data: CourseCreate,
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Crea un nuovo corso."""
    validate_write(db, data.model_dump(exclude_unset=True), scope, None)
    return CourseService.create(db, data)


@router.get("/courses", response_model=list[CourseResponse])
async def list_courses(
    company_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista corsi."""
    company_id = scope if scope is not None else company_id
    return CourseService.get_all(db, company_id, skip, limit)


@router.get("/courses/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: int,
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ottieni corso per ID."""
    resource = require_resource(db, "course_id", course_id, scope)
    try:
        return CourseService.get_by_id(db, course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    data: CourseUpdate,
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Aggiorna corso."""
    resource = require_resource(db, "course_id", course_id, scope)
    validate_write(db, data.model_dump(exclude_unset=True), scope, owner_id(db, resource))
    try:
        return CourseService.update(db, course_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Elimina corso (soft delete)."""
    resource = require_resource(db, "course_id", course_id, scope)
    try:
        CourseService.delete(db, course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Edizioni ---

@router.post("/editions", response_model=EditionResponse, status_code=status.HTTP_201_CREATED)
async def create_edition(
    data: EditionCreate,
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Crea una nuova edizione."""
    validate_write(db, data.model_dump(exclude_unset=True), scope, None)
    return EditionService.create(db, data)


@router.get("/courses/{course_id}/editions", response_model=list[EditionResponse])
async def list_editions(
    course_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista edizioni di un corso."""
    resource = require_resource(db, "course_id", course_id, scope)
    return EditionService.get_by_course(db, course_id, skip, limit)


@router.get("/editions/{edition_id}", response_model=EditionResponse)
async def get_edition(
    edition_id: int,
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ottieni edizione per ID."""
    resource = require_resource(db, "edition_id", edition_id, scope)
    try:
        return EditionService.get_by_id(db, edition_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/editions/{edition_id}", response_model=EditionResponse)
async def update_edition(
    edition_id: int,
    data: EditionUpdate,
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Aggiorna edizione."""
    resource = require_resource(db, "edition_id", edition_id, scope)
    validate_write(db, data.model_dump(exclude_unset=True), scope, owner_id(db, resource))
    try:
        return EditionService.update(db, edition_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/editions/{edition_id}/complete", response_model=EditionResponse)
async def complete_edition(
    edition_id: int,
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Segna edizione come completata."""
    resource = require_resource(db, "edition_id", edition_id, scope)
    try:
        return EditionService.complete(db, edition_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Partecipazioni ---

@router.post("/participations", response_model=ParticipationResponse, status_code=status.HTTP_201_CREATED)
async def create_participation(
    data: ParticipationCreate,
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Registra partecipazione lavoratore."""
    validate_write(db, data.model_dump(exclude_unset=True), scope, None)
    return ParticipationService.create(db, data)


@router.get("/editions/{edition_id}/participations", response_model=list[ParticipationResponse])
async def list_participations_by_edition(
    edition_id: int,
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista partecipanti a un'edizione."""
    resource = require_resource(db, "edition_id", edition_id, scope)
    return ParticipationService.get_by_edition(db, edition_id)


@router.get("/workers/{worker_id}/participations", response_model=list[ParticipationResponse])
async def list_participations_by_worker(
    worker_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista formazione di un lavoratore."""
    resource = require_resource(db, "worker_id", worker_id, scope)
    return ParticipationService.get_by_worker(db, worker_id, skip, limit)


@router.put("/participations/{participation_id}", response_model=ParticipationResponse)
async def update_participation(
    participation_id: int,
    data: ParticipationUpdate,
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Aggiorna partecipazione/attestato."""
    resource = require_resource(db, "participation_id", participation_id, scope)
    validate_write(db, data.model_dump(exclude_unset=True), scope, owner_id(db, resource))
    try:
        return ParticipationService.update(db, participation_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/participations/{participation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_participation(
    participation_id: int,
    scope: int | None = Depends(get_company_scope),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Elimina partecipazione."""
    resource = require_resource(db, "participation_id", participation_id, scope)
    try:
        ParticipationService.delete(db, participation_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
