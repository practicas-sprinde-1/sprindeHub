from fastapi import status

from app.models.project import Project


def aux_create_project(
        admin_headers,
        api_client,
        client_id: int,
        name: str = "Proyecto auxiliar",
        description: str = "Descripción del  auxiliar",
) -> Project:
    response = api_client.post(
        "/api/v1/projects",
        json={
            "name": name,
            "description": description,
            "client_id": client_id,
        },
        headers=admin_headers
    )
    return response.json()


def test_create_project(api_client, created_client, admin_headers):
    response = api_client.post(
        "/api/v1/projects",
        json={
            "name": "Proyecto test",
            "description": "Descripcion test",
            "client_id": created_client["id"],
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_201_CREATED

    body = response.json()
    assert body["id"] is not None
    assert body["name"] == "Proyecto test"
    assert body["description"] == "Descripcion test"
    assert body["client_id"] == created_client["id"]


def test_create_project_with_nonexistent_client(api_client, admin_headers):
    response = api_client.post(
        "/api/v1/projects",
        json={
            "name": "Proyecto test",
            "description": "test",
            "client_id": 999999,
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_project_with_archived_client(api_client, archived_client, admin_headers):
    response = api_client.post(
        "/api/v1/projects",
        json={
            "name": "Proyecto test",
            "description": "test",
            "client_id": archived_client["id"],
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_list_projects(api_client, created_client, admin_headers):
    project = aux_create_project(admin_headers, api_client, created_client["id"])

    response = api_client.get("/api/v1/projects", headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body["total"] == 1
    assert body["offset"] == 0
    assert body["limit"] == 20
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == project["id"]


def test_list_projects_returns_total_and_respects_pagination(
        api_client, created_client, admin_headers):
    first_project = aux_create_project(
        admin_headers,
        api_client,
        created_client["id"],
        name="Primer proyecto",
    )
    second_project = aux_create_project(
        admin_headers,
        api_client,
        created_client["id"],
        name="Segundo proyecto",
    )

    response = api_client.get(
        "/api/v1/projects?offset=1&limit=1",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["total"] == 2
    assert body["offset"] == 1
    assert body["limit"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == second_project["id"]
    assert first_project["id"] != second_project["id"]


def test_list_projects_includes_the_data_required_by_the_table(
        api_client, created_client, admin_headers):
    project = aux_create_project(admin_headers, api_client, created_client["id"])
    project_id = project["id"]

    resources = (
        ("/api/v1/environments", {"type": "production", "url": "https://erp.acme.es"}),
        ("/api/v1/environments", {"type": "staging", "url": "https://staging.erp.acme.es"}),
        ("/api/v1/repositories", {"type": "backend", "url": "https://github.com/sprinde/acme-erp-api"}),
        ("/api/v1/services", {"name": "Hetzner"}),
        ("/api/v1/domains", {"url": "https://erp.acme.es"}),
        ("/api/v1/commands", {"name": "deploy", "instruction": "./deploy.sh production"}),
        ("/api/v1/links", {"title": "Runbook", "url": "https://docs.acme.es/runbook"}),
        ("/api/v1/notes", {"description": "Facturación", "content": "Se ejecuta cada noche."}),
    )

    for url, payload in resources:
        response = api_client.post(
            url,
            json={"project_id": project_id, **payload},
            headers=admin_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED

    response = api_client.get("/api/v1/projects", headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["total"] == 1
    row = body["items"][0]
    assert row == {
        "id": project_id,
        "name": "Proyecto auxiliar",
        "client": {"id": created_client["id"], "name": "Cliente de prueba"},
        "environments": [
            {"id": row["environments"][0]["id"], "type": "production", "url": "https://erp.acme.es"},
            {"id": row["environments"][1]["id"], "type": "staging", "url": "https://staging.erp.acme.es"},
        ],
        "repositories": [
            {"id": row["repositories"][0]["id"], "type": "backend", "url": "https://github.com/sprinde/acme-erp-api"}
        ],
        "services": [{"id": row["services"][0]["id"], "name": "Hetzner"}],
        "domains": [{"id": row["domains"][0]["id"], "url": "https://erp.acme.es"}],
        "commands_count": 1,
        "links_count": 1,
        "notes_count": 1,
    }

    detail_response = api_client.get(
        f"/api/v1/projects/{project_id}",
        headers=admin_headers,
    )
    assert detail_response.status_code == status.HTTP_200_OK

    detail = detail_response.json()
    assert detail["client"]["name"] == "Cliente de prueba"
    assert detail["environments"][0]["type"] == "production"
    assert detail["repositories"][0]["type"] == "backend"
    assert detail["services"][0]["name"] == "Hetzner"
    assert detail["domains"][0]["url"] == "https://erp.acme.es"
    assert detail["commands"][0]["instruction"] == "./deploy.sh production"
    assert detail["links"][0]["title"] == "Runbook"
    assert detail["notes"][0]["content"] == "Se ejecuta cada noche."


def test_get_project_by_id(api_client, created_client, admin_headers):
    project = aux_create_project(admin_headers, api_client, created_client["id"])

    response = api_client.get(f"/api/v1/projects/{project['id']}", headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body["id"] == project["id"]
    assert body["name"] == project["name"]
    assert body["client_id"] == created_client["id"]


def test_get_non_exist_project(api_client, admin_headers):
    non_exist_project: int = 9999
    response = api_client.get(f"/api/v1/projects/{non_exist_project}", headers=admin_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_projects_by_client(api_client, created_client, admin_headers):
    first_project = aux_create_project(
        admin_headers,
        api_client,
        created_client["id"],
        name="test1",
    )

    second_project = aux_create_project(
        admin_headers,
        api_client,
        created_client["id"],
        name="test2",
    )

    response = api_client.get(
        f"/api/v1/projects/client/{created_client['id']}",
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert body["items"][0]["id"] == first_project["id"]
    assert body["items"][1]["id"] == second_project["id"]


def test_update_project_name_and_description(api_client, created_client, admin_headers):
    project = aux_create_project(admin_headers, api_client, created_client["id"])

    response = api_client.patch(
        f"/api/v1/projects/{project['id']}",
        json={
            "name": "test update",
            "description": "test update",
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body["name"] == "test update"
    assert body["description"] == "test update"
    assert body["client_id"] == created_client["id"]


def test_update_project_client_id(api_client, created_client, admin_headers):
    project = aux_create_project(admin_headers, api_client, created_client["id"])

    second_client_json = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Segundo cliente",
            "cif": "B87654321",
            "phone": "600987987",
        },
        headers=admin_headers
    )

    assert second_client_json.status_code == status.HTTP_201_CREATED
    second_client = second_client_json.json()

    response = api_client.patch(
        f"/api/v1/projects/{project['id']}",
        json={
            "client_id": second_client["id"],
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["client_id"] == second_client["id"]


def test_update_project_to_archived_client(
        api_client,
        created_client,
        archived_client,
        admin_headers):
    project = aux_create_project(admin_headers, api_client, created_client["id"])

    response = api_client.patch(
        f"/api/v1/projects/{project['id']}",
        json={
            "client_id": archived_client["id"],
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_update_project_to_nonexistent_client(api_client, created_client, admin_headers):
    project = aux_create_project(admin_headers, api_client, created_client["id"])

    response = api_client.patch(
        f"/api/v1/projects/{project['id']}",
        json={
            "client_id": 999999,
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_project(api_client, created_client, admin_headers):
    project = aux_create_project(admin_headers, api_client, created_client["id"])

    response = api_client.delete(
        f"/api/v1/projects/{project['id']}",
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_project_is_not_found_after_deletion(api_client, created_client, admin_headers):
    project = aux_create_project(admin_headers, api_client, created_client["id"])

    delete_response = api_client.delete(
        f"/api/v1/projects/{project['id']}",
        headers=admin_headers
    )

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    response = api_client.get(f"/api/v1/projects/{project['id']}", headers=admin_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Proyecto no encontrado"
