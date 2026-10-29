"""Tenant isolation exercised through real APIs and a real SQLite database."""
from collections.abc import Iterator
from datetime import date
import importlib
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.core.database import Base, get_db
from app.core.dependencies import get_current_active_user
from app.models import Company, User, Worker, Document, MedicalVisit, HealthProtocol


@pytest.fixture
def tenant_api():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        for i in (1, 2):
            db.add(Company(id=i, ragione_sociale=f'Company {i}', partita_iva=f'{i:011}', codice_fiscale=f'{i:016}'))
            db.add(Worker(id=i, company_id=i, codice_fiscale=f'{i:016}', nome='Nome', cognome='Cognome', data_nascita=date(1990, 1, 1), data_assunzione=date(2020, 1, 1), mansione='Tecnico'))
            db.add(Document(id=i, company_id=i, titolo=f'Doc {i}', categoria='ALTRO', storage_key=f'{i}.pdf', filename_originale='doc.pdf', mime_type='application/pdf', dimensione_bytes=10))
            db.add(MedicalVisit(id=i, company_id=i, worker_id=i, tipo='PERIODICA', data_visita=date(2026, 1, 1)))
            db.add(HealthProtocol(id=i, company_id=i, titolo=f'Protocol {i}'))
        db.commit()
    users = {
        'admin': User(id=10, email='admin@example.com', role='ADMIN', is_active=True),
        'a': User(id=11, email='a@example.com', role='COMPANY_ADMIN', company_id=1, is_active=True),
        'b': User(id=12, email='b@example.com', role='COMPANY_ADMIN', company_id=2, is_active=True),
        'unassigned': User(id=13, email='no@example.com', role='HR', is_active=True),
    }
    selected = ['admin']
    app = FastAPI()
    for name in ('companies', 'workers', 'deadlines', 'documents', 'medical', 'training', 'dpi', 'attendance'):
        app.include_router(importlib.import_module(f'app.api.{name}').router)
    def database() -> Iterator[Session]:
        with Session(engine) as db:
            yield db
    app.dependency_overrides[get_db] = database
    app.dependency_overrides[get_current_active_user] = lambda: users[selected[0]]
    with TestClient(app) as client:
        yield client, selected
    engine.dispose()


@pytest.mark.parametrize('path', ['workers', 'medical/visits', 'documents'])
def test_admin_sees_every_company(tenant_api, path: str) -> None:
    client, _ = tenant_api
    response = client.get(f'/api/v1/{path}')
    assert response.status_code == 200
    assert {row['id'] for row in response.json()} == {1, 2}
    assert client.get(f'/api/v1/{path}/2').status_code == 200


@pytest.mark.parametrize('path', ['workers', 'medical/visits', 'documents'])
def test_companies_cannot_read_each_other(tenant_api, path: str) -> None:
    client, selected = tenant_api
    for user, own, other in [('a', 1, 2), ('b', 2, 1)]:
        selected[0] = user
        response = client.get(f'/api/v1/{path}')
        assert response.status_code == 200
        assert {row['id'] for row in response.json()} == {own}
        assert client.get(f'/api/v1/{path}/{other}').status_code == 404
        assert client.get(f'/api/v1/{path}?company_id={other}').json() == []


@pytest.mark.parametrize(('path', 'payload'), [
    ('workers', dict(company_id=2, codice_fiscale='ABCDEF12G34H567I', nome='Nome', cognome='Cognome', data_nascita='1990-01-01', data_assunzione='2020-01-01', mansione='Tecnico')),
    ('medical/visits', dict(company_id=2, worker_id=2, tipo='PERIODICA', data_visita='2026-01-01')),
    ('documents', dict(company_id=2, titolo='Doc', categoria='ALTRO', storage_key='new.pdf', filename_originale='new.pdf', mime_type='application/pdf', dimensione_bytes=10)),
])
def test_cross_company_create_forbidden(tenant_api, path: str, payload: dict) -> None:
    client, selected = tenant_api
    selected[0] = 'a'
    assert client.post(f'/api/v1/{path}', json=payload).status_code == 403


def test_missing_company_forbidden(tenant_api) -> None:
    client, selected = tenant_api
    selected[0] = 'unassigned'
    assert client.get('/api/v1/workers').status_code == 403


def test_foreign_relationship_and_updates(tenant_api) -> None:
    client, selected = tenant_api
    selected[0] = 'a'
    assert client.post('/api/v1/medical/visits', json=dict(company_id=1, worker_id=2, tipo='PERIODICA', data_visita='2026-01-01')).status_code == 403
    assert client.put('/api/v1/documents/2', json={'titolo': 'Changed'}).status_code == 404
    assert client.get('/api/v1/documents/2/download').status_code == 404
    assert client.get('/api/v1/companies/2/stats').status_code == 404
    assert [row['id'] for row in client.get('/api/v1/companies').json()] == [1]
    assert client.get('/api/v1/medical/protocols/2').status_code == 404
    assert client.get('/api/v1/training/workers/2/participations').status_code == 404
    assert client.get('/api/v1/attendance/timbrature/worker/2').status_code == 404

