# EngiPro - Development Guide

Guida completa per lo sviluppo locale di EngiPro.

---

## 🚀 Quick Start (Docker Compose)

```bash
# 1. Clonare il repository
git clone <your-repo>
cd engipro

# 2. Avviare i container
docker-compose up -d

# 3. Verificare i servizi
docker-compose ps

# 4. Accedere alle API
# Backend: http://localhost:8000
# Swagger docs: http://localhost:8000/api/docs
# MinIO console: http://localhost:9001 (minioadmin/minioadmin)
```

---

## 🖥️ Local Development (Senza Docker)

### Prerequisiti
- Python 3.11+
- PostgreSQL 16 (oppure usa Docker per solo DB)
- Redis 7 (opzionale, per cache)

### Setup Backend

```bash
# 1. Navigare nella cartella backend
cd backend

# 2. Creare environment virtuale
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Installare dipendenze
pip install -r requirements.txt

# 4. Configurare environment
cp .env.example .env
# Modificare .env con i tuoi dati (database, JWT secret, etc.)

# 5. (OPZIONALE) Avviare solo servizi Docker
# Da un altro terminal:
docker-compose up -d postgres redis minio

# 6. Avviare FastAPI
uvicorn app.main:app --reload
```

API disponibile su: `http://localhost:8000`

---

## 🧪 Testing

### Eseguire test di autenticazione

```bash
# Installa pytest
pip install pytest pytest-asyncio

# Esegui i test
pytest tests/ -v

# Con coverage
pytest tests/ --cov=app --cov-report=html
```

### Test manuale con curl

```bash
# 1. Registrazione
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User"
  }'

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'

# 3. Usare access_token (da login) per accedere a /me
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

# 4. Refresh token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<REFRESH_TOKEN>"
  }'
```

---

## 📊 Database Migrations (Alembic)

```bash
# Creare una nuova migrazione
alembic revision --autogenerate -m "Add new table"

# Eseguire le migrazioni
alembic upgrade head

# Rollback ultima migrazione
alembic downgrade -1

# Vedere storia migrazioni
alembic history
```

---

## 🔐 Security

### JWT Secrets

In **production**, cambia il SECRET_KEY in `.env`:

```bash
# Generare una nuova secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Password Requirements
- Minimo 8 caratteri
- Hashing: Argon2id
- Validazione lato server

---

## 🛠️ Struttura API

### Autenticazione

```
POST   /api/v1/auth/register         - Registrazione nuovo utente
POST   /api/v1/auth/login            - Login
POST   /api/v1/auth/refresh          - Refresh access token
GET    /api/v1/auth/me               - Profilo utente corrente
POST   /api/v1/auth/logout           - Logout (client-side)
```

### Aziende

```
GET    /api/v1/companies             - Elenco aziende
POST   /api/v1/companies             - Crea azienda (ADMIN)
GET    /api/v1/companies/{id}        - Dettagli azienda
PUT    /api/v1/companies/{id}        - Aggiorna azienda (ADMIN/COMPANY_ADMIN)
DELETE /api/v1/companies/{id}        - Cancella azienda (ADMIN)
GET    /api/v1/companies/{id}/stats  - Statistiche azienda
```

---

## 🐛 Debugging

### Log livello DEBUG

Nel file `.env`, usa:
```
DEBUG=true
ENV=development
SQLALCHEMY_ECHO=true
```

### Ispezionare database

```bash
# Accedere a PostgreSQL via Docker
docker-compose exec postgres psql -U engipro -d engipro

# Query utili
\dt                    # Elenco tabelle
SELECT * FROM users;   # Elenco utenti
```

### MinIO Console

Accedi a: `http://localhost:9001`
- Username: minioadmin
- Password: minioadmin

---

## 📝 Naming Conventions

- **Python**: snake_case (functions, variables, files)
- **TypeScript/React**: camelCase (functions, variables)
- **Database**: snake_case (tables, columns)
- **API endpoints**: kebab-case (e.g., `/api/v1/users-stats`)
- **Classes**: PascalCase

---

## 🔄 Development Workflow

1. **Creare branch** per feature
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Fare commit frequenti**
   ```bash
   git commit -m "feat: add new endpoint"
   ```

3. **Push e PR** su GitHub

4. **Eseguire tests** prima di mergare
   ```bash
   pytest tests/
   black app/  # Formattazione
   flake8 app/ # Linting
   ```

---

## 📚 Risorse Utili

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org)
- [Pydantic Validation](https://docs.pydantic.dev)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8949)

---

**Versione**: 0.1.0  
**Last Updated**: 2026-02-27
