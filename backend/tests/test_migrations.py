"""Exercise migrations independently of ORM create_all."""
from pathlib import Path
import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from app.core.config import settings
from app.core.database import Base


def test_migration_roundtrip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    url = f"sqlite:///{tmp_path / 'migration.db'}"
    monkeypatch.setattr(settings, "DATABASE_URL", url)
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    command.upgrade(config, "head")
    engine = sa.create_engine(url)
    with engine.connect() as connection:
        inspector = sa.inspect(connection)
        assert set(inspector.get_table_names()) == set(Base.metadata.tables) | {"alembic_version"}
        assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []
        assert any(fk["constrained_columns"] == ["responsabile_id"]
                   for fk in inspector.get_foreign_keys("departments"))
    command.downgrade(config, "base")
    with engine.connect() as connection:
        assert set(sa.inspect(connection).get_table_names()) <= {"alembic_version"}
        assert connection.execute(sa.text("SELECT count(*) FROM alembic_version")).scalar() == 0
    engine.dispose()
