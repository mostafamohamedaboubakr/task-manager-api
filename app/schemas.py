"""
Pydantic schemas = the shape of data going IN and OUT of the API.

Why separate from models.py?
- models.py describes how data is STORED (e.g. hashed_password).
- schemas.py describes what the API ACCEPTS and RETURNS (e.g. we accept a
  plain password on signup, but never send any password back).

Pydantic validates incoming JSON automatically: if a field is missing or has
the wrong type, FastAPI returns a 422 error with a clear message for free.
"""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import Priority


# ---------- Users ----------
class UserCreate(BaseModel):
    """Body for POST /auth/register."""

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserOut(BaseModel):
    """What we return about a user. Note: no password field!"""

    # Lets Pydantic read data straight from a SQLAlchemy object.
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime


# ---------- Auth ----------
class Token(BaseModel):
    """Returned by POST /auth/login."""

    access_token: str
    token_type: str = "bearer"


# ---------- Tasks ----------
class TaskCreate(BaseModel):
    """Body for POST /tasks."""

    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    priority: Priority = Priority.medium
    due_date: date | None = None


class TaskUpdate(BaseModel):
    """
    Body for PATCH /tasks/{id}.

    Every field is optional: the client sends only what it wants to change.
    """

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    completed: bool | None = None
    priority: Priority | None = None
    due_date: date | None = None


class TaskOut(BaseModel):
    """What we return for a task."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    completed: bool
    priority: Priority
    due_date: date | None
    created_at: datetime
    updated_at: datetime


class TaskList(BaseModel):
    """A page of tasks plus the total count (useful for pagination in a UI)."""

    total: int
    items: list[TaskOut]
