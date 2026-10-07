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
            "refresh_token":token["refresh_token"]
        }
    )

    assert response_refresh.status_code == status.HTTP_201_CREATED

    new_access_token = response_refresh.json()

    assert new_access_token["access_token"] is not token["access_token"]


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
            "refresh_token":"invalidToken"
        }
    )

    assert response_refresh.status_code == status.HTTP_401_UNAUTHORIZED


def test_any_endpoint_without_login(
        api_client
):
    response = api_client.get(
        "api/v1/clients"
    )

    assert  response.status_code == status.HTTP_401_UNAUTHORIZED

def test_token_invalido_devuelve_401(api_client):
    response = api_client.get(
        "/api/v1/clients",
        headers={
            "Authorization": "Bearer tokenmanpulado"
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED





