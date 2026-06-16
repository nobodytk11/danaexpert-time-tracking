"""Shared pytest fixtures.

Each test gets a fresh in-memory SQLite database and a TestClient whose `get_db`
dependency is overridden to use that database. Real HTTP-style calls, real SQL,
no mocks of our own code.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    """Register + log in a user and return ready-to-use auth headers."""
    client.post("/auth/register", json={"email": "a@b.com", "password": "pw12345"})
    resp = client.post(
        "/auth/login", json={"email": "a@b.com", "password": "pw12345"}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
