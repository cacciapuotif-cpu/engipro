"""
Pytest configuration — runs before any test module imports the app.
"""
import os

# Test fixtures create their own schema; use SQLite without PostgreSQL.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

import pytest


@pytest.fixture(autouse=True)
def redis_offline(monkeypatch: pytest.MonkeyPatch) -> None:
    """All tests run without network; dedicated tests inject a fake Redis."""
    monkeypatch.setattr('app.core.redis_client.get_redis', lambda: None)
    monkeypatch.setattr('app.core.rate_limit.get_redis', lambda: None)
