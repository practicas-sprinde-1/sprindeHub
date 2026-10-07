import os
os.environ["ENV_FILE"] = ".env.test"

from app.security.models.user_model import User, RoleType
from app.security.schemas.user_token_schemas import AccessToken, Token
from app.security.utils import hash_password



from app.models.client import Client
from app.models.project import Project

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database.dependency import get_db
from app.database.session import sessionLocal, engine
from fastapi import status
from main import app


@pytest.fixture(autouse=True)
def clean_tables():
    with engine.begin() as connection:
        connection.execute(text("DELETE FROM logs"))
        connection.execute(text("DELETE FROM user_clients"))
        connection.execute(text("DELETE FROM notes"))
        connection.execute(text("DELETE FROM commands"))
        connection.execute(text("DELETE FROM services"))
        connection.execute(text("DELETE FROM links"))
        connection.execute(text("DELETE FROM domains"))
        connection.execute(text("DELETE FROM repositories"))
        connection.execute(text("DELETE FROM environments"))
        connection.execute(text("DELETE FROM projects"))
        connection.execute(text("DELETE FROM clients"))
        connection.execute(text("DELETE FROM users"))

    yield

    with engine.begin() as connection:
        connection.execute(text("DELETE FROM logs"))
        connection.execute(text("DELETE FROM user_clients"))
        connection.execute(text("DELETE FROM notes"))
        connection.execute(text("DELETE FROM commands"))
        connection.execute(text("DELETE FROM services"))
        connection.execute(text("DELETE FROM links"))
        connection.execute(text("DELETE FROM domains"))
        connection.execute(text("DELETE FROM repositories"))
        connection.execute(text("DELETE FROM environments"))
        connection.execute(text("DELETE FROM projects"))
        connection.execute(text("DELETE FROM clients"))
        connection.execute(text("DELETE FROM users"))


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
def created_client(api_client, admin_headers) -> Client:
    response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Cliente de prueba",
            "cif": "B12345678",
            "phone": "600123123",
        },
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest.fixture
def archived_client(api_client, admin_headers) -> Client:
    create_response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Cliente archivado",
            "cif": "B87654321",
            "phone": "600987987",
        },
        headers=admin_headers,
    )

    assert create_response.status_code == status.HTTP_201_CREATED
    client = create_response.json()

    archive_response = api_client.patch(
        f"/api/v1/clients/{client['id']}/archive",
        headers=admin_headers
    )

    assert archive_response.status_code == status.HTTP_200_OK
    return archive_response.json()


@pytest.fixture
def created_project(
        api_client,
        created_client
, admin_headers) -> Project:
    response = api_client.post(
        "/api/v1/projects",
        json={
            "name": "Proyecto conftest",
            "description": "Descripción proyecto conftest",
            "client_id": created_client["id"],
        },
        headers=admin_headers,
    )
    return response.json()


@pytest.fixture
def archived_project(
        api_client,
        created_client
, admin_headers) -> Project:
    response = api_client.post(
        "/api/v1/projects",
        json={
            "name": "Proyecto archivado",
            "description": "Descripción proyecto archivado",
            "client_id": created_client["id"],
        },
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_201_CREATED
    project = response.json()

    archive_response = api_client.patch(
        f"/api/v1/projects/{project['id']}/archive",
        headers=admin_headers
    )

    assert archive_response.status_code == status.HTTP_200_OK
    return archive_response.json()


@pytest.fixture
def restored_project(
        api_client,
        created_client
, admin_headers,archived_project) -> Project:

    project = archived_project

    restored_response = api_client.patch(
        f"/api/v1/projects/{project['id']}/restore",
        headers=admin_headers
    )

    assert restored_response.status_code == status.HTTP_200_OK
    assert restored_response["is_active"] is True
    return restored_response.json()

@pytest.fixture
def admin_user():
    db = sessionLocal()

    admin = User(
        email="admin@test.com",
        username="admin",
        password_hash=hash_password("passwordde+10"),
        role=RoleType.ADMIN,
        is_active=True,
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    try:
        yield admin
    finally:
        db.close()

@pytest.fixture
def created_guest(api_client) -> User:
    response = api_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@test.com",
            "username": "test",
            "password": "1234567890",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest.fixture
def login_admin_token(api_client,admin_user) -> Token:
    response = api_client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user.email,
            "password": "passwordde+10"
        }
    )

    assert response.status_code == status.HTTP_200_OK
    return response.json()

@pytest.fixture
def admin_headers(login_admin_token) -> dict:
    return {
        "Authorization": (
            f"Bearer {login_admin_token['access_token']}"
        )
    }

@pytest.fixture
def user_type_user() :
    db = sessionLocal()

    user = User(
        email="user@test.com",
        username="user",
        password_hash=hash_password("passwordde+10"),
        role=RoleType.USER,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    try:
        yield user
    finally:
        db.close()



@pytest.fixture
def login_user_token(api_client, user_type_user) -> Token:
    response = api_client.post(
        "/api/v1/auth/login",
        json={
            "email": user_type_user.email,
            "password": "passwordde+10"
        }
    )

    assert response.status_code == status.HTTP_200_OK
    return response.json()

@pytest.fixture
def user_headers(login_user_token) -> dict:
    return {
        "Authorization": (
            f"Bearer {login_user_token['access_token']}"
        )
    }


@pytest.fixture
def user_with_client(api_client, created_client, admin_headers, user_type_user):
    response = api_client.post(
        f"/api/v1/admin/user-clients/users/{user_type_user.id}/clients",
        json={
        "client_id": created_client["id"]
        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()

