"""
Unit tests for Medical module.
"""
import pytest
from unittest.mock import MagicMock
from datetime import date, datetime, timezone
from app.models.medical import HealthProtocol, MedicalVisit, VisitType, VisitStatus, VisitOutcome
from app.schemas.medical import HealthProtocolCreate, HealthProtocolUpdate, MedicalVisitCreate, MedicalVisitUpdate
from app.services.medical import HealthProtocolService, MedicalVisitService


def make_protocol(**kwargs):
    defaults = dict(
        id=1, company_id=1, titolo="Protocollo Sanitario 2026",
        descrizione=None, data_approvazione=date(2026, 1, 1),
        medico_competente="Dr. Rossi", is_active=True,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    p = MagicMock(spec=HealthProtocol)
    for k, v in defaults.items():
        setattr(p, k, v)
    return p


def make_visit(**kwargs):
    defaults = dict(
        id=1, worker_id=1, company_id=1, protocol_id=None,
        tipo=VisitType.PERIODICA, stato=VisitStatus.SCHEDULED,
        esito=None, data_visita=date(2026, 6, 1),
        data_prossima_visita=None, medico="Dr. Rossi",
        struttura="Clinica Test", limitazioni=None,
        prescrizioni=None, note=None,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    v = MagicMock(spec=MedicalVisit)
    for k, v2 in defaults.items():
        setattr(v, k, v2)
    return v


class TestHealthProtocolService:

    def test_create_protocol(self):
        db = MagicMock()
        data = HealthProtocolCreate(company_id=1, titolo="Protocollo 2026")
        db.refresh.side_effect = lambda x: None
        HealthProtocolService.create(db, data)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_get_by_id_found(self):
        db = MagicMock()
        protocol = make_protocol()
        db.query.return_value.filter.return_value.first.return_value = protocol
        result = HealthProtocolService.get_by_id(db, 1)
        assert result.id == 1
        assert result.titolo == "Protocollo Sanitario 2026"

    def test_get_by_id_not_found(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(ValueError, match="non trovato"):
            HealthProtocolService.get_by_id(db, 999)

    def test_update_protocol(self):
        db = MagicMock()
        protocol = make_protocol()
        db.query.return_value.filter.return_value.first.return_value = protocol
        data = HealthProtocolUpdate(titolo="Protocollo Aggiornato")
        HealthProtocolService.update(db, 1, data)
        assert protocol.titolo == "Protocollo Aggiornato"
        db.commit.assert_called_once()

    def test_delete_protocol_soft(self):
        db = MagicMock()
        protocol = make_protocol()
        db.query.return_value.filter.return_value.first.return_value = protocol
        HealthProtocolService.delete(db, 1)
        assert protocol.is_active == False
        db.commit.assert_called_once()


class TestMedicalVisitService:

    def test_create_visit(self):
        db = MagicMock()
        data = MedicalVisitCreate(
            worker_id=1, company_id=1,
            tipo=VisitType.PERIODICA, data_visita=date(2026, 6, 1),
        )
        db.refresh.side_effect = lambda x: None
        MedicalVisitService.create(db, data)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_get_by_id_found(self):
        db = MagicMock()
        visit = make_visit()
        db.query.return_value.filter.return_value.first.return_value = visit
        result = MedicalVisitService.get_by_id(db, 1)
        assert result.id == 1

    def test_get_by_id_not_found(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(ValueError, match="non trovata"):
            MedicalVisitService.get_by_id(db, 999)

    def test_complete_visit(self):
        db = MagicMock()
        visit = make_visit()
        db.query.return_value.filter.return_value.first.return_value = visit
        MedicalVisitService.complete(db, 1, VisitOutcome.IDONEO, date(2027, 6, 1))
        assert visit.stato == VisitStatus.COMPLETED
        assert visit.esito == VisitOutcome.IDONEO
        assert visit.data_prossima_visita == date(2027, 6, 1)
        db.commit.assert_called_once()

    def test_cancel_visit(self):
        db = MagicMock()
        visit = make_visit()
        db.query.return_value.filter.return_value.first.return_value = visit
        MedicalVisitService.cancel(db, 1)
        assert visit.stato == VisitStatus.CANCELLED
        db.commit.assert_called_once()

    def test_visit_type_enum(self):
        assert VisitType.PREVENTIVA == "PREVENTIVA"
        assert VisitType.PERIODICA == "PERIODICA"
        assert VisitOutcome.IDONEO == "IDONEO"
        assert VisitOutcome.NON_IDONEO == "NON_IDONEO"
