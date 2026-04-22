"""
Integration tests — auth endpoints (register, login, /me).
"""


class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/auth/register", json={
            "email": "user@example.com",
            "username": "user1",
            "password": "password123",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == "user@example.com"
        assert "id" in body
        assert "hashed_password" not in body

    def test_duplicate_email_returns_409(self, client, registered_user):
        resp = client.post("/auth/register", json={
            "email": registered_user["email"],
            "username": "other",
            "password": "password123",
        })
        assert resp.status_code == 409

    def test_duplicate_username_returns_409(self, client, registered_user):
        resp = client.post("/auth/register", json={
            "email": "other@example.com",
            "username": registered_user["username"],
            "password": "password123",
        })
        assert resp.status_code == 409

    def test_invalid_email_returns_422(self, client):
        resp = client.post("/auth/register", json={
            "email": "bad-email",
            "username": "user1",
            "password": "password123",
        })
        assert resp.status_code == 422

    def test_short_password_returns_422(self, client):
        resp = client.post("/auth/register", json={
            "email": "user@example.com",
            "username": "user1",
            "password": "short",
        })
        assert resp.status_code == 422


class TestLogin:
    def test_login_success_returns_token(self, client, registered_user):
        resp = client.post("/auth/login", json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()
        assert resp.json()["token_type"] == "bearer"

    def test_wrong_password_returns_401(self, client, registered_user):
        resp = client.post("/auth/login", json={
            "email": registered_user["email"],
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    def test_unknown_email_returns_401(self, client):
        resp = client.post("/auth/login", json={
            "email": "ghost@example.com",
            "password": "password123",
        })
        assert resp.status_code == 401


class TestMe:
    def test_me_with_valid_token(self, client, registered_user, auth_headers):
        resp = client.get("/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == registered_user["email"]

    def test_me_without_token_returns_403(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 403

    def test_me_with_invalid_token_returns_401(self, client):
        resp = client.get("/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
        assert resp.status_code == 401
