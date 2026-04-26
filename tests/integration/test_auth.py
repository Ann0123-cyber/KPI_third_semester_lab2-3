class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/auth/register", json={"email": "u@e.com", "username": "user1", "password": "password123"})
        assert resp.status_code == 201
        assert resp.json()["email"] == "u@e.com"

    def test_duplicate_email_returns_409(self, client, registered_user):
        resp = client.post("/auth/register", json={"email": registered_user["email"], "username": "other", "password": "password123"})
        assert resp.status_code == 409

    def test_duplicate_username_returns_409(self, client, registered_user):
        resp = client.post("/auth/register", json={"email": "other@e.com", "username": registered_user["username"], "password": "password123"})
        assert resp.status_code == 409

    def test_invalid_email_returns_422(self, client):
        resp = client.post("/auth/register", json={"email": "bad", "username": "user1", "password": "password123"})
        assert resp.status_code == 422

    def test_short_password_returns_400(self, client):
        resp = client.post("/auth/register", json={"email": "u@e.com", "username": "user1", "password": "short"})
        assert resp.status_code == 400

class TestLogin:
    def test_login_success(self, client, registered_user):
        resp = client.post("/auth/login", json={"email": registered_user["email"], "password": registered_user["password"]})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_wrong_password_returns_401(self, client, registered_user):
        resp = client.post("/auth/login", json={"email": registered_user["email"], "password": "wrong"})
        assert resp.status_code == 401

class TestMe:
    def test_me_returns_profile(self, client, registered_user, auth_headers):
        resp = client.get("/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == registered_user["email"]

    def test_me_without_token_returns_403(self, client):
        assert client.get("/auth/me").status_code == 403

    def test_me_invalid_token_returns_401(self, client):
        assert client.get("/auth/me", headers={"Authorization": "Bearer bad.token"}).status_code == 401
