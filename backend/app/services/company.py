"""
Company service - business logic for company operations.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Company, Worker
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyService:
    """Company service."""
    
    @staticmethod
    def create(db: Session, company_data: CompanyCreate) -> Company:
        """
        Create a new company.
        
        Args:
            db: Database session
            company_data: Company data
        
        Returns:
            Created company
        
        Raises:
            ValueError: If P.IVA or CF already exists
        """
        # Check if P.IVA already exists
        existing_piva = db.query(Company).filter(
            Company.partita_iva == company_data.partita_iva
        ).first()
        if existing_piva:
            raise ValueError(f"Company with P.IVA {company_data.partita_iva} already exists")
        
        # Check if CF already exists
        existing_cf = db.query(Company).filter(
            Company.codice_fiscale == company_data.codice_fiscale
        ).first()
        if existing_cf:
            raise ValueError(f"Company with CF {company_data.codice_fiscale} already exists")
        
        # Create company
        company = Company(**company_data.dict())
        db.add(company)
        db.commit()
        db.refresh(company)
        
        return company
    
    @staticmethod
    def get_by_id(db: Session, company_id: int) -> Company:
        """Get company by ID."""
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError(f"Company with ID {company_id} not found")
        return company
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Company]:
        """Get all companies with pagination."""
        return db.query(Company).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, company_id: int, company_data: CompanyUpdate) -> Company:
        """Update company."""
        company = CompanyService.get_by_id(db, company_id)
        
        update_data = company_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(company, key, value)
        
        db.add(company)
        db.commit()
        db.refresh(company)
        
        return company
    
    @staticmethod
    def delete(db: Session, company_id: int) -> None:
        """Delete company (soft delete - keep data)."""
        company = CompanyService.get_by_id(db, company_id)
        
        # Soft delete: mark workers as inactive instead of deleting
        db.query(Worker).filter(Worker.company_id == company_id).update(
            {"is_active": False},
            synchronize_session=False,
        )
        
        db.delete(company)
        db.commit()
    
    @staticmethod
    def get_stats(db: Session, company_id: int) -> dict:
        """Get company statistics."""
        company = CompanyService.get_by_id(db, company_id)
        
        worker_count = db.query(func.count(Worker.id)).filter(
            Worker.company_id == company_id
        ).scalar()
        
        return {
            "id": company.id,
            "ragione_sociale": company.ragione_sociale,
            "total_workers": worker_count,
            "locations": len(company.locations),
            "departments": len(company.departments),
        }
