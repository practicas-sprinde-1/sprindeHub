from fastapi import status


def test_create_client(api_client, admin_headers):
    response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Empresa de prueba",
            "cif": "B12345678",
            "phone": "600123123",
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_201_CREATED

    body = response.json()
    assert body["id"] is not None
    assert body["name"] == "Empresa de prueba"
    assert body["cif"] == "B12345678"
    assert body["phone"] == "600123123"


def test_create_client_rejects_empty_name(api_client, admin_headers):
    response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "",
            "cif": "B12345678",
            "phone": "600123123",
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_client_rejects_empty_phone(api_client, admin_headers):
    response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Prueba",
            "cif": "B12345678",
            "phone": "",
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_client_rejects_name_longer(api_client, admin_headers):
    response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq",
            "cif": "B12345678",
            "phone": "600123456",
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_client_requires_name(api_client, admin_headers):
    response = api_client.post(
        "/api/v1/clients",
        json={
            "cif": "B12345678",
            "phone": "600123456",
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_client_requires_phone(api_client, admin_headers):
    response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Prueba",
            "cif": "B12345678"

        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_client_rejects_phone_longer(api_client, admin_headers):
    response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Prueba",
            "cif": "B12345678",
            "phone": "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq",
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_client_rejects_cif_longer(api_client, admin_headers):
    response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Prueba",
            "cif": "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq",
            "phone": "600123123",
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_get_client_by_id_success(api_client, user_headers, admin_headers):
    create_response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Prueba",
            "cif": "B12345678",
            "phone": "600123123",
        },
        headers=admin_headers
    )

    assert create_response.status_code == status.HTTP_201_CREATED

    client_id = create_response.json()["id"]

    response = api_client.get(
        f"/api/v1/clients/{client_id}",
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["id"] == client_id
    assert body["name"] == "Prueba"
    assert body["cif"] == "B12345678"
    assert body["phone"] == "600123123"


def test_get_client_by_id_not_found(api_client, admin_headers):
    non_exist_client: int = 9999

    response = api_client.get(f"/api/v1/clients/{non_exist_client}",headers=admin_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_client_by_id_rejects_non_integer_id(api_client, admin_headers):
    invalid_data: str = "abc"

    response = api_client.get(f"/api/v1/clients/{invalid_data}",headers=admin_headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_list_clients_returns_empty_list(api_client, admin_headers):
    response = api_client.get(f"/api/v1/clients/",headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == []


def test_list_clients_returns_clients(api_client, admin_headers):
    create_response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Prueba",
            "cif": "B12345678",
            "phone": "600123123",
        },
        headers=admin_headers
    )

    assert create_response.status_code == status.HTTP_201_CREATED

    created_client = create_response.json()

    response = api_client.get(f"/api/v1/clients/",headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == [
        {
            "id": created_client["id"],
            "name": "Prueba",
            "cif": "B12345678",
            "phone": "600123123",
            "is_active":True
        }
    ]


def test_list_clients_respects_limit(api_client, admin_headers):
    response = api_client.get(f"/api/v1/clients?limit=20",headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_clients_respects_offset(api_client, admin_headers):
    response = api_client.get(f"/api/v1/clients?offset=1",headers=admin_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_clients_rejects_negative_offset(api_client, admin_headers):
    response = api_client.get(f"/api/v1/clients?offset=-1",headers=admin_headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_list_clients_rejects_zero_limit(api_client, admin_headers):
    response = api_client.get(f"/api/v1/clients?limit=0",headers=admin_headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_list_clients_rejects_greater_limit(api_client, admin_headers):
    response = api_client.get(f"/api/v1/clients?limit=101",headers=admin_headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_update_client_name_success(api_client, admin_headers):
    create_response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Prueba",
            "cif": "B12345678",
            "phone": "600123123",
        },
        headers=admin_headers
    )

    assert create_response.status_code == status.HTTP_201_CREATED

    client_id = create_response.json()["id"]

    update_response = api_client.patch(
        f"/api/v1/clients/{client_id}",
        json={
            "name": "Prueba updated",
        },
        headers=admin_headers
    )

    assert update_response.status_code == status.HTTP_200_OK

    body = update_response.json()
    assert body["id"] == client_id
    assert body["name"] == "Prueba updated"
    assert body["cif"] == "B12345678"
    assert body["phone"] == "600123123"


def test_update_client_phone_success(api_client, admin_headers):
    create_response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Prueba",
            "cif": "B12345678",
            "phone": "600123123",
        },
        headers=admin_headers
    )

    assert create_response.status_code == status.HTTP_201_CREATED

    client_id = create_response.json()["id"]

    update_response = api_client.patch(
        f"/api/v1/clients/{client_id}",
        json={
            "phone": "6123456789"
        },
        headers=admin_headers
    )

    assert update_response.status_code == status.HTTP_200_OK

    body = update_response.json()
    assert body["id"] == client_id
    assert body["name"] == "Prueba"
    assert body["cif"] == "B12345678"
    assert body["phone"] == "6123456789"


def test_update_client_cif_success(api_client, admin_headers):
    create_response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Prueba",
            "cif": "B12345678",
            "phone": "600123123",
        },
        headers=admin_headers
    )

    assert create_response.status_code == status.HTTP_201_CREATED

    client_id = create_response.json()["id"]

    update_response = api_client.patch(
        f"/api/v1/clients/{client_id}",
        json={
            "cif": "C123456789"
        },
        headers=admin_headers
    )

    assert update_response.status_code == status.HTTP_200_OK

    body = update_response.json()
    assert body["id"] == client_id
    assert body["name"] == "Prueba"
    assert body["cif"] == "C123456789"
    assert body["phone"] == "600123123"


def test_update_client_not_found(api_client, admin_headers):
    non_exist_client: int = 9999
    update_response = api_client.patch(
        f"/api/v1/clients/{non_exist_client}",
        json={
            "cif": "C123456789"
        },
        headers=admin_headers
    )

    assert update_response.status_code == status.HTTP_404_NOT_FOUND


def test_update_client_rejects_empty_name(api_client, admin_headers):
    response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Prueba",
            "cif": "B12345678",
            "phone": "600123123",
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_201_CREATED

    client_id = response.json()["id"]

    update_response = api_client.patch(
        f"/api/v1/clients/{client_id}",
        json={
            "name": ""
        },
        headers=admin_headers
    )

    assert update_response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_update_client_rejects_longer_name(api_client, admin_headers):
    response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Prueba",
            "cif": "B12345678",
            "phone": "600123123",
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_201_CREATED

    client_id = response.json()["id"]

    update_response = api_client.patch(
        f"/api/v1/clients/{client_id}",
        json={
            "name": "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq"
        },
        headers=admin_headers
    )

    assert update_response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_update_client_rejects_empty_phone(api_client, admin_headers):
    response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Prueba",
            "cif": "B12345678",
            "phone": "600123123",
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_201_CREATED

    client_id = response.json()["id"]

    update_response = api_client.patch(
        f"/api/v1/clients/{client_id}",
        json={
            "phone": ""
        },
        headers=admin_headers
    )

    assert update_response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_delete_client_success(api_client, admin_headers):
    response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Prueba",
            "cif": "B12345678",
            "phone": "600123123",
        },
        headers=admin_headers
    )

    assert response.status_code == status.HTTP_201_CREATED

    client_id = response.json()["id"]

    delete_response = api_client.delete(
        f"/api/v1/clients/{client_id}",
        headers=admin_headers
    )

    assert delete_response.status_code == status.HTTP_200_OK


def test_delete_client_not_found(api_client, admin_headers):
    non_exist_client: int = 9999
    delete_response = api_client.delete(
        f"/api/v1/clients/{non_exist_client}",
        headers=admin_headers
    )

    assert delete_response.status_code == status.HTTP_404_NOT_FOUND


def test_client_is_not_found_after_deletion(api_client, admin_headers):
    create_response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Prueba",
            "phone": "600123123",
        },
        headers=admin_headers
    )

    assert create_response.status_code == status.HTTP_201_CREATED

    client_id = create_response.json()["id"]

    delete_response = api_client.delete(
        f"/api/v1/clients/{client_id}",
        headers=admin_headers
    )

    assert delete_response.status_code == status.HTTP_200_OK

    get_response = api_client.get(
        f"/api/v1/clients/{client_id}",
        headers=admin_headers
    )

    assert get_response.status_code == status.HTTP_404_NOT_FOUND
