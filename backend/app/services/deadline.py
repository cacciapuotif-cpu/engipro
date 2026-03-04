"""
Deadline service - business logic.
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
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
