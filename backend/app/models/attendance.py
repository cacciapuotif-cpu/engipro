"""
Attendance model - gestione presenze e timbrature.
"""
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey, Enum as SqlEnum, Float, Time
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum
from app.core.database import Base


class TimbratureType(str, PyEnum):
    ENTRATA = "ENTRATA"
    USCITA = "USCITA"
    PAUSA_INIZIO = "PAUSA_INIZIO"
    PAUSA_FINE = "PAUSA_FINE"


class TimbratureMethod(str, PyEnum):
    GPS = "GPS"
    MANUALE = "MANUALE"
    NFC = "NFC"
    QR_CODE = "QR_CODE"


class AttendanceStatus(str, PyEnum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    HALF_DAY = "HALF_DAY"
    HOLIDAY = "HOLIDAY"
    SICK = "SICK"
    PERMIT = "PERMIT"


class Timbratura(Base):
    """Singola timbratura GPS/manuale."""
    __tablename__ = "timbrature"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    tipo = Column(SqlEnum(TimbratureType), nullable=False, index=True)
    metodo = Column(SqlEnum(TimbratureMethod), nullable=False, default=TimbratureMethod.MANUALE)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    latitudine = Column(Float, nullable=True)
    longitudine = Column(Float, nullable=True)
    accuratezza_metri = Column(Float, nullable=True)
    indirizzo = Column(String(500), nullable=True)
    note = Column(String(500), nullable=True)
    is_valid = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    worker = relationship("Worker", back_populates="timbrature")
    company = relationship("Company", back_populates="timbrature")

    def __repr__(self):
        return f"<Timbratura worker={self.worker_id} tipo={self.tipo} ts={self.timestamp}>"


class AttendanceRecord(Base):
    """Registro giornaliero presenze."""
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    data = Column(Date, nullable=False, index=True)
    stato = Column(SqlEnum(AttendanceStatus), nullable=False, default=AttendanceStatus.PRESENT, index=True)
    ora_entrata = Column(DateTime(timezone=True), nullable=True)
    ora_uscita = Column(DateTime(timezone=True), nullable=True)
    ore_lavorate = Column(Float, nullable=True)
    ore_straordinario = Column(Float, default=0.0, nullable=False)
    note = Column(String(500), nullable=True)
    approvato = Column(Boolean, default=False, nullable=False)
    approvato_da = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    worker = relationship("Worker", back_populates="attendance_records")
    company = relationship("Company", back_populates="attendance_records")

    def __repr__(self):
        return f"<AttendanceRecord worker={self.worker_id} data={self.data} stato={self.stato}>"
