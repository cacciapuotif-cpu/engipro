# EngiPro — stato verificato

Aggiornato il 29 ottobre 2026. Repository `cacciapuotif-cpu/engipro`, branch `codex/production-hardening`. Nessun cambio di branch o modifica ad altri worktree.

## Risultati

Ambiente Windows/PowerShell, Python **3.11** in `backend/.venv`. Dipendenze installate da `backend/requirements.txt`; frontend preparato con `npm install`. Nessun virtualenv, node_modules, dist o database committato.

| Passaggio | Test aggiunti nel commit della priorità | Suite completa verificata | Commit |
| --- | ---: | --- | --- |
| Baseline | — | 73 passed, 19 warnings in 40.65s | baseline |
| P1 migrazioni reali | 1 | 74 passed, 20 warnings in 40.13s | e43dc94 |
| P2 MinIO | 6 | 80 passed, 20 warnings in 40.06s | 40a06b7 |
| P3 Redis/logout/rate limit | 5 | 85 passed, 20 warnings in 47.94s | 2705dcf |
| P4 password/seed | 9 | 94 passed, 20 warnings in 101.15s | ca502ba |
| P5 isolamento aziende | 11 | 105 passed, 20 warnings in 48.50s | 1748d20 |
| P6 audit | 11 | 116 passed, 20 warnings in 67.60s | 54762c4 |
| Correzioni trasversali | 11 | **127 passed, 20 warnings in 78.79s** | 542ac54 |

Totale: **54 casi di test aggiunti**, contando i casi parametrizzati. Attribuzione finale: P1 2, P2 7, P3 5, P4 10, P5 19, P6 11. I conteggi includono le verifiche aggiuntive trasversali.

Build frontend riuscita alla baseline e dopo P3/P5. Ultima esecuzione:

```text
> engipro-frontend@0.1.0 build
> vite build
vite v5.4.21 building for production...
✓ 31 modules transformed.
dist/index.html                  0.41 kB │ gzip:  0.30 kB
dist/assets/index-6klio8S5.js  209.09 kB │ gzip: 60.22 kB
✓ built in 1.95s
```

## P1 — completata

Migrazione iniziale esplicita delle 16 tabelle originarie, enum, indici e vincoli; FK circolare aggiunta dopo la creazione delle tabelle. Configurazione Alembic da settings, rimozione di create_all dall'app, bootstrap Compose con migrazioni prima del seed. Test upgrade/downgrade, parità con metadata, FK circolare e generazione SQL PostgreSQL.

File: `backend/alembic.ini`, `backend/alembic/env.py`, `backend/alembic/versions/001_initial_schema.py`, `backend/app/main.py`, `backend/tests/conftest.py`, `backend/tests/test_migrations.py`, `docker-compose.yml`. Eliminato `backend/alembic/versions/001_add_deadlines_table.py`.

## P2 — completata

Storage MinIO lazy con dependency sostituibile, bucket inizializzato al primo uso, upload limitato, tipi MIME ammessi e download 302 firmato. Rimosso uploads_data. Endpoint pubblico separato configurabile per URL raggiungibili dal browser. Test di adapter e API con storage mockato.

File: `backend/app/core/storage.py`, `backend/app/api/documents.py`, `backend/app/core/config.py`, `backend/.env.example`, `backend/tests/test_storage.py`, `backend/tests/test_documents.py`, `docker-compose.yml`.

## P3 — completata

JTI su access/refresh; blacklist Redis con TTL residuo; verifica su autenticazione e refresh. Logout revoca anche il refresh opzionale. Middleware con finestre per IP e proxy fidati configurabili, Retry-After e degradazione quando Redis non risponde. Frontend chiama il logout prima di cancellare i token. Test senza rete con Redis finto.

File: `backend/app/core/redis_client.py`, `backend/app/core/rate_limit.py`, `backend/app/core/security.py`, `backend/app/core/config.py`, `backend/app/services/auth.py`, `backend/app/api/auth.py`, `backend/app/main.py`, `backend/.env.example`, `backend/tests/conftest.py`, `backend/tests/test_redis_security.py`, `frontend/src/api.js`, `frontend/src/App.jsx`, `docker-compose.yml`.

## P4 — completata

Password di almeno 10 caratteri, maiuscola, minuscola, cifra e speciale; errori italiani. Seed senza credenziale incorporata e con logging; richiede ADMIN_INITIAL_PASSWORD al primo avvio anche in sviluppo. Le password positive dei test preesistenti rispettavano già la nuova policy. Registrazione pubblica limitata al ruolo WORKER per impedire l'autoassegnazione di ADMIN.

