"""
Unit tests for Documents module.
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from app.models.document import Document, DocumentCategory, DocumentStatus
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.services.document import DocumentService


def make_document(**kwargs):
    defaults = dict(
        id=1, company_id=1, worker_id=None,
        titolo="Test Documento", descrizione="Descrizione test",
        categoria=DocumentCategory.SICUREZZA, stato=DocumentStatus.ACTIVE,
        storage_key="companies/1/documents/test.pdf",
        filename_originale="test.pdf", mime_type="application/pdf",
        dimensione_bytes=1024, versione=1,
        documento_padre_id=None, is_active=True,
        created_by=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        data_emissione=None, data_scadenza=None,
    )
    defaults.update(kwargs)
    d = MagicMock(spec=Document)
    for k, v in defaults.items():
        setattr(d, k, v)
    return d


def make_create_data(**kwargs):
    defaults = dict(
        company_id=1, titolo="Documento Sicurezza",
        categoria=DocumentCategory.SICUREZZA,
        filename_originale="doc.pdf", mime_type="application/pdf",
        dimensione_bytes=2048,
        storage_key="companies/1/documents/doc.pdf",
    )
    defaults.update(kwargs)
    return DocumentCreate(**defaults)


class TestDocumentService:

    def test_create_document(self):
        db = MagicMock()
        data = make_create_data()
        db.refresh.side_effect = lambda x: None
        DocumentService.create(db, data, user_id=1)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_get_by_id_found(self):
        db = MagicMock()
        doc = make_document()
        db.query.return_value.filter.return_value.first.return_value = doc
        result = DocumentService.get_by_id(db, 1)
        assert result.id == 1
        assert result.titolo == "Test Documento"

    def test_get_by_id_not_found(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(ValueError, match="non trovato"):
            DocumentService.get_by_id(db, 999)

    def test_get_all_no_filters(self):
        db = MagicMock()
        docs = [make_document(id=i) for i in range(3)]
        db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = docs
        result = DocumentService.get_all(db)
        assert len(result) == 3

    def test_update_document(self):
        db = MagicMock()
        doc = make_document()
        db.query.return_value.filter.return_value.first.return_value = doc
        data = DocumentUpdate(titolo="Nuovo Titolo", stato=DocumentStatus.ARCHIVED)
        DocumentService.update(db, 1, data)
        assert doc.titolo == "Nuovo Titolo"
        assert doc.stato == DocumentStatus.ARCHIVED
        db.commit.assert_called_once()

    def test_delete_document_soft(self):
        db = MagicMock()
        doc = make_document()
        db.query.return_value.filter.return_value.first.return_value = doc
        DocumentService.delete(db, 1)
        assert doc.is_active == False
        db.commit.assert_called_once()

    def test_new_version(self):
        db = MagicMock()
        old_doc = make_document(versione=1)
        db.query.return_value.filter.return_value.first.return_value = old_doc
        db.refresh.side_effect = lambda x: None
        data = make_create_data()
        DocumentService.new_version(db, 1, data, user_id=1)
        assert old_doc.stato == DocumentStatus.ARCHIVED
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_generate_storage_key(self):
        key = DocumentService._generate_storage_key(1, "documento.pdf")
        assert key.startswith("companies/1/documents/")
        assert key.endswith(".pdf")

    def test_document_category_enum(self):
        assert DocumentCategory.SICUREZZA == "SICUREZZA"
        assert DocumentCategory.FORMAZIONE == "FORMAZIONE"
        assert DocumentCategory.MEDICINA == "MEDICINA"
