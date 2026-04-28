"""Unit-тести Task Command Handlers — без БД."""
import pytest
from app.application.commands.projects.create_project_command import CreateProjectCommand
from app.application.commands.tasks.create_task_command import CreateTaskCommand
from app.application.commands.tasks.update_task_command import UpdateTaskCommand
from app.application.commands.tasks.delete_task_command import DeleteTaskCommand
from app.application.handlers.command_handlers.projects.create_project_handler import CreateProjectHandler
from app.application.handlers.command_handlers.tasks.create_task_handler import CreateTaskHandler
from app.application.handlers.command_handlers.tasks.update_task_handler import UpdateTaskHandler
from app.application.handlers.command_handlers.tasks.delete_task_handler import DeleteTaskHandler
from app.domain.errors import ProjectNotFoundError, TaskNotFoundError, InvalidStatusTransitionError
from app.domain.models.task import TaskStatus
from tests.unit.domain.fake_repositories import FakeProjectRepository, FakeTaskRepository, FakeUserRepository


def make_repos():
    pr = FakeProjectRepository()
    tr = FakeTaskRepository()
    ur = FakeUserRepository()
    pid = CreateProjectHandler(pr).handle(CreateProjectCommand(name="P1", owner_id=1))
    return pr, tr, ur, pid


class TestCreateTaskHandler:
    def test_returns_id(self):
        pr, tr, ur, pid = make_repos()
        task_id = CreateTaskHandler(tr, pr, ur).handle(
            CreateTaskCommand(title="T1", project_id=pid, owner_id=1))
        assert type(task_id) is int

    def test_wrong_owner_raises(self):
        pr, tr, ur, pid = make_repos()
        with pytest.raises(ProjectNotFoundError):
            CreateTaskHandler(tr, pr, ur).handle(
                CreateTaskCommand(title="T1", project_id=pid, owner_id=99))


class TestUpdateTaskHandler:
    def setup_method(self):
        self.pr, self.tr, self.ur, self.pid = make_repos()
        self.task_id = CreateTaskHandler(self.tr, self.pr, self.ur).handle(
            CreateTaskCommand(title="T1", project_id=self.pid, owner_id=1))
        self.handler = UpdateTaskHandler(self.tr, self.pr, self.ur)

    def test_update_returns_none(self):
        result = self.handler.handle(UpdateTaskCommand(
            project_id=self.pid, task_id=self.task_id, owner_id=1, status=TaskStatus.IN_PROGRESS))
        assert result is None

    def test_valid_status_transition(self):
        self.handler.handle(UpdateTaskCommand(
            project_id=self.pid, task_id=self.task_id, owner_id=1, status=TaskStatus.IN_PROGRESS))
        task = self.tr.get_by_id(self.task_id)
        assert task.status == TaskStatus.IN_PROGRESS

    def test_invalid_transition_raises(self):
        with pytest.raises(InvalidStatusTransitionError):
            self.handler.handle(UpdateTaskCommand(
                project_id=self.pid, task_id=self.task_id, owner_id=1, status=TaskStatus.DONE))

    def test_nonexistent_task_raises(self):
        with pytest.raises(TaskNotFoundError):
            self.handler.handle(UpdateTaskCommand(
                project_id=self.pid, task_id=9999, owner_id=1))


class TestDeleteTaskHandler:
    def test_delete_returns_none(self):
        pr, tr, ur, pid = make_repos()
        tid = CreateTaskHandler(tr, pr, ur).handle(CreateTaskCommand(title="T", project_id=pid, owner_id=1))
        result = DeleteTaskHandler(tr, pr).handle(DeleteTaskCommand(project_id=pid, task_id=tid, owner_id=1))
        assert result is None
        assert tr.get_by_id(tid) is None

    def test_nonexistent_raises(self):
        pr, tr, ur, pid = make_repos()
        with pytest.raises(TaskNotFoundError):
            DeleteTaskHandler(tr, pr).handle(DeleteTaskCommand(project_id=pid, task_id=9999, owner_id=1))

