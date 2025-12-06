# tests/test_api.py
import os
import sys
import uuid
from pathlib import Path

# Añadimos el root al path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import mongomock
from application import app
from migrations._001_init_clinica import main as run_migration


# ------------------------------------------------------------------
# Setup the mocking service
# ------------------------------------------------------------------
@pytest.fixture(autouse=True)
def mock_mongo(monkeypatch):
    """Reemplaza pymongo.MongoClient por mongomock en toda la app"""
    mock_client = mongomock.MongoClient()

    # Monkey-patch global so 'from application import myclient' gets mocked.
    monkeypatch.setattr("application.myclient", mock_client)

    # Also patch pymongo.MongoClient to point to the mock client.
    monkeypatch.setattr("pymongo.MongoClient", lambda *args, **kwargs: mock_client)

    # Execute the migration script on the mocked client.
    #...This works with any other changes because of the previous patches
    os.environ["MONGODB_URI"] = "mongodb://localhost:27017/Clinica_test"
    os.environ["MONGODB_DB"] = "Clinica_test"
    run_migration()

    yield mock_client

    # The mock object stops existing once we are out of the tests, but we do this just in case.
    mock_client.drop_database("Clinica_test")

# ------------------------------------------------------------------
# Setup the client
# ------------------------------------------------------------------
@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test-secret-key-12345"
    with app.test_client() as c:
        yield c


@pytest.fixture
def auth_client(client):
    """Registra y loguea un usuario único por test"""
    username = f"user_{uuid.uuid4().hex[:8]}"

    # Registro
    resp = client.post("/register", json={
        "username": username,
        "password": "password123",
        "name": "Test", "lastname": "User",
        "email": f"{username}@test.com",
        "phone": "600000000",
        "date": "01/01/1990"
    })
    assert resp.status_code == 200

    # Login
    resp = client.post("/login", json={
        "username": username,
        "password": "password123"
    })
    assert resp.status_code == 200
    token = resp.get_json()["access_token"]

    # Añadimos header de autorización
    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    return client


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------
def test_root(client):
    assert client.get("/").status_code == 200

def test_register_and_login(client):
    username = f"ana_{uuid.uuid4().hex[:6]}"
    client.post("/register", json={
        "username": username, "password": "ana123",
        "name": "Ana", "lastname": "Pérez", "email": "ana@test.com",
        "phone": "600111222", "date": "15/05/1995"
    })
    resp = client.post("/login", json={"username": username, "password": "ana123"})
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()

def test_get_centers(auth_client):
    resp = auth_client.get("/centers")
    assert resp.status_code == 200
    centers = resp.get_json()
    assert len(centers) == 2
    assert "Centro de Salud Madrid Norte" in [c["name"] for c in centers]

def test_create_appointment(auth_client):
    resp = auth_client.post("/date/create", json={
        "center": "Centro de Salud Madrid Norte",
        "date": "31/12/2025 10:00:00"
    })
    assert resp.status_code == 200
    assert resp.get_json()["msg"] == "Date created successfully"

def test_duplicate_appointment_fails(auth_client):
    auth_client.post("/date/create", json={
        "center": "Centro Médico Madrid Sur",
        "date": "30/12/2025 14:00:00"
    })
    resp = auth_client.post("/date/create", json={
        "center": "Centro Médico Madrid Sur",
        "date": "30/12/2025 14:00:00"
    })
    assert resp.status_code == 400
    assert "already taken" in resp.get_json()["msg"]

def test_get_user_appointments(auth_client):
    auth_client.post("/date/create", json={
        "center": "Centro de Salud Madrid Norte",
        "date": "25/12/2025 12:00:00"
    })
    resp = auth_client.get("/date/getByUser")
    assert resp.status_code == 200
    assert any(a["date"] == "25/12/2025 12:00:00" for a in resp.get_json())

def test_cancel_appointment(auth_client):
    auth_client.post("/date/create", json={
        "center": "Centro Médico Madrid Sur",
        "date": "29/12/2025 18:00:00"
    })
    resp = auth_client.post("/date/delete", json={
        "date": "29/12/2025 18:00:00",
        "center": "Centro Médico Madrid Sur"
    })
    assert resp.status_code == 200
    resp = auth_client.get("/date/getByUser")
    assert "29/12/2025 18:00:00" not in [a["date"] for a in resp.get_json()]

def test_profile(auth_client):
    resp = auth_client.get("/profile")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "username" in data
    assert "email" in data
    assert "password" not in data