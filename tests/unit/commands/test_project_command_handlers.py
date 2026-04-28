"""
Unit-тести Command Handlers — без БД, без HTTP.
Fake репозиторії замість SQL.
"""
import pytest
from app.application.commands.projects.create_project_command import CreateProjectCommand
from app.application.commands.projects.update_project_command import UpdateProjectCommand
from app.application.commands.projects.delete_project_command import DeleteProjectCommand
from app.application.handlers.command_handlers.projects.create_project_handler import CreateProjectHandler
from app.application.handlers.command_handlers.projects.update_project_handler import UpdateProjectHandler
from app.application.handlers.command_handlers.projects.delete_project_handler import DeleteProjectHandler
from app.domain.errors import ProjectNotFoundError, DuplicateProjectNameError, DomainError
from tests.unit.domain.fake_repositories import FakeProjectRepository


class TestCreateProjectHandler:
    def setup_method(self):
        self.repo = FakeProjectRepository()
        self.handler = CreateProjectHandler(self.repo)

    def test_returns_id(self):
        project_id = self.handler.handle(CreateProjectCommand(name="Alpha", owner_id=1))
        assert isinstance(project_id, int)
        assert project_id > 0

    def test_command_returns_only_id_not_full_object(self):
        result = self.handler.handle(CreateProjectCommand(name="Alpha", owner_id=1))
        # команда повертає лише int — не ProjectReadModel, не доменну модель
        assert type(result) is int

    def test_duplicate_name_raises(self):
        self.handler.handle(CreateProjectCommand(name="Alpha", owner_id=1))
        with pytest.raises(DuplicateProjectNameError):
            self.handler.handle(CreateProjectCommand(name="Alpha", owner_id=1))

    def test_same_name_different_owner_ok(self):
        self.handler.handle(CreateProjectCommand(name="Alpha", owner_id=1))
        pid = self.handler.handle(CreateProjectCommand(name="Alpha", owner_id=2))
        assert pid > 0

    def test_empty_name_raises(self):
        with pytest.raises(DomainError):
            self.handler.handle(CreateProjectCommand(name="  ", owner_id=1))


class TestUpdateProjectHandler:
    def setup_method(self):
        self.repo = FakeProjectRepository()
        create = CreateProjectHandler(self.repo)
        self.project_id = create.handle(CreateProjectCommand(name="Alpha", owner_id=1))
        self.handler = UpdateProjectHandler(self.repo)

    def test_update_returns_none(self):
        result = self.handler.handle(UpdateProjectCommand(project_id=self.project_id, owner_id=1, name="Beta"))
        assert result is None  # команда нічого не повертає

    def test_name_updated(self):
        self.handler.handle(UpdateProjectCommand(project_id=self.project_id, owner_id=1, name="Beta"))
        project = self.repo.get_by_id(self.project_id)
        assert project.name == "Beta"

    def test_wrong_owner_raises(self):
        with pytest.raises(ProjectNotFoundError):
            self.handler.handle(UpdateProjectCommand(project_id=self.project_id, owner_id=99, name="Beta"))

    def test_duplicate_name_raises(self):
        CreateProjectHandler(self.repo).handle(CreateProjectCommand(name="Beta", owner_id=1))
        with pytest.raises(DuplicateProjectNameError):
            self.handler.handle(UpdateProjectCommand(project_id=self.project_id, owner_id=1, name="Beta"))


class TestDeleteProjectHandler:
    def test_delete_returns_none(self):
        repo = FakeProjectRepository()
        pid = CreateProjectHandler(repo).handle(CreateProjectCommand(name="Alpha", owner_id=1))
        result = DeleteProjectHandler(repo).handle(DeleteProjectCommand(project_id=pid, owner_id=1))
        assert result is None

    def test_deleted_project_gone(self):
        repo = FakeProjectRepository()
        pid = CreateProjectHandler(repo).handle(CreateProjectCommand(name="Alpha", owner_id=1))
        DeleteProjectHandler(repo).handle(DeleteProjectCommand(project_id=pid, owner_id=1))
        assert repo.get_by_id(pid) is None

    def test_wrong_owner_raises(self):
        repo = FakeProjectRepository()
        pid = CreateProjectHandler(repo).handle(CreateProjectCommand(name="Alpha", owner_id=1))
        with pytest.raises(ProjectNotFoundError):
            DeleteProjectHandler(repo).handle(DeleteProjectCommand(project_id=pid, owner_id=99))
