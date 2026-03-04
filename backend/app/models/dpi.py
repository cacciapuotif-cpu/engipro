"""
DPI model - gestione Dispositivi di Protezione Individuale.
"""
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey, Enum as SqlEnum, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
from app.core.database import Base


class DPICategory(str, PyEnum):
    TESTA = "TESTA"
    OCCHI_VISO = "OCCHI_VISO"
    UDITO = "UDITO"
    VIE_RESPIRATORIE = "VIE_RESPIRATORIE"
    MANI_BRACCIA = "MANI_BRACCIA"
    PIEDI_GAMBE = "PIEDI_GAMBE"
    CORPO = "CORPO"
    ANTICADUTA = "ANTICADUTA"
    ALTRO = "ALTRO"


class DPIStatus(str, PyEnum):
    AVAILABLE = "AVAILABLE"
    ASSIGNED = "ASSIGNED"
    MAINTENANCE = "MAINTENANCE"
    DISPOSED = "DISPOSED"


class AssignmentStatus(str, PyEnum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    LOST = "LOST"


class DPIItem(Base):
    """Catalogo DPI."""
    __tablename__ = "dpi_items"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    codice = Column(String(50), nullable=False, index=True)
    nome = Column(String(255), nullable=False, index=True)
    descrizione = Column(Text, nullable=True)
    categoria = Column(SqlEnum(DPICategory), nullable=False, index=True)
    stato = Column(SqlEnum(DPIStatus), nullable=False, default=DPIStatus.AVAILABLE, index=True)
    marca = Column(String(100), nullable=True)
    modello = Column(String(100), nullable=True)
    taglia = Column(String(20), nullable=True)
    numero_serie = Column(String(100), nullable=True, unique=True)
    data_acquisto = Column(Date, nullable=True)
    data_scadenza = Column(Date, nullable=True, index=True)
    costo = Column(Float, nullable=True)
    note = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    company = relationship("Company", back_populates="dpi_items")
    assegnazioni = relationship("DPIAssignment", back_populates="dpi_item")

    def __repr__(self):
        return f"<DPIItem {self.codice} - {self.nome}>"


class DPIAssignment(Base):
    """Assegnazione DPI a lavoratore."""
    __tablename__ = "dpi_assignments"

    id = Column(Integer, primary_key=True, index=True)
    dpi_item_id = Column(Integer, ForeignKey("dpi_items.id"), nullable=False, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    stato = Column(SqlEnum(AssignmentStatus), nullable=False, default=AssignmentStatus.ACTIVE, index=True)
    data_assegnazione = Column(Date, nullable=False, index=True)
    data_restituzione = Column(Date, nullable=True)
    note = Column(Text, nullable=True)
    firma_ricevuta = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    dpi_item = relationship("DPIItem", back_populates="assegnazioni")
    worker = relationship("Worker", back_populates="dpi_assignments")
    company = relationship("Company", back_populates="dpi_assignments")

    def __repr__(self):
        return f"<DPIAssignment dpi={self.dpi_item_id} worker={self.worker_id}>"
