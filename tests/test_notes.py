from app.models.note import Note
from fastapi import status


def aux_create_note(
        admin_headers,
        api_client,
        client_id: int
) -> Note:
    response = api_client.post(
        "/api/v1/notes",
        json={
            "project_id": client_id,
            "description": "description test",
            "content": "note auxiliar"
        },
        headers=admin_headers
    )
    return response.json()


def test_create_note(
        api_client,
        created_project
        , admin_headers):
    response = api_client.post(
        "/api/v1/notes",
        json={
            "content": "content test ",
            "project_id": created_project["id"],
            "description": "description test",

        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["id"] is not None
    assert body["project_id"] == created_project["id"]
    assert body["description"] == "description test"
    assert body["content"] == "content test "


def test_create_note_fail_id_project(
        api_client,
        created_project
        , admin_headers):
    false_project_id = 9999
    response = api_client.post(
        "/api/v1/notes",
        json={
            "project_id": 9999,
            "description": "description test",
            "content": "content test "
        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_note_archived_project(
        api_client,
        archived_project,
        admin_headers):
    response = api_client.post(
        "/api/v1/notes",
        json={
            "project_id": archived_project["id"],
            "description": "description test",
            "content": "content test "
        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_note_fail_description(
        api_client,
        created_project
        , admin_headers):
    false_project_id = 9999
    response = api_client.post(
        "/api/v1/notes",
        json={
            "project_id": 9999,
            "description": "",
            "content": "content test "
        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_list_notes(api_client, created_project, admin_headers):
    note = aux_create_note(admin_headers, api_client, created_project["id"])

    response = api_client.get("/api/v1/notes", headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == note["id"]


def test_get_note_by_id(api_client, created_project, admin_headers):
    note = aux_create_note(admin_headers, api_client, created_project["id"])
    response = api_client.get("/api/v1/notes", headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body[0]["id"] == note["id"]


def test_get_notes_by_projects(api_client, created_project, admin_headers):
    first_note = aux_create_note(admin_headers, api_client, created_project["id"])
    second_note = aux_create_note(admin_headers, api_client, created_project["id"])

    id_project: int = created_project["id"]

    response = api_client.get(f"/api/v1/notes/project/{id_project}", headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body) == 2
    assert body[0]["id"] == first_note["id"]
    assert body[1]["id"] == second_note["id"]


def test_update_note(api_client, created_project, admin_headers):
    note = aux_create_note(admin_headers, api_client, created_project["id"])

    response = api_client.patch(
        f"/api/v1/notes/{note["id"]}",
        json={
            "description": "description update",
            "id_project": created_project["id"],
            "content": "content test "
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()


def test_update_note_to_archived_project(
        api_client,
        created_project,
        archived_project
        , admin_headers):
    note = aux_create_note(admin_headers, api_client, created_project["id"])

    response = api_client.patch(
        f"/api/v1/notes/{note["id"]}",
        json={
            "description": "description update",
            "project_id": archived_project["id"],
            "content": "content test "
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_delete_note(
        api_client,
        created_project
        , admin_headers):
    note = aux_create_note(admin_headers, api_client, created_project["id"])

    response = api_client.delete(
        f"/api/v1/notes/{note["id"]}",
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_project_with_notes(
        api_client,
        created_project
        , admin_headers):
    note = aux_create_note(admin_headers, api_client, created_project["id"])

    response = api_client.delete(
        f"/api/v1/projects/{created_project["id"]}",
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_409_CONFLICT
