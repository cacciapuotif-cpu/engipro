"""
Document service - business logic.
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone
from app.models.document import Document, DocumentStatus, DocumentCategory
from app.schemas.document import DocumentCreate, DocumentUpdate
import uuid


class DocumentService:

    @staticmethod
    def _generate_storage_key(company_id: int, filename: str) -> str:
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
        return f"companies/{company_id}/documents/{uuid.uuid4()}.{ext}"

    @staticmethod
    def create(db: Session, data: DocumentCreate, user_id: Optional[int] = None) -> Document:
        doc = Document(**data.model_dump(), created_by=user_id)
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    def get_by_id(db: Session, document_id: int) -> Document:
        doc = db.query(Document).filter(
            Document.id == document_id,
            Document.is_active == True
        ).first()
        if not doc:
            raise ValueError(f"Documento {document_id} non trovato")
        return doc

    @staticmethod
    def get_all(
        db: Session,
        company_id: Optional[int] = None,
        worker_id: Optional[int] = None,
        categoria: Optional[DocumentCategory] = None,
        stato: Optional[DocumentStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Document]:
        query = db.query(Document).filter(Document.is_active == True)
        if company_id:
            query = query.filter(Document.company_id == company_id)
        if worker_id:
            query = query.filter(Document.worker_id == worker_id)
        if categoria:
            query = query.filter(Document.categoria == categoria)
        if stato:
            query = query.filter(Document.stato == stato)
        return query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, document_id: int, data: DocumentUpdate) -> Document:
        doc = DocumentService.get_by_id(db, document_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(doc, field, value)
        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    def delete(db: Session, document_id: int) -> None:
        doc = DocumentService.get_by_id(db, document_id)
        doc.is_active = False
        db.commit()

    @staticmethod
    def new_version(db: Session, document_id: int, data: DocumentCreate, user_id: Optional[int] = None) -> Document:
        old_doc = DocumentService.get_by_id(db, document_id)
        old_doc.stato = DocumentStatus.ARCHIVED
        new_doc = Document(
            **data.model_dump(),
            versione=old_doc.versione + 1,
            documento_padre_id=old_doc.id,
            created_by=user_id,
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        return new_doc

    @staticmethod
    def get_versions(db: Session, document_id: int) -> list[Document]:
        doc = DocumentService.get_by_id(db, document_id)
        return db.query(Document).filter(
            Document.documento_padre_id == doc.documento_padre_id or Document.id == document_id
        ).order_by(Document.versione.desc()).all()
