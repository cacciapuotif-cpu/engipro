"""
DPI schemas - Pydantic request/response models.
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from app.models.dpi import DPICategory, DPIStatus, AssignmentStatus


class DPIItemBase(BaseModel):
    codice: str = Field(..., min_length=1, max_length=50)
    nome: str = Field(..., min_length=1, max_length=255)
    descrizione: Optional[str] = None
    categoria: DPICategory
    marca: Optional[str] = Field(None, max_length=100)
    modello: Optional[str] = Field(None, max_length=100)
    taglia: Optional[str] = Field(None, max_length=20)
    numero_serie: Optional[str] = Field(None, max_length=100)
    data_acquisto: Optional[date] = None
    data_scadenza: Optional[date] = None
    costo: Optional[float] = Field(None, ge=0)
    note: Optional[str] = None


class DPIItemCreate(DPIItemBase):
    company_id: int


class DPIItemUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    descrizione: Optional[str] = None
    categoria: Optional[DPICategory] = None
    stato: Optional[DPIStatus] = None
    marca: Optional[str] = Field(None, max_length=100)
    modello: Optional[str] = Field(None, max_length=100)
    taglia: Optional[str] = Field(None, max_length=20)
    data_scadenza: Optional[date] = None
    costo: Optional[float] = Field(None, ge=0)
    note: Optional[str] = None


class DPIItemResponse(DPIItemBase):
    id: int
    company_id: int
    stato: DPIStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DPIAssignmentBase(BaseModel):
    worker_id: int
    data_assegnazione: date
    note: Optional[str] = None
    firma_ricevuta: bool = False


class DPIAssignmentCreate(DPIAssignmentBase):
    dpi_item_id: int
    company_id: int


class DPIAssignmentUpdate(BaseModel):
    stato: Optional[AssignmentStatus] = None
    data_restituzione: Optional[date] = None
    note: Optional[str] = None
    firma_ricevuta: Optional[bool] = None


class DPIAssignmentResponse(DPIAssignmentBase):
    id: int
    dpi_item_id: int
    company_id: int
    stato: AssignmentStatus
    data_restituzione: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
