"""
Unit tests for Deadlines module.
"""
import pytest
from unittest.mock import MagicMock
from datetime import date
from app.models.deadline import Deadline, DeadlineType, DeadlineStatus, DeadlinePriority
from app.schemas.deadline import DeadlineCreate, DeadlineUpdate
from app.services.deadline import DeadlineService


def make_deadline(**kwargs):
    defaults = dict(
        id=1, company_id=1, worker_id=None,
        tipo=DeadlineType.FORMAZIONE, titolo="Test Scadenza",
        descrizione="Descrizione test", data_scadenza=date(2026, 12, 31),
        data_completamento=None, stato=DeadlineStatus.PENDING,
        priorita=DeadlinePriority.MEDIUM, giorni_preavviso=7,
        note=None, assegnato_a=None, notification_count=0,
    )
    defaults.update(kwargs)
    d = MagicMock(spec=Deadline)
    for k, v in defaults.items():
        setattr(d, k, v)
    return d


class TestDeadlineService:

    def test_create_deadline(self):
        db = MagicMock()
        data = DeadlineCreate(
            company_id=1, tipo=DeadlineType.FORMAZIONE,
            titolo="Corso Sicurezza", data_scadenza=date(2026, 12, 31),
        )
        db.refresh.side_effect = lambda x: None
        DeadlineService.create(db, data)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_get_by_id_found(self):
        db = MagicMock()
        deadline = make_deadline()
        db.query.return_value.filter.return_value.first.return_value = deadline
        result = DeadlineService.get_by_id(db, 1)
        assert result.id == 1
        assert result.titolo == "Test Scadenza"

    def test_get_by_id_not_found(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(ValueError, match="non trovata"):
            DeadlineService.get_by_id(db, 999)

    def test_get_all(self):
        db = MagicMock()
        deadlines = [make_deadline(id=i) for i in range(3)]
        db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = deadlines
        result = DeadlineService.get_all(db)
        assert len(result) == 3

    def test_update_deadline(self):
        db = MagicMock()
        deadline = make_deadline()
        db.query.return_value.filter.return_value.first.return_value = deadline
        data = DeadlineUpdate(titolo="Nuovo Titolo", stato=DeadlineStatus.ALERT)
        DeadlineService.update(db, 1, data)
        assert deadline.titolo == "Nuovo Titolo"
        assert deadline.stato == DeadlineStatus.ALERT
        db.commit.assert_called_once()

    def test_delete_deadline(self):
        db = MagicMock()
        deadline = make_deadline()
        db.query.return_value.filter.return_value.first.return_value = deadline
        DeadlineService.delete(db, 1)
        db.delete.assert_called_once_with(deadline)
        db.commit.assert_called_once()

    def test_complete_deadline(self):
        db = MagicMock()
        deadline = make_deadline()
        db.query.return_value.filter.return_value.first.return_value = deadline
        DeadlineService.complete(db, 1)
        assert deadline.stato == DeadlineStatus.COMPLETED
        assert deadline.data_completamento == date.today()
        db.commit.assert_called_once()

    def test_deadline_status_enum(self):
        assert DeadlineStatus.PENDING == "PENDING"
        assert DeadlineStatus.EXPIRED == "EXPIRED"
        assert DeadlineStatus.COMPLETED == "COMPLETED"

    def test_deadline_type_enum(self):
        assert DeadlineType.FORMAZIONE == "FORMAZIONE"
        assert DeadlineType.VISITA_MEDICA == "VISITA_MEDICA"
