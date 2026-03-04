"""
DPI service - business logic.
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.models.dpi import DPIItem, DPIAssignment, DPIStatus, AssignmentStatus, DPICategory
from app.schemas.dpi import DPIItemCreate, DPIItemUpdate, DPIAssignmentCreate, DPIAssignmentUpdate


class DPIItemService:

    @staticmethod
    def create(db: Session, data: DPIItemCreate) -> DPIItem:
        item = DPIItem(**data.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def get_by_id(db: Session, item_id: int) -> DPIItem:
        item = db.query(DPIItem).filter(DPIItem.id == item_id, DPIItem.is_active == True).first()
        if not item:
            raise ValueError(f"DPI {item_id} non trovato")
        return item

    @staticmethod
    def get_all(
        db: Session,
        company_id: Optional[int] = None,
        categoria: Optional[DPICategory] = None,
        stato: Optional[DPIStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DPIItem]:
        query = db.query(DPIItem).filter(DPIItem.is_active == True)
        if company_id:
            query = query.filter(DPIItem.company_id == company_id)
        if categoria:
            query = query.filter(DPIItem.categoria == categoria)
        if stato:
            query = query.filter(DPIItem.stato == stato)
        return query.order_by(DPIItem.nome).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, item_id: int, data: DPIItemUpdate) -> DPIItem:
        item = DPIItemService.get_by_id(db, item_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete(db: Session, item_id: int) -> None:
        item = DPIItemService.get_by_id(db, item_id)
        item.is_active = False
        db.commit()


class DPIAssignmentService:

    @staticmethod
    def create(db: Session, data: DPIAssignmentCreate) -> DPIAssignment:
        # Aggiorna stato DPI ad ASSIGNED
        item = db.query(DPIItem).filter(DPIItem.id == data.dpi_item_id).first()
        if item:
            item.stato = DPIStatus.ASSIGNED
        assignment = DPIAssignment(**data.model_dump())
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    @staticmethod
    def get_by_id(db: Session, assignment_id: int) -> DPIAssignment:
        a = db.query(DPIAssignment).filter(DPIAssignment.id == assignment_id).first()
        if not a:
            raise ValueError(f"Assegnazione {assignment_id} non trovata")
        return a

    @staticmethod
    def get_by_worker(db: Session, worker_id: int, skip: int = 0, limit: int = 100) -> list[DPIAssignment]:
        return db.query(DPIAssignment).filter(
            DPIAssignment.worker_id == worker_id
        ).order_by(DPIAssignment.data_assegnazione.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_company(db: Session, company_id: int, skip: int = 0, limit: int = 100) -> list[DPIAssignment]:
        return db.query(DPIAssignment).filter(
            DPIAssignment.company_id == company_id
        ).order_by(DPIAssignment.data_assegnazione.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, assignment_id: int, data: DPIAssignmentUpdate) -> DPIAssignment:
        assignment = DPIAssignmentService.get_by_id(db, assignment_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(assignment, field, value)
        db.commit()
        db.refresh(assignment)
        return assignment

    @staticmethod
    def return_dpi(db: Session, assignment_id: int) -> DPIAssignment:
        assignment = DPIAssignmentService.get_by_id(db, assignment_id)
        assignment.stato = AssignmentStatus.RETURNED
        assignment.data_restituzione = date.today()
        # Libera il DPI
        item = db.query(DPIItem).filter(DPIItem.id == assignment.dpi_item_id).first()
        if item:
            item.stato = DPIStatus.AVAILABLE
        db.commit()
        db.refresh(assignment)
        return assignment
