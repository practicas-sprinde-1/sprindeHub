from fastapi import status

def get_client_logs(
        api_client,
        admin_headers,
        client_id
) -> list[dict]:
    response = api_client.get(
        f"/api/v1/admin/logs/entities/CLIENT/{client_id}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    return response.json()

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

def test_create_log(
    api_client,
    admin_headers,
    admin_user,
    created_client,
):
    logs = get_client_logs(
        api_client,
        admin_headers,
        created_client["id"],
    )

    assert len(logs) == 1

    log = logs[0]
    assert log["user_id"] == admin_user.id
    assert log["action"] == "CREATE"
    assert log["affected_entity"] == "CLIENT"
    assert log["affected_entity_id"] == created_client["id"]

def test_update_log(
    api_client,
    admin_headers,
    admin_user,
    created_client,
):
    response = api_client.patch(
        f"/api/v1/clients/{created_client['id']}/archive",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_active"] is False

    logs = get_client_logs(
        api_client,
        admin_headers,
        created_client["id"],
    )

    update_logs = [
        log for log in logs
        if log["action"] == "UPDATE"
    ]

    assert len(update_logs) == 1

    log = update_logs[0]
    assert log["user_id"] == admin_user.id
    assert log["affected_entity"] == "CLIENT"
    assert log["affected_entity_id"] == created_client["id"]

def test_second_update_log(
    api_client,
    admin_headers,
    admin_user,
    created_client,
):
    archive_response = api_client.patch(
        f"/api/v1/clients/{created_client['id']}/archive",
        headers=admin_headers,
    )
    assert archive_response.status_code == status.HTTP_200_OK

    restore_response = api_client.patch(
        f"/api/v1/clients/{created_client['id']}/restore",
        headers=admin_headers,
    )
    assert restore_response.status_code == status.HTTP_200_OK
    assert restore_response.json()["is_active"] is True

    logs = get_client_logs(
        api_client,
        admin_headers,
        created_client["id"],
    )

    update_logs = [
        log for log in logs
        if log["action"] == "UPDATE"
    ]

    assert len(update_logs) == 2

    for log in update_logs:
        assert log["user_id"] == admin_user.id
        assert log["affected_entity"] == "CLIENT"
        assert log["affected_entity_id"] == created_client["id"]

def test_delete_log(
    api_client,
    admin_headers,
    admin_user,
    created_client,
):
    client_id = created_client["id"]

    response = api_client.delete(
        f"/api/v1/clients/{client_id}",
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    logs = get_client_logs(
        api_client,
        admin_headers,
        client_id,
    )

    delete_logs = [
        log for log in logs
        if log["action"] == "DELETE"
    ]

    assert len(delete_logs) == 1

    log = delete_logs[0]
    assert log["user_id"] == admin_user.id
    assert log["affected_entity"] == "CLIENT"
    assert log["affected_entity_id"] == client_id

