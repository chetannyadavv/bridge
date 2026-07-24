from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine, SessionLocal
from app.routers.disputes import router as disputes_router
from app.routers.websocket import router as websocket_router
from app.seed import seed_if_empty

app = FastAPI(title="Bridge API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(disputes_router)
app.include_router(websocket_router)


@app.on_event("startup")
def on_startup() -> None:
    # Sprint 3: schema is created directly from the SQLAlchemy models.
    # The schema here is small and stable enough that Alembic migrations
    # aren't needed yet — add them when schema changes need to be applied
    # to an existing database without dropping data.
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}
