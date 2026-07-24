# Bridge

A shared negotiation workspace for card disputes — cardholder and
merchant see the same evidence board, timeline, and settlement
recommendation in real time.

```
bridge/
  bridge-frontend/   React + TypeScript + Vite
  bridge-backend/    FastAPI + SQLAlchemy + PostgreSQL
  docker-compose.yml # Postgres + backend
```

## Run everything

**1. Start Postgres + the backend:**

```bash
docker compose up --build
```

This starts Postgres on `localhost:5433` and the FastAPI backend on
`localhost:8001`, auto-creating the schema and seeding a demo dispute on
first boot. Confirm it's up: `curl http://localhost:8001/health`.

**2. Start the frontend** (separate terminal):

```bash
cd bridge-frontend
npm install
cp .env.example .env   # points at http://localhost:8000 by default
npm run dev
```

Open `http://localhost:5173`.

## Sprint history

- **Sprint 1** — frontend skeleton, routing, mock UI for all pages
- **Sprint 2** — frontend made functional with in-memory state (no backend)
- **Sprint 3** — real FastAPI + PostgreSQL backend; frontend now calls it
  via `bridge-frontend/src/services/`, same UI, same UX
- Not yet built: AI recommendations (currently mock logic in the
  backend), authentication, WebSockets/realtime sync

See `bridge-frontend/README.md` and `bridge-backend/README.md` for
details on each half.
