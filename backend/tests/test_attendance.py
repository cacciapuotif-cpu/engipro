"""
Unit tests for Attendance module.
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import date, datetime, timezone
from app.models.attendance import Timbratura, AttendanceRecord, TimbratureType, TimbratureMethod, AttendanceStatus
from app.schemas.attendance import TimbratureCreate, AttendanceRecordCreate, AttendanceRecordUpdate
from app.services.attendance import TimbratureService, AttendanceRecordService


def make_timbratura(**kwargs):
    defaults = dict(
        id=1, worker_id=1, company_id=1,
        tipo=TimbratureType.ENTRATA, metodo=TimbratureMethod.GPS,
        timestamp=datetime(2026, 6, 1, 8, 0, 0, tzinfo=timezone.utc),
        latitudine=45.4654, longitudine=9.1859,
        accuratezza_metri=5.0, indirizzo="Via Roma 1, Milano",
        note=None, is_valid=True,
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    t = MagicMock(spec=Timbratura)
    for k, v in defaults.items():
        setattr(t, k, v)
    return t


def make_record(**kwargs):
    defaults = dict(
        id=1, worker_id=1, company_id=1,
        data=date(2026, 6, 1), stato=AttendanceStatus.PRESENT,
        ora_entrata=datetime(2026, 6, 1, 8, 0, tzinfo=timezone.utc),
        ora_uscita=datetime(2026, 6, 1, 17, 0, tzinfo=timezone.utc),
        ore_lavorate=9.0, ore_straordinario=1.0,
        note=None, approvato=False, approvato_da=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    r = MagicMock(spec=AttendanceRecord)
    for k, v in defaults.items():
        setattr(r, k, v)
    return r


class TestTimbratureService:

    def test_create_timbratura_entrata(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        db.refresh.side_effect = lambda x: None
        data = TimbratureCreate(
            worker_id=1, company_id=1,
            tipo=TimbratureType.ENTRATA,
            metodo=TimbratureMethod.GPS,
            timestamp=datetime(2026, 6, 1, 8, 0, tzinfo=timezone.utc),
            latitudine=45.4654, longitudine=9.1859,
        )
        TimbratureService.create(db, data)
        db.add.assert_called()
        db.commit.assert_called_once()

    def test_create_timbratura_uscita_calcola_ore(self):
        db = MagicMock()
        record = make_record(
            ora_entrata=datetime(2026, 6, 1, 8, 0, tzinfo=timezone.utc),
            ora_uscita=None, ore_lavorate=None
        )
        db.query.return_value.filter.return_value.first.return_value = record
        db.refresh.side_effect = lambda x: None
        data = TimbratureCreate(
            worker_id=1, company_id=1,
            tipo=TimbratureType.USCITA,
            metodo=TimbratureMethod.GPS,
            timestamp=datetime(2026, 6, 1, 17, 0, tzinfo=timezone.utc),
        )
        TimbratureService.create(db, data)
        assert record.ore_lavorate == 9.0
        assert record.ore_straordinario == 1.0

    def test_get_by_worker(self):
        db = MagicMock()
        timbrature = [make_timbratura(id=i) for i in range(3)]
        db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = timbrature
        result = TimbratureService.get_by_worker(db, 1)
        assert len(result) == 3


class TestAttendanceRecordService:

    def test_create_record(self):
        db = MagicMock()
        data = AttendanceRecordCreate(
            worker_id=1, company_id=1,
            data=date(2026, 6, 1),
            stato=AttendanceStatus.PRESENT,
        )
        db.refresh.side_effect = lambda x: None
        AttendanceRecordService.create(db, data)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_get_by_id_found(self):
        db = MagicMock()
        record = make_record()
        db.query.return_value.filter.return_value.first.return_value = record
        result = AttendanceRecordService.get_by_id(db, 1)
        assert result.id == 1

    def test_get_by_id_not_found(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(ValueError, match="non trovato"):
            AttendanceRecordService.get_by_id(db, 999)

    def test_update_record(self):
        db = MagicMock()
        record = make_record()
        db.query.return_value.filter.return_value.first.return_value = record
        data = AttendanceRecordUpdate(stato=AttendanceStatus.SICK, note="Malattia")
        AttendanceRecordService.update(db, 1, data)
        assert record.stato == AttendanceStatus.SICK
        assert record.note == "Malattia"
        db.commit.assert_called_once()

    def test_approve_record(self):
        db = MagicMock()
        record = make_record()
        db.query.return_value.filter.return_value.first.return_value = record
        AttendanceRecordService.approve(db, 1, user_id=5)
        assert record.approvato == True
        assert record.approvato_da == 5
        db.commit.assert_called_once()

    def test_attendance_status_enum(self):
        assert AttendanceStatus.PRESENT == "PRESENT"
        assert AttendanceStatus.SICK == "SICK"
        assert TimbratureType.ENTRATA == "ENTRATA"
        assert TimbratureMethod.GPS == "GPS"
