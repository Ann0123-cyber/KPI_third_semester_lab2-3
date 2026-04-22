"""
Integration tests — projects CRUD endpoints.
"""


class TestCreateProject:
    def test_create_success(self, client, auth_headers):
        resp = client.post("/projects/", json={"name": "Alpha"}, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["name"] == "Alpha"

    def test_create_without_auth_returns_403(self, client):
        resp = client.post("/projects/", json={"name": "Alpha"})
        assert resp.status_code == 403

    def test_duplicate_name_returns_409(self, client, auth_headers):
        client.post("/projects/", json={"name": "Alpha"}, headers=auth_headers)
        resp = client.post("/projects/", json={"name": "Alpha"}, headers=auth_headers)
        assert resp.status_code == 409

    def test_empty_name_returns_422(self, client, auth_headers):
        resp = client.post("/projects/", json={"name": "  "}, headers=auth_headers)
        assert resp.status_code == 422


class TestListProjects:
    def test_list_returns_own_projects_only(self, client, auth_headers):
        client.post("/projects/", json={"name": "P1"}, headers=auth_headers)
        client.post("/projects/", json={"name": "P2"}, headers=auth_headers)
        resp = client.get("/projects/", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_other_users_projects_not_visible(self, client, auth_headers):
        client.post("/projects/", json={"name": "P1"}, headers=auth_headers)

        client.post("/auth/register", json={
            "email": "bob@example.com", "username": "bob", "password": "secret123"
        })
        bob_token = client.post("/auth/login", json={
            "email": "bob@example.com", "password": "secret123"
        }).json()["access_token"]
        bob_headers = {"Authorization": f"Bearer {bob_token}"}

        resp = client.get("/projects/", headers=bob_headers)
        assert resp.json() == []


class TestGetProject:
    def test_get_existing_project(self, client, auth_headers, project):
        resp = client.get(f"/projects/{project['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == project["name"]

    def test_get_nonexistent_returns_404(self, client, auth_headers):
        resp = client.get("/projects/9999", headers=auth_headers)
        assert resp.status_code == 404


class TestUpdateProject:
    def test_update_name(self, client, auth_headers, project):
        resp = client.patch(
            f"/projects/{project['id']}", json={"name": "Renamed"}, headers=auth_headers
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Renamed"

    def test_rename_to_existing_name_returns_409(self, client, auth_headers):
        p1 = client.post("/projects/", json={"name": "P1"}, headers=auth_headers).json()
        client.post("/projects/", json={"name": "P2"}, headers=auth_headers)
        resp = client.patch(f"/projects/{p1['id']}", json={"name": "P2"}, headers=auth_headers)
        assert resp.status_code == 409


class TestDeleteProject:
    def test_delete_existing(self, client, auth_headers, project):
        resp = client.delete(f"/projects/{project['id']}", headers=auth_headers)
        assert resp.status_code == 204
        assert client.get(f"/projects/{project['id']}", headers=auth_headers).status_code == 404

    def test_delete_nonexistent_returns_404(self, client, auth_headers):
        resp = client.delete("/projects/9999", headers=auth_headers)
        assert resp.status_code == 404
