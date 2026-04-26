"""Unit-тести use cases для задач."""
import pytest
from app.application.use_cases.projects.create_project import CreateProjectUseCase, CreateProjectCommand
from app.application.use_cases.tasks.create_task import CreateTaskUseCase, CreateTaskCommand
from app.application.use_cases.tasks.update_task import UpdateTaskUseCase, UpdateTaskCommand
from app.application.use_cases.tasks.delete_task import DeleteTaskUseCase, DeleteTaskCommand
from app.domain.errors import (
    ProjectNotFoundError, TaskNotFoundError, InvalidStatusTransitionError
)
from app.domain.models.task import TaskStatus
from tests.unit.domain.fake_repositories import FakeProjectRepository, FakeTaskRepository, FakeUserRepository


def setup_repos():
    project_repo = FakeProjectRepository()
    task_repo = FakeTaskRepository()
    user_repo = FakeUserRepository()
    project = CreateProjectUseCase(project_repo).execute(CreateProjectCommand(name="P1", owner_id=1))
    return project_repo, task_repo, user_repo, project


class TestCreateTaskUseCase:
    def test_creates_task_in_existing_project(self):
        project_repo, task_repo, user_repo, project = setup_repos()
        uc = CreateTaskUseCase(task_repo, project_repo, user_repo)
        task = uc.execute(CreateTaskCommand(title="T1", project_id=project.id, owner_id=1))
        assert task.id is not None
        assert task.status == TaskStatus.TODO

    def test_wrong_owner_raises_not_found(self):
        project_repo, task_repo, user_repo, project = setup_repos()
        uc = CreateTaskUseCase(task_repo, project_repo, user_repo)
        with pytest.raises(ProjectNotFoundError):
            uc.execute(CreateTaskCommand(title="T1", project_id=project.id, owner_id=99))


class TestUpdateTaskStatusUseCase:
    def setup_method(self):
        self.project_repo, self.task_repo, self.user_repo, self.project = setup_repos()
        uc = CreateTaskUseCase(self.task_repo, self.project_repo, self.user_repo)
        self.task = uc.execute(CreateTaskCommand(title="T1", project_id=self.project.id, owner_id=1))
        self.update_uc = UpdateTaskUseCase(self.task_repo, self.project_repo, self.user_repo)

    def test_todo_to_in_progress(self):
        t = self.update_uc.execute(UpdateTaskCommand(
            project_id=self.project.id, task_id=self.task.id, owner_id=1,
            status=TaskStatus.IN_PROGRESS,
        ))
        assert t.status == TaskStatus.IN_PROGRESS

    def test_invalid_transition_raises_domain_error(self):
        with pytest.raises(InvalidStatusTransitionError):
            self.update_uc.execute(UpdateTaskCommand(
                project_id=self.project.id, task_id=self.task.id, owner_id=1,
                status=TaskStatus.DONE,  # todo → done is forbidden
            ))

    def test_nonexistent_task_raises(self):
        with pytest.raises(TaskNotFoundError):
            self.update_uc.execute(UpdateTaskCommand(
                project_id=self.project.id, task_id=9999, owner_id=1,
            ))


class TestDeleteTaskUseCase:
    def test_deletes_task(self):
        project_repo, task_repo, user_repo, project = setup_repos()
        task = CreateTaskUseCase(task_repo, project_repo, user_repo).execute(
            CreateTaskCommand(title="T1", project_id=project.id, owner_id=1)
        )
        DeleteTaskUseCase(task_repo, project_repo).execute(
            DeleteTaskCommand(project_id=project.id, task_id=task.id, owner_id=1)
        )
        assert task_repo.get_by_id(task.id) is None
