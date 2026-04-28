from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.infrastructure.orm.base import Base
from app.infrastructure.database import engine
from app.domain.errors import DomainError
from app.presentation.routers.error_handlers import domain_error_handler
from app.presentation.routers.auth_router import router as auth_router
from app.presentation.routers.projects_router import router as projects_router
from app.presentation.routers.tasks_router import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Task Manager API — Lab 3 (CQS)", version="3.0.0", lifespan=lifespan)
app.add_exception_handler(DomainError, domain_error_handler)
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(tasks_router)


@app.get("/health")
def health():
    return {"status": "ok"}
