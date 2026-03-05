"""
Company management API routes.
"""
from fastapi import Path, APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_role
from app.models import User, UserRole
from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyStatsResponse,
)
from app.services.company import CompanyService

router = APIRouter(prefix="/api/v1/companies", tags=["Companies"])


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Create a new company (ADMIN only).
    
    Args:
        company_data: Company data
        db: Database session
        current_user: Current authenticated user (must be ADMIN)
    
    Returns:
        Created company
    """
    try:
        company = CompanyService.create(db, company_data)
        return company
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("", response_model=list[CompanyResponse])
async def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all companies with pagination.
    
    Args:
        skip: Skip first N records
        limit: Limit results to N records
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        List of companies
    """
    companies = CompanyService.get_all(db, skip, limit)
    return companies


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get company by ID.
    
    Args:
        company_id: Company ID
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Company data
    """
    try:
        company = CompanyService.get_by_id(db, company_id)
        return company
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.COMPANY_ADMIN)),
):
    """
    Update company (ADMIN or COMPANY_ADMIN only).
    
    Args:
        company_id: Company ID
        company_data: Updated company data
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Updated company
    """
    try:
        company = CompanyService.update(db, company_id, company_data)
        return company
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Delete company (ADMIN only, soft delete).
    
    Args:
        company_id: Company ID
        db: Database session
        current_user: Current authenticated user
    """
    try:
        CompanyService.delete(db, company_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{company_id}/stats", response_model=CompanyStatsResponse)
async def get_company_stats(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get company statistics.
    
    Args:
        company_id: Company ID
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Company statistics
    """
    try:
        stats = CompanyService.get_stats(db, company_id)
        return stats
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
