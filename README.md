# EngiPro

Applicazione per la gestione di aziende, lavoratori, scadenze, documenti, medicina del lavoro, formazione, DPI e presenze. Il repository contiene un backend FastAPI e un frontend React in JavaScript con Vite. Non contiene app mobile, workflow n8n o sistemi AI multi-agente.

## Stack e struttura

- `backend/app`: API, modelli SQLAlchemy, schemi Pydantic v2, servizi e configurazione.
- `backend/alembic`: migrazioni `001` (schema iniziale), `002` (audit), `003` (soft delete).
- `backend/tests`: test unitari e API su SQLite, Redis sostituito nei test e MinIO mockato.
- `frontend/src`: interfaccia React 18 e client API; build con Vite 5.
- `docker-compose.yml` e `nginx/`: PostgreSQL 16, Redis 7, MinIO, backend, frontend e reverse proxy.

## Avvio con Docker Compose

Il comando backend applica le migrazioni, esegue il seed e avvia Uvicorn. Il seed crea `admin@engipro.it` solo se manca e richiede `ADMIN_INITIAL_PASSWORD`, anche in sviluppo. La password deve avere almeno 10 caratteri, una maiuscola, una minuscola, una cifra e un carattere speciale.

In PowerShell impostare una password privata e gli indirizzi necessari nell'ambiente o in un file `.env` locale escluso da Git. La configurazione è descritta in `backend/.env.example`.

```powershell
$env:ADMIN_INITIAL_PASSWORD = Read-Host 'Password iniziale admin'
$env:MINIO_PUBLIC_ENDPOINT = 'localhost:9002'
$env:MINIO_PUBLIC_SECURE = 'false'
docker compose up -d --build
```

| Servizio | Accesso locale previsto dal Compose |
| --- | --- |
| Interfaccia via Nginx | http://localhost:81 |
| API diretta | http://localhost:8002/api/v1 |
| Swagger | http://localhost:8002/api/docs |
| Health | http://localhost:8002/health |
| PostgreSQL | localhost:5433 |
| Redis | localhost:6380 |
| MinIO API / console | http://localhost:9002 / http://localhost:9003 |

Il Compose incluso usa credenziali e impostazioni di sviluppo. Per un ambiente pubblico occorre configurare segreti privati, `ENV=production`, `DEBUG=false`, TLS, CORS e restrizioni di rete. Non è stato eseguito un deploy Docker/ZimaOS durante questo intervento.

## Backend locale e test su Windows

```powershell
py -3.11 -m venv backend\.venv
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
# Modificare .env con DATABASE_URL e gli endpoint effettivamente raggiungibili.
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m scripts.seed
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Le porte pubblicate dal Compose sono 5433 per PostgreSQL, 6380 per Redis e 9002 per MinIO; adattare gli esempi `.env` se si usano questi servizi dal processo Python locale. All'interno del Compose il backend usa i nomi dei servizi e le porte interne.

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

I test non richiedono PostgreSQL, Redis o MinIO attivi. Risultato verificato: **127 passed, 20 warnings**. Le deprecazioni Pydantic/SQLAlchemy/Argon2 e gli avvisi sul ciclo delle FK nelle fixture sono ancora presenti.

Per il frontend, dalla cartella `frontend`:

```powershell
npm install
npm run build
```

Build verificata: 31 moduli trasformati. `npm install` segnala 2 vulnerabilità (1 moderata, 1 alta), non corrette in questo intervento. Il proxy di sviluppo Vite attuale usa il nome Docker `backend`; per avviarlo direttamente su Windows serve un endpoint backend risolvibile.

## Migrazioni e database esistenti

Lo schema non viene più creato durante l'import dell'applicazione. Su un database vuoto usare `alembic upgrade head`. Su database già creati con `create_all`, la migrazione iniziale può trovare tabelle esistenti: prima effettuare un backup e verificare la corrispondenza dello schema con `001`. Solo dopo una riconciliazione verificata è possibile impostare il baseline con `alembic stamp 001` e applicare le revisioni successive. Non effettuare uno stamp automatico su schemi non verificati.

Le migrazioni sono provate con upgrade/downgrade su SQLite; la generazione SQL PostgreSQL è verificata senza esecuzione su un server PostgreSQL reale. Le cancellazioni di dominio esposte dalle API usano `is_active=False`.

## Autenticazione e isolamento aziendale

Access token JWT di 8 ore, refresh token di 7 giorni, hash Argon2 e identificatore `jti` distinto per ogni token. `POST /api/v1/auth/logout` richiede il Bearer access token e accetta un body opzionale `{"refresh_token":"..."}`; i token vengono revocati in Redis fino alla scadenza.

La registrazione pubblica consente soltanto il ruolo WORKER. L'assegnazione di aziende e ruoli privilegiati richiede una procedura amministrativa sul database: non esiste un'interfaccia di gestione utenti dedicata. Gli utenti non ADMIN senza azienda ricevono 403 sulle API di dominio. Le risorse di altre aziende non sono visibili e i riferimenti non autorizzati sono rifiutati.

Il rate limiting usa finestre di 60 secondi per IP: 10 richieste condivise tra login e registrazione, 300 sul resto di `/api/`, con risposta 429 e `Retry-After`. I limiti sono configurabili. `TRUSTED_PROXY_NETWORKS` accetta una lista JSON di IP/CIDR: includere soltanto l'indirizzo del proxy Nginx fidato. Senza configurazione, X-Forwarded-For è ignorato. Il limite Nginx già presente è separato.

Quando Redis non risponde, il backend registra warning e continua senza rate limiting né garanzia di revoca dei token. Monitorare i warning: un logout senza Redis non invalida il JWT sul server.

## Documenti e audit

Gli upload accettano i MIME di PDF, JPEG, PNG, DOCX e XLSX, con limite `MAX_UPLOAD_FILE_SIZE` (50 MiB predefiniti). I file sono salvati in MinIO con chiavi `companies/{company_id}/documents/{uuid}.{ext}`. Il download autenticato `GET /api/v1/documents/{id}/download` risponde con un redirect 302 a un URL firmato valido un'ora.

Configurare `MINIO_PUBLIC_ENDPOINT` con un host:porta raggiungibile dal browser, `MINIO_PUBLIC_SECURE` per HTTPS e `MINIO_REGION` per la firma. I link firmati consentono l'accesso fino alla loro scadenza anche dopo il logout. Gli oggetti già presenti nel precedente filesystem uploads non vengono trasferiti automaticamente.

L'audit registra metadati delle richieste personali/sanitarie e delle modifiche, inclusi login/logout riusciti o falliti. Non registra body o password. Ha sessione indipendente; eventuali errori vengono registrati nei log e non interrompono la richiesta. Le righe sono immutabili via ORM e tramite trigger nelle migrazioni SQLite/PostgreSQL.

Solo ADMIN può usare `GET /api/v1/audit/logs` e `/api/v1/audit/logs/export`, con filtri `user_id`, `resource_type`, `from_date`, `to_date`; la lista supporta `skip` e `limit`. L'export è CSV in streaming. Queste misure tecniche non costituiscono una certificazione di conformità GDPR o D.Lgs. 81/08; retention, procedure organizzative e verifica operativa restano da definire.

Dettaglio delle modifiche e verifiche: [STATUS.md](STATUS.md).
