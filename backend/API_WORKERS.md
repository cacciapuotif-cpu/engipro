# Worker API Documentation

API endpoints per la gestione dei lavoratori/dipendenti.

---

## 📋 Endpoint Summary

| Method | Endpoint | Descrizione |
|--------|----------|-----------|
| POST | `/api/v1/workers` | Crea lavoratore |
| GET | `/api/v1/workers?company_id={id}` | Elenca lavoratori |
| GET | `/api/v1/workers/search` | Cerca lavoratore |
| GET | `/api/v1/workers/{worker_id}` | Dettagli lavoratore |
| GET | `/api/v1/workers/cf/{cf}` | Trova per codice fiscale |
| PUT | `/api/v1/workers/{worker_id}` | Aggiorna lavoratore |
| DELETE | `/api/v1/workers/{worker_id}` | Cancella (soft delete) |
| POST | `/api/v1/workers/{worker_id}/status/{status}` | Cambia stato |
| GET | `/api/v1/workers/roles/rspp` | Elenca RSPP |
| GET | `/api/v1/workers/roles/rls` | Elenca RLS |
| GET | `/api/v1/workers/department/{dept_id}` | Lavoratori per reparto |
| GET | `/api/v1/workers/location/{loc_id}` | Lavoratori per sede |

---

## 🔐 Autenticazione

Tutte le richieste richiedono `Authorization: Bearer <ACCESS_TOKEN>`

```bash
curl -X GET http://localhost:8000/api/v1/workers \
  -H "Authorization: Bearer <token>"
```

---

## 📝 Dettagli Endpoint

### CREATE - POST `/api/v1/workers`

Creare un nuovo lavoratore.

**Permessi**: ADMIN, COMPANY_ADMIN, HR

**Request Body**:
```json
{
  "company_id": 1,
  "codice_fiscale": "RSSMRA90A01F839U",
  "nome": "Marco",
  "cognome": "Rossi",
  "data_nascita": "1990-01-01",
  "luogo_nascita": "Napoli",
  "mansione": "Operaio",
  "tipo_contratto": "FULL_TIME",
  "data_assunzione": "2023-01-15",
  "data_cessazione": null,
  "location_id": null,
  "department_id": null,
  "email": "marco.rossi@example.com",
  "telefono": "+39 333 1234567",
  "is_rspp": false,
  "is_rls": false,
  "is_medico_competente": false
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "company_id": 1,
  "codice_fiscale": "RSSMRA90A01F839U",
  "nome": "Marco",
  "cognome": "Rossi",
  "data_nascita": "1990-01-01",
  "mansione": "Operaio",
  "tipo_contratto": "FULL_TIME",
  "data_assunzione": "2023-01-15",
  "stato": "ACTIVE",
  "is_rspp": false,
  "is_rls": false,
  "is_medico_competente": false,
  "is_active": true,
  "created_at": "2026-02-27T10:00:00+00:00",
  "updated_at": "2026-02-27T10:00:00+00:00"
}
```

---

### LIST - GET `/api/v1/workers?company_id={id}&status={status}&skip={skip}&limit={limit}`

Elencare lavoratori con opzionali filtri.

