def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "anand@example.com",
            "full_name": "Anand Reddy",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "anand@example.com"
    assert data["full_name"] == "Anand Reddy"
    assert data["is_active"] is True
    assert "password_hash" not in data
    assert "password" not in data


def test_register_duplicate_email(client):
    payload = {
        "email": "anand@example.com",
        "full_name": "Anand Reddy",
        "password": "StrongPassword123!",
    }

    first_response = client.post("/api/v1/auth/register", json=payload)
    second_response = client.post("/api/v1/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_register_invalid_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "full_name": "Anand Reddy",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 422


def test_register_short_password(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "anand@example.com",
            "full_name": "Anand Reddy",
            "password": "short",
        },
    )

    assert response.status_code == 422


def test_login_success(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "anand@example.com",
            "full_name": "Anand Reddy",
            "password": "StrongPassword123!",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "anand@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "anand@example.com",
            "full_name": "Anand Reddy",
            "password": "StrongPassword123!",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "anand@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_current_user_without_token(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_current_user_with_valid_token(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "anand@example.com",
            "full_name": "Anand Reddy",
            "password": "StrongPassword123!",
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "anand@example.com",
            "password": "StrongPassword123!",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "anand@example.com"
    assert response.json()["full_name"] == "Anand Reddy"
    assert "password_hash" not in response.json()


def test_current_user_with_invalid_token(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401
