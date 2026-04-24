"""
Domain errors — не знають про HTTP, фреймворки, ORM.
Presentation layer відображає їх у HTTP-статуси.
"""


class DomainError(Exception):
    """Базовий клас для всіх доменних помилок."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


# ── Auth ──────────────────────────────────────────────────────────────────────

class EmailAlreadyExistsError(DomainError):
    def __init__(self, email: str):
        super().__init__(f"Email '{email}' is already registered")


class UsernameAlreadyExistsError(DomainError):
    def __init__(self, username: str):
        super().__init__(f"Username '{username}' is already taken")


class InvalidCredentialsError(DomainError):
    def __init__(self):
        super().__init__("Invalid email or password")


# ── Project ───────────────────────────────────────────────────────────────────

class ProjectNotFoundError(DomainError):
    def __init__(self, project_id: int):
        super().__init__(f"Project {project_id} not found")


class DuplicateProjectNameError(DomainError):
    def __init__(self, name: str):
        super().__init__(f"You already have a project named '{name}'")


# ── Task ──────────────────────────────────────────────────────────────────────

class TaskNotFoundError(DomainError):
    def __init__(self, task_id: int):
        super().__init__(f"Task {task_id} not found")


class InvalidStatusTransitionError(DomainError):
    def __init__(self, from_status: str, to_status: str, allowed: list[str]):
        super().__init__(
            f"Cannot transition task from '{from_status}' to '{to_status}'. "
            f"Allowed: {allowed}"
        )


class AssigneeNotFoundError(DomainError):
    def __init__(self, user_id: int):
        super().__init__(f"User {user_id} not found")


# ── Value Object validation ───────────────────────────────────────────────────

class InvalidEmailError(DomainError):
    def __init__(self, value: str):
        super().__init__(f"'{value}' is not a valid email address")


class InvalidUsernameError(DomainError):
    def __init__(self, value: str):
        super().__init__(
            f"'{value}' is not a valid username. "
            "Must be 3–32 characters, only letters/digits/underscores."
        )


class DueDateInPastError(DomainError):
    def __init__(self):
        super().__init__("Due date must be in the future")
