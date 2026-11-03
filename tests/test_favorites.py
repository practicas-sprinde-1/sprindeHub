from fastapi import status


def test_user_can_favorite_and_unfavorite_client(
        api_client,
        user_headers,
        user_with_client,
        created_client,
):
    client_id = created_client["id"]

    favorite_response = api_client.patch(
        f"/api/v1/clients/{client_id}/favorite",
        headers=user_headers,
    )

    assert favorite_response.status_code == status.HTTP_200_OK
    assert favorite_response.json()["is_favorite"] is True

    duplicate_favorite_response = api_client.patch(
        f"/api/v1/clients/{client_id}/favorite",
        headers=user_headers,
    )

    assert duplicate_favorite_response.status_code == status.HTTP_409_CONFLICT
    assert duplicate_favorite_response.json() == {
        "detail": "El cliente ya está en favoritos"
    }

    list_response = api_client.get(
        "/api/v1/clients/favorites",
        headers=user_headers,
    )

    assert list_response.status_code == status.HTTP_200_OK
    page = list_response.json()
    assert page["total"] == 1
    assert page["offset"] == 0
    assert page["limit"] == 20
    assert len(page["items"]) == 1
    assert page["items"][0]["id"] == client_id
    assert page["items"][0]["is_favorite"] is True
    empty_page = api_client.get(
        "/api/v1/clients/favorites?offset=1&limit=1", headers=user_headers
    ).json()
    assert empty_page == {"items": [], "total": 1, "offset": 1, "limit": 1}

    unfavorite_response = api_client.patch(
        f"/api/v1/clients/{client_id}/unfavorite",
        headers=user_headers,
    )

    assert unfavorite_response.status_code == status.HTTP_200_OK
    assert unfavorite_response.json()["is_favorite"] is False
    assert api_client.get("/api/v1/clients/favorites", headers=user_headers).json() == {
        "items": [], "total": 0, "offset": 0, "limit": 20,
    }


def test_user_can_favorite_and_unfavorite_project(
        api_client,
        user_headers,
        user_with_client,
        created_project,
):
    project_id = created_project["id"]

    favorite_response = api_client.patch(
        f"/api/v1/projects/{project_id}/favorite",
        headers=user_headers,
    )

    assert favorite_response.status_code == status.HTTP_200_OK
    assert favorite_response.json()["is_favorite"] is True

    duplicate_favorite_response = api_client.patch(
        f"/api/v1/projects/{project_id}/favorite",
        headers=user_headers,
    )

    assert duplicate_favorite_response.status_code == status.HTTP_409_CONFLICT
    assert duplicate_favorite_response.json() == {
        "detail": "El proyecto ya está en favoritos"
    }

    list_response = api_client.get(
        "/api/v1/projects/favorites",
        headers=user_headers,
    )

    assert list_response.status_code == status.HTTP_200_OK
    page = list_response.json()
    assert page["total"] == 1
    assert page["offset"] == 0
    assert page["limit"] == 20
    assert len(page["items"]) == 1
    assert page["items"][0]["id"] == project_id
    assert page["items"][0]["is_favorite"] is True
    empty_page = api_client.get(
        "/api/v1/projects/favorites?offset=1&limit=1", headers=user_headers
    ).json()
    assert empty_page == {"items": [], "total": 1, "offset": 1, "limit": 1}
    assert page["items"][0]["client"]["id"] == created_project["client_id"]
    assert page["items"][0]["environments"] == []
    assert page["items"][0]["commands_count"] == 0

    unfavorite_response = api_client.patch(
        f"/api/v1/projects/{project_id}/unfavorite",
        headers=user_headers,
    )

    assert unfavorite_response.status_code == status.HTTP_200_OK
    assert unfavorite_response.json()["is_favorite"] is False
    assert api_client.get("/api/v1/projects/favorites", headers=user_headers).json() == {
        "items": [], "total": 0, "offset": 0, "limit": 20,
    }
