from datetime import date
from typing import Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.dependencies import get_current_active_user
from app.models import Company, User, UserRole, Worker, MedicalVisit, Document
from app.models.medical import VisitType
from app.models.document import DocumentCategory


@pytest.fixture
def tenants(api_db: Session) -> None:
    api_db.add(Company(id=2, ragione_sociale="B", partita_iva="22345678901", codice_fiscale="BBBBBBBBBBBBBBBB"))
    for cid in (1, 2):
        api_db.add(User(id=cid+1, email=f"company{cid}@example.com", hashed_password="unused",
                        role=UserRole.COMPANY_ADMIN, company_id=cid))
        api_db.add(Worker(id=cid, company_id=cid, nome=f"Worker{cid}", cognome="Test",
                          codice_fiscale=f"TSTWRK90A01H50{cid}Z", data_nascita=date(1990,1,1),
                          mansione="Test", data_assunzione=date(2020,1,1)))
    api_db.flush()
    for cid in (1, 2):
        api_db.add(MedicalVisit(id=cid, company_id=cid, worker_id=cid,
                                tipo=VisitType.PERIODICA, data_visita=date(2026,1,1)))
        api_db.add(Document(id=cid, company_id=cid, titolo=f"Doc{cid}",
                            categoria=DocumentCategory.MEDICINA,
                            storage_key=f"companies/{cid}/documents/test.pdf", filename_originale="test.pdf",
                            mime_type="application/pdf", dimensione_bytes=10))
    api_db.commit()


@pytest.mark.parametrize("path", ["workers", "medical/visits", "documents"])
def test_tenant_lists_and_details(api_client: TestClient, api_db: Session, tenants: None, path: str) -> None:
    assert len(api_client.get(f"/api/v1/{path}").json()) == 2
    for user_id, cid, foreign in ((2,1,2),(3,2,1)):
        app.dependency_overrides[get_current_active_user] = lambda: api_db.get(User, user_id)
        response = api_client.get(f"/api/v1/{path}")
        assert response.status_code == 200, response.text
        assert [row["id"] for row in response.json()] == [cid]
        assert api_client.get(f"/api/v1/{path}/{foreign}").status_code == 404
        assert api_client.get(f"/api/v1/{path}/{cid}").status_code == 200
        assert all(row["id"] == cid for row in api_client.get(f"/api/v1/{path}?company_id={foreign}").json())


@pytest.mark.parametrize("path,payload", [
    ("workers", dict(company_id=2, nome="Test", cognome="Test", codice_fiscale="RSSMRA90A01F839U",
                     data_nascita="1990-01-01", mansione="Test", data_assunzione="2020-01-01")),
    ("medical/visits", dict(company_id=2, worker_id=2, tipo="PERIODICA", data_visita="2026-01-01")),
    ("documents", dict(company_id=2, titolo="Other", categoria="MEDICINA", filename_originale="x.pdf",
                       mime_type="application/pdf", dimensione_bytes=1, storage_key="companies/2/documents/new.pdf")),
])
def test_cross_company_create_rejected(api_client: TestClient, api_db: Session, tenants: None,
                                       path: str, payload: dict[str, Any]) -> None:
    app.dependency_overrides[get_current_active_user] = lambda: api_db.get(User, 2)
    assert api_client.post(f"/api/v1/{path}", json=payload).status_code == 403


def test_foreign_links_rejected(api_client: TestClient, api_db: Session, tenants: None) -> None:
    app.dependency_overrides[get_current_active_user] = lambda: api_db.get(User, 2)
    response = api_client.post("/api/v1/medical/visits", json={"company_id":1,"worker_id":2,"tipo":"PERIODICA","data_visita":"2026-01-01"})
    assert response.status_code == 404
    response = api_client.post("/api/v1/documents/upload", data={"company_id":2}, files={"file":("x.pdf",b"pdf","application/pdf")})
    assert response.status_code == 403


def test_companies_and_unassigned_user(api_client: TestClient, api_db: Session, tenants: None) -> None:
    app.dependency_overrides[get_current_active_user] = lambda: api_db.get(User, 2)
    assert [row["id"] for row in api_client.get("/api/v1/companies").json()] == [1]
    assert api_client.get("/api/v1/companies/2/stats").status_code == 404
    api_db.get(User, 2).company_id = None
    api_db.commit()
    assert api_client.get("/api/v1/workers").status_code == 403


def test_registration_cannot_grant_admin(api_client: TestClient) -> None:
    response = api_client.post("/api/v1/auth/register", json={"email":"intruder@example.com","password":"StrongPass123!","role":"ADMIN"})
    assert response.status_code == 400


@pytest.mark.parametrize("path", ["workers", "medical/visits", "documents"])
def test_cross_company_update_rejected(api_client: TestClient, api_db: Session, tenants: None, path: str) -> None:
    app.dependency_overrides[get_current_active_user] = lambda: api_db.get(User, 2)
    assert api_client.put(f"/api/v1/{path}/1", json={"company_id":2}).status_code == 403
    assert api_client.put(f"/api/v1/{path}/2", json={}).status_code == 404


def test_document_versions_do_not_leak_roots(api_client: TestClient, api_db: Session, tenants: None) -> None:
    app.dependency_overrides[get_current_active_user] = lambda: api_db.get(User, 2)
    response = api_client.get("/api/v1/documents/1/versions")
    assert response.status_code == 200
    assert [row["id"] for row in response.json()] == [1]
    assert api_client.get("/api/v1/documents/2/download").status_code == 404
