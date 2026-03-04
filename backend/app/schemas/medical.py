"""
Medical schemas - Pydantic request/response models.
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from app.models.medical import VisitType, VisitOutcome, VisitStatus


class HealthProtocolBase(BaseModel):
    titolo: str = Field(..., min_length=1, max_length=255)
    descrizione: Optional[str] = None
    data_approvazione: Optional[date] = None
    medico_competente: Optional[str] = Field(None, max_length=255)


class HealthProtocolCreate(HealthProtocolBase):
    company_id: int


class HealthProtocolUpdate(BaseModel):
    titolo: Optional[str] = Field(None, min_length=1, max_length=255)
    descrizione: Optional[str] = None
    data_approvazione: Optional[date] = None
    medico_competente: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class HealthProtocolResponse(HealthProtocolBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MedicalVisitBase(BaseModel):
    tipo: VisitType
    data_visita: date
    data_prossima_visita: Optional[date] = None
    medico: Optional[str] = Field(None, max_length=255)
    struttura: Optional[str] = Field(None, max_length=255)
    limitazioni: Optional[str] = None
    prescrizioni: Optional[str] = None
    note: Optional[str] = None
    protocol_id: Optional[int] = None


class MedicalVisitCreate(MedicalVisitBase):
    worker_id: int
    company_id: int


class MedicalVisitUpdate(BaseModel):
    tipo: Optional[VisitType] = None
    stato: Optional[VisitStatus] = None
    esito: Optional[VisitOutcome] = None
    data_visita: Optional[date] = None
    data_prossima_visita: Optional[date] = None
    medico: Optional[str] = Field(None, max_length=255)
    struttura: Optional[str] = Field(None, max_length=255)
    limitazioni: Optional[str] = None
    prescrizioni: Optional[str] = None
    note: Optional[str] = None


class MedicalVisitResponse(MedicalVisitBase):
    id: int
    worker_id: int
    company_id: int
    stato: VisitStatus
    esito: Optional[VisitOutcome] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
