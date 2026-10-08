from fastapi import status

API_PREFIX = "/api/v1/auth/"


def test_register(
        api_client
):
    response = api_client.post(
        f"{API_PREFIX}register",
        json={
            "email": "user@example.com",
            "username": "string",
            "password": "stringstri"
        }
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = response.json()

    assert user["email"] == "user@example.com"
    assert user["username"] == "string"


def test_register_with_incorrect_data(
        api_client
):
    response = api_client.post(
        f"{API_PREFIX}register",
        json={
            "email": "user",
            "username": "",
            "password": ""
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_register_with_duplicated_data(
        api_client
):
    response_post = api_client.post(
        f"{API_PREFIX}register",
        json={
            "email": "user@example.com",
            "username": "string",
            "password": "stringstri"
        }
    )

    assert response_post.status_code == status.HTTP_201_CREATED

    user = response_post.json()

    assert user["email"] == "user@example.com"
    assert user["username"] == "string"

    response = api_client.post(
        f"{API_PREFIX}register",
        json={
            "email": "user@example.com",
            "username": "string",
            "password": "stringstri"
        }
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_login(
        api_client
):
    response_post = api_client.post(
        f"{API_PREFIX}register",
        json={
            "email": "user@example.com",
            "username": "string",
            "password": "stringstri"
        }
    )

    assert response_post.status_code == status.HTTP_201_CREATED

    response_login = api_client.post(
        f"{API_PREFIX}login",
        json={
            "email": "user@example.com",
            "password": "stringstri"
        }
    )

    assert response_login.status_code == status.HTTP_200_OK

    token = response_login.json()

    assert token["access_token"] is not None
    assert token["refresh_token"] is not None


def test_fail_login(
        api_client
):
    response_login = api_client.post(
        f"{API_PREFIX}login",
        json={
            "email": "user@example.com",
            "password": "stringstri"
        }
    )

    assert response_login.status_code == status.HTTP_401_UNAUTHORIZED


def test_inactive_user_login(
        api_client,
        created_inactive_user
):
    response_login = api_client.post(
        f"{API_PREFIX}login",
        json={
            "email": "user@test.com",
            "password": "passwordde+10"
        }
    )

    assert response_login.status_code == status.HTTP_403_FORBIDDEN


def test_create_new_access_token(
        api_client,

):
    response_post = api_client.post(
        f"{API_PREFIX}register",
        json={
            "email": "user@example.com",
            "username": "string",
            "password": "stringstri"
        }
    )

    assert response_post.status_code == status.HTTP_201_CREATED

    response_login = api_client.post(
        f"{API_PREFIX}login",
        json={
            "email": "user@example.com",
            "password": "stringstri"
        }
    )

    assert response_login.status_code == status.HTTP_200_OK

    token = response_login.json()

    response_refresh = api_client.post(
        f"{API_PREFIX}refresh",
        json={
            "refresh_token": token["refresh_token"]
        }
    )

    assert response_refresh.status_code == status.HTTP_201_CREATED

    access_token = response_refresh.json()["access_token"]

    user_header = {
        "Authorization": f"Bearer {access_token}"
    }

    response_get = api_client.get(
        "api/v1/users/me",
        headers=user_header
    )

    assert response_get.status_code == status.HTTP_200_OK



def test_invalid_refresh_token(
        api_client,

):
    response_post = api_client.post(
        f"{API_PREFIX}register",
        json={
            "email": "user@example.com",
            "username": "string",
            "password": "stringstri"
        }
    )

    assert response_post.status_code == status.HTTP_201_CREATED

    response_login = api_client.post(
        f"{API_PREFIX}login",
        json={
            "email": "user@example.com",
            "password": "stringstri"
        }
    )

    assert response_login.status_code == status.HTTP_200_OK

    token = response_login.json()

    response_refresh = api_client.post(
        f"{API_PREFIX}refresh",
        json={
            "refresh_token": "invalidToken"
        }
    )

    assert response_refresh.status_code == status.HTTP_401_UNAUTHORIZED


def test_any_endpoint_without_login(
        api_client
):
    response = api_client.get(
        "api/v1/clients"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_token_invalid(api_client):
    response = api_client.get(
        "/api/v1/clients",
        headers={
            "Authorization": "Bearer tokenmanpulado"
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_using_access_token_in_refresh_token_spot(
        api_client,
):
    response_post = api_client.post(
        f"{API_PREFIX}register",
        json={
            "email": "user@example.com",
            "username": "string",
            "password": "stringstri"
        }
    )

    assert response_post.status_code == status.HTTP_201_CREATED

    response_login = api_client.post(
        f"{API_PREFIX}login",
        json={
            "email": "user@example.com",
            "password": "stringstri"
        }
    )

    assert response_login.status_code == status.HTTP_200_OK

    token = response_login.json()

    access_token = token["access_token"]

    response_refresh = api_client.post(
        f"{API_PREFIX}refresh",
        json={
            "refresh_token": access_token
        },
    )

    assert response_refresh.status_code == status.HTTP_401_UNAUTHORIZED


def test_access_to_profile_by_desactivated_user(
        api_client,
        admin_headers
):
    response_post = api_client.post(
        f"{API_PREFIX}register",
        json={
            "email": "user@example.com",
            "username": "string",
            "password": "stringstri"
        }
    )

    assert response_post.status_code == status.HTTP_201_CREATED

    user_id = response_post.json()["id"]

    response_login = api_client.post(
        f"{API_PREFIX}login",
        json={
            "email": "user@example.com",
            "password": "stringstri"
        }
    )

    assert response_login.status_code == status.HTTP_200_OK

    token = response_login.json()

    access_token = token["access_token"]

    response_admin = api_client.patch(
        f"/api/v1/admin/users/{user_id}",
        json={
            "is_active": False
        },
        headers=admin_headers
    )

    assert response_admin.status_code == status.HTTP_200_OK

    user_header = {
        "Authorization":f"Bearer {access_token}"
    }

    response_profile = api_client.get(
        "/api/v1/users/me",
        headers=user_header
    )

    assert response_profile.status_code == status.HTTP_403_FORBIDDEN


def test_access_to_refresh_by_desactivated_user(
        api_client,
        admin_headers
):
    response_post = api_client.post(
        f"{API_PREFIX}register",
        json={
            "email": "user@example.com",
            "username": "string",
            "password": "stringstri"
        }
    )

    assert response_post.status_code == status.HTTP_201_CREATED

    user_id = response_post.json()["id"]

    response_login = api_client.post(
        f"{API_PREFIX}login",
        json={
            "email": "user@example.com",
            "password": "stringstri"
        }
    )

    assert response_login.status_code == status.HTTP_200_OK

    token = response_login.json()

    access_token = token["access_token"]
    refresh_token = token["refresh_token"]

    response_admin = api_client.patch(
        f"/api/v1/admin/users/{user_id}",
        json={
            "is_active": False
        },
        headers=admin_headers
    )

    assert response_admin.status_code == status.HTTP_200_OK

    user_header = {
        "Authorization":f"Bearer {access_token}"
    }



    response_profile = api_client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token":refresh_token
        },
        headers=user_header
    )

    assert response_profile.status_code == status.HTTP_403_FORBIDDEN





