from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.database import Base, engine
from app.routers import auth_router, projects_router, tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use Alembic in production instead)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Task Manager API",
    description="REST API for managing projects and tasks",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(tasks_router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
