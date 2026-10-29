"""
Documents API routes.
"""
from fastapi import Path, APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from fastapi.responses import RedirectResponse
from app.core.config import settings
from app.core.storage import MinIOStorage, get_storage
from app.core.database import get_db
from app.core.tenancy import enforce_company_scope
from app.core.dependencies import get_current_active_user
from app.models import User
from app.models.document import DocumentCategory, DocumentStatus
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.services.document import DocumentService

router = APIRouter(dependencies=[Depends(enforce_company_scope)], prefix="/api/v1/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    titolo: str = Form(None),
    categoria: str = Form("ALTRO"),
    company_id: int = Form(...),
    worker_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    storage: MinIOStorage = Depends(get_storage),
) -> DocumentResponse:
    """Carica un documento (multipart upload)."""
    content_bytes = await file.read(settings.MAX_UPLOAD_FILE_SIZE + 1)
    if len(content_bytes) > settings.MAX_UPLOAD_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File troppo grande")
    allowed = {
        "application/pdf": "pdf", "image/jpeg": "jpg", "image/png": "png",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    }
    if file.content_type not in allowed:
        raise HTTPException(status_code=415, detail="Tipo di file non ammesso")
    try:
        category = DocumentCategory(categoria)
    except ValueError:
        raise HTTPException(status_code=422, detail="Categoria non valida")
    ext = allowed[file.content_type]
    storage_key = f"companies/{company_id}/documents/{uuid.uuid4()}.{ext}"
    
    doc_data = DocumentCreate(
        company_id=company_id,
        worker_id=worker_id,
        titolo=titolo or file.filename or "Documento",
        categoria=category,
        storage_key=storage_key,
        filename_originale=file.filename or f"documento.{ext}",
        mime_type=file.content_type or "application/octet-stream",
        dimensione_bytes=len(content_bytes),
    )
    storage.upload_file(storage_key, content_bytes, file.content_type)
    try:
        return DocumentService.create(db, doc_data, user_id=current_user.id)
    except Exception:
        storage.delete_file(storage_key)
        raise


@router.get("/{document_id}/download", response_class=RedirectResponse)
async def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    storage: MinIOStorage = Depends(get_storage),
) -> RedirectResponse:
    try:
        document = DocumentService.get_by_id(db, document_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return RedirectResponse(storage.get_presigned_url(document.storage_key), status_code=302)


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Crea un nuovo documento."""
    return DocumentService.create(db, data, user_id=current_user.id)


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    company_id: Optional[int] = Query(None),
    worker_id: Optional[int] = Query(None),
    categoria: Optional[DocumentCategory] = Query(None),
    stato: Optional[DocumentStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista documenti con filtri opzionali."""
    return DocumentService.get_all(db, company_id, worker_id, categoria, stato, skip, limit)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ottieni documento per ID."""
    try:
        return DocumentService.get_by_id(db, document_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Aggiorna documento."""
    try:
        return DocumentService.update(db, document_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Elimina documento (soft delete)."""
    try:
        DocumentService.delete(db, document_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{document_id}/version", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def new_version(
    document_id: int,
    data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Crea nuova versione di un documento."""
    try:
        return DocumentService.new_version(db, document_id, data, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{document_id}/versions", response_model=list[DocumentResponse])
async def get_versions(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ottieni tutte le versioni di un documento."""
    try:
        return DocumentService.get_versions(db, document_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

