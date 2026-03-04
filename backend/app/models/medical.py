"""
Medical model - gestione medicina del lavoro e visite mediche.
"""
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey, Enum as SqlEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
from app.core.database import Base


class VisitType(str, PyEnum):
    PREVENTIVA = "PREVENTIVA"
    PERIODICA = "PERIODICA"
    REINTEGRO = "REINTEGRO"
    CAMBIO_MANSIONE = "CAMBIO_MANSIONE"
    CESSAZIONE = "CESSAZIONE"
    STRAORDINARIA = "STRAORDINARIA"


class VisitOutcome(str, PyEnum):
    IDONEO = "IDONEO"
    IDONEO_LIMITAZIONI = "IDONEO_LIMITAZIONI"
    IDONEO_PRESCRIZIONI = "IDONEO_PRESCRIZIONI"
    NON_IDONEO_TEMPORANEO = "NON_IDONEO_TEMPORANEO"
    NON_IDONEO = "NON_IDONEO"


class VisitStatus(str, PyEnum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"


class HealthProtocol(Base):
    """Protocollo sanitario aziendale."""
    __tablename__ = "health_protocols"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    titolo = Column(String(255), nullable=False)
    descrizione = Column(Text, nullable=True)
    data_approvazione = Column(Date, nullable=True)
    medico_competente = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    company = relationship("Company", back_populates="health_protocols")
    visite = relationship("MedicalVisit", back_populates="protocol")

    def __repr__(self):
        return f"<HealthProtocol {self.titolo}>"


class MedicalVisit(Base):
    """Visita medica lavoratore."""
    __tablename__ = "medical_visits"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False, index=True)
    protocol_id = Column(Integer, ForeignKey("health_protocols.id"), nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    tipo = Column(SqlEnum(VisitType), nullable=False, index=True)
    stato = Column(SqlEnum(VisitStatus), nullable=False, default=VisitStatus.SCHEDULED, index=True)
    esito = Column(SqlEnum(VisitOutcome), nullable=True)

    data_visita = Column(Date, nullable=False, index=True)
    data_prossima_visita = Column(Date, nullable=True, index=True)
    medico = Column(String(255), nullable=True)
    struttura = Column(String(255), nullable=True)

    limitazioni = Column(Text, nullable=True)
    prescrizioni = Column(Text, nullable=True)
    note = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    worker = relationship("Worker", back_populates="visite_mediche")
    protocol = relationship("HealthProtocol", back_populates="visite")
    company = relationship("Company", back_populates="visite_mediche")

    def __repr__(self):
        return f"<MedicalVisit worker={self.worker_id} tipo={self.tipo} data={self.data_visita}>"
