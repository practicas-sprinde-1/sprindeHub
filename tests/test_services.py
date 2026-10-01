from app.models.service import Service
from fastapi import status

def aux_create_service(
        api_client,
        client_id:int
        ) -> Service:
    response = api_client.post(
        "/api/v1/services",
        json={
            "project_id":client_id,
            "name": "name test",
        }
    )
    return response.json()


def test_create_service(
        api_client,
        created_project
):
    response = api_client.post(
        "/api/v1/services",
        json={
            "project_id": created_project["id"],
            "name": "name test",
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["id"] is not None
    assert body["project_id"] == created_project["id"]
    assert body["name"] == "name test"


def test_create_service_fail_id_project(
        api_client,
        created_project
):
    false_project_id = 9999
    response = api_client.post(
        "/api/v1/services",
        json={
            "project_id": 9999,
            "name": "name test",
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND



def test_create_service_archived_project(
        api_client,
        archived_project,
):
    response = api_client.post(
        "/api/v1/services",
        json={
            "project_id": archived_project["id"],
            "name": "name test",
        }
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_service_fail_name(
        api_client,
        created_project
):
    false_project_id = 9999
    response = api_client.post(
        "/api/v1/services",
        json={
            "project_id": 9999,
            "name": "",
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_list_services(api_client, created_project):
    service = aux_create_service(api_client,created_project["id"])

    response = api_client.get("/api/v1/services")

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert len(body)==1
    assert body[0]["id"]==service["id"]

def test_get_service_by_id(api_client,created_project):
    service = aux_create_service(api_client, created_project["id"])
    response = api_client.get("/api/v1/services")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body[0]["id"] == service["id"]

def test_get_services_by_projects(api_client,created_project):
    first_service = aux_create_service(api_client, created_project["id"])
    second_service = aux_create_service(api_client, created_project["id"])

    id_project:int = created_project["id"]

    response = api_client.get(f"/api/v1/services/project/{id_project}")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body)==2
    assert body[0]["id"] == first_service["id"]
    assert body[1]["id"] == second_service["id"]

def test_update_service(api_client,created_project):
    service = aux_create_service(api_client,created_project["id"])

    response = api_client.patch(
        f"/api/v1/services/{service["id"]}",
        json={
            "name":"name update",
            "id_project":created_project["id"]
        }
    )

    assert  response.status_code==status.HTTP_200_OK

    body = response.json()

def test_update_service_to_archived_project(
        api_client,
        created_project,
        archived_project
):
    service = aux_create_service(api_client,created_project["id"])

    response = api_client.patch(
        f"/api/v1/services/{service["id"]}",
        json={
            "name": "name update",
            "project_id": archived_project["id"]
        }
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_delete_service(
        api_client,
        created_project
):
    service = aux_create_service(api_client,created_project["id"])

    response = api_client.delete(
        f"/api/v1/services/{service["id"]}"
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_delete_project_with_services(
        api_client,
        created_project
):
    service = aux_create_service(api_client,created_project["id"])

    response = api_client.delete(
        f"/api/v1/projects/{created_project["id"]}"
    )

    assert response.status_code == status.HTTP_409_CONFLICT






