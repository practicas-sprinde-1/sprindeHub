from fastapi import status

def test_get_logs(
        api_client,
        admin_headers,
        created_client

):
    response = api_client.get(
        "/api/v1/admin/logs",
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json())==1

def test_get_logs_without_login(
        api_client,
):
    response = api_client.get(
        "/api/v1/admin/logs",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_logs_without_admin(
        api_client,
        user_headers
):
    response = api_client.get(
        "/api/v1/admin/logs",
        headers=user_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_user_logs(
        api_client,
        admin_headers,
        created_user_type_user,
        created_client,
        user_headers,
        user_with_client
):
    update_response = api_client.patch(
        f"/api/v1/clients/{created_client['id']}",
        json={"name": "Test"},
        headers=user_headers,
    )

    assert update_response.status_code == status.HTTP_200_OK

    response = api_client.get(
        f"/api/v1/admin/logs/users/{created_user_type_user.id}",
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json())==1

def test_get_entity_logs(
        api_client,
        admin_headers,
        created_client
):
    response = api_client.get(
        f"/api/v1/admin/logs/entities/CLIENT/{created_client["id"]}",
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json())==1
    assert response.json()[0]["affected_entity_id"]==created_client["id"]

