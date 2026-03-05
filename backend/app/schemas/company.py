"""
Pydantic schemas for Company operations.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CompanyBase(BaseModel):
    """Base company schema."""
    ragione_sociale: str
    partita_iva: str = Field(pattern=r"^\d{11}$")
    codice_fiscale: str = Field(pattern=r"^[A-Z0-9]{16}$")
    codice_ateco: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None


class CompanyCreate(CompanyBase):
    """Schema for company creation."""
    pass


class CompanyUpdate(BaseModel):
    """Schema for company update."""
    ragione_sociale: Optional[str] = None
    codice_ateco: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None


class CompanyResponse(CompanyBase):
    """Company response schema."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CompanyStatsResponse(BaseModel):
    """Company statistics response."""
    id: int
    ragione_sociale: str
    total_workers: int
    locations: int
    departments: int
