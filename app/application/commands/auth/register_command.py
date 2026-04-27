from dataclasses import dataclass

@dataclass(frozen=True)
class RegisterUserCommand:
    email: str
    username: str
    password: str
