"""
Unit-тести Rich Domain Model Task.
Тестуємо поведінку (transition_to) — жодної БД.
"""
import pytest
from app.domain.models.task import Task, TaskStatus, TaskPriority
from app.domain.errors import InvalidStatusTransitionError


def make_task(**kwargs) -> Task:
    defaults = dict(title="Do something", project_id=1)
    return Task(**{**defaults, **kwargs})


class TestTaskTransitions:
    def test_todo_to_in_progress(self):
        task = make_task()
        task.transition_to(TaskStatus.IN_PROGRESS)
        assert task.status == TaskStatus.IN_PROGRESS

    def test_todo_to_cancelled(self):
        task = make_task()
        task.transition_to(TaskStatus.CANCELLED)
        assert task.status == TaskStatus.CANCELLED

    def test_todo_to_done_raises(self):
        task = make_task()
        with pytest.raises(InvalidStatusTransitionError) as exc:
            task.transition_to(TaskStatus.DONE)
        assert "todo" in exc.value.message
        assert "done" in exc.value.message

    def test_in_progress_to_done(self):
        task = make_task(status=TaskStatus.IN_PROGRESS)
        task.transition_to(TaskStatus.DONE)
        assert task.status == TaskStatus.DONE

    def test_in_progress_to_todo(self):
        task = make_task(status=TaskStatus.IN_PROGRESS)
        task.transition_to(TaskStatus.TODO)
        assert task.status == TaskStatus.TODO

    def test_done_to_todo_reopen(self):
        task = make_task(status=TaskStatus.DONE)
        task.transition_to(TaskStatus.TODO)
        assert task.status == TaskStatus.TODO

    def test_done_to_in_progress_raises(self):
        task = make_task(status=TaskStatus.DONE)
        with pytest.raises(InvalidStatusTransitionError):
            task.transition_to(TaskStatus.IN_PROGRESS)

    def test_cancelled_to_todo(self):
        task = make_task(status=TaskStatus.CANCELLED)
        task.transition_to(TaskStatus.TODO)
        assert task.status == TaskStatus.TODO

    def test_cancelled_to_done_raises(self):
        task = make_task(status=TaskStatus.CANCELLED)
        with pytest.raises(InvalidStatusTransitionError):
            task.transition_to(TaskStatus.DONE)


class TestTaskUpdateDetails:
    def test_update_title(self):
        task = make_task(title="Old")
        task.update_details(title="New")
        assert task.title == "New"

    def test_update_priority(self):
        task = make_task()
        task.update_details(priority=TaskPriority.CRITICAL)
        assert task.priority == TaskPriority.CRITICAL

    def test_partial_update_leaves_other_fields(self):
        task = make_task(title="Keep", priority=TaskPriority.HIGH)
        task.update_details(title="Changed")
        assert task.priority == TaskPriority.HIGH

    def test_assign_to(self):
        task = make_task()
        task.assign_to(42)
        assert task.assignee_id == 42
