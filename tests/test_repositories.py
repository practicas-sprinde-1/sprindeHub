from app.models.repository import Repository
from fastapi import status


def aux_create_repository(
        admin_headers,
        api_client,
        client_id: int
) -> Repository:
    response = api_client.post(
        "/api/v1/repositories",
        json={
            "type": "backend",
            "project_id": client_id,
            "url": "http://test.test",
        },
        headers=admin_headers
    )
    return response.json()


def test_create_repository(
        api_client,
        created_project
        , admin_headers):
    response = api_client.post(
        "/api/v1/repositories",
        json={
            "type": "backend",
            "project_id": created_project["id"],
            "url": "http://test.test",
        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["id"] is not None
    assert body["type"] == "backend"
    assert body["project_id"] == created_project["id"]
    assert body["url"] == "http://test.test"


def test_create_repository_fail_id_project(
        api_client,
        created_project
        , admin_headers):
    false_project_id = 9999
    response = api_client.post(
        "/api/v1/repositories",
        json={
            "type": "backend",
            "project_id": 9999,
            "url": "http://test.test",
        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_repository_fail_type(
        api_client,
        created_project
        , admin_headers):
    false_project_id = 9999
    response = api_client.post(
        "/api/v1/repositories",
        json={
            "type": "fail",
            "project_id": created_project["id"],
            "url": "http://test.test",
        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_repository_archived_project(
        api_client,
        archived_project,
        admin_headers):
    response = api_client.post(
        "/api/v1/repositories",
        json={
            "type": "backend",
            "project_id": archived_project["id"],
            "url": "http://test.test",
        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_repository_fail_url(
        api_client,
        created_project
        , admin_headers):
    false_project_id = 9999
    response = api_client.post(
        "/api/v1/repositories",
        json={
            "type": "backend",
            "project_id": 9999,
            "url": "test.test",
        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_list_repositories(api_client, created_project, admin_headers):
    repository = aux_create_repository(admin_headers, api_client, created_project["id"])

    response = api_client.get("/api/v1/repositories", headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == repository["id"]


def test_get_repository_by_id(api_client, created_project, admin_headers):
    repository = aux_create_repository(admin_headers, api_client, created_project["id"])
    response = api_client.get("/api/v1/repositories", headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body[0]["id"] == repository["id"]


def test_get_repositories_by_projects(api_client, created_project, admin_headers):
    first_repository = aux_create_repository(admin_headers, api_client, created_project["id"])
    second_repository = aux_create_repository(admin_headers, api_client, created_project["id"])

    id_project: int = created_project["id"]

    response = api_client.get(f"/api/v1/repositories/project/{id_project}", headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body) == 2
    assert body[0]["id"] == first_repository["id"]
    assert body[1]["id"] == second_repository["id"]


def test_update_repository(api_client, created_project, admin_headers):
    repository = aux_create_repository(admin_headers, api_client, created_project["id"])

    response = api_client.patch(
        f"/api/v1/repositories/{repository["id"]}",
        json={
            "type": "frontend",
            "url": "http://update",
            "id_project": created_project["id"]
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body["type"] == "frontend"


def test_update_repository_to_archived_project(
        api_client,
        created_project,
        archived_project
        , admin_headers):
    repository = aux_create_repository(admin_headers, api_client, created_project["id"])

    response = api_client.patch(
        f"/api/v1/repositories/{repository["id"]}",
        json={
            "type": "frontend",
            "url": "http://update",
            "project_id": archived_project["id"]
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_delete_repository(
        api_client,
        created_project
        , admin_headers):
    repository = aux_create_repository(admin_headers, api_client, created_project["id"])

    response = api_client.delete(
        f"/api/v1/repositories/{repository["id"]}",
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_project_with_repositories(
        api_client,
        created_project
        , admin_headers):
    repository = aux_create_repository(admin_headers, api_client, created_project["id"])

    response = api_client.delete(
        f"/api/v1/projects/{created_project["id"]}",
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_409_CONFLICT
