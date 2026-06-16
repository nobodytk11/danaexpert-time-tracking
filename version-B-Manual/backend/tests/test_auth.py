"""Integration tests for the authentication endpoints."""


def test_register_creates_user_and_hides_password(client):
    resp = client.post(
        "/auth/register", json={"email": "new@user.com", "password": "pw12345"}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "new@user.com"
    assert "hashed_password" not in body
    assert "password" not in body


def test_register_duplicate_email_is_rejected(client):
    client.post("/auth/register", json={"email": "dup@user.com", "password": "pw12345"})
    resp = client.post(
        "/auth/register", json={"email": "dup@user.com", "password": "pw12345"}
    )
    assert resp.status_code == 400


def test_login_returns_access_token(client):
    client.post("/auth/register", json={"email": "log@user.com", "password": "pw12345"})
    resp = client.post(
        "/auth/login", json={"email": "log@user.com", "password": "pw12345"}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password_is_unauthorized(client):
    client.post("/auth/register", json={"email": "log2@user.com", "password": "pw12345"})
    resp = client.post(
        "/auth/login", json={"email": "log2@user.com", "password": "WRONG"}
    )
    assert resp.status_code == 401
