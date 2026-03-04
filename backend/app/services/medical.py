"""
Medical service - business logic.
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.models.medical import HealthProtocol, MedicalVisit, VisitStatus, VisitOutcome, VisitType
from app.schemas.medical import HealthProtocolCreate, HealthProtocolUpdate, MedicalVisitCreate, MedicalVisitUpdate


class HealthProtocolService:

    @staticmethod
    def create(db: Session, data: HealthProtocolCreate) -> HealthProtocol:
        protocol = HealthProtocol(**data.model_dump())
        db.add(protocol)
        db.commit()
        db.refresh(protocol)
        return protocol

    @staticmethod
    def get_by_id(db: Session, protocol_id: int) -> HealthProtocol:
        protocol = db.query(HealthProtocol).filter(
            HealthProtocol.id == protocol_id,
            HealthProtocol.is_active == True
        ).first()
        if not protocol:
            raise ValueError(f"Protocollo {protocol_id} non trovato")
        return protocol

    @staticmethod
    def get_all(db: Session, company_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> list[HealthProtocol]:
        query = db.query(HealthProtocol).filter(HealthProtocol.is_active == True)
        if company_id:
            query = query.filter(HealthProtocol.company_id == company_id)
        return query.order_by(HealthProtocol.titolo).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, protocol_id: int, data: HealthProtocolUpdate) -> HealthProtocol:
        protocol = HealthProtocolService.get_by_id(db, protocol_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(protocol, field, value)
        db.commit()
        db.refresh(protocol)
        return protocol

    @staticmethod
    def delete(db: Session, protocol_id: int) -> None:
        protocol = HealthProtocolService.get_by_id(db, protocol_id)
        protocol.is_active = False
        db.commit()


class MedicalVisitService:

    @staticmethod
    def create(db: Session, data: MedicalVisitCreate) -> MedicalVisit:
        visit = MedicalVisit(**data.model_dump())
        db.add(visit)
        db.commit()
        db.refresh(visit)
        return visit

    @staticmethod
    def get_by_id(db: Session, visit_id: int) -> MedicalVisit:
        visit = db.query(MedicalVisit).filter(MedicalVisit.id == visit_id).first()
        if not visit:
            raise ValueError(f"Visita {visit_id} non trovata")
        return visit

    @staticmethod
    def get_all(
        db: Session,
        company_id: Optional[int] = None,
        worker_id: Optional[int] = None,
        tipo: Optional[VisitType] = None,
        stato: Optional[VisitStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[MedicalVisit]:
        query = db.query(MedicalVisit)
        if company_id:
            query = query.filter(MedicalVisit.company_id == company_id)
        if worker_id:
            query = query.filter(MedicalVisit.worker_id == worker_id)
        if tipo:
            query = query.filter(MedicalVisit.tipo == tipo)
        if stato:
            query = query.filter(MedicalVisit.stato == stato)
        return query.order_by(MedicalVisit.data_visita.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, visit_id: int, data: MedicalVisitUpdate) -> MedicalVisit:
        visit = MedicalVisitService.get_by_id(db, visit_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(visit, field, value)
        db.commit()
        db.refresh(visit)
        return visit

    @staticmethod
    def complete(db: Session, visit_id: int, esito: VisitOutcome, data_prossima: Optional[date] = None) -> MedicalVisit:
        visit = MedicalVisitService.get_by_id(db, visit_id)
        visit.stato = VisitStatus.COMPLETED
        visit.esito = esito
        if data_prossima:
            visit.data_prossima_visita = data_prossima
        db.commit()
        db.refresh(visit)
        return visit

    @staticmethod
    def cancel(db: Session, visit_id: int) -> MedicalVisit:
        visit = MedicalVisitService.get_by_id(db, visit_id)
        visit.stato = VisitStatus.CANCELLED
        db.commit()
        db.refresh(visit)
        return visit
