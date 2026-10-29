"""Real endpoint tests with a deterministic Redis substitute."""
from unittest.mock import MagicMock, patch
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.auth import router
from app.core.database import get_db
from app.core.rate_limit import RateLimitMiddleware, client_ip
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.models import User
from starlette.requests import Request


class FakeRedis:
    def __init__(self) -> None:
        self.data: dict[str, int | str] = {}
        self.ttls: dict[str, int] = {}
        self.key = ''

    def exists(self, key: str) -> bool:
        return key in self.data

    def setex(self, key: str, ttl: int, value: str) -> None:
        self.data[key] = value
        self.ttls[key] = ttl

    def pipeline(self, transaction: bool = True) -> 'FakeRedis':
        return self

    def incr(self, key: str) -> None:
        self.key = key

    def expire(self, key: str, ttl: int) -> None:
        self.ttls[key] = ttl

    def execute(self) -> list[int]:
        count = int(self.data.get(self.key, 0)) + 1
        self.data[self.key] = count
        return [count, 1]


@pytest.fixture
def redis_client(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr('app.core.redis_client.get_redis', lambda: fake)
    monkeypatch.setattr('app.core.rate_limit.get_redis', lambda: fake)
    app = FastAPI()
    app.include_router(router)
    app.add_middleware(RateLimitMiddleware)
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = User(id=1, email='user@example.com', is_active=True)
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as client:
        yield client, fake


def test_logout_revokes_both_tokens(redis_client) -> None:
    client, fake = redis_client
    access, refresh = create_access_token('1'), create_refresh_token('1')
    headers = {'Authorization': f'Bearer {access}'}
    assert client.post('/api/v1/auth/logout', headers=headers, json={'refresh_token': refresh}).status_code == 204
    assert client.get('/api/v1/auth/me', headers=headers).status_code == 401
    assert client.post('/api/v1/auth/refresh', json={'refresh_token': refresh}).status_code == 401
    for token in (access, refresh):
        assert fake.ttls[f"blacklist:{decode_token(token)['jti']}"] > 0


def test_eleventh_login_limited(redis_client) -> None:
    client, _ = redis_client
    with patch('app.api.auth.AuthService.login', side_effect=ValueError('Invalid')):
        for _ in range(10):
            assert client.post('/api/v1/auth/login', json={'email': 'u@example.com', 'password': 'x'}).status_code == 401
        response = client.post('/api/v1/auth/login', json={'email': 'u@example.com', 'password': 'x'})
    assert response.status_code == 429
    assert 1 <= int(response.headers['retry-after']) <= 60


def test_without_redis_no_limit(redis_client, monkeypatch) -> None:
    client, _ = redis_client
    monkeypatch.setattr('app.core.redis_client.get_redis', lambda: None)
    monkeypatch.setattr('app.core.rate_limit.get_redis', lambda: None)
    with patch('app.api.auth.AuthService.login', side_effect=ValueError('Invalid')):
        for _ in range(12):
            assert client.post('/api/v1/auth/login', json={'email': 'u@example.com', 'password': 'x'}).status_code == 401
    access = create_access_token('1')
    assert client.post('/api/v1/auth/logout', headers={'Authorization': f'Bearer {access}'}).status_code == 204


def test_unique_jti() -> None:
    tokens = [create_access_token('1'), create_access_token('1'), create_refresh_token('1')]
    assert len({decode_token(token)['jti'] for token in tokens}) == 3


def test_forwarded_ip_trusted_only(monkeypatch) -> None:
    from app.core.config import settings
    request = Request({'type': 'http', 'client': ('192.0.2.5', 1000), 'headers': [(b'x-forwarded-for', b'1.2.3.4, 5.6.7.8')]})
    assert client_ip(request) == '192.0.2.5'
    monkeypatch.setattr(settings, 'TRUSTED_PROXY_NETWORKS', ['192.0.2.5/32'])
    assert client_ip(request) == '5.6.7.8'
