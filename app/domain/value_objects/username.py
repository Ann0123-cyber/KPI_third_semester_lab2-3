"""Username — Value Object."""
import re
from dataclasses import dataclass

from app.domain.errors import InvalidUsernameError

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")


@dataclass(frozen=True)
class Username:
    value: str

    def __post_init__(self):
        if not _USERNAME_RE.match(self.value):
            raise InvalidUsernameError(self.value)

    def __str__(self) -> str:
        return self.value
