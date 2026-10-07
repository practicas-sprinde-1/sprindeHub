from fastapi import status

from tests.conftest import created_client

API_PREFIX = "api/v1/admin/"


def test_create_client(
        api_client,
        admin_headers,
):
    response = api_client.post(
        f"{API_PREFIX}users",
        json={
            "email": "user@example.com",
            "username": "string",
            "password": "stringstri",
            "role": "GUEST",
            "is_active": True
        },
        headers=admin_headers

    )

    assert response.status_code == status.HTTP_201_CREATED

    assert response.json()["email"] == "user@example.com"


def test_fail_create_client_by_user(
        api_client,
        user_headers,
):
    response = api_client.post(
        f"{API_PREFIX}users",
        json={
            "email": "user@example.com",
            "username": "string",
            "password": "stringstri",
            "role": "GUEST",
            "is_active": True
        },
        headers=user_headers

    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_client_access_by_user(
        api_client,
        user_with_client,
        user_headers
):
    response = api_client.get(
        "api/v1/clients",
        headers=user_headers
    )

    assert response.status_code == status.HTTP_200_OK


def test_client_id_access_by_user(
        api_client,
        user_with_client,
        user_headers
        , created_client):
    response = api_client.get(
        f"api/v1/clients/{created_client["id"]}",
        headers=user_headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert created_client["id"]==user_with_client["client_id"]



def test_client_fail_access_by_user(
        api_client,
        user_with_client,
        user_headers
):
    response = api_client.get(
        "api/v1/clients",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_client_fail_modify_by_user(
        api_client,
        user_headers
        , created_client):
    response = api_client.patch(
        f"api/v1/clients/{created_client["id"]}",
        json={
            "name": "string",
            "cif": "string",
            "phone": "string"
        },
        headers=user_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


