"""Audit writes, access controls, filtering, exports and immutability."""
from typing import Any, Iterator
from collections.abc import Iterator
from datetime import datetime, timezone
from unittest.mock import patch
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from app.api.audit import router as audit_router
from app.api.workers import router as worker_router
from app.api.medical import router as medical_router
from app.api.auth import router as auth_router
from app.core.audit_middleware import AuditMiddleware
from app.core.database import Base, get_db
from app.core.dependencies import get_current_active_user
from app.models import User, Company, AuditLog
from app.services.audit import AuditService


@pytest.fixture
def audit_api(monkeypatch: Any) -> Iterator[Any]:
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    monkeypatch.setattr('app.services.audit.SessionLocal', factory)
    with factory() as db:
        db.add(Company(id=1, ragione_sociale='Azienda', partita_iva='12345678901', codice_fiscale='1234567890123456'))
        db.add(User(id=1, email='admin@example.com', hashed_password='unused', role='ADMIN', is_active=True))
        db.commit()
    selected = ['ADMIN']
    app = FastAPI()
    for router in (audit_router, worker_router, medical_router, auth_router):
        app.include_router(router)
    app.add_middleware(AuditMiddleware)
    def database() -> Iterator[Session]:
        with factory() as db:
            yield db
    def user(request: Request) -> User:
        request.state.user_id = 1
        return User(id=1, email='admin@example.com', role=selected[0], company_id=1, is_active=True)
    app.dependency_overrides[get_db] = database
    app.dependency_overrides[get_current_active_user] = user
    with TestClient(app) as client:
        yield client, factory, selected
    engine.dispose()


def test_worker_post_logged(audit_api: Any) -> None:
    client, factory, _ = audit_api
    response = client.post('/api/v1/workers', json=dict(company_id=1, codice_fiscale='ABCDEF12G34H567I', nome='Nome', cognome='Cognome', data_nascita='1990-01-01', data_assunzione='2020-01-01', mansione='Tecnico'))
    assert response.status_code == 201
    with factory() as db:
        row = db.query(AuditLog).one()
        assert (row.action, row.resource_type, row.user_id, row.status_code) == ('POST', 'workers', 1, 201)
        assert row.path == '/api/v1/workers'


def test_medical_read_logged(audit_api: Any) -> None:
    client, factory, _ = audit_api
    assert client.get('/api/v1/medical/visits').status_code == 200
    with factory() as db:
        row = db.query(AuditLog).one()
        assert (row.action, row.resource_type, row.status_code) == ('GET', 'medical', 200)


def test_audit_admin_only(audit_api: Any) -> None:
    client, _, selected = audit_api
    selected[0] = 'COMPANY_ADMIN'
    assert client.get('/api/v1/audit/logs').status_code == 403
    assert client.get('/api/v1/audit/logs/export').status_code == 403


def test_filters_and_csv(audit_api: Any) -> None:
    client, factory, _ = audit_api
    with factory() as db:
        for year, resource in [(2024, 'workers'), (2025, 'medical'), (2026, 'workers')]:
            db.add(AuditLog(user_id=1, action='GET', resource_type=resource, path='/api/v1/' + resource, ip_address='127.0.0.1', user_agent='=DANGEROUS()', status_code=200, timestamp=datetime(year, 1, 1, tzinfo=timezone.utc)))
        db.commit()
    filters = {'user_id': 1, 'resource_type': 'workers', 'from_date': '2025-01-01T00:00:00Z', 'to_date': '2027-01-01T00:00:00Z'}
    response = client.get('/api/v1/audit/logs', params=filters)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['timestamp'].startswith('2026')
    assert client.get('/api/v1/audit/logs', params={'user_id': 999}).json() == []
    assert len(client.get('/api/v1/audit/logs', params={'skip': 1, 'limit': 1}).json()) == 1
    response = client.get('/api/v1/audit/logs/export', params=filters)
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('text/csv')
    lines = response.text.splitlines()
    assert lines[0] == 'id,user_id,action,resource_type,resource_id,path,ip_address,user_agent,status_code,timestamp'
    assert len(lines) == 2
    assert "'=DANGEROUS()" in response.text


def test_failed_login_logged_without_password(audit_api: Any) -> None:
    client, factory, _ = audit_api
    with patch('app.api.auth.AuthService.login', side_effect=ValueError('Invalid')):
        assert client.post('/api/v1/auth/login', json={'email': 'bad@example.com', 'password': 'SensitivePassword!'}).status_code == 401
    with factory() as db:
        row = db.query(AuditLog).one()
        assert row.status_code == 401 and row.resource_type == 'auth'
        assert 'SensitivePassword!' not in str(row.__dict__)


def test_audit_writer_never_raises() -> None:
    with patch('app.services.audit.SessionLocal', side_effect=RuntimeError('database unavailable')):
        AuditService.log(user_id=None, action='GET', resource_type='workers', resource_id=None, path='/api/v1/workers', ip_address='127.0.0.1', user_agent='', status_code=200)


def test_audit_orm_immutable(audit_api: Any) -> None:
    client, factory, _ = audit_api
    client.get('/api/v1/medical/visits')
    with factory() as db:
        row = db.query(AuditLog).one()
        row.action = 'DELETE'
        with pytest.raises(ValueError, match='immutabile'):
            db.commit()
        db.rollback()
        db.delete(db.query(AuditLog).one())
        with pytest.raises(ValueError, match='immutabile'):
            db.commit()
        db.rollback()


def test_successful_login_and_logout_logged(audit_api: Any) -> None:
    from app.core.security import create_access_token, create_refresh_token
    from app.schemas import TokenResponse
    client, factory, _ = audit_api
    token = create_access_token('1')
    tokens = TokenResponse(access_token=token, refresh_token=create_refresh_token('1'), expires_in=3600)
    with patch('app.api.auth.AuthService.login', return_value=tokens):
        assert client.post('/api/v1/auth/login', json={'email': 'admin@example.com', 'password': 'UnusedPassword1!'}).status_code == 200
    assert client.post('/api/v1/auth/logout', headers={'Authorization': f'Bearer {token}'}).status_code == 204
    with factory() as db:
        rows = db.query(AuditLog).order_by(AuditLog.id).all()
        assert [(row.path, row.status_code, row.user_id) for row in rows] == [('/api/v1/auth/login', 200, 1), ('/api/v1/auth/logout', 204, 1)]


def test_excluded_routes_not_logged(audit_api: Any) -> None:
    client, factory, _ = audit_api
    for path in ('/health', '/api/docs', '/api/openapi.json'):
        client.get(path)
    with factory() as db:
        assert db.query(AuditLog).count() == 0
