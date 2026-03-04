"""
Document schemas - Pydantic request/response models.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.document import DocumentCategory, DocumentStatus


class DocumentBase(BaseModel):
    titolo: str = Field(..., min_length=1, max_length=255)
    descrizione: Optional[str] = Field(None, max_length=1000)
    categoria: DocumentCategory
    data_emissione: Optional[datetime] = None
    data_scadenza: Optional[datetime] = None
    worker_id: Optional[int] = None


class DocumentCreate(DocumentBase):
    company_id: int
    filename_originale: str
    mime_type: str
    dimensione_bytes: int
    storage_key: str


class DocumentUpdate(BaseModel):
    titolo: Optional[str] = Field(None, min_length=1, max_length=255)
    descrizione: Optional[str] = Field(None, max_length=1000)
    categoria: Optional[DocumentCategory] = None
    stato: Optional[DocumentStatus] = None
    data_emissione: Optional[datetime] = None
    data_scadenza: Optional[datetime] = None


class DocumentResponse(DocumentBase):
    id: int
    company_id: int
    stato: DocumentStatus
    storage_key: str
    filename_originale: str
    mime_type: str
    dimensione_bytes: int
    versione: int
    documento_padre_id: Optional[int] = None
    is_active: bool
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    upload_url: str
    storage_key: str
    document_id: int
