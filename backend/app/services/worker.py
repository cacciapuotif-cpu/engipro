"""
Worker service - business logic for worker operations.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timezone
from app.models import Worker, Company, Location, Department, WorkerStatus
from app.schemas.worker import WorkerCreate, WorkerUpdate


class WorkerService:
    """Worker service."""
    
    @staticmethod
    def create(db: Session, worker_data: WorkerCreate) -> Worker:
        """
        Create a new worker.
        
        Args:
            db: Database session
            worker_data: Worker data
        
        Returns:
            Created worker
        
        Raises:
            ValueError: If CF already exists or company/location not found
        """
        # Check if CF already exists
        existing_cf = db.query(Worker).filter(
            Worker.codice_fiscale == worker_data.codice_fiscale
        ).first()
        if existing_cf:
            raise ValueError(f"Worker with CF {worker_data.codice_fiscale} already exists")
        
        # Verify company exists
        company = db.query(Company).filter(Company.id == worker_data.company_id).first()
        if not company:
            raise ValueError(f"Company with ID {worker_data.company_id} not found")
        
        # Verify location if provided
        if worker_data.location_id:
            location = db.query(Location).filter(Location.id == worker_data.location_id).first()
            if not location or location.company_id != worker_data.company_id:
                raise ValueError("Location not found or doesn't belong to this company")
        
        # Verify department if provided
        if worker_data.department_id:
            department = db.query(Department).filter(Department.id == worker_data.department_id).first()
            if not department or department.company_id != worker_data.company_id:
                raise ValueError("Department not found or doesn't belong to this company")
        
        # Create worker
        worker = Worker(**worker_data.dict())
        db.add(worker)
        db.commit()
        db.refresh(worker)
        
        return worker
    
    @staticmethod
    def get_by_id(db: Session, worker_id: int) -> Worker:
        """Get worker by ID."""
        worker = db.query(Worker).filter(Worker.id == worker_id).first()
        if not worker:
            raise ValueError(f"Worker with ID {worker_id} not found")
        return worker
    
    @staticmethod
    def get_by_cf(db: Session, codice_fiscale: str) -> Worker:
        """Get worker by codice fiscale."""
        worker = db.query(Worker).filter(
            Worker.codice_fiscale == codice_fiscale
        ).first()
        if not worker:
            raise ValueError(f"Worker with CF {codice_fiscale} not found")
        return worker
    
    @staticmethod
    def get_all(
        db: Session,
        company_id: int,
        skip: int = 0,
        limit: int = 100,
        filter_status: WorkerStatus = None,
    ) -> list[Worker]:
        """
        Get all workers for a company with optional filtering.
        
        Args:
            db: Database session
            company_id: Company ID
            skip: Skip first N records
            limit: Limit results to N records
            filter_status: Filter by worker status (ACTIVE, INACTIVE, etc.)
        
        Returns:
            List of workers
        """
        query = db.query(Worker).filter(Worker.company_id == company_id)
        
        if filter_status:
            query = query.filter(Worker.stato == filter_status)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_department(db: Session, department_id: int) -> list[Worker]:
        """Get all workers in a department."""
        return db.query(Worker).filter(Worker.department_id == department_id).all()
    
    @staticmethod
    def get_by_location(db: Session, location_id: int) -> list[Worker]:
        """Get all workers in a location."""
        return db.query(Worker).filter(Worker.location_id == location_id).all()
    
    @staticmethod
    def update(db: Session, worker_id: int, worker_data: WorkerUpdate) -> Worker:
        """
        Update worker.
        
        Args:
            db: Database session
            worker_id: Worker ID
            worker_data: Updated worker data
        
        Returns:
            Updated worker
        """
        worker = WorkerService.get_by_id(db, worker_id)
        
        # Verify location if being updated
        if worker_data.location_id:
            location = db.query(Location).filter(Location.id == worker_data.location_id).first()
            if not location or location.company_id != worker.company_id:
                raise ValueError("Location not found or doesn't belong to this company")
        
        # Verify department if being updated
        if worker_data.department_id:
            department = db.query(Department).filter(Department.id == worker_data.department_id).first()
            if not department or department.company_id != worker.company_id:
                raise ValueError("Department not found or doesn't belong to this company")
        
        update_data = worker_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(worker, key, value)
        
        db.add(worker)
        db.commit()
        db.refresh(worker)
        
        return worker
    
    @staticmethod
    def delete(db: Session, worker_id: int) -> None:
        """
        Soft delete worker (mark as inactive).
        
        Args:
            db: Database session
            worker_id: Worker ID
        """
        worker = WorkerService.get_by_id(db, worker_id)
        worker.is_active = False
        worker.stato = WorkerStatus.INACTIVE
        db.add(worker)
        db.commit()
    
    @staticmethod
    def change_status(
        db: Session,
        worker_id: int,
        new_status: WorkerStatus,
    ) -> Worker:
        """
        Change worker status.
        
        Args:
            db: Database session
            worker_id: Worker ID
            new_status: New status
        
        Returns:
            Updated worker
        """
        worker = WorkerService.get_by_id(db, worker_id)
        worker.stato = new_status
        if new_status == WorkerStatus.INACTIVE or new_status == WorkerStatus.TERMINATED:
            worker.is_active = False
        elif new_status == WorkerStatus.ACTIVE:
            worker.is_active = True
        
        db.add(worker)
        db.commit()
        db.refresh(worker)
        
        return worker
    
    @staticmethod
    def search(
        db: Session,
        company_id: int,
        query: str,
    ) -> list[Worker]:
        """
        Search workers by name, CF, or mansione.
        
        Args:
            db: Database session
            company_id: Company ID
            query: Search query
        
        Returns:
            List of matching workers
        """
        search_term = f"%{query}%"
        return db.query(Worker).filter(
            and_(
                Worker.company_id == company_id,
                or_(
                    Worker.nome.ilike(search_term),
                    Worker.cognome.ilike(search_term),
                    Worker.codice_fiscale.ilike(search_term),
                    Worker.mansione.ilike(search_term),
                ),
            ),
        ).all()
    
    @staticmethod
    def get_rspp_list(db: Session, company_id: int) -> list[Worker]:
        """Get all RSPP workers in company."""
        return db.query(Worker).filter(
            and_(
                Worker.company_id == company_id,
                Worker.is_rspp == True,
            ),
        ).all()
    
    @staticmethod
    def get_rls_list(db: Session, company_id: int) -> list[Worker]:
        """Get all RLS workers in company."""
        return db.query(Worker).filter(
            and_(
                Worker.company_id == company_id,
                Worker.is_rls == True,
            ),
        ).all()
    
    @staticmethod
    def count_active(db: Session, company_id: int) -> int:
        """Count active workers in company."""
        return db.query(func.count(Worker.id)).filter(
            and_(
                Worker.company_id == company_id,
                Worker.stato == WorkerStatus.ACTIVE,
            ),
        ).scalar()