**Query Parameters**:
- `company_id` (required): ID azienda
- `status` (optional): Filtra per stato (ACTIVE, INACTIVE, ON_LEAVE, TERMINATED)
- `skip` (optional, default: 0): Skip primi N record
- `limit` (optional, default: 100): Limita risultati a N record (max 1000)

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "nome": "Marco",
    "cognome": "Rossi",
    "codice_fiscale": "RSSMRA90A01F839U",
    "mansione": "Operaio",
    "stato": "ACTIVE",
    "is_active": true
  }
]
```

---

### SEARCH - GET `/api/v1/workers/search?company_id={id}&q={query}`

Cercare lavoratori per nome, cognome, CF, o mansione.

**Query Parameters**:
- `company_id` (required): ID azienda
- `q` (required): Query di ricerca (minimo 1 carattere)

**Example**:
```bash
GET /api/v1/workers/search?company_id=1&q=Marco
```

**Response** (200 OK): Lista di lavoratori corrispondenti

---

### GET BY ID - GET `/api/v1/workers/{worker_id}`

Ottenere dettagli completi di un lavoratore.

**Path Parameters**:
- `worker_id` (required): ID lavoratore

**Response** (200 OK): Oggetto WorkerResponse completo

---

### GET BY CF - GET `/api/v1/workers/cf/{codice_fiscale}`

Trovare lavoratore per codice fiscale.

**Path Parameters**:
- `codice_fiscale` (required): Codice fiscale (16 caratteri)

**Response** (200 OK): Oggetto WorkerResponse

---

### UPDATE - PUT `/api/v1/workers/{worker_id}`

Aggiornare dati lavoratore.

**Permessi**: ADMIN, COMPANY_ADMIN, HR, MANAGER

**Request Body** (tutti i campi opzionali):
```json
{
  "nome": "Marco",
  "cognome": "Rossi",
  "mansione": "Operaio Senior",
  "tipo_contratto": "FULL_TIME",
  "data_cessazione": null,
  "location_id": 2,
  "department_id": 3,
  "email": "marco.rossi@example.com",
  "telefono": "+39 333 9999999",
  "is_rspp": true,
  "is_rls": false,
  "is_medico_competente": false,
  "stato": "ACTIVE"
}
```

**Response** (200 OK): Oggetto WorkerResponse aggiornato

---

### DELETE - DELETE `/api/v1/workers/{worker_id}`

Cancellare (soft delete) un lavoratore (non elimina, solo marca come inattivo).

**Permessi**: ADMIN, COMPANY_ADMIN

**Response** (204 No Content)

---

### CHANGE STATUS - POST `/api/v1/workers/{worker_id}/status/{new_status}`

Cambiar lo stato del lavoratore.

**Permessi**: ADMIN, COMPANY_ADMIN, HR

**Path Parameters**:
- `worker_id` (required): ID lavoratore
- `new_status` (required): Nuovo stato (ACTIVE, INACTIVE, ON_LEAVE, TERMINATED)

**Response** (200 OK): Oggetto WorkerResponse con nuovo stato

---

### LIST RSPP - GET `/api/v1/workers/roles/rspp?company_id={id}`

Elencare tutti i responsabili della sicurezza (RSPP).

**Query Parameters**:
- `company_id` (required): ID azienda

**Response** (200 OK): Lista di WorkerListResponse (RSPP)

---

### LIST RLS - GET `/api/v1/workers/roles/rls?company_id={id}`

Elencare tutti i rappresentanti dei lavoratori (RLS).

**Query Parameters**:
- `company_id` (required): ID azienda

**Response** (200 OK): Lista di WorkerListResponse (RLS)

---

### BY DEPARTMENT - GET `/api/v1/workers/department/{department_id}`

Elencare lavoratori di un reparto.

**Path Parameters**:
- `department_id` (required): ID reparto

**Response** (200 OK): Lista di WorkerListResponse

---

### BY LOCATION - GET `/api/v1/workers/location/{location_id}`

Elencare lavoratori di una sede.

**Path Parameters**:
- `location_id` (required): ID sede

**Response** (200 OK): Lista di WorkerListResponse

---

## 🏷️ Tipi di Contratto

```
FULL_TIME          - Tempo pieno
PART_TIME          - Tempo parziale
TEMPORARY          - Temporaneo
APPRENTICE         - Apprendistato
PROJECT            - Progettuale
```

---

## 📊 Stati Lavoratore

```
ACTIVE             - Attivo
INACTIVE           - Inattivo
ON_LEAVE           - In congedo
TERMINATED         - Cessato
```

---

## 🧪 Esempi cURL

### Registrazione e Login

```bash
# 1. Registrazione
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"AdminPassword123!","role":"ADMIN"}'

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"AdminPassword123!"}'

# 3. Copiare access_token dalla risposta
TOKEN="<access_token>"
```

### CRUD Workers

```bash
# Creare lavoratore
curl -X POST http://localhost:8000/api/v1/workers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id":1,
    "codice_fiscale":"RSSMRA90A01F839U",
    "nome":"Marco","cognome":"Rossi",
    "data_nascita":"1990-01-01",
    "mansione":"Operaio",
    "tipo_contratto":"FULL_TIME",
    "data_assunzione":"2023-01-15"
  }'

# Elencare lavoratori
curl -X GET "http://localhost:8000/api/v1/workers?company_id=1" \
  -H "Authorization: Bearer $TOKEN"

# Cercare per nome
curl -X GET "http://localhost:8000/api/v1/workers/search?company_id=1&q=Marco" \
  -H "Authorization: Bearer $TOKEN"

# Dettagli lavoratore
curl -X GET http://localhost:8000/api/v1/workers/1 \
  -H "Authorization: Bearer $TOKEN"

# Aggiornare lavoratore
curl -X PUT http://localhost:8000/api/v1/workers/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mansione":"Operaio Senior","is_rspp":true}'

# Cambiare stato
curl -X POST http://localhost:8000/api/v1/workers/1/status/ON_LEAVE \
  -H "Authorization: Bearer $TOKEN"

# Cancellare lavoratore (soft delete)
curl -X DELETE http://localhost:8000/api/v1/workers/1 \
  -H "Authorization: Bearer $TOKEN"

# Elencare RSPP
curl -X GET "http://localhost:8000/api/v1/workers/roles/rspp?company_id=1" \
  -H "Authorization: Bearer $TOKEN"
```

---

## ❌ Error Codes

| Code | Descrizione |
|------|-----------|
| 201 | Lavoratore creato |
| 200 | Operazione riuscita |
| 204 | Eliminato (no content) |
| 400 | Bad request (CF duplicato, dati invalidi) |
| 401 | Non autenticato |
| 403 | Non autorizzato (permessi insufficienti) |
| 404 | Lavoratore/Azienda non trovato |
| 500 | Server error |

---

## 🔒 Permessi Richiesti

| Endpoint | Permessi |
|----------|----------|
| POST /workers | ADMIN, COMPANY_ADMIN, HR |
| GET /workers | Qualsiasi utente autenticato |
| GET /workers/{id} | Qualsiasi utente autenticato |
| GET /workers/search | Qualsiasi utente autenticato |
| GET /workers/cf/{cf} | Qualsiasi utente autenticato |
| PUT /workers/{id} | ADMIN, COMPANY_ADMIN, HR, MANAGER |
| DELETE /workers/{id} | ADMIN, COMPANY_ADMIN |
| POST /workers/{id}/status | ADMIN, COMPANY_ADMIN, HR |
| GET /workers/roles/* | Qualsiasi utente autenticato |
| GET /workers/department/* | Qualsiasi utente autenticato |
| GET /workers/location/* | Qualsiasi utente autenticato |

---

**Versione API**: 1.0  
**Last Updated**: 2026-02-27
