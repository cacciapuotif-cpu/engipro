"""
Document model - gestione documenti aziendali e lavoratori.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum as SqlEnum, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
from app.core.database import Base


class DocumentCategory(str, PyEnum):
    SICUREZZA = "SICUREZZA"
    FORMAZIONE = "FORMAZIONE"
    MEDICINA = "MEDICINA"
    CONTRATTO = "CONTRATTO"
    DPI = "DPI"
    ALTRO = "ALTRO"


class DocumentStatus(str, PyEnum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    ARCHIVED = "ARCHIVED"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True, index=True)

    # File info
    titolo = Column(String(255), nullable=False, index=True)
    descrizione = Column(String(1000), nullable=True)
    categoria = Column(SqlEnum(DocumentCategory), nullable=False, index=True)
    stato = Column(SqlEnum(DocumentStatus), nullable=False, default=DocumentStatus.ACTIVE, index=True)

    # Storage (MinIO)
    storage_key = Column(String(500), nullable=False, unique=True)
    filename_originale = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    dimensione_bytes = Column(BigInteger, nullable=False)

    # Versioning
    versione = Column(Integer, default=1, nullable=False)
    documento_padre_id = Column(Integer, ForeignKey("documents.id"), nullable=True)

    # Validity
    data_emissione = Column(DateTime(timezone=True), nullable=True)
    data_scadenza = Column(DateTime(timezone=True), nullable=True)

    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)

    # Audit
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    company = relationship("Company", back_populates="documents")
    worker = relationship("Worker", back_populates="documents")
    documento_padre = relationship("Document", foreign_keys=[documento_padre_id], remote_side="Document.id", back_populates="versioni_precedenti")
    versioni_precedenti = relationship("Document", foreign_keys="Document.documento_padre_id", back_populates="documento_padre")

    def __repr__(self) -> str:
        return f"<Document {self.titolo} v{self.versione}>"
