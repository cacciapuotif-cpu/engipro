"""
Unit tests for DPI module.
"""
import pytest
from unittest.mock import MagicMock
from datetime import date, datetime, timezone
from app.models.dpi import DPIItem, DPIAssignment, DPICategory, DPIStatus, AssignmentStatus
from app.schemas.dpi import DPIItemCreate, DPIItemUpdate, DPIAssignmentCreate, DPIAssignmentUpdate
from app.services.dpi import DPIItemService, DPIAssignmentService


def make_dpi_item(**kwargs):
    defaults = dict(
        id=1, company_id=1, codice="DPI-001", nome="Casco Protettivo",
        descrizione=None, categoria=DPICategory.TESTA, stato=DPIStatus.AVAILABLE,
        marca="3M", modello="H700", taglia="L", numero_serie="SN001",
        data_acquisto=date(2026, 1, 1), data_scadenza=date(2028, 1, 1),
        costo=45.0, note=None, is_active=True,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    d = MagicMock(spec=DPIItem)
    for k, v in defaults.items():
        setattr(d, k, v)
    return d


def make_assignment(**kwargs):
    defaults = dict(
        id=1, dpi_item_id=1, worker_id=1, company_id=1,
        stato=AssignmentStatus.ACTIVE, data_assegnazione=date(2026, 1, 1),
        data_restituzione=None, note=None, firma_ricevuta=False,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    a = MagicMock(spec=DPIAssignment)
    for k, v in defaults.items():
        setattr(a, k, v)
    return a


class TestDPIItemService:

    def test_create_dpi_item(self):
        db = MagicMock()
        data = DPIItemCreate(
            company_id=1, codice="DPI-001", nome="Casco",
            categoria=DPICategory.TESTA,
        )
        db.refresh.side_effect = lambda x: None
        DPIItemService.create(db, data)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_get_by_id_found(self):
        db = MagicMock()
        item = make_dpi_item()
        db.query.return_value.filter.return_value.first.return_value = item
        result = DPIItemService.get_by_id(db, 1)
        assert result.id == 1
        assert result.codice == "DPI-001"

    def test_get_by_id_not_found(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(ValueError, match="non trovato"):
            DPIItemService.get_by_id(db, 999)

    def test_update_dpi_item(self):
        db = MagicMock()
        item = make_dpi_item()
        db.query.return_value.filter.return_value.first.return_value = item
        data = DPIItemUpdate(nome="Casco Aggiornato", stato=DPIStatus.MAINTENANCE)
        DPIItemService.update(db, 1, data)
        assert item.nome == "Casco Aggiornato"
        assert item.stato == DPIStatus.MAINTENANCE
        db.commit.assert_called_once()

    def test_delete_dpi_item_soft(self):
        db = MagicMock()
        item = make_dpi_item()
        db.query.return_value.filter.return_value.first.return_value = item
        DPIItemService.delete(db, 1)
        assert item.is_active == False
        db.commit.assert_called_once()


class TestDPIAssignmentService:

    def test_create_assignment(self):
        db = MagicMock()
        item = make_dpi_item()
        db.query.return_value.filter.return_value.first.return_value = item
        data = DPIAssignmentCreate(
            dpi_item_id=1, worker_id=1, company_id=1,
            data_assegnazione=date(2026, 1, 1),
        )
        db.refresh.side_effect = lambda x: None
        DPIAssignmentService.create(db, data)
        assert item.stato == DPIStatus.ASSIGNED
        db.commit.assert_called_once()

    def test_get_by_id_not_found(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(ValueError, match="non trovata"):
            DPIAssignmentService.get_by_id(db, 999)

    def test_return_dpi(self):
        db = MagicMock()
        assignment = make_assignment()
        item = make_dpi_item(stato=DPIStatus.ASSIGNED)
        db.query.return_value.filter.return_value.first.side_effect = [assignment, item]
        DPIAssignmentService.return_dpi(db, 1)
        assert assignment.stato == AssignmentStatus.RETURNED
        assert assignment.data_restituzione == date.today()
        assert item.stato == DPIStatus.AVAILABLE
        db.commit.assert_called_once()

    def test_update_assignment(self):
        db = MagicMock()
        assignment = make_assignment()
        db.query.return_value.filter.return_value.first.return_value = assignment
        data = DPIAssignmentUpdate(firma_ricevuta=True)
        DPIAssignmentService.update(db, 1, data)
        assert assignment.firma_ricevuta == True
        db.commit.assert_called_once()

    def test_dpi_category_enum(self):
        assert DPICategory.TESTA == "TESTA"
        assert DPICategory.ANTICADUTA == "ANTICADUTA"
        assert DPIStatus.AVAILABLE == "AVAILABLE"
        assert AssignmentStatus.ACTIVE == "ACTIVE"
