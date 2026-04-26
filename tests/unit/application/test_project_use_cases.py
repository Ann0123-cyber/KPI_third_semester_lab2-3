"""
Unit-тести Application Layer (Use Cases).
Репозиторії замінені fake-реалізаціями — БД не потрібна.
"""
import pytest
from app.application.use_cases.projects.create_project import CreateProjectUseCase, CreateProjectCommand
from app.application.use_cases.projects.list_projects import ListProjectsUseCase
from app.application.use_cases.projects.get_project import GetProjectUseCase
from app.application.use_cases.projects.update_project import UpdateProjectUseCase, UpdateProjectCommand
from app.application.use_cases.projects.delete_project import DeleteProjectUseCase, DeleteProjectCommand
from app.domain.errors import ProjectNotFoundError, DuplicateProjectNameError, DomainError
from tests.unit.domain.fake_repositories import FakeProjectRepository


class TestCreateProjectUseCase:
    def setup_method(self):
        self.repo = FakeProjectRepository()
        self.uc = CreateProjectUseCase(self.repo)

    def test_creates_and_persists_project(self):
        p = self.uc.execute(CreateProjectCommand(name="Alpha", owner_id=1))
        assert p.id is not None
        assert p.name == "Alpha"
        assert p.owner_id == 1

    def test_duplicate_name_raises(self):
        self.uc.execute(CreateProjectCommand(name="Alpha", owner_id=1))
        with pytest.raises(DuplicateProjectNameError):
            self.uc.execute(CreateProjectCommand(name="Alpha", owner_id=1))

    def test_same_name_different_owner_ok(self):
        self.uc.execute(CreateProjectCommand(name="Alpha", owner_id=1))
        p = self.uc.execute(CreateProjectCommand(name="Alpha", owner_id=2))
        assert p.id is not None


class TestListProjectsUseCase:
    def test_returns_only_owner_projects(self):
        repo = FakeProjectRepository()
        uc = CreateProjectUseCase(repo)
        uc.execute(CreateProjectCommand(name="P1", owner_id=1))
        uc.execute(CreateProjectCommand(name="P2", owner_id=1))
        uc.execute(CreateProjectCommand(name="P3", owner_id=2))
        result = ListProjectsUseCase(repo).execute(owner_id=1)
        assert len(result) == 2
        assert all(p.owner_id == 1 for p in result)


class TestGetProjectUseCase:
    def setup_method(self):
        self.repo = FakeProjectRepository()
        create = CreateProjectUseCase(self.repo)
        self.project = create.execute(CreateProjectCommand(name="Alpha", owner_id=1))
        self.uc = GetProjectUseCase(self.repo)

    def test_returns_project_for_owner(self):
        p = self.uc.execute(self.project.id, owner_id=1)
        assert p.name == "Alpha"

    def test_wrong_owner_raises_not_found(self):
        with pytest.raises(ProjectNotFoundError):
            self.uc.execute(self.project.id, owner_id=99)

    def test_nonexistent_id_raises_not_found(self):
        with pytest.raises(ProjectNotFoundError):
            self.uc.execute(9999, owner_id=1)


class TestUpdateProjectUseCase:
    def setup_method(self):
        self.repo = FakeProjectRepository()
        create = CreateProjectUseCase(self.repo)
        self.project = create.execute(CreateProjectCommand(name="Alpha", owner_id=1))
        self.uc = UpdateProjectUseCase(self.repo)

    def test_updates_name(self):
        p = self.uc.execute(UpdateProjectCommand(project_id=self.project.id, owner_id=1, name="Beta"))
        assert p.name == "Beta"

    def test_empty_name_raises(self):
        with pytest.raises(DomainError):
            self.uc.execute(UpdateProjectCommand(project_id=self.project.id, owner_id=1, name="  "))

    def test_rename_to_existing_name_raises(self):
        create = CreateProjectUseCase(self.repo)
        create.execute(CreateProjectCommand(name="Beta", owner_id=1))
        with pytest.raises(DuplicateProjectNameError):
            self.uc.execute(UpdateProjectCommand(project_id=self.project.id, owner_id=1, name="Beta"))


class TestDeleteProjectUseCase:
    def test_deletes_existing(self):
        repo = FakeProjectRepository()
        p = CreateProjectUseCase(repo).execute(CreateProjectCommand(name="Alpha", owner_id=1))
        DeleteProjectUseCase(repo).execute(DeleteProjectCommand(project_id=p.id, owner_id=1))
        assert repo.get_by_id(p.id) is None

    def test_wrong_owner_raises(self):
        repo = FakeProjectRepository()
        p = CreateProjectUseCase(repo).execute(CreateProjectCommand(name="Alpha", owner_id=1))
        with pytest.raises(ProjectNotFoundError):
            DeleteProjectUseCase(repo).execute(DeleteProjectCommand(project_id=p.id, owner_id=99))