File: `backend/app/core/security.py`, `backend/app/core/config.py`, `backend/app/schemas/user.py`, `backend/app/services/auth.py`, `backend/scripts/seed.py`, `backend/.env.example`, `backend/tests/test_password_policy.py`, `docker-compose.yml`.

## P5 — completata

Scope per ruolo e azienda su tutti gli otto router di dominio. Filtri ORM limitati alla sessione della singola richiesta, inclusi conteggi e risorse indirette; controllo dei riferimenti nei body e nei path. Dettagli esterni 404, creazioni/modifiche aziendali vietate 403. Corrette le API frontend workers. Test con due aziende e ADMIN/COMPANY_ADMIN A/B; copertura aggiuntiva formazione, DPI, scadenze, presenze e soft delete.

File: `backend/app/core/dependencies.py`, `backend/app/core/tenancy.py`, `backend/app/api/companies.py`, `backend/app/api/workers.py`, `backend/app/api/deadlines.py`, `backend/app/api/documents.py`, `backend/app/api/medical.py`, `backend/app/api/training.py`, `backend/app/api/dpi.py`, `backend/app/api/attendance.py`, `frontend/src/api.js`, `backend/tests/test_multitenancy.py`.

Correzioni della regola globale soft delete: `backend/alembic/versions/003_domain_soft_delete.py`, `backend/app/models/company.py`, `backend/app/models/deadline.py`, `backend/app/models/training.py`, `backend/app/services/company.py`, `backend/app/services/deadline.py`, `backend/app/services/training.py`, `backend/tests/test_deadlines.py`, `backend/tests/test_training.py`. I test esistenti ora richiedono la conservazione della riga con is_active=False e vietano db.delete; il mock della lista scadenze include il filtro dei record attivi. Motivo documentato nel commit 542ac54.

## P6 — completata

Audit append-only con sessione propria e scrittura che non interrompe le richieste. Metadati soltanto, nessun body o password. Middleware per letture personali/sanitarie, modifiche e autenticazione; utenti autorizzati identificati anche su login. Query e CSV streaming ADMIN con filtri; protezione da formule nei campi CSV controllabili dal client. Trigger di immutabilità e protezioni ORM.

File: `backend/app/models/audit_log.py`, `backend/app/models/__init__.py`, `backend/alembic/versions/002_audit_log.py`, `backend/app/services/audit.py`, `backend/app/core/audit_middleware.py`, `backend/app/api/audit.py`, `backend/app/main.py`, `backend/app/core/dependencies.py`, `backend/app/api/auth.py`, `backend/tests/test_audit.py`, `backend/tests/test_migrations.py`.

## Limiti e lavoro operativo restante

- Docker non disponibile nel sistema: nessuna esecuzione di docker compose up, immagini o deploy ZimaOS.
- Migrazioni eseguite su SQLite; SQL PostgreSQL generato e controllato, senza prova su PostgreSQL reale.
- Redis/MinIO provati con sostituti, senza integrazione con server reali. Verificare URL firmati dal browser e IP del proxy nel deploy.
- Nessun test end-to-end del frontend nel browser. Design visivo invariato.
- Su database creati in precedenza con create_all serve backup e riconciliazione prima del baseline Alembic. Non applicare automaticamente stamp a schemi non verificati.
- I vecchi file uploads locali non vengono importati in MinIO automaticamente.
- Degrado Redis intenzionale: senza Redis niente limite né garanzia di revoca. Audit best-effort: un errore di scrittura produce un log applicativo, non il blocco della richiesta.
- Restano 20 warning di deprecazione/ciclo FK nelle fixture. npm segnala 2 vulnerabilità (1 moderata, 1 alta); nessun aggiornamento forzato delle dipendenze.
- Compose ancora orientato allo sviluppo: segreti, TLS, CORS, firewall, alta disponibilità e backup immutabili richiedono configurazione e verifica operativa.
- Gestione organizzativa dei consensi, retention, diritti degli interessati e conformità normativa non sono certificati da questi test. Non esiste una UI dedicata per amministrare utenti/ruoli.

README aggiornato alle sole componenti presenti. Push e PR vengono effettuati dopo questo aggiornamento; l'esito e il link sono riportati nel riepilogo della sessione.
