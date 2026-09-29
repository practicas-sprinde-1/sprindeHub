from fastapi import status


def test_create_client(api_client):
    response = api_client.post(
        "/api/v1/clients",
        json={
            "name": "Empresa de prueba",
            "cif": "B12345678",
            "phone": "600123123",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    body = response.json()
    assert body["id"] is not None
    assert body["name"] == "Empresa de prueba"
    assert body["cif"] == "B12345678"
    assert body["phone"] == "600123123"


    