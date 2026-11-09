def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_success(client):
    response = client.post(
        "/auth/register",
        json={"username": "bob", "email": "bob@example.com", "password": "secret123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "bob"
    # The password (or its hash) must never be returned.
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_username(client):
    body = {"username": "bob", "email": "bob@example.com", "password": "secret123"}
    client.post("/auth/register", json=body)
    response = client.post("/auth/register", json={**body, "email": "other@example.com"})
    assert response.status_code == 409


def test_register_validation_error(client):
    # Password too short and email invalid -> 422 from Pydantic validation.
    response = client.post(
        "/auth/register",
        json={"username": "bob", "email": "not-an-email", "password": "123"},
    )
    assert response.status_code == 422


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={"username": "bob", "email": "bob@example.com", "password": "secret123"},
    )
    response = client.post("/auth/login", data={"username": "bob", "password": "wrong-pass"})
    assert response.status_code == 401


def test_me_requires_token(client):
    assert client.get("/auth/me").status_code == 401


def test_me_with_invalid_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401


def test_me_with_valid_token(client, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "alice"
