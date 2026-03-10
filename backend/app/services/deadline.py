"""
Deadline service - business logic.
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, timedelta
from app.models.deadline import Deadline, DeadlineStatus
from app.schemas.deadline import DeadlineCreate, DeadlineUpdate


class DeadlineService:

    @staticmethod
    def create(db: Session, data: DeadlineCreate) -> Deadline:
        deadline = Deadline(**data.model_dump())
        db.add(deadline)
        db.commit()
        db.refresh(deadline)
        return deadline

    @staticmethod
    def get_by_id(db: Session, deadline_id: int) -> Deadline:
        deadline = db.query(Deadline).filter(Deadline.id == deadline_id).first()
        if not deadline:
            raise ValueError(f"Deadline {deadline_id} non trovata")
        return deadline

    @staticmethod
    def get_all(
        db: Session,
        company_id: Optional[int] = None,
        worker_id: Optional[int] = None,
        stato: Optional[DeadlineStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Deadline]:
        query = db.query(Deadline)
        if company_id:
            query = query.filter(Deadline.company_id == company_id)
        if worker_id:
            query = query.filter(Deadline.worker_id == worker_id)
        if stato:
            query = query.filter(Deadline.stato == stato)
        return query.order_by(Deadline.data_scadenza).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, deadline_id: int, data: DeadlineUpdate) -> Deadline:
        deadline = DeadlineService.get_by_id(db, deadline_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(deadline, field, value)
        db.commit()
        db.refresh(deadline)
        return deadline

    @staticmethod
    def delete(db: Session, deadline_id: int) -> None:
        deadline = DeadlineService.get_by_id(db, deadline_id)
        db.delete(deadline)
        db.commit()

    @staticmethod
    def complete(db: Session, deadline_id: int) -> Deadline:
        deadline = DeadlineService.get_by_id(db, deadline_id)
        deadline.stato = DeadlineStatus.COMPLETED
        deadline.data_completamento = date.today()
        db.commit()
        db.refresh(deadline)
        return deadline

    @staticmethod
    def get_upcoming_alerts(db: Session, company_id: int, days: int = 7) -> list[Deadline]:
        """
        Ritorna scadenze in alert entro N giorni.
        
        Args:
            db: Database session
            company_id: Filtra per azienda
            days: Giorni di preavviso (default 7)
        
        Returns:
            Lista di scadenze imminenti
        """
        today = date.today()
        alert_until = today + timedelta(days=days)
        
        return db.query(Deadline).filter(
            Deadline.company_id == company_id,
            Deadline.data_scadenza >= today,
            Deadline.data_scadenza <= alert_until,
            Deadline.stato.in_([DeadlineStatus.PENDING, DeadlineStatus.ALERT])
        ).order_by(Deadline.data_scadenza).all()

    @staticmethod
    def get_expired(db: Session, company_id: int) -> list[Deadline]:
        """
        Ritorna scadenze scadute non completate.
        
        Args:
            db: Database session
            company_id: Filtra per azienda
        
        Returns:
            Lista di scadenze scadute
        """
        today = date.today()
        
        return db.query(Deadline).filter(
            Deadline.company_id == company_id,
            Deadline.data_scadenza < today,
            Deadline.stato.in_([DeadlineStatus.PENDING, DeadlineStatus.ALERT])
        ).order_by(Deadline.data_scadenza).all()

    @staticmethod
    def get_by_type_and_status(
        db: Session,
        company_id: int,
        deadline_type: Optional[str] = None,
        stato: Optional[DeadlineStatus] = None,
    ) -> list[Deadline]:
        """
        Ritorna scadenze filtrate per tipo e stato.
        
        Args:
            db: Database session
            company_id: Filtra per azienda
            deadline_type: Tipo di scadenza (opzionale)
            stato: Stato scadenza (opzionale)
        
        Returns:
            Lista di scadenze filtrate
        """
        query = db.query(Deadline).filter(Deadline.company_id == company_id)
        
        if deadline_type:
            query = query.filter(Deadline.tipo == deadline_type)
        if stato:
            query = query.filter(Deadline.stato == stato)
        
        return query.order_by(Deadline.data_scadenza).all()

    @staticmethod
    def get_dashboard_summary(db: Session, company_id: int) -> dict:
        """
        Ritorna un riepilogo per dashboard.
        
        Args:
            db: Database session
            company_id: Filtra per azienda
        
        Returns:
            Dict con conteggi per categoria
        """
        total = db.query(Deadline).filter(
            Deadline.company_id == company_id,
            Deadline.stato != DeadlineStatus.COMPLETED
        ).count()
        
        expired = DeadlineService.get_expired(db, company_id)
        alerts = DeadlineService.get_upcoming_alerts(db, company_id)
        
        return {
            'total_pending': total,
            'expired_count': len(expired),
            'alert_count': len(alerts),
            'by_priority': {
                'HIGH': db.query(Deadline).filter(
                    Deadline.company_id == company_id,
                    Deadline.priorita == 'HIGH',
                    Deadline.stato != DeadlineStatus.COMPLETED
                ).count(),
                'MEDIUM': db.query(Deadline).filter(
                    Deadline.company_id == company_id,
                    Deadline.priorita == 'MEDIUM',
                    Deadline.stato != DeadlineStatus.COMPLETED
                ).count(),
                'LOW': db.query(Deadline).filter(
                    Deadline.company_id == company_id,
                    Deadline.priorita == 'LOW',
                    Deadline.stato != DeadlineStatus.COMPLETED
                ).count(),
            }
        }
