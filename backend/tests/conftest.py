"""
Test Configuration and Fixtures
Sets up mock MongoDB database and FastAPI TestClient with dependency overrides.
"""

import pytest
import mongomock
from fastapi.testclient import TestClient

from app.main import app
from app.api.deps import get_db
from app.db.init_db import init_db
from app.db.mongodb import db_manager


@pytest.fixture(autouse=True)
def mock_db_connection(monkeypatch):
    """Prevent network calls to MongoDB during testing."""
    monkeypatch.setattr(db_manager, "connect", lambda: True)
    monkeypatch.setattr(db_manager, "close", lambda: None)


@pytest.fixture
def mock_db():
    """
    Creates an isolated in-memory MongoDB database instance for each test.
    Initializes indexes on the mock database.
    """
    client = mongomock.MongoClient()
    db = client["test_edumanage"]
    init_db(db)
    return db


@pytest.fixture
def client(mock_db):
    """
    FastAPI TestClient with overridden get_db dependency pointing to mock_db.
    """
    app.dependency_overrides[get_db] = lambda: mock_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
