"""
Attendance service - business logic.
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime, timezone
from app.models.attendance import Timbratura, AttendanceRecord, AttendanceStatus, TimbratureType
from app.schemas.attendance import TimbratureCreate, AttendanceRecordCreate, AttendanceRecordUpdate


class TimbratureService:

    @staticmethod
    def create(db: Session, data: TimbratureCreate) -> Timbratura:
        timbratura = Timbratura(**data.model_dump())
        db.add(timbratura)
        # Auto-aggiorna o crea record giornaliero
        TimbratureService._sync_attendance_record(db, data)
        db.commit()
        db.refresh(timbratura)
        return timbratura

    @staticmethod
    def _sync_attendance_record(db: Session, data: TimbratureCreate) -> None:
        """Sincronizza il record giornaliero in base alle timbrature."""
        record_date = data.timestamp.date()
        record = db.query(AttendanceRecord).filter(
            AttendanceRecord.worker_id == data.worker_id,
            AttendanceRecord.company_id == data.company_id,
            AttendanceRecord.data == record_date,
        ).first()
        if not record:
            record = AttendanceRecord(
                worker_id=data.worker_id,
                company_id=data.company_id,
                data=record_date,
                stato=AttendanceStatus.PRESENT,
            )
            db.add(record)
        if data.tipo == TimbratureType.ENTRATA:
            record.ora_entrata = data.timestamp
        elif data.tipo == TimbratureType.USCITA:
            record.ora_uscita = data.timestamp
            if record.ora_entrata:
                delta = data.timestamp - record.ora_entrata
                record.ore_lavorate = round(delta.total_seconds() / 3600, 2)
                if record.ore_lavorate > 8:
                    record.ore_straordinario = round(record.ore_lavorate - 8, 2)

    @staticmethod
    def get_by_worker(
        db: Session,
        worker_id: int,
        data_inizio: Optional[date] = None,
        data_fine: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Timbratura]:
        query = db.query(Timbratura).filter(Timbratura.worker_id == worker_id)
        if data_inizio:
            query = query.filter(Timbratura.timestamp >= datetime(data_inizio.year, data_inizio.month, data_inizio.day, tzinfo=timezone.utc))
        if data_fine:
            query = query.filter(Timbratura.timestamp <= datetime(data_fine.year, data_fine.month, data_fine.day, 23, 59, 59, tzinfo=timezone.utc))
        return query.order_by(Timbratura.timestamp.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_company(
        db: Session,
        company_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Timbratura]:
        return db.query(Timbratura).filter(
            Timbratura.company_id == company_id
        ).order_by(Timbratura.timestamp.desc()).offset(skip).limit(limit).all()


class AttendanceRecordService:

    @staticmethod
    def create(db: Session, data: AttendanceRecordCreate) -> AttendanceRecord:
        record = AttendanceRecord(**data.model_dump())
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def get_by_id(db: Session, record_id: int) -> AttendanceRecord:
        record = db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
        if not record:
            raise ValueError(f"Record presenze {record_id} non trovato")
        return record

    @staticmethod
    def get_all(
        db: Session,
        company_id: Optional[int] = None,
        worker_id: Optional[int] = None,
        data_inizio: Optional[date] = None,
        data_fine: Optional[date] = None,
        stato: Optional[AttendanceStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AttendanceRecord]:
        query = db.query(AttendanceRecord)
        if company_id:
            query = query.filter(AttendanceRecord.company_id == company_id)
        if worker_id:
            query = query.filter(AttendanceRecord.worker_id == worker_id)
        if data_inizio:
            query = query.filter(AttendanceRecord.data >= data_inizio)
        if data_fine:
            query = query.filter(AttendanceRecord.data <= data_fine)
        if stato:
            query = query.filter(AttendanceRecord.stato == stato)
        return query.order_by(AttendanceRecord.data.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, record_id: int, data: AttendanceRecordUpdate) -> AttendanceRecord:
        record = AttendanceRecordService.get_by_id(db, record_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def approve(db: Session, record_id: int, user_id: int) -> AttendanceRecord:
        record = AttendanceRecordService.get_by_id(db, record_id)
        record.approvato = True
        record.approvato_da = user_id
        db.commit()
        db.refresh(record)
        return record
