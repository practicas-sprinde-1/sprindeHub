from fastapi import status

API_PREFIX = "/api/v1/admin/user-clients"

def test_assign_user_to_client(
 api_client,
    admin_headers,
    created_client,
    created_user_type_user,
):
    response = api_client.post(
        f"{API_PREFIX}/users/{created_user_type_user.id}/clients",
        json={
            "client_id": created_client["id"],
        },
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_201_CREATED

    relation = response.json()
    assert relation["user_id"] == created_user_type_user.id
    assert relation["client_id"] == created_client["id"]

def test_user_cannot_assign_user_to_client(
    api_client,
    user_headers,
    created_client,
    created_user_type_user,
):
    response = api_client.post(
        f"{API_PREFIX}/users/{created_user_type_user.id}/clients",
        json={
            "client_id": created_client["id"],
        },
        headers=user_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_cannot_assign_nonexistent_user(
    api_client,
    admin_headers,
    created_client,
):
    response = api_client.post(
        f"{API_PREFIX}/users/999999/clients",
        json={
            "client_id": created_client["id"],
        },
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_cannot_assign_user_to_nonexistent_client(
    api_client,
    admin_headers,
    created_user_type_user,
):
    response = api_client.post(
        f"{API_PREFIX}/users/{created_user_type_user.id}/clients",
        json={
            "client_id": 999999,
        },
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_cannot_repeat_user_client(
    api_client,
    admin_headers,
    created_client,
    created_user_type_user,
    user_with_client,
):
    response = api_client.post(
        f"{API_PREFIX}/users/{created_user_type_user.id}/clients",
        json={
            "client_id": created_client["id"],
        },
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_409_CONFLICT

def test_can_list_client_from_user_by_id(
    api_client,
    admin_headers,
    created_user_type_user,
    user_with_client,
):
    response = api_client.get(
        f"{API_PREFIX}/{created_user_type_user.id}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    relations = response.json()
    assert len(relations) == 1
    assert relations[0]["user_id"] == created_user_type_user.id

def test_can_list_users_with_client_access(
    api_client,
    admin_headers,
    created_client,
    created_user_type_user,
    user_with_client,
):
    response = api_client.get(
        f"{API_PREFIX}/clients/{created_client['id']}/users",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    relations = response.json()
    assert len(relations) == 1
    assert relations[0]["user_id"] == created_user_type_user.id
    assert relations[0]["client_id"] == created_client["id"]

def test_can_revoke_user_client_access(
    api_client,
    admin_headers,
    created_client,
    created_user_type_user,
    user_with_client,
):
    response = api_client.delete(
        f"{API_PREFIX}/users/{created_user_type_user.id}/clients/{created_client['id']}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    check_response = api_client.get(
        f"{API_PREFIX}/",
        params={
            "user_id": created_user_type_user.id,
            "client_id": created_client["id"],
        },
        headers=admin_headers,
    )

    assert check_response.status_code == status.HTTP_404_NOT_FOUND

def test_user_denied_access_after_revocation(
    api_client,
    admin_headers,
    user_headers,
    created_client,
    created_user_type_user,
    user_with_client,
):
    access_response = api_client.get(
        f"/api/v1/clients/{created_client['id']}",
        headers=user_headers,
    )
    assert access_response.status_code == status.HTTP_200_OK

    revoke_response = api_client.delete(
        f"{API_PREFIX}/users/{created_user_type_user.id}/clients/{created_client['id']}",
        headers=admin_headers,
    )
    assert revoke_response.status_code == status.HTTP_200_OK

    denied_response = api_client.get(
        f"/api/v1/clients/{created_client['id']}",
        headers=user_headers,
    )
    assert denied_response.status_code == status.HTTP_403_FORBIDDEN
