"""Маппінг DomainError → HTTP статуси. Єдине місце де домен зустрічається з HTTP."""
from fastapi import Request
from fastapi.responses import JSONResponse

from app.domain.errors import (
    DomainError,
    EmailAlreadyExistsError, UsernameAlreadyExistsError, DuplicateProjectNameError,
    ProjectNotFoundError, TaskNotFoundError, AssigneeNotFoundError,
    InvalidCredentialsError,
    InvalidStatusTransitionError,
    InvalidEmailError, InvalidUsernameError, DueDateInPastError,
)


def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    if isinstance(exc, (ProjectNotFoundError, TaskNotFoundError, AssigneeNotFoundError)):
        status_code = 404
    elif isinstance(exc, (EmailAlreadyExistsError, UsernameAlreadyExistsError, DuplicateProjectNameError)):
        status_code = 409
    elif isinstance(exc, InvalidCredentialsError):
        status_code = 401
    elif isinstance(exc, (InvalidStatusTransitionError, DueDateInPastError)):
        status_code = 400
    elif isinstance(exc, (InvalidEmailError, InvalidUsernameError)):
        status_code = 422
    else:
        status_code = 400

    return JSONResponse(status_code=status_code, content={"detail": exc.message})
