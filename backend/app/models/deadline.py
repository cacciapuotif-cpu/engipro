"""
Deadline model - represents deadlines/scadenze for workers and companies.
"""
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey, Enum as SqlEnum, Float
from sqlalchemy.orm import relationship
from datetime import datetime, date, timezone
from enum import Enum as PyEnum
from app.core.database import Base


class DeadlineType(str, PyEnum):
    """Deadline type enumeration."""
    FORMAZIONE = "FORMAZIONE"
    VISITA_MEDICA = "VISITA_MEDICA"
    MANUTENZIONE_ATTREZZATURA = "MANUTENZIONE_ATTREZZATURA"
    VERIFICA_PERIODICA = "VERIFICA_PERIODICA"
    RINNOVO_DOCUMENTO = "RINNOVO_DOCUMENTO"
    SOSTITUZIONE_DPI = "SOSTITUZIONE_DPI"
    ALTRO = "ALTRO"


class DeadlineStatus(str, PyEnum):
    """Deadline status enumeration."""
    PENDING = "PENDING"
    ALERT = "ALERT"
    EXPIRED = "EXPIRED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class DeadlinePriority(str, PyEnum):
    """Deadline priority enumeration."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Deadline(Base):
    """Deadline/Scadenza model."""
    
    __tablename__ = "deadlines"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True, index=True)
    
    # Deadline info
    tipo = Column(SqlEnum(DeadlineType), nullable=False, index=True)
    titolo = Column(String(255), nullable=False, index=True)
    descrizione = Column(String(1000), nullable=True)
    
    # Dates
    data_scadenza = Column(Date, nullable=False, index=True)
    data_completamento = Column(Date, nullable=True)
    
    # Status and priority
    stato = Column(SqlEnum(DeadlineStatus), nullable=False, default=DeadlineStatus.PENDING, index=True)
    priorita = Column(SqlEnum(DeadlinePriority), nullable=False, default=DeadlinePriority.MEDIUM)
    
    # Notifications
    giorni_preavviso = Column(Integer, default=7, nullable=False)
    last_notification_sent = Column(DateTime(timezone=True), nullable=True)
    notification_count = Column(Integer, default=0, nullable=False)
    
    # Assignment and tracking
    assegnato_a = Column(Integer, ForeignKey("workers.id"), nullable=True)  # Person responsible
    note = Column(String(1000), nullable=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="deadlines")
    worker = relationship("Worker", foreign_keys=[worker_id], back_populates="deadlines")
    assigned_to = relationship("Worker", foreign_keys=[assegnato_a])
    
    def __repr__(self) -> str:
        return f"<Deadline {self.titolo} - {self.data_scadenza}>"
