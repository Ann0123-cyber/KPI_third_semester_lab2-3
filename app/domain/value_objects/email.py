"""Email — Value Object. Немає ідентичності, порівнюється за значенням."""
import re
from dataclasses import dataclass

from app.domain.errors import InvalidEmailError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not _EMAIL_RE.match(self.value):
            raise InvalidEmailError(self.value)

    def __str__(self) -> str:
        return self.value
