"""
Entry point of the API.

Run it with:
    uvicorn app.main:app --reload

Then open http://127.0.0.1:8000/docs for interactive documentation.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once at startup: create the tables if they don't exist yet.
    # (Bigger projects use a migration tool like Alembic instead.)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Task Manager API",
    description="A REST API for managing personal tasks, with JWT authentication.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/", tags=["Health"])
def health_check():
    """Simple check that the API is running."""
    return {"status": "ok", "docs": "/docs"}
