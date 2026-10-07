from fastapi import status


def test_user_profile(
        api_client,
        user_headers,
        created_user_type_user
):
    response = api_client.get(
        "/api/v1/users/me",
        headers=user_headers
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.json()["id"] == created_user_type_user.id


def test_update_profile(
        api_client,
        user_headers,
        created_user_type_user
):
    response = api_client.patch(
        "/api/v1/users/me",
        json={
            "email": "user@example.com",
            "username": "string"
        },
        headers=user_headers
    )

    assert response.status_code == status.HTTP_200_OK


def test_duplicate_data(
        api_client,
        user_headers,
        admin_headers
):
    response_post = api_client.post(
        "/api/v1/admin/users",
        json={
            "email": "user@example.com",
            "username": "string",
            "password": "1234567890"
        },
        headers=admin_headers
    )

    assert response_post.status_code == status.HTTP_201_CREATED

    response = api_client.patch(
        "/api/v1/users/me",
        json={
            "email": "user@example.com",
            "username": "string"
        },
        headers=user_headers
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_change_password(
        api_client,
        user_headers
):
    response = api_client.patch(
        "/api/v1/users/me/password",
        json={
            "current_password": "passwordde+10",
            "new_password": "stringstri"
        },
        headers=user_headers
    )
    assert response.status_code == status.HTTP_200_OK


def test_change_invalid_password(
        api_client,
        user_headers
):
    response = api_client.patch(
        "/api/v1/users/me/password",
        json={
            "current_password": "1234567890",
            "new_password": "stringstri"
        },
        headers=user_headers
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_with_old_and_new_password(
        api_client,
        user_headers,
        admin_headers
):
    response = api_client.patch(
        "/api/v1/users/me/password",
        json={
            "current_password": "passwordde+10",
            "new_password": "stringstri"
        },
        headers=user_headers
    )
    assert response.status_code == status.HTTP_200_OK

    response_fail_login = api_client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@test.com",
            "password": "passwordde+10"
        }
    )

    assert response_fail_login.status_code == status.HTTP_401_UNAUTHORIZED

    response_login = api_client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@test.com",
            "password": "stringstri"
        }
    )

    assert response_login.status_code == status.HTTP_200_OK


def test_create_and_update_user(
        api_client,
        admin_headers,
        created_user_type_user
):
    response = api_client.post(
        "/api/v1/admin/users",
        json={
            "email": "user@example.com",
            "username": "string",
            "password": "stringstri",
            "role": "GUEST",
            "is_active": True
        },
        headers=admin_headers
    )

    assert response.status_code==status.HTTP_201_CREATED

    response = api_client.patch(
        f"/api/v1/admin/users/{created_user_type_user.id}",
        json={
            "role": "GUEST",
            "is_active": True
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_200_OK

def test_create_and_update_user_without_admin(
        api_client,
        created_user_type_user,
        user_headers
):
    response = api_client.post(
        "/api/v1/admin/users",
        json={
            "email": "user@example.com",
            "username": "string",
            "password": "stringstri",
            "role": "GUEST",
            "is_active": True
        },
        headers=user_headers
    )

    assert response.status_code==status.HTTP_403_FORBIDDEN

    response = api_client.patch(
        f"/api/v1/admin/users/{created_user_type_user.id}",
        json={
            "role": "GUEST",
            "is_active": True
        },
        headers=user_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
