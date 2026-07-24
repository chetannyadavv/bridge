# Bridge — Backend

FastAPI + SQLAlchemy + PostgreSQL backend for the Negotiation Table
product (Sprint 3). Replaces the frontend's Sprint 1/2 in-memory mock
data with a real, persisted API.

No AI, no auth, no background workers in this sprint.

## Quick start (Docker — recommended)

From the `bridge/` root (one level up from this folder):

```bash
docker compose up --build
```

This starts:
- **Postgres** on `localhost:5433` (db `bridge`, user/password `bridge`/`bridge`)
- **FastAPI** on `localhost:8001`, auto-creating the schema and seeding
  demo data on first boot

Check it's up: `curl http://localhost:8001/health` → `{"status": "ok"}`

Interactive API docs: `http://localhost:8001/docs`

## Quick start (local, without Docker)

Requires a running Postgres instance.

```bash
cd bridge-backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit BRIDGE_DATABASE_URL if needed
uvicorn app.main:app --reload
```

## Project structure

```
bridge-backend/
  app/
    main.py            # FastAPI app, CORS, startup (create_all + seed)
    config.py           # Settings (env-driven, BRIDGE_ prefix)
    database.py          # Engine, session factory, get_db dependency
    seed.py             # Seeds the Sprint 1/2 demo dispute (dsp_8841) + a few others
    models/              # SQLAlchemy models
    schemas/              # Pydantic request/response models
    services/             # Business logic (routes stay thin)
    routers/
      disputes.py         # All /disputes* routes
  Dockerfile
  requirements.txt
  .env.example
```

## Database schema

Five tables, minimal relationships, no over-engineering:

- **transactions** — the underlying charge
- **disputes** — the central entity
- **evidence** — evidence items per dispute
- **timeline_events** — chronological event log
- **recommendations** — settlement recommendation history

## API endpoints

| Method | Path | Notes |
|---|---|---|
| GET | `/disputes` | List all disputes, newest first |
| POST | `/disputes` | Create a dispute |
| GET | `/disputes/{id}` | Single dispute |
| GET | `/disputes/{id}/timeline` | Chronological timeline events |
| GET | `/disputes/{id}/evidence` | Evidence items, oldest first |
| POST | `/disputes/{id}/evidence` | Add evidence + recompute recommendation |
| GET | `/disputes/{id}/recommendation` | Full recommendation history |
| POST | `/disputes/{id}/recommendation/accept` | Accept a recommendation |

## WebSocket endpoint (Sprint 4)

`ws://localhost:8001/ws/disputes/{dispute_id}?role=cardholder|merchant|analyst`

One room per dispute id. No client -> server message protocol — this is
a push-only channel; anything a client sends is read and ignored.

On connect (and reconnect), the server immediately pushes a full state
snapshot as four messages:

```json
{"type": "dispute_updated", "payload": { ...DisputeOut }}
{"type": "evidence_updated", "payload": [ ...EvidenceOut[] ]}
{"type": "timeline_updated", "payload": [ ...TimelineEventOut[] ]}
{"type": "recommendation_updated", "payload": [ ...RecommendationOut[] ]}
```

Then, after any mutation (`POST /disputes/{id}/evidence`,
`POST /disputes/{id}/recommendation/accept`), the same four messages are
re-broadcast to everyone in that dispute's room. A `presence_updated`
message (`{"roles": [...]}`) is also broadcast whenever someone joins or
leaves.

**Design choice — full snapshots, not diffs:** every broadcast (and the
initial connect push) sends the dispute's *complete* current state, not
an incremental change. This sidesteps ordering/duplication bugs under
concurrent writes entirely — a client always replaces its local state
with what the server currently says is true — and it's what makes
reconnection trivial: there's no "catch-up" logic needed beyond
reconnecting and receiving the next snapshot.

**Concurrency:** a per-dispute `asyncio.Lock` (`ConnectionManager.lock_for`)
serializes the "read current DB state → broadcast" step in the REST
routes, so two near-simultaneous evidence submissions each get a clean,
uninterleaved turn to broadcast — no client ever sees a partial or
out-of-order snapshot.

**Unknown dispute ids:** the connection is rejected with close code
`4404` before `accept()`, rather than silently accepted and never
broadcast to.

**Single-instance limitation:** room state lives in an in-memory
`ConnectionManager` singleton. This is correct for the single backend
instance this sprint (and this architecture) runs — a horizontally
scaled deployment would need a shared broker (e.g. Redis pub/sub)
instead, which is out of scope here.

## The recommendation seam (for Sprint 5)

`app/services/recommendation_service.py::compute_recommendation()` is the
**only** place a recommendation is computed. Sprint 5 should replace
this function's body with a real call without changing its signature,
its callers, or any response shape.

## Not implemented (by design)

- AI / OpenAI API calls
- Authentication, login, JWT
- WebSocket rooms (implemented in Sprint 4)
- Background workers, Redis, Celery, caching
- Alembic migrations (schema created via `create_all`)

## CORS

Allows `http://localhost:5173` (Vite dev) and `http://localhost:4173`
(Vite preview) by default. Add more via `BRIDGE_CORS_ORIGINS`.
