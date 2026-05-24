# EngiPro — Status & Development Context
_Ultimo aggiornamento: 2026-03-29_

## Dove siamo
- Progetto full-stack presente in `/DATA/engipro`
- Stack reale confermato: FastAPI + SQLAlchemy + PostgreSQL + Redis + MinIO + React/Vite + Nginx + Docker Compose
- Repository git inizializzata, ma `STATUS.md` era ancora un placeholder
- Frontend e backend esistono entrambi, ma il livello di maturita' non e' uniforme

## Architettura reale rilevata
- Root: `backend/`, `frontend/`, `nginx/`, `docker-compose.yml`, `README.md`, `DEVELOPMENT.md`
- Servizi Docker previsti: `postgres`, `redis`, `minio`, `backend`, `frontend`, `nginx`
- Porte esposte:
  - PostgreSQL `5433`
  - Redis `6380`
  - MinIO API `9002`
  - MinIO console `9003`
  - Backend FastAPI `8002`
  - Nginx reverse proxy `81`

## Backend: stato reale
- Struttura applicativa completa con cartelle `api`, `models`, `schemas`, `services`, `core`
- Router presenti e cablati in `app/main.py`:
  - `auth`
  - `companies`
  - `workers`
  - `deadlines`
  - `documents`
  - `training`
  - `medical`
  - `dpi`
  - `attendance`
- Test presenti in `backend/tests/` per:
  - auth
  - workers
  - deadlines
  - documents
  - training
  - medical
  - dpi
  - attendance
- Migrazioni alembic quasi assenti: trovata solo `001_add_deadlines_table.py`

## Frontend: stato reale
- Frontend presente con Vite + React
- Codice concentrato soprattutto in `frontend/src/App.jsx` e `frontend/src/api.js`
- UI ampia e dimostrativa, con dashboard e viste per piu' moduli
- Nessuna struttura modulare frontend rilevata: niente cartelle dedicate per pagine, componenti, stato globale o routing
- `package.json` include solo dipendenze base React/Vite; il frontend sembra una single-page app monolitica

## Documentazione vs codice
- `README.md` sottostima e insieme sovrastima il progetto:
  - sottostima: dichiara "API Core in progress", ma nel codice sono gia' presenti molti endpoint CRUD e moduli operativi
  - sovrastima: cita `mobile/`, `n8n-workflows/` e app mobile React Native, ma queste directory non sono presenti nella repo
- Lo stato reale va quindi considerato: backend piu' avanzato della documentazione, roadmap prodotto piu' avanzata del codice reale lato mobile/automation

## Problemi tecnici gia' emersi
- `backend/app/main.py` esegue `Base.metadata.create_all(bind=engine)` all'avvio:
  - pratica fragile in presenza di Alembic
  - al momento importa esplicitamente solo alcuni modelli; `User`, `Company` e `Worker` non sono importati in `main.py`
  - rischio concreto: bootstrap schema incompleto se quei modelli non vengono caricati altrove prima di `create_all`
- `backend/app/api/workers.py` ha una firma incoerente in `search_workers`:
  - `company_id` e' definito come `Path(...)`, ma non esiste nel path
  - dovrebbe essere `Query(...)`
- `frontend/src/api.js` non e' allineato al backend:
  - usa `GET /workers/company/{cid}` che non esiste nel router backend
  - usa `PUT /workers/{id}/status/{s}` ma il backend espone `POST /workers/{worker_id}/status/{new_status}`
- CORS default in `backend/app/core/config.py` punta a `localhost:3000` e `3001`, mentre il frontend qui gira via Vite/Nginx su porte diverse; serve riallineamento ambienti
- Test non verificati localmente in questa sessione:
  - tentativo di esecuzione fallito per assenza di `pytest` nell'ambiente corrente
- In root sono presenti file/artefatti anomali da capire o pulire:
  - `=`
  - `[backend`
  - `[backend]`
  - `-d`
  - `-H`
  - `CACHED`
  - `exporting`
  - `naming`
  - `transferring`
  - `writing`

## Valutazione sintetica
- Backend: base solida, copertura funzionale ampia, ma con segnali di incoerenza tra bootstrap DB, migrazioni e contratti API
- Frontend: buona demo funzionale/visuale, ma architettura ancora acerba e con mismatch rispetto agli endpoint reali
- DevOps locale: compose gia' predisposto e leggibile, sufficiente per ambiente sviluppo
- Progetto non ancora in stato "production-ready"

## Decisioni/assunzioni prese in questa sessione
- Ho usato `STATUS.md` esistente come punto di partenza, ma era solo un placeholder e non conteneva stato operativo reale
- Non ho esplorato la repo "da zero": ho ricostruito lo stato leggendo i file chiave gia' presenti
- Considero questo aggiornamento come baseline iniziale affidabile per le prossime sessioni

## Ultimo lavoro fatto
- Letto `STATUS.md` iniziale e verificato che fosse solo un placeholder
- Letta la struttura reale del progetto e i file chiave di backend, frontend, compose e nginx
- Mappati i router FastAPI realmente presenti e confrontati con README e frontend
- Individuati i primi mismatch tecnici concreti:
  - firma errata di `search_workers`
  - endpoint frontend `workers` non allineati al backend
  - uso fragile di `create_all` insieme ad Alembic
- Tentata esecuzione test backend, non completata per assenza di `pytest` nell'ambiente corrente
- Riscritto `STATUS.md` come baseline operativa reale per le prossime sessioni

## Pendente / Prossimi passi consigliati
- [ ] Correggere i mismatch API frontend/backend, iniziando dal modulo workers
- [ ] Sistemare `search_workers` in backend (`company_id` da `Path` a `Query`)
- [ ] Decidere la strategia schema DB: solo Alembic oppure `create_all`; evitare doppio binario
- [ ] Verificare che tutti i modelli vengano importati prima della creazione tabelle, oppure rimuovere del tutto `create_all` dall'avvio app
- [ ] Eseguire i test in ambiente con dipendenze installate e registrare i risultati reali
- [ ] Aggiornare `README.md` per riflettere il codice reale ed eliminare roadmap/componenti non presenti
- [ ] Ripulire o classificare gli artefatti anomali nella root del progetto
- [ ] Modularizzare il frontend (`components`, `views`, `hooks`, `services`) per ridurre il monolite in `App.jsx`
- [ ] Verificare la presenza/assenza di autenticazione effettiva e flussi login reali nel frontend contro gli endpoint backend

## Focus consigliato prossima sessione
- Prima priorita': riallineamento contratti API tra frontend e backend
- Seconda priorita': strategia database/migrazioni e bootstrap schema
- Terza priorita': esecuzione test reale e pulizia della documentazione
