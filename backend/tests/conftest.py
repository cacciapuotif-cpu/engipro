"""
Pytest configuration — runs before any test module imports the app.
"""
import os

# Point application configuration at SQLite; fixtures create their own schema.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from collections.abc import Iterator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import Base, get_db
from app.core.dependencies import get_current_active_user
from app.models import User, UserRole, Company


@pytest.fixture
def api_db() -> Iterator[Session]:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(Company(id=1, ragione_sociale="A", partita_iva="12345678901", codice_fiscale="AAAAAAAAAAAAAAAA"))
        db.add(User(id=1, email="admin@example.com", hashed_password="unused", role=UserRole.ADMIN))
        db.commit()
        yield db
    engine.dispose()


@pytest.fixture
def api_client(api_db: Session) -> Iterator[TestClient]:
    original = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = lambda: api_db
    app.dependency_overrides[get_current_active_user] = lambda: api_db.get(User, 1)
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original)


@pytest.fixture(autouse=True)
def no_real_redis(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.core.redis_client.get_redis", lambda: None)
