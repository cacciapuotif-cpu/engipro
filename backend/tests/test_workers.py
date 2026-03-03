"""
Tests for worker endpoints.
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models import User, Company, Worker, UserRole, WorkerStatus
from app.core.security import hash_password


# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_db():
    """Clean database before each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def admin_user(db=None):
    """Create an admin user and get token."""
    # Create a company first
    db = TestingSessionLocal()
    company = Company(
        ragione_sociale="Test Company",
        partita_iva="12345678901",
        codice_fiscale="TESTCF0001",
    )
    db.add(company)
    db.commit()
    
    # Create admin user
    user = User(
        email="admin@example.com",
        hashed_password=hash_password("AdminPassword123!"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.close()
    
    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "AdminPassword123!",
        },
    )
    token = login_response.json()["access_token"]
    
    return token, company.id


def test_create_worker(admin_user):
    """Test creating a worker."""
    token, company_id = admin_user
    
    response = client.post(
        "/api/v1/workers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_id": company_id,
            "codice_fiscale": "RSSMRA90A01F839U",
            "nome": "Marco",
            "cognome": "Rossi",
            "data_nascita": "1990-01-01",
            "mansione": "Operaio",
            "tipo_contratto": "FULL_TIME",
            "data_assunzione": "2023-01-15",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Marco"
    assert data["cognome"] == "Rossi"
    assert data["stato"] == "ACTIVE"


def test_create_duplicate_cf(admin_user):
    """Test creating worker with duplicate CF."""
    token, company_id = admin_user
    
    # Create first worker
    client.post(
        "/api/v1/workers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_id": company_id,
            "codice_fiscale": "RSSMRA90A01F839U",
            "nome": "Marco",
            "cognome": "Rossi",
            "data_nascita": "1990-01-01",
            "mansione": "Operaio",
            "tipo_contratto": "FULL_TIME",
            "data_assunzione": "2023-01-15",
        },
    )
    
    # Try to create second worker with same CF
    response = client.post(
        "/api/v1/workers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_id": company_id,
            "codice_fiscale": "RSSMRA90A01F839U",
            "nome": "Maria",
            "cognome": "Rossi",
            "data_nascita": "1991-02-02",
            "mansione": "Impiegata",
            "tipo_contratto": "FULL_TIME",
            "data_assunzione": "2023-02-01",
        },
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_list_workers(admin_user):
    """Test listing workers."""
    token, company_id = admin_user
    
    # Create multiple workers
    for i in range(3):
        client.post(
            "/api/v1/workers",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "company_id": company_id,
                "codice_fiscale": f"CF{'0000000' + str(i)}",
                "nome": f"Worker{i}",
                "cognome": "Test",
                "data_nascita": "1990-01-01",
                "mansione": "Operaio",
                "tipo_contratto": "FULL_TIME",
                "data_assunzione": "2023-01-15",
            },
        )
    
    # List workers
    response = client.get(
        f"/api/v1/workers?company_id={company_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_search_workers(admin_user):
    """Test searching workers by name."""
    token, company_id = admin_user
    
    # Create worker
    client.post(
        "/api/v1/workers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_id": company_id,
            "codice_fiscale": "RSSMRA90A01F839U",
            "nome": "Marco",
            "cognome": "Rossi",
            "data_nascita": "1990-01-01",
            "mansione": "Operaio Qualificato",
            "tipo_contratto": "FULL_TIME",
            "data_assunzione": "2023-01-15",
        },
    )
    
    # Search
    response = client.get(
        f"/api/v1/workers/search?company_id={company_id}&q=Marco",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nome"] == "Marco"


def test_update_worker(admin_user):
    """Test updating worker."""
    token, company_id = admin_user
    
    # Create worker
    create_response = client.post(
        "/api/v1/workers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_id": company_id,
            "codice_fiscale": "RSSMRA90A01F839U",
            "nome": "Marco",
            "cognome": "Rossi",
            "data_nascita": "1990-01-01",
            "mansione": "Operaio",
            "tipo_contratto": "FULL_TIME",
            "data_assunzione": "2023-01-15",
        },
    )
    worker_id = create_response.json()["id"]
    
    # Update worker
    response = client.put(
        f"/api/v1/workers/{worker_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "mansione": "Operaio Senior",
            "is_rspp": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mansione"] == "Operaio Senior"
    assert data["is_rspp"] == True


def test_change_worker_status(admin_user):
    """Test changing worker status."""
    token, company_id = admin_user
    
    # Create worker
    create_response = client.post(
        "/api/v1/workers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_id": company_id,
            "codice_fiscale": "RSSMRA90A01F839U",
            "nome": "Marco",
            "cognome": "Rossi",
            "data_nascita": "1990-01-01",
            "mansione": "Operaio",
            "tipo_contratto": "FULL_TIME",
            "data_assunzione": "2023-01-15",
        },
    )
    worker_id = create_response.json()["id"]
    
    # Change status to ON_LEAVE
    response = client.post(
        f"/api/v1/workers/{worker_id}/status/ON_LEAVE",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["stato"] == "ON_LEAVE"


def test_delete_worker(admin_user):
    """Test deleting (soft delete) worker."""
    token, company_id = admin_user
    
    # Create worker
    create_response = client.post(
        "/api/v1/workers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_id": company_id,
            "codice_fiscale": "RSSMRA90A01F839U",
            "nome": "Marco",
            "cognome": "Rossi",
            "data_nascita": "1990-01-01",
            "mansione": "Operaio",
            "tipo_contratto": "FULL_TIME",
            "data_assunzione": "2023-01-15",
        },
    )
    worker_id = create_response.json()["id"]
    
    # Delete worker
    response = client.delete(
        f"/api/v1/workers/{worker_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204
    
    # Verify worker is marked as inactive
    get_response = client.get(
        f"/api/v1/workers/{worker_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = get_response.json()
    assert data["is_active"] == False
    assert data["stato"] == "INACTIVE"
