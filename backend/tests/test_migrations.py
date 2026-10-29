"""Verify reversible migrations and parity with ORM metadata."""
from pathlib import Path

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect

from app.core.config import settings
from app.core.database import Base


def test_initial_schema_roundtrip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    url = f"sqlite:///{(tmp_path / 'migration.sqlite').as_posix()}"
    monkeypatch.setattr(settings, "DATABASE_URL", url)
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    engine = create_engine(url)
    command.upgrade(config, "head")
    with engine.connect() as connection:
        assert set(inspect(connection).get_table_names()) == set(Base.metadata.tables) | {"alembic_version"}
        assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []
        fks = inspect(connection).get_foreign_keys("departments")
        assert any(fk["referred_table"] == "workers" and fk["constrained_columns"] == ["responsabile_id"] for fk in fks)
    command.downgrade(config, "base")
    with engine.connect() as connection:
        assert inspect(connection).get_table_names() == ["alembic_version"]
        assert connection.exec_driver_sql("SELECT count(*) FROM alembic_version").scalar_one() == 0
    command.upgrade(config, "head")
    command.downgrade(config, "base")
    engine.dispose()


@pytest.mark.parametrize('action', ['UPDATE', 'DELETE'])
def test_audit_database_immutable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, action: str) -> None:
    from sqlalchemy.exc import IntegrityError
    url = f"sqlite:///{(tmp_path / 'audit.sqlite').as_posix()}"
    monkeypatch.setattr(settings, 'DATABASE_URL', url)
    config = Config(str(Path(__file__).resolve().parents[1] / 'alembic.ini'))
    command.upgrade(config, 'head')
    engine = create_engine(url)
    with engine.begin() as connection:
        connection.exec_driver_sql("INSERT INTO audit_logs (action, resource_type, path, ip_address, user_agent, status_code, timestamp) VALUES ('GET', 'workers', '/api/v1/workers', '127.0.0.1', '', 200, CURRENT_TIMESTAMP)")
    with engine.begin() as connection:
        with pytest.raises(IntegrityError, match='immutabile'):
            connection.exec_driver_sql("UPDATE audit_logs SET action = 'PUT'" if action == 'UPDATE' else 'DELETE FROM audit_logs')
    engine.dispose()
