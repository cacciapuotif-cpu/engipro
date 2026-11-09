from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from redis.exceptions import ConnectionError as RedisConnectionError
from app.main import app
from app.core.dependencies import get_current_active_user
from app.core import redis_client
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, int | str] = {}
        self.ttls: dict[str, int] = {}
        self.key = ""

    def exists(self, key: str) -> bool:
        return key in self.values

    def setex(self, key: str, ttl: int, value: str) -> None:
        self.values[key] = value
        self.ttls[key] = ttl

    def pipeline(self, transaction: bool = True) -> "FakeRedis":
        return self

    def __enter__(self) -> "FakeRedis":
        return self

    def __exit__(self, *args: object) -> None:
        pass

    def incr(self, key: str) -> "FakeRedis":
        self.key = key
        self.values[key] = int(self.values.get(key, 0)) + 1
        return self

    def expire(self, key: str, ttl: int) -> "FakeRedis":
        self.ttls[key] = ttl
        return self

    def execute(self) -> list[int]:
        return [int(self.values[self.key]), 1]


@pytest.fixture
def fake_redis(monkeypatch: pytest.MonkeyPatch) -> FakeRedis:
    fake = FakeRedis()
    monkeypatch.setattr(redis_client, "get_redis", lambda: fake)
    return fake


def test_logout_revokes_both_tokens(api_client: TestClient, fake_redis: FakeRedis) -> None:
    app.dependency_overrides.pop(get_current_active_user)
    access, refresh = create_access_token("1"), create_refresh_token("1")
    headers = {"Authorization": f"Bearer {access}"}
    assert api_client.get("/api/v1/auth/me", headers=headers).status_code == 200
    assert api_client.post("/api/v1/auth/logout", headers=headers, json={"refresh_token": refresh}).status_code == 204
    assert api_client.get("/api/v1/auth/me", headers=headers).status_code == 401
    assert api_client.post("/api/v1/auth/refresh", json={"refresh_token": refresh}).status_code == 401
    ttl = fake_redis.ttls[f"blacklist:{decode_token(access)['jti']}"]
    assert 0 < ttl <= settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


def test_login_rate_limit(api_client: TestClient, fake_redis: FakeRedis) -> None:
    for _ in range(10):
        assert api_client.post("/api/v1/auth/login", json={}).status_code == 422
    response = api_client.post("/api/v1/auth/login", json={})
    assert response.status_code == 429
    assert 1 <= int(response.headers["Retry-After"]) <= 60


def test_without_redis(api_client: TestClient) -> None:
    for _ in range(11):
        assert api_client.post("/api/v1/auth/login", json={}).status_code == 422
    headers = {"Authorization": f"Bearer {create_access_token('1')}"}
    assert api_client.post("/api/v1/auth/logout", headers=headers).status_code == 204


def test_untrusted_forwarding_cannot_evade_limit(api_client: TestClient, fake_redis: FakeRedis) -> None:
    for i in range(10):
        assert api_client.post("/api/v1/auth/login", json={}, headers={"X-Forwarded-For": f"192.0.2.{i}"}).status_code == 422
    assert api_client.post("/api/v1/auth/login", json={}, headers={"X-Forwarded-For": "192.0.2.99"}).status_code == 429


def test_trusted_proxy_uses_last_address(api_client: TestClient, fake_redis: FakeRedis, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "TRUSTED_PROXY_IPS", ["testclient"])
    for i in range(10):
        assert api_client.post("/api/v1/auth/login", json={}, headers={"X-Forwarded-For": f"192.0.2.{i}, 192.0.2.100"}).status_code == 422
    assert api_client.post("/api/v1/auth/login", json={}, headers={"X-Forwarded-For": "192.0.2.101"}).status_code == 422
    assert api_client.post("/api/v1/auth/login", json={}, headers={"X-Forwarded-For": "192.0.2.100"}).status_code == 429


def test_tokens_have_unique_ids() -> None:
    assert decode_token(create_access_token("1"))["jti"] != decode_token(create_access_token("1"))["jti"]
    assert decode_token(create_refresh_token("1"))["jti"]


def test_redis_connection_failure(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    # Undo the autouse patch to exercise the connection function itself.
    monkeypatch.undo()
    client = MagicMock()
    client.ping.side_effect = RedisConnectionError()
    monkeypatch.setattr(redis_client, "_client", client)
    assert redis_client.get_redis() is None
    assert "Redis non disponibile" in caplog.text
