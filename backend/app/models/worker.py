"""
Worker model - represents employees/workers in the system.
"""
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship
from datetime import datetime, date, timezone
from enum import Enum as PyEnum
from app.core.database import Base


class ContractType(str, PyEnum):
    """Contract type enumeration."""
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    TEMPORARY = "TEMPORARY"
    APPRENTICE = "APPRENTICE"
    PROJECT = "PROJECT"


class WorkerStatus(str, PyEnum):
    """Worker status enumeration."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ON_LEAVE = "ON_LEAVE"
    TERMINATED = "TERMINATED"


class Worker(Base):
    """Worker/Employee model."""
    
    __tablename__ = "workers"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    responsabile_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
    
    # Personal data
    codice_fiscale = Column(String(16), unique=True, nullable=False, index=True)
    nome = Column(String(100), nullable=False)
    cognome = Column(String(100), nullable=False)
    data_nascita = Column(Date, nullable=False)
    luogo_nascita = Column(String(100), nullable=True)
    
    # Contact
    email = Column(String(255), nullable=True)
    telefono = Column(String(20), nullable=True)
    
    # Employment
    mansione = Column(String(255), nullable=False)
    tipo_contratto = Column(SqlEnum(ContractType), nullable=False, default=ContractType.FULL_TIME)
    data_assunzione = Column(Date, nullable=False)
    data_cessazione = Column(Date, nullable=True)
    
    # Status
    stato = Column(SqlEnum(WorkerStatus), nullable=False, default=WorkerStatus.ACTIVE)
    
    # Roles
    is_rspp = Column(Boolean, default=False, nullable=False)
    is_rls = Column(Boolean, default=False, nullable=False)
    is_medico_competente = Column(Boolean, default=False, nullable=False)
    
    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Audit
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="workers")
    location = relationship("Location", back_populates="workers")
    department = relationship("Department", back_populates="workers")
    user = relationship("User", back_populates="worker", uselist=False)
    
    def __repr__(self) -> str:
        return f"<Worker {self.cognome} {self.nome}>"
