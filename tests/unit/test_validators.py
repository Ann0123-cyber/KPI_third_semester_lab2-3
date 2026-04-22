"""
Unit tests — перевіряють валідацію та бізнес-правила без звернення до БД чи фреймворку.
"""
from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.schemas.task import TaskCreate, TaskUpdate
from app.models.task import TaskStatus, ALLOWED_TRANSITIONS
from app.services.auth_service import hash_password, verify_password


# ─── Password hashing ──────────────────────────────────────────────────────────

class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = hash_password("mypassword")
        assert hashed != "mypassword"

    def test_correct_password_verifies(self):
        hashed = hash_password("correct")
        assert verify_password("correct", hashed) is True

    def test_wrong_password_fails(self):
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False


# ─── UserCreate validation ─────────────────────────────────────────────────────

class TestUserCreateSchema:
    def test_valid_user(self):
        u = UserCreate(email="bob@example.com", username="bob_99", password="strongpass")
        assert u.email == "bob@example.com"

    def test_invalid_email(self):
        with pytest.raises(ValidationError, match="email"):
            UserCreate(email="not-an-email", username="bob", password="strongpass")

    def test_short_password(self):
        with pytest.raises(ValidationError, match="8 characters"):
            UserCreate(email="bob@example.com", username="bob", password="short")

    def test_invalid_username_special_chars(self):
        with pytest.raises(ValidationError):
            UserCreate(email="bob@example.com", username="bo b!", password="strongpass")

    def test_username_too_short(self):
        with pytest.raises(ValidationError):
            UserCreate(email="bob@example.com", username="bo", password="strongpass")


# ─── ProjectCreate validation ──────────────────────────────────────────────────

class TestProjectSchema:
    def test_valid_project(self):
        p = ProjectCreate(name="My Project")
        assert p.name == "My Project"

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError, match="empty"):
            ProjectCreate(name="   ")

    def test_name_too_long(self):
        with pytest.raises(ValidationError, match="128"):
            ProjectCreate(name="x" * 129)

    def test_update_none_name_allowed(self):
        p = ProjectUpdate(name=None)
        assert p.name is None

    def test_update_empty_name_rejected(self):
        with pytest.raises(ValidationError, match="empty"):
            ProjectUpdate(name="  ")


# ─── TaskCreate validation ─────────────────────────────────────────────────────

class TestTaskSchema:
    def _future(self, days=1):
        return datetime.now(timezone.utc) + timedelta(days=days)

    def _past(self, days=1):
        return datetime.now(timezone.utc) - timedelta(days=days)

    def test_valid_task(self):
        t = TaskCreate(title="Do something", due_date=self._future())
        assert t.title == "Do something"

    def test_empty_title_rejected(self):
        with pytest.raises(ValidationError, match="empty"):
            TaskCreate(title="  ")

    def test_title_too_long(self):
        with pytest.raises(ValidationError, match="256"):
            TaskCreate(title="a" * 257)

    def test_past_due_date_rejected(self):
        with pytest.raises(ValidationError, match="future"):
            TaskCreate(title="Task", due_date=self._past())

    def test_no_due_date_allowed(self):
        t = TaskCreate(title="Task")
        assert t.due_date is None


# ─── Status transition invariant ───────────────────────────────────────────────

class TestStatusTransitions:
    def test_todo_can_go_to_in_progress(self):
        assert TaskStatus.IN_PROGRESS in ALLOWED_TRANSITIONS[TaskStatus.TODO]

    def test_todo_cannot_go_to_done_directly(self):
        assert TaskStatus.DONE not in ALLOWED_TRANSITIONS[TaskStatus.TODO]

    def test_in_progress_can_go_to_done(self):
        assert TaskStatus.DONE in ALLOWED_TRANSITIONS[TaskStatus.IN_PROGRESS]

    def test_done_can_be_reopened(self):
        assert TaskStatus.TODO in ALLOWED_TRANSITIONS[TaskStatus.DONE]

    def test_cancelled_can_be_reopened(self):
        assert TaskStatus.TODO in ALLOWED_TRANSITIONS[TaskStatus.CANCELLED]

    def test_all_statuses_have_transitions_defined(self):
        for status in TaskStatus:
            assert status in ALLOWED_TRANSITIONS
