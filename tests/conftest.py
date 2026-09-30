import os

os.environ["ENV_FILE"] = ".env.test"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database.dependency import get_db
from app.database.session import sessionLocal, engine
from fastapi import status
from main import app


@pytest.fixture(autouse=True)
def clean_clients_table():
    with engine.begin() as connection:
        connection.execute(text("DELETE FROM projects"))
        connection.execute(text("DELETE FROM clients"))

    yield

    with engine.begin() as connection:
        connection.execute(text("DELETE FROM projects"))
        connection.execute(text("DELETE FROM clients"))


@pytest.fixture
def api_client():
    def override_get_db():
        db = sessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

@pytest.fixture
def created_client(api_client):
    response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Cliente de prueba",
            "cif": "B12345678",
            "phone": "600123123",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest.fixture
def archived_client(api_client):
    create_response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Cliente archivado",
            "cif": "B87654321",
            "phone": "600987987",
        },
    )

    assert create_response.status_code == status.HTTP_201_CREATED
    client = create_response.json()

    archive_response = api_client.patch(
        f"/api/v1/clients/{client['id']}/archive"
    )

    assert archive_response.status_code == status.HTTP_200_OK
    return archive_response.json()

