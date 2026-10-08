from app.models.command import Command
from fastapi import status


def aux_create_command(
        admin_headers,
        api_client,
        client_id: int,
) -> Command:
    response = api_client.post(
        "/api/v1/commands",
        json={
            "project_id": client_id,
            "name": "name test",
            "instruction": "command auxiliar"
        },
        headers=admin_headers
    )
    return response.json()


def test_create_command(
        api_client,
        created_project
        , admin_headers):
    response = api_client.post(
        "/api/v1/commands",
        json={
            "instruction": "instruction test ",
            "project_id": created_project["id"],
            "name": "name test"
        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["id"] is not None
    assert body["project_id"] == created_project["id"]
    assert body["name"] == "name test"
    assert body["instruction"] == "instruction test "


def test_create_command_fail_id_project(
        api_client,
        created_project
        , admin_headers):
    false_project_id = 9999
    response = api_client.post(
        "/api/v1/commands",
        json={
            "project_id": 9999,
            "name": "name test",
            "instruction": "instruction test "
        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_command_archived_project(
        api_client,
        archived_project,
        admin_headers):
    response = api_client.post(
        "/api/v1/commands",
        json={
            "project_id": archived_project["id"],
            "name": "name test",
            "instruction": "instruction test "
        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_command_fail_name(
        api_client,
        created_project
        , admin_headers):
    false_project_id = 9999
    response = api_client.post(
        "/api/v1/commands",
        json={
            "project_id": 9999,
            "name": "",
            "instruction": "instruction test "
        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_list_commands(api_client, created_project, admin_headers):
    command = aux_create_command(admin_headers, api_client, created_project["id"])

    response = api_client.get("/api/v1/commands", headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == command["id"]


def test_get_command_by_id(api_client, created_project, admin_headers):
    command = aux_create_command(admin_headers, api_client, created_project["id"], )
    response = api_client.get("/api/v1/commands", headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body[0]["id"] == command["id"]


def test_get_commands_by_projects(api_client, created_project, admin_headers):
    first_command = aux_create_command(admin_headers, api_client, created_project["id"])
    second_command = aux_create_command(admin_headers, api_client, created_project["id"])

    id_project: int = created_project["id"]

    response = api_client.get(f"/api/v1/commands/project/{id_project}", headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body) == 2
    assert body[0]["id"] == first_command["id"]
    assert body[1]["id"] == second_command["id"]


def test_update_command(api_client, created_project, admin_headers):
    command = aux_create_command(admin_headers, api_client, created_project["id"])

    response = api_client.patch(
        f"/api/v1/commands/{command["id"]}",
        json={
            "name": "name update",
            "id_project": created_project["id"],
            "instruction": "instruction test "
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()


def test_update_command_to_archived_project(
        api_client,
        created_project,
        archived_project
        , admin_headers):
    command = aux_create_command(admin_headers, api_client, created_project["id"])

    response = api_client.patch(
        f"/api/v1/commands/{command["id"]}",
        json={
            "name": "name update",
            "project_id": archived_project["id"],
            "instruction": "instruction test "
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_delete_command(
        api_client,
        created_project
        , admin_headers):
    command = aux_create_command(admin_headers, api_client, created_project["id"])

    response = api_client.delete(
        f"/api/v1/commands/{command["id"]}",
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_project_with_commands(
        api_client,
        created_project
        , admin_headers):
    command = aux_create_command(admin_headers, api_client, created_project["id"])

    response = api_client.delete(
        f"/api/v1/projects/{created_project["id"]}",
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_409_CONFLICT
