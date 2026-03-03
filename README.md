# EngiPro 🛡️

**Piattaforma cloud completa per la gestione della sicurezza sul lavoro e della medicina del lavoro, conforme al D.Lgs. 81/08**

---

## 📋 Descrizione

EngiPro è una piattaforma full-stack per aziende e lavoratori che consente:

- **Aziende**: Gestione completa della sicurezza, scadenze, documenti, formazione, visite mediche, DPI, presenze
- **Lavoratori**: Portale personale con app mobile per accedere a documenti, timbrature GPS, ferie, segnalazioni

---

## 🛠️ Stack Tecnologico

| Componente | Tecnologia |
|-----------|-----------|
| Backend | Python 3.11 + FastAPI |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Object Storage | MinIO (S3-compatible) |
| Frontend Web | React + TypeScript |
| App Mobile | React Native + Expo |
| Automazione | n8n self-hosted |
| Containerizzazione | Docker + Docker Compose |
| CI/CD | GitHub Actions |

---

## 📁 Struttura Progetto

```
engipro/
├── backend/
│   ├── app/
│   │   ├── api/           # Router FastAPI
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── services/      # Business logic
│   │   ├── core/          # Config, security, utils
│   │   └── main.py        # FastAPI app entry point
│   ├── alembic/           # Database migrations
│   ├── tests/             # Unit tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/
│   └── package.json
├── mobile/
│   ├── src/
│   └── package.json
├── n8n-workflows/
├── docker-compose.yml
└── README.md
```

---

## 🚀 Avvio Rapido

### Prerequisiti
- Docker e Docker Compose installati
- Python 3.11+ (per sviluppo locale)
- Node.js 18+ (per frontend)

### Con Docker Compose

```bash
# Clonare il repository
git clone https://github.com/...your-repo.../engipro.git
cd engipro

# Avviare i servizi
docker-compose up -d

# Migrazioni database (solo primo avvio)
docker-compose exec backend alembic upgrade head

# API disponibile su: http://localhost:8000
# Swagger docs: http://localhost:8000/api/docs
# MinIO console: http://localhost:9001 (minioadmin / minioadmin)
```

### Sviluppo Locale

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Avviare Docker Compose per soli servizi (postgres, redis, minio)
docker-compose up -d postgres redis minio
# Avviare FastAPI
uvicorn app.main:app --reload
```

---

## 🔑 Moduli Implementati

### ✅ Fase 1 - Backend (Completato)
- [x] Struttura FastAPI
- [x] Modelli SQLAlchemy (User, Company, Worker, Location, Department)
- [x] Autenticazione JWT (access + refresh tokens)
- [x] Hashing password Argon2
- [x] Configurazione environment
- [x] Docker Compose setup

### 📋 Fase 2 - API Core (In Progress)
- [ ] CRUD Aziende
- [ ] CRUD Lavoratori
- [ ] Modulo Scadenze
- [ ] Modulo Documenti

### 📱 Fase 3 - App Mobile
- [ ] Setup React Native
- [ ] Autenticazione + Biometrico
- [ ] Timbratura GPS
- [ ] Visualizzazione documenti

### ⚙️ Fase 4 - Automazione n8n
- [ ] Workflow alert scadenze
- [ ] Workflow onboarding dipendenti
- [ ] Distribuzione buste paga
- [ ] Gestione visite mediche

---

## 📚 Documentazione API

Una volta avviato il backend, accedi a:

```
http://localhost:8000/api/docs  (Swagger UI)
http://localhost:8000/redoc     (ReDoc)
```

---

## 🔒 Sicurezza

- JWT con scadenza 24h (access token) + 7 giorni (refresh token)
- Password: Argon2id, minimo 8 caratteri
- CORS configurato
- Rate limiting: 1000 req/ora per API key
- Input validation Pydantic
- SQL injection protection (SQLAlchemy ORM)
- File upload: max 50MB, validazione MIME type
- Audit logging operazioni sensibili
- GDPR compliance (soft delete, export dati, diritto oblio)

---

## 📧 Contatti

Per domande o problemi:
- Email: support@engipro.it
- Issues: GitHub issues

---

## 📄 Licenza

Proprietaria - EngiPro © 2024

---

**Versione**: 0.1.0  
**Ultimo aggiornamento**: 2026-02-27
