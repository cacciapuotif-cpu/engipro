"""
Deadline schemas - Pydantic request/response models.
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from app.models.deadline import DeadlineType, DeadlineStatus, DeadlinePriority


class DeadlineBase(BaseModel):
    tipo: DeadlineType
    titolo: str = Field(..., min_length=1, max_length=255)
    descrizione: Optional[str] = Field(None, max_length=1000)
    data_scadenza: date
    stato: DeadlineStatus = DeadlineStatus.PENDING
    priorita: DeadlinePriority = DeadlinePriority.MEDIUM
    giorni_preavviso: int = Field(7, ge=1)
    note: Optional[str] = Field(None, max_length=1000)
    worker_id: Optional[int] = None
    assegnato_a: Optional[int] = None


class DeadlineCreate(DeadlineBase):
    company_id: int


class DeadlineUpdate(BaseModel):
    tipo: Optional[DeadlineType] = None
    titolo: Optional[str] = Field(None, min_length=1, max_length=255)
    descrizione: Optional[str] = Field(None, max_length=1000)
    data_scadenza: Optional[date] = None
    data_completamento: Optional[date] = None
    stato: Optional[DeadlineStatus] = None
    priorita: Optional[DeadlinePriority] = None
    giorni_preavviso: Optional[int] = Field(None, ge=1)
    note: Optional[str] = Field(None, max_length=1000)
    assegnato_a: Optional[int] = None


class DeadlineResponse(DeadlineBase):
    id: int
    company_id: int
    data_completamento: Optional[date] = None
    notification_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
