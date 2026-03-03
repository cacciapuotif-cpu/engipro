"""
Company models - represents companies and their locations/departments.
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class Company(Base):
    """Company model."""
    
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    ragione_sociale = Column(String(255), nullable=False, index=True)
    partita_iva = Column(String(11), unique=True, nullable=False, index=True)
    codice_fiscale = Column(String(16), unique=True, nullable=False, index=True)
    codice_ateco = Column(String(10), nullable=True)
    
    # Contact
    email = Column(String(255), nullable=True)
    telefono = Column(String(20), nullable=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="company")
    locations = relationship("Location", back_populates="company", cascade="all, delete-orphan")
    departments = relationship("Department", back_populates="company", cascade="all, delete-orphan")
    workers = relationship("Worker", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Company {self.ragione_sociale}>"


class Location(Base):
    """Company location/sede."""
    
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    nome = Column(String(255), nullable=False)
    indirizzo = Column(String(255), nullable=False)
    numero = Column(String(10), nullable=True)
    cap = Column(String(5), nullable=True)
    citta = Column(String(100), nullable=True)
    provincia = Column(String(2), nullable=True)
    
    # Geolocalizzazione
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    geofence_radius = Column(Integer, default=500, nullable=False)  # meters
    
    # Audit
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="locations")
    workers = relationship("Worker", back_populates="location")
    
    def __repr__(self) -> str:
        return f"<Location {self.nome}>"


class Department(Base):
    """Company department/reparto."""
    
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    nome = Column(String(255), nullable=False, index=True)
    descrizione = Column(String(500), nullable=True)
    responsabile_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="departments")
    workers = relationship("Worker", back_populates="department")
    
    def __repr__(self) -> str:
        return f"<Department {self.nome}>"
