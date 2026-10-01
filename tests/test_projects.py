from fastapi import status

from app.models.project import Project


def aux_create_project(
        api_client,
        client_id: int,
        name: str = "Proyecto auxiliar",
        description: str = "Descripción del  auxiliar",
)->Project:
    response = api_client.post(
        "/api/v1/projects",
        json={
            "name": name,
            "description": description,
            "client_id": client_id,
        },
    )
    return response.json()

def test_create_project(api_client, created_client):
    response = api_client.post(
        "/api/v1/projects",
        json={
            "name": "Proyecto test",
            "description": "Descripcion test",
            "client_id": created_client["id"],
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    body = response.json()
    assert body["id"] is not None
    assert body["name"] == "Proyecto test"
    assert body["description"] == "Descripcion test"
    assert body["client_id"] == created_client["id"]

def test_create_project_with_nonexistent_client(api_client):
    response = api_client.post(
        "/api/v1/projects",
        json={
            "name": "Proyecto test",
            "description": "test",
            "client_id": 999999,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_project_with_archived_client(api_client, archived_client):
    response = api_client.post(
        "/api/v1/projects",
        json={
            "name": "Proyecto test",
            "description": "test",
            "client_id": archived_client["id"],
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT

def test_list_projects(api_client, created_client):
    project = aux_create_project(api_client, created_client["id"])

    response = api_client.get("/api/v1/projects")

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == project["id"]

def test_get_project_by_id(api_client, created_client):
    project = aux_create_project(api_client, created_client["id"])

    response = api_client.get(f"/api/v1/projects/{project['id']}")

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body["id"] == project["id"]
    assert body["name"] == project["name"]
    assert body["client_id"] == created_client["id"]

def test_get_non_exist_project(api_client):
    non_exist_project:int=9999
    response = api_client.get(f"/api/v1/projects/{non_exist_project}")

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_list_projects_by_client(api_client, created_client):
    first_project = aux_create_project(
        api_client,
        created_client["id"],
        name="test1",
    )

    second_project = aux_create_project(
        api_client,
        created_client["id"],
        name="test2",
    )

    response = api_client.get(
        f"/api/v1/projects/client/{created_client['id']}"
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert len(body) == 2
    assert body[0]["id"] == first_project["id"]
    assert body[1]["id"]== second_project["id"]

def test_update_project_name_and_description(api_client, created_client):
    project = aux_create_project(api_client, created_client["id"])

    response = api_client.patch(
        f"/api/v1/projects/{project['id']}",
        json={
            "name": "test update",
            "description": "test update",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body["name"] == "test update"
    assert body["description"] == "test update"
    assert body["client_id"] == created_client["id"]

def test_update_project_client_id(api_client, created_client):
    project = aux_create_project(api_client, created_client["id"])

    second_client_json = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Segundo cliente",
            "cif": "B87654321",
            "phone": "600987987",
        },
    )

    assert second_client_json.status_code == status.HTTP_201_CREATED
    second_client = second_client_json.json()

    response = api_client.patch(
        f"/api/v1/projects/{project['id']}",
        json={
            "client_id": second_client["id"],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["client_id"] == second_client["id"]

def test_update_project_to_archived_client(
        api_client,
        created_client,
        archived_client,
):
    project = aux_create_project(api_client, created_client["id"])

    response = api_client.patch(
        f"/api/v1/projects/{project['id']}",
        json={
            "client_id": archived_client["id"],
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT

def test_update_project_to_nonexistent_client(api_client, created_client):
    project = aux_create_project(api_client, created_client["id"])

    response = api_client.patch(
        f"/api/v1/projects/{project['id']}",
        json={
            "client_id": 999999,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_project(api_client, created_client):
    project = aux_create_project(api_client, created_client["id"])

    response = api_client.delete(
        f"/api/v1/projects/{project['id']}"
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_project_is_not_found_after_deletion(api_client, created_client):
    project = aux_create_project(api_client, created_client["id"])

    delete_response = api_client.delete(
        f"/api/v1/projects/{project['id']}"
    )

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    response = api_client.get(f"/api/v1/projects/{project['id']}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Proyecto no encontrado"

