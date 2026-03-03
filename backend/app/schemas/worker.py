"""
Pydantic schemas for Worker operations.
"""
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from app.models.worker import ContractType, WorkerStatus


class WorkerBase(BaseModel):
    """Base worker schema."""
    codice_fiscale: str = Field(regex=r"^[A-Z0-9]{16}$")
    nome: str = Field(min_length=1, max_length=100)
    cognome: str = Field(min_length=1, max_length=100)
    data_nascita: date
    luogo_nascita: Optional[str] = None
    mansione: str = Field(min_length=1, max_length=255)
    tipo_contratto: ContractType = ContractType.FULL_TIME
    data_assunzione: date
    data_cessazione: Optional[date] = None


class WorkerCreate(WorkerBase):
    """Schema for worker creation."""
    company_id: int
    location_id: Optional[int] = None
    department_id: Optional[int] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    is_rspp: bool = False
    is_rls: bool = False
    is_medico_competente: bool = False


class WorkerUpdate(BaseModel):
    """Schema for worker update."""
    nome: Optional[str] = None
    cognome: Optional[str] = None
    mansione: Optional[str] = None
    tipo_contratto: Optional[ContractType] = None
    data_cessazione: Optional[date] = None
    location_id: Optional[int] = None
    department_id: Optional[int] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    is_rspp: Optional[bool] = None
    is_rls: Optional[bool] = None
    is_medico_competente: Optional[bool] = None
    stato: Optional[WorkerStatus] = None


class WorkerResponse(WorkerBase):
    """Worker response schema."""
    id: int
    company_id: int
    location_id: Optional[int]
    department_id: Optional[int]
    email: Optional[str]
    telefono: Optional[str]
    stato: WorkerStatus
    is_rspp: bool
    is_rls: bool
    is_medico_competente: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkerListResponse(BaseModel):
    """Worker list item schema (minimal)."""
    id: int
    nome: str
    cognome: str
    codice_fiscale: str
    mansione: str
    stato: WorkerStatus
    is_active: bool


class WorkerHistoryResponse(BaseModel):
    """Worker history/mansioni response."""
    id: int
    worker_id: int
    mansione_precedente: str
    mansione_nuova: str
    data_cambio: datetime
    note: Optional[str] = None
