"""
Integration tests — tasks CRUD endpoints + status transition invariant.
"""
from datetime import datetime, timedelta, timezone


def future_date(days=1):
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def past_date(days=1):
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


class TestCreateTask:
    def test_create_success(self, client, auth_headers, project):
        resp = client.post(
            f"/projects/{project['id']}/tasks/",
            json={"title": "Write tests", "priority": "high"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "Write tests"
        assert body["status"] == "todo"

    def test_create_with_future_due_date(self, client, auth_headers, project):
        resp = client.post(
            f"/projects/{project['id']}/tasks/",
            json={"title": "Task", "due_date": future_date(3)},
            headers=auth_headers,
        )
        assert resp.status_code == 201

    def test_past_due_date_returns_422(self, client, auth_headers, project):
        resp = client.post(
            f"/projects/{project['id']}/tasks/",
            json={"title": "Task", "due_date": past_date(1)},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_empty_title_returns_422(self, client, auth_headers, project):
        resp = client.post(
            f"/projects/{project['id']}/tasks/",
            json={"title": "  "},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_nonexistent_project_returns_404(self, client, auth_headers):
        resp = client.post(
            "/projects/9999/tasks/",
            json={"title": "Task"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_without_auth_returns_403(self, client, project):
        resp = client.post(f"/projects/{project['id']}/tasks/", json={"title": "Task"})
        assert resp.status_code == 403


class TestListTasks:
    def test_list_tasks(self, client, auth_headers, project):
        client.post(f"/projects/{project['id']}/tasks/", json={"title": "T1"}, headers=auth_headers)
        client.post(f"/projects/{project['id']}/tasks/", json={"title": "T2"}, headers=auth_headers)
        resp = client.get(f"/projects/{project['id']}/tasks/", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestGetTask:
    def test_get_existing_task(self, client, auth_headers, project):
        task = client.post(
            f"/projects/{project['id']}/tasks/", json={"title": "T1"}, headers=auth_headers
        ).json()
        resp = client.get(f"/projects/{project['id']}/tasks/{task['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == task["id"]

    def test_get_nonexistent_task_returns_404(self, client, auth_headers, project):
        resp = client.get(f"/projects/{project['id']}/tasks/9999", headers=auth_headers)
        assert resp.status_code == 404


class TestStatusTransitions:
    def _create_task(self, client, auth_headers, project):
        return client.post(
            f"/projects/{project['id']}/tasks/",
            json={"title": "Status task"},
            headers=auth_headers,
        ).json()

    def test_todo_to_in_progress(self, client, auth_headers, project):
        task = self._create_task(client, auth_headers, project)
        resp = client.patch(
            f"/projects/{project['id']}/tasks/{task['id']}",
            json={"status": "in_progress"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "in_progress"

    def test_todo_to_done_directly_returns_400(self, client, auth_headers, project):
        task = self._create_task(client, auth_headers, project)
        resp = client.patch(
            f"/projects/{project['id']}/tasks/{task['id']}",
            json={"status": "done"},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "Cannot transition" in resp.json()["detail"]

    def test_in_progress_to_done(self, client, auth_headers, project):
        task = self._create_task(client, auth_headers, project)
        client.patch(
            f"/projects/{project['id']}/tasks/{task['id']}",
            json={"status": "in_progress"},
            headers=auth_headers,
        )
        resp = client.patch(
            f"/projects/{project['id']}/tasks/{task['id']}",
            json={"status": "done"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "done"

    def test_done_to_todo_reopen(self, client, auth_headers, project):
        task = self._create_task(client, auth_headers, project)
        client.patch(f"/projects/{project['id']}/tasks/{task['id']}", json={"status": "in_progress"}, headers=auth_headers)
        client.patch(f"/projects/{project['id']}/tasks/{task['id']}", json={"status": "done"}, headers=auth_headers)
        resp = client.patch(
            f"/projects/{project['id']}/tasks/{task['id']}",
            json={"status": "todo"},
            headers=auth_headers,
        )
        assert resp.status_code == 200


class TestDeleteTask:
    def test_delete_task(self, client, auth_headers, project):
        task = client.post(
            f"/projects/{project['id']}/tasks/", json={"title": "To delete"}, headers=auth_headers
        ).json()
        resp = client.delete(f"/projects/{project['id']}/tasks/{task['id']}", headers=auth_headers)
        assert resp.status_code == 204

    def test_delete_nonexistent_returns_404(self, client, auth_headers, project):
        resp = client.delete(f"/projects/{project['id']}/tasks/9999", headers=auth_headers)
        assert resp.status_code == 404
