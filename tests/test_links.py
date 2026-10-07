from app.models.link import Link
from fastapi import status

def aux_create_link(
admin_headers,
        api_client,
        client_id:int
        ) -> Link:
    response = api_client.post(
        "/api/v1/links",
        json={
            "project_id":client_id,
            "url": "http://test.test",
            "title":"link auxiliar"
        },
        headers=admin_headers
    )
    return response.json()


def test_create_link(
        api_client,
        created_project
, admin_headers):
    response = api_client.post(
        "/api/v1/links",
        json={
            "title": "link test",
            "project_id": created_project["id"],
            "url": "http://test.test",

        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["id"] is not None
    assert body["project_id"] == created_project["id"]
    assert body["url"] == "http://test.test"
    assert body["title"] == "link test"


def test_create_link_fail_id_project(
        api_client,
        created_project
, admin_headers):
    false_project_id = 9999
    response = api_client.post(
        "/api/v1/links",
        json={
            "project_id": 9999,
            "url": "http://test.test",
            "title": "link test"
        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND



def test_create_link_archived_project(
        api_client,
        archived_project,
admin_headers):
    response = api_client.post(
        "/api/v1/links",
        json={
            "project_id": archived_project["id"],
            "url": "http://test.test",
            "title": "link test"
        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_link_fail_url(
        api_client,
        created_project
, admin_headers):
    false_project_id = 9999
    response = api_client.post(
        "/api/v1/links",
        json={
            "project_id": 9999,
            "url": "test.test",
            "title": "link test"
        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_list_links(api_client, created_project, admin_headers):
    link = aux_create_link(admin_headers,api_client,created_project["id"])

    response = api_client.get("/api/v1/links",headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert len(body)==1
    assert body[0]["id"]==link["id"]

def test_get_link_by_id(api_client, created_project, admin_headers):
    link = aux_create_link(admin_headers,api_client, created_project["id"])
    response = api_client.get("/api/v1/links",headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body[0]["id"] == link["id"]

def test_get_links_by_projects(api_client, created_project, admin_headers):
    first_link = aux_create_link(admin_headers,api_client, created_project["id"])
    second_link = aux_create_link(admin_headers,api_client, created_project["id"])

    id_project:int = created_project["id"]

    response = api_client.get(f"/api/v1/links/project/{id_project}",headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body)==2
    assert body[0]["id"] == first_link["id"]
    assert body[1]["id"] == second_link["id"]

def test_update_link(api_client, created_project, admin_headers):
    link = aux_create_link(admin_headers,api_client,created_project["id"])

    response = api_client.patch(
        f"/api/v1/links/{link["id"]}",
        json={
            "url":"http://update",
            "id_project":created_project["id"],
            "title": "link test"
        },
        headers=admin_headers
    )

    assert  response.status_code==status.HTTP_200_OK

    body = response.json()

def test_update_link_to_archived_project(
        api_client,
        created_project,
        archived_project
, admin_headers):
    link = aux_create_link(admin_headers,api_client,created_project["id"])

    response = api_client.patch(
        f"/api/v1/links/{link["id"]}",
        json={
            "url": "http://update",
            "project_id": archived_project["id"],
            "title": "link test"
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_delete_link(
        api_client,
        created_project
, admin_headers):
    link = aux_create_link(admin_headers,api_client,created_project["id"])

    response = api_client.delete(
        f"/api/v1/links/{link["id"]}",headers=admin_headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_delete_project_with_links(
        api_client,
        created_project
, admin_headers):
    link = aux_create_link(admin_headers,api_client,created_project["id"])

    response = api_client.delete(
        f"/api/v1/projects/{created_project["id"]}",headers=admin_headers
    )

    assert response.status_code == status.HTTP_409_CONFLICT






