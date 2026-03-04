"""
Training schemas - Pydantic request/response models.
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from app.models.training import CourseType, CourseStatus, EditionStatus, Attestato


class CourseBase(BaseModel):
    codice: str = Field(..., min_length=1, max_length=50)
    titolo: str = Field(..., min_length=1, max_length=255)
    descrizione: Optional[str] = Field(None, max_length=1000)
    tipo: CourseType = CourseType.OBBLIGATORIO
    durata_ore: float = Field(8.0, ge=0.5)
    validita_anni: Optional[int] = Field(None, ge=1)
    provider: Optional[str] = Field(None, max_length=255)


class CourseCreate(CourseBase):
    company_id: int


class CourseUpdate(BaseModel):
    titolo: Optional[str] = Field(None, min_length=1, max_length=255)
    descrizione: Optional[str] = Field(None, max_length=1000)
    tipo: Optional[CourseType] = None
    stato: Optional[CourseStatus] = None
    durata_ore: Optional[float] = Field(None, ge=0.5)
    validita_anni: Optional[int] = Field(None, ge=1)
    provider: Optional[str] = Field(None, max_length=255)


class CourseResponse(CourseBase):
    id: int
    company_id: int
    stato: CourseStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EditionBase(BaseModel):
    data_inizio: date
    data_fine: date
    luogo: Optional[str] = Field(None, max_length=255)
    docente: Optional[str] = Field(None, max_length=255)
    max_partecipanti: Optional[int] = Field(None, ge=1)
    note: Optional[str] = Field(None, max_length=1000)


class EditionCreate(EditionBase):
    course_id: int


class EditionUpdate(BaseModel):
    data_inizio: Optional[date] = None
    data_fine: Optional[date] = None
    luogo: Optional[str] = Field(None, max_length=255)
    docente: Optional[str] = Field(None, max_length=255)
    max_partecipanti: Optional[int] = Field(None, ge=1)
    stato: Optional[EditionStatus] = None
    note: Optional[str] = Field(None, max_length=1000)


class EditionResponse(EditionBase):
    id: int
    course_id: int
    stato: EditionStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ParticipationBase(BaseModel):
    worker_id: int
    esito: Attestato = Attestato.ASSENTE
    data_attestato: Optional[date] = None
    data_scadenza_attestato: Optional[date] = None
    numero_attestato: Optional[str] = Field(None, max_length=100)
    note: Optional[str] = Field(None, max_length=500)


class ParticipationCreate(ParticipationBase):
    edition_id: int


class ParticipationUpdate(BaseModel):
    esito: Optional[Attestato] = None
    data_attestato: Optional[date] = None
    data_scadenza_attestato: Optional[date] = None
    numero_attestato: Optional[str] = Field(None, max_length=100)
    note: Optional[str] = Field(None, max_length=500)


class ParticipationResponse(ParticipationBase):
    id: int
    edition_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
