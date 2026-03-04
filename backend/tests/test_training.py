"""
Unit tests for Training module.
"""
import pytest
from unittest.mock import MagicMock
from datetime import date, datetime, timezone
from app.models.training import Course, CourseEdition, CourseParticipation, CourseType, CourseStatus, EditionStatus, Attestato
from app.schemas.training import CourseCreate, CourseUpdate, EditionCreate, EditionUpdate, ParticipationCreate, ParticipationUpdate
from app.services.training import CourseService, EditionService, ParticipationService


def make_course(**kwargs):
    defaults = dict(
        id=1, company_id=1, codice="FORM-001", titolo="Corso Sicurezza",
        descrizione=None, tipo=CourseType.OBBLIGATORIO, stato=CourseStatus.ACTIVE,
        durata_ore=8.0, validita_anni=2, provider=None, is_active=True,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    c = MagicMock(spec=Course)
    for k, v in defaults.items():
        setattr(c, k, v)
    return c


def make_edition(**kwargs):
    defaults = dict(
        id=1, course_id=1, data_inizio=date(2026, 6, 1), data_fine=date(2026, 6, 1),
        luogo="Sede", docente="Docente Test", max_partecipanti=20,
        stato=EditionStatus.PLANNED, note=None,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    e = MagicMock(spec=CourseEdition)
    for k, v in defaults.items():
        setattr(e, k, v)
    return e


def make_participation(**kwargs):
    defaults = dict(
        id=1, edition_id=1, worker_id=1, esito=Attestato.ASSENTE,
        data_attestato=None, data_scadenza_attestato=None,
        numero_attestato=None, note=None,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    p = MagicMock(spec=CourseParticipation)
    for k, v in defaults.items():
        setattr(p, k, v)
    return p


class TestCourseService:

    def test_create_course(self):
        db = MagicMock()
        data = CourseCreate(company_id=1, codice="FORM-001", titolo="Corso Sicurezza", durata_ore=8.0)
        db.refresh.side_effect = lambda x: None
        CourseService.create(db, data)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_get_by_id_found(self):
        db = MagicMock()
        course = make_course()
        db.query.return_value.filter.return_value.first.return_value = course
        result = CourseService.get_by_id(db, 1)
        assert result.id == 1
        assert result.codice == "FORM-001"

    def test_get_by_id_not_found(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(ValueError, match="non trovato"):
            CourseService.get_by_id(db, 999)

    def test_update_course(self):
        db = MagicMock()
        course = make_course()
        db.query.return_value.filter.return_value.first.return_value = course
        data = CourseUpdate(titolo="Nuovo Titolo")
        CourseService.update(db, 1, data)
        assert course.titolo == "Nuovo Titolo"
        db.commit.assert_called_once()

    def test_delete_course_soft(self):
        db = MagicMock()
        course = make_course()
        db.query.return_value.filter.return_value.first.return_value = course
        CourseService.delete(db, 1)
        assert course.is_active == False
        db.commit.assert_called_once()


class TestEditionService:

    def test_create_edition(self):
        db = MagicMock()
        data = EditionCreate(course_id=1, data_inizio=date(2026, 6, 1), data_fine=date(2026, 6, 1))
        db.refresh.side_effect = lambda x: None
        EditionService.create(db, data)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_get_by_id_not_found(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(ValueError, match="non trovata"):
            EditionService.get_by_id(db, 999)

    def test_complete_edition(self):
        db = MagicMock()
        edition = make_edition()
        db.query.return_value.filter.return_value.first.return_value = edition
        EditionService.complete(db, 1)
        assert edition.stato == EditionStatus.COMPLETED
        db.commit.assert_called_once()


class TestParticipationService:

    def test_create_participation(self):
        db = MagicMock()
        data = ParticipationCreate(edition_id=1, worker_id=1)
        db.refresh.side_effect = lambda x: None
        ParticipationService.create(db, data)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_update_participation(self):
        db = MagicMock()
        p = make_participation()
        db.query.return_value.filter.return_value.first.return_value = p
        data = ParticipationUpdate(esito=Attestato.SUPERATO, data_attestato=date(2026, 6, 1))
        ParticipationService.update(db, 1, data)
        assert p.esito == Attestato.SUPERATO
        db.commit.assert_called_once()

    def test_delete_participation(self):
        db = MagicMock()
        p = make_participation()
        db.query.return_value.filter.return_value.first.return_value = p
        ParticipationService.delete(db, 1)
        db.delete.assert_called_once_with(p)
        db.commit.assert_called_once()

    def test_attestato_enum(self):
        assert Attestato.SUPERATO == "SUPERATO"
        assert Attestato.NON_SUPERATO == "NON_SUPERATO"
        assert Attestato.ASSENTE == "ASSENTE"
