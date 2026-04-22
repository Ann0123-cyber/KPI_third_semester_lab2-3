import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# In-memory SQLite — shared across connections via StaticPool
engine_test = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def registered_user(client):
    payload = {"email": "alice@example.com", "username": "alice", "password": "secret123"}
    client.post("/auth/register", json=payload)
    return payload


@pytest.fixture
def auth_headers(client, registered_user):
    resp = client.post("/auth/login", json={
        "email": registered_user["email"],
        "password": registered_user["password"],
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def project(client, auth_headers):
    resp = client.post("/projects/", json={"name": "Test Project"}, headers=auth_headers)
    return resp.json()
