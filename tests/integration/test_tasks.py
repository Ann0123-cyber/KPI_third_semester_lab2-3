from datetime import datetime, timedelta, timezone

def future_date(days=1):
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()

def past_date(days=1):
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

class TestCreateTask:
    def test_create_success(self, client, auth_headers, project):
        resp = client.post(f"/projects/{project['id']}/tasks/", json={"title": "T1"}, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["status"] == "todo"

    def test_past_due_date_returns_422(self, client, auth_headers, project):
        resp = client.post(f"/projects/{project['id']}/tasks/", json={"title": "T", "due_date": past_date()}, headers=auth_headers)
        assert resp.status_code == 422

    def test_empty_title_returns_422(self, client, auth_headers, project):
        assert client.post(f"/projects/{project['id']}/tasks/", json={"title": "  "}, headers=auth_headers).status_code == 422

    def test_nonexistent_project_returns_404(self, client, auth_headers):
        assert client.post("/projects/9999/tasks/", json={"title": "T"}, headers=auth_headers).status_code == 404

class TestStatusTransitions:
    def _make_task(self, client, auth_headers, project):
        return client.post(f"/projects/{project['id']}/tasks/", json={"title": "T"}, headers=auth_headers).json()

    def test_todo_to_in_progress(self, client, auth_headers, project):
        task = self._make_task(client, auth_headers, project)
        resp = client.patch(f"/projects/{project['id']}/tasks/{task['id']}", json={"status": "in_progress"}, headers=auth_headers)
        assert resp.json()["status"] == "in_progress"

    def test_todo_to_done_directly_returns_400(self, client, auth_headers, project):
        task = self._make_task(client, auth_headers, project)
        resp = client.patch(f"/projects/{project['id']}/tasks/{task['id']}", json={"status": "done"}, headers=auth_headers)
        assert resp.status_code == 400
        assert "Cannot transition" in resp.json()["detail"]

    def test_in_progress_to_done(self, client, auth_headers, project):
        task = self._make_task(client, auth_headers, project)
        client.patch(f"/projects/{project['id']}/tasks/{task['id']}", json={"status": "in_progress"}, headers=auth_headers)
        resp = client.patch(f"/projects/{project['id']}/tasks/{task['id']}", json={"status": "done"}, headers=auth_headers)
        assert resp.json()["status"] == "done"

class TestDeleteTask:
    def test_delete_task(self, client, auth_headers, project):
        task = client.post(f"/projects/{project['id']}/tasks/", json={"title": "T"}, headers=auth_headers).json()
        assert client.delete(f"/projects/{project['id']}/tasks/{task['id']}", headers=auth_headers).status_code == 204

    def test_delete_nonexistent_returns_404(self, client, auth_headers, project):
        assert client.delete(f"/projects/{project['id']}/tasks/9999", headers=auth_headers).status_code == 404
