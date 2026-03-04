"""
Attendance schemas - Pydantic request/response models.
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from app.models.attendance import TimbratureType, TimbratureMethod, AttendanceStatus


class TimbratureBase(BaseModel):
    tipo: TimbratureType
    metodo: TimbratureMethod = TimbratureMethod.MANUALE
    timestamp: datetime
    latitudine: Optional[float] = Field(None, ge=-90, le=90)
    longitudine: Optional[float] = Field(None, ge=-180, le=180)
    accuratezza_metri: Optional[float] = Field(None, ge=0)
    indirizzo: Optional[str] = Field(None, max_length=500)
    note: Optional[str] = Field(None, max_length=500)


class TimbratureCreate(TimbratureBase):
    worker_id: int
    company_id: int


class TimbratureResponse(TimbratureBase):
    id: int
    worker_id: int
    company_id: int
    is_valid: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AttendanceRecordBase(BaseModel):
    data: date
    stato: AttendanceStatus = AttendanceStatus.PRESENT
    ora_entrata: Optional[datetime] = None
    ora_uscita: Optional[datetime] = None
    ore_lavorate: Optional[float] = Field(None, ge=0, le=24)
    ore_straordinario: float = Field(0.0, ge=0)
    note: Optional[str] = Field(None, max_length=500)


class AttendanceRecordCreate(AttendanceRecordBase):
    worker_id: int
    company_id: int


class AttendanceRecordUpdate(BaseModel):
    stato: Optional[AttendanceStatus] = None
    ora_entrata: Optional[datetime] = None
    ora_uscita: Optional[datetime] = None
    ore_lavorate: Optional[float] = Field(None, ge=0, le=24)
    ore_straordinario: Optional[float] = Field(None, ge=0)
    note: Optional[str] = Field(None, max_length=500)
    approvato: Optional[bool] = None


class AttendanceRecordResponse(AttendanceRecordBase):
    id: int
    worker_id: int
    company_id: int
    approvato: bool
    approvato_da: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
