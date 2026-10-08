from fastapi import status

from tests.conftest import created_client

API_PREFIX = "api/v1/admin/"


def test_create_client(
        api_client,
        admin_headers,
):
    response = api_client.post(
        f"{API_PREFIX}users",
        json={
            "email": "user@example.com",
            "username": "string",
            "password": "stringstri",
            "role": "GUEST",
            "is_active": True
        },
        headers=admin_headers

    )

    assert response.status_code == status.HTTP_201_CREATED

    assert response.json()["email"] == "user@example.com"


def test_fail_create_client_by_user(
        api_client,
        user_headers,
):
    response = api_client.post(
        f"{API_PREFIX}users",
        json={
            "email": "user@example.com",
            "username": "string",
            "password": "stringstri",
            "role": "GUEST",
            "is_active": True
        },
        headers=user_headers

    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_client_access_by_user(
        api_client,
        user_with_client,
        user_headers
):
    response = api_client.get(
        "api/v1/clients",
        headers=user_headers
    )

    assert response.status_code == status.HTTP_200_OK


def test_client_id_access_by_user(
        api_client,
        user_with_client,
        user_headers
        , created_client):
    response = api_client.get(
        f"api/v1/clients/{created_client["id"]}",
        headers=user_headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert created_client["id"] == user_with_client["client_id"]


def test_client_fail_access_by_user(
        api_client,
        user_with_client,
        user_headers
):
    response = api_client.get(
        "api/v1/clients",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_client_fail_modify_by_user(
        api_client,
        user_headers
        , created_client):
    response = api_client.patch(
        f"api/v1/clients/{created_client["id"]}",
        json={
            "name": "string",
            "cif": "string",
            "phone": "string"
        },
        headers=user_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_modify_client_by_user(
        api_client,
        user_headers,
        user_with_client,
        created_client):
    response = api_client.patch(
        f"api/v1/clients/{created_client["id"]}",
        json={
            "name": "string",
            "cif": "string",
            "phone": "string"
        },
        headers=user_headers
    )

    assert response.status_code == status.HTTP_200_OK


def test_modify_project_by_user(
        api_client,
        user_headers,
        user_with_client,
        created_project,
        created_client):
    response = api_client.get(
        f"api/v1/projects/client/{created_client["id"]}",
        headers=user_headers
    )

    assert response.status_code == status.HTTP_200_OK

    project_id = response.json()[0]["id"]

    update_response = api_client.patch(
        f"api/v1/projects/{project_id}",
        json={
            "name": "string",
            "description": "string",
        },
        headers=user_headers
    )

    assert update_response.status_code == status.HTTP_200_OK


def test_modify_project_resource_by_user(
        api_client,
        user_headers,
        user_with_client,
        created_project,
        created_client):
    post_response = api_client.post(
        f"api/v1/repositories",
        json={
            "type": "backend",
            "url": "http://",
            "project_id": created_project["id"]
        },
        headers=user_headers
    )

    assert post_response.status_code == status.HTTP_201_CREATED


def test_client_access_by_unauthorized_logged_user(
        api_client,
        user_headers,
        admin_headers,
):
    client_response = api_client.post(
        "api/v1/clients",
        json={
            "name": "string",
            "cif": "string",
            "phone": "string"
        },
        headers=admin_headers
    )
    assert client_response.status_code == status.HTTP_201_CREATED

    client_id = client_response.json()["id"]
    response = api_client.get(
        f"api/v1/clients/{client_id}",
        headers=user_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_project_access_by_unauthorized_logged_user(
        api_client,
        user_headers,
        admin_headers,
        created_client
):
    project_response = api_client.post(
        f"api/v1/projects",
        json={
            "name": "string",
            "description": "string",
            "client_id": created_client["id"]
        },
        headers=admin_headers
    )

    assert project_response.status_code == status.HTTP_201_CREATED

    project_id = project_response.json()["id"]

    response = api_client.get(
        f"api/v1/projects/{project_id}",
        headers=user_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_guest_read_clients_and_projects(
        api_client,
        guest_headers,
        guest_with_client,
        created_client,
        created_project,
):
    clients_response = api_client.get(
        "/api/v1/clients",
        headers=guest_headers,
    )

    assert clients_response.status_code == status.HTTP_200_OK
    assert clients_response.json()[0]["id"] == created_client["id"]

    client_response = api_client.get(
        f"/api/v1/clients/{created_client['id']}",
        headers=guest_headers,
    )

    assert client_response.status_code == status.HTTP_200_OK
    assert client_response.json()["id"] == created_client["id"]

    projects_response = api_client.get(
        f"/api/v1/projects/client/{created_client['id']}",
        headers=guest_headers,
    )

    assert projects_response.status_code == status.HTTP_200_OK
    assert projects_response.json()[0]["id"] == created_project["id"]


def test_guest_unauthorized_writer_on_assigned_client(
        api_client,
        guest_headers,
        guest_with_client,
        created_client,
):
    create_response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Cliente",
            "cif": "A123456789",
            "phone": "123456789",
        },
        headers=guest_headers,
    )

    assert create_response.status_code == status.HTTP_403_FORBIDDEN

    update_response = api_client.patch(
        f"/api/v1/clients/{created_client['id']}",
        json={
            "name": "test",
        },
        headers=guest_headers,
    )

    assert update_response.status_code == status.HTTP_403_FORBIDDEN

    archive_response = api_client.patch(
        f"/api/v1/clients/{created_client['id']}/archive",
        headers=guest_headers,
    )

    assert archive_response.status_code == status.HTTP_403_FORBIDDEN

    delete_response = api_client.delete(
        f"/api/v1/clients/{created_client['id']}",
        headers=guest_headers,
    )

    assert delete_response.status_code == status.HTTP_403_FORBIDDEN


def test_guest_cannot_read_unassigned_client(
        api_client,
        admin_headers,
        guest_headers,
        guest_with_client,
):
    other_client_response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Cliente no autorizado",
            "cif": "A123456789",
            "phone": "123456789",
        },
        headers=admin_headers,
    )

    assert other_client_response.status_code == status.HTTP_201_CREATED

    other_client = other_client_response.json()

    response = api_client.get(
        f"/api/v1/clients/{other_client['id']}",
        headers=guest_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_project_with_assigned_client(
        api_client,
        user_with_client,
        user_headers,
        created_client
):
    response = api_client.post(
        "/api/v1/projects",
        json={
            "name": "string",
            "description": "string",
            "client_id": created_client["id"]
        },
        headers=user_headers
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_update_unauthorized_client(
        api_client,
        user_headers,
        created_client
):
    response = api_client.patch(
        f"/api/v1/clients/{created_client["id"]}",
        json={
            "name": "string",
            "cif": "string",
            "phone": "string"
        },
        headers=user_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_unauthorized_project(
        api_client,
        user_headers,
        created_client,
        created_project
):
    response = api_client.patch(
        f"/api/v1/projects/{created_project["id"]}",
        json={
            "name": "string",
            "description": "string",
            "client_id": 1
        },
    headers = user_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

