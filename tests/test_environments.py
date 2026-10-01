from app.models.environment import Environment
from fastapi import status



def aux_create_environment(
        api_client,
        client_id:int
        ) -> Environment:
    response = api_client.post(
        "/api/v1/environments",
        json={
            "type": "development",
            "project_id":client_id,
            "url": "http://test.test",
        }
    )
    return response.json()


def test_create_environment(
        api_client,
        created_project
):
    response = api_client.post(
        "/api/v1/environments",
        json={
            "type": "development",
            "project_id": created_project["id"],
            "url": "http://test.test",
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["id"] is not None
    assert body["type"] == "development"
    assert body["project_id"] == created_project["id"]
    assert body["url"] == "http://test.test"


def test_create_environment_fail_id_project(
        api_client,
        created_project
):
    false_project_id = 9999
    response = api_client.post(
        "/api/v1/environments",
        json={
            "type": "development",
            "project_id": 9999,
            "url": "http://test.test",
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_environment_fail_type(
        api_client,
        created_project
):
    false_project_id = 9999
    response = api_client.post(
        "/api/v1/environments",
        json={
            "type": "fail",
            "project_id": created_project["id"],
            "url": "http://test.test",
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_environment_archived_project(
        api_client,
        archived_project,
):
    response = api_client.post(
        "/api/v1/environments",
        json={
            "type": "development",
            "project_id": archived_project["id"],
            "url": "http://test.test",
        }
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_environment_fail_url(
        api_client,
        created_project
):
    false_project_id = 9999
    response = api_client.post(
        "/api/v1/environments",
        json={
            "type": "development",
            "project_id": 9999,
            "url": "test.test",
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_list_environments(api_client, created_project):
    environment = aux_create_environment(api_client,created_project["id"])

    response = api_client.get("/api/v1/environments")

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert len(body)==1
    assert body[0]["id"]==environment["id"]

def test_get_environment_by_id(api_client,created_project):
    environment = aux_create_environment(api_client, created_project["id"])
    response = api_client.get("/api/v1/environments")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body[0]["id"] == environment["id"]

def test_get_environments_by_projects(api_client,created_project):
    first_environment = aux_create_environment(api_client, created_project["id"])
    second_environment = aux_create_environment(api_client, created_project["id"])

    id_project:int = created_project["id"]

    response = api_client.get(f"/api/v1/environments/project/{id_project}")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body)==2
    assert body[0]["id"] == first_environment["id"]
    assert body[1]["id"] == second_environment["id"]

def test_update_environment(api_client,created_project):
    environment = aux_create_environment(api_client,created_project["id"])

    response = api_client.patch(
        f"/api/v1/environments/{environment["id"]}",
        json={
            "type":"staging",
            "url":"http://update",
            "id_project":created_project["id"]
        }
    )

    assert  response.status_code==status.HTTP_200_OK

    body = response.json()
    assert body["type"]=="staging"

def test_update_environment_to_archived_project(
        api_client,
        created_project,
        archived_project
):
    environment = aux_create_environment(api_client,created_project["id"])

    response = api_client.patch(
        f"/api/v1/environments/{environment["id"]}",
        json={
            "type": "staging",
            "url": "http://update",
            "project_id": archived_project["id"]
        }
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_delete_environment(
        api_client,
        created_project
):
    environment = aux_create_environment(api_client,created_project["id"])

    response = api_client.delete(
        f"/api/v1/environments/{environment["id"]}"
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_delete_project_with_environments(
        api_client,
        created_project
):
    environment = aux_create_environment(api_client,created_project["id"])

    response = api_client.delete(
        f"/api/v1/projects/{created_project["id"]}"
    )

    assert response.status_code == status.HTTP_409_CONFLICT






