"""
Training model - gestione formazione, corsi ed attestati.
"""
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey, Enum as SqlEnum, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
from app.core.database import Base


class CourseType(str, PyEnum):
    OBBLIGATORIO = "OBBLIGATORIO"
    FACOLTATIVO = "FACOLTATIVO"
    AGGIORNAMENTO = "AGGIORNAMENTO"


class CourseStatus(str, PyEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class EditionStatus(str, PyEnum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Attestato(str, PyEnum):
    SUPERATO = "SUPERATO"
    NON_SUPERATO = "NON_SUPERATO"
    ASSENTE = "ASSENTE"


class Course(Base):
    """Catalogo corsi di formazione."""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    codice = Column(String(50), nullable=False, index=True)
    titolo = Column(String(255), nullable=False, index=True)
    descrizione = Column(String(1000), nullable=True)
    tipo = Column(SqlEnum(CourseType), nullable=False, default=CourseType.OBBLIGATORIO)
    stato = Column(SqlEnum(CourseStatus), nullable=False, default=CourseStatus.ACTIVE)
    durata_ore = Column(Float, nullable=False, default=8.0)
    validita_anni = Column(Integer, nullable=True)
    provider = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    company = relationship("Company", back_populates="courses")
    editions = relationship("CourseEdition", back_populates="course")

    def __repr__(self):
        return f"<Course {self.codice} - {self.titolo}>"


class CourseEdition(Base):
    """Edizioni/sessioni di un corso."""
    __tablename__ = "course_editions"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    data_inizio = Column(Date, nullable=False, index=True)
    data_fine = Column(Date, nullable=False)
    luogo = Column(String(255), nullable=True)
    docente = Column(String(255), nullable=True)
    max_partecipanti = Column(Integer, nullable=True)
    stato = Column(SqlEnum(EditionStatus), nullable=False, default=EditionStatus.PLANNED)
    note = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    course = relationship("Course", back_populates="editions")
    partecipazioni = relationship("CourseParticipation", back_populates="edition")

    def __repr__(self):
        return f"<CourseEdition {self.course_id} - {self.data_inizio}>"


class CourseParticipation(Base):
    """Partecipazione lavoratore a un'edizione del corso + attestato."""
    __tablename__ = "course_participations"

    id = Column(Integer, primary_key=True, index=True)
    edition_id = Column(Integer, ForeignKey("course_editions.id"), nullable=False, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False, index=True)
    esito = Column(SqlEnum(Attestato), nullable=False, default=Attestato.ASSENTE)
    data_attestato = Column(Date, nullable=True)
    data_scadenza_attestato = Column(Date, nullable=True)
    numero_attestato = Column(String(100), nullable=True)
    note = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    edition = relationship("CourseEdition", back_populates="partecipazioni")
    worker = relationship("Worker", back_populates="partecipazioni")

    def __repr__(self):
        return f"<CourseParticipation worker={self.worker_id} edition={self.edition_id}>"
