"""
Unit-тести фабрик — перевіряємо інваріанти.
Fake репозиторії замість БД.
"""
from datetime import datetime, timedelta, timezone

import pytest

from app.domain.errors import (
    EmailAlreadyExistsError, UsernameAlreadyExistsError,
    DuplicateProjectNameError, AssigneeNotFoundError,
    DueDateInPastError, InvalidEmailError, InvalidUsernameError, DomainError,
)
from app.domain.factories.project_factory import ProjectFactory
from app.domain.factories.task_factory import TaskFactory
from app.domain.factories.user_factory import UserFactory
from app.domain.models.task import TaskPriority
from app.domain.value_objects.email import Email
from app.domain.value_objects.username import Username
from tests.unit.domain.fake_repositories import FakeUserRepository, FakeProjectRepository


def fake_hasher(password: str) -> str:
    return f"hashed:{password}"


# ── UserFactory ───────────────────────────────────────────────────────────────

class TestUserFactory:
    def setup_method(self):
        self.repo = FakeUserRepository()
        self.factory = UserFactory(self.repo, fake_hasher)

    def test_creates_user_with_hashed_password(self):
        user = self.factory.create("alice@example.com", "alice", "password123")
        assert user.hashed_password == "hashed:password123"
        assert str(user.email) == "alice@example.com"
        assert str(user.username) == "alice"

    def test_invalid_email_raises_domain_error(self):
        with pytest.raises(InvalidEmailError):
            self.factory.create("bad-email", "alice", "password123")

    def test_invalid_username_raises_domain_error(self):
        with pytest.raises(InvalidUsernameError):
            self.factory.create("alice@example.com", "a!", "password123")

    def test_short_password_raises_domain_error(self):
        with pytest.raises(DomainError, match="8 characters"):
            self.factory.create("alice@example.com", "alice", "short")

    def test_duplicate_email_raises_error(self):
        # factory only creates, use case saves — simulate by saving directly
        user = self.factory.create("alice@example.com", "alice", "password123")
        self.repo.save(user)
        with pytest.raises(EmailAlreadyExistsError):
            self.factory.create("alice@example.com", "other", "password123")

    def test_duplicate_username_raises_error(self):
        user = self.factory.create("alice@example.com", "alice", "password123")
        self.repo.save(user)
        with pytest.raises(UsernameAlreadyExistsError):
            self.factory.create("other@example.com", "alice", "password123")


# ── ProjectFactory ────────────────────────────────────────────────────────────

class TestProjectFactory:
    def setup_method(self):
        self.repo = FakeProjectRepository()
        self.factory = ProjectFactory(self.repo)

    def test_creates_project(self):
        p = self.factory.create("My Project", owner_id=1)
        assert p.name == "My Project"
        assert p.owner_id == 1

    def test_empty_name_raises_error(self):
        with pytest.raises(DomainError, match="empty"):
            self.factory.create("  ", owner_id=1)

    def test_name_too_long_raises_error(self):
        with pytest.raises(DomainError, match="128"):
            self.factory.create("x" * 129, owner_id=1)

    def test_duplicate_name_same_owner_raises_error(self):
        p = self.factory.create("Alpha", owner_id=1)
        self.repo.save(p)
        with pytest.raises(DuplicateProjectNameError):
            self.factory.create("Alpha", owner_id=1)

    def test_same_name_different_owner_is_allowed(self):
        p = self.factory.create("Alpha", owner_id=1)
        self.repo.save(p)
        p2 = self.factory.create("Alpha", owner_id=2)  # no error
        assert p2.name == "Alpha"


# ── TaskFactory ───────────────────────────────────────────────────────────────

class TestTaskFactory:
    def setup_method(self):
        self.user_repo = FakeUserRepository()
        self.factory = TaskFactory(self.user_repo)

    def _future(self, days=1):
        return datetime.now(timezone.utc) + timedelta(days=days)

    def _past(self, days=1):
        return datetime.now(timezone.utc) - timedelta(days=days)

    def test_creates_task(self):
        t = self.factory.create("Write tests", project_id=1)
        assert t.title == "Write tests"
        assert t.project_id == 1

    def test_empty_title_raises_error(self):
        with pytest.raises(DomainError, match="empty"):
            self.factory.create("  ", project_id=1)

    def test_title_too_long_raises_error(self):
        with pytest.raises(DomainError, match="256"):
            self.factory.create("x" * 257, project_id=1)

    def test_past_due_date_raises_error(self):
        with pytest.raises(DueDateInPastError):
            self.factory.create("Task", project_id=1, due_date=self._past())

    def test_future_due_date_ok(self):
        t = self.factory.create("Task", project_id=1, due_date=self._future())
        assert t.due_date is not None

    def test_nonexistent_assignee_raises_error(self):
        with pytest.raises(AssigneeNotFoundError):
            self.factory.create("Task", project_id=1, assignee_id=999)

    def test_existing_assignee_ok(self):
        from app.domain.models.user import User
        user = User(email=Email("a@b.com"), username=Username("bob"), hashed_password="x", id=1)
        self.user_repo.save(user)
        t = self.factory.create("Task", project_id=1, assignee_id=1)
        assert t.assignee_id == 1
