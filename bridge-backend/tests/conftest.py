import os

# Must happen before any `app.*` import anywhere (including other test
# modules pytest collects) — app.database creates the SQLAlchemy engine
# at import time using this env var. Tests run against SQLite so they
# don't require a running Postgres instance; the app itself still
# defaults to Postgres in real deployment (see .env.example).
os.environ.setdefault("BRIDGE_DATABASE_URL", "sqlite:///./test_bridge.db")

import pytest  # noqa: E402


@pytest.fixture(scope="session")
def client():
    """A TestClient backed by a fresh SQLite file for the whole test
    session — used only by the integration regression tests. Pure unit
    tests (decision engine, evidence validator, etc.) don't need this at
    all, since they operate on plain in-memory objects with no DB."""
    db_path = "test_bridge.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client

    if os.path.exists(db_path):
        os.remove(db_path)
