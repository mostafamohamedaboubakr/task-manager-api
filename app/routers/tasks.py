"""
Task endpoints — full CRUD (Create, Read, Update, Delete).

HTTP method  ->  meaning
    POST     ->  create something new
    GET      ->  read (never changes data)
    PATCH    ->  partially update
    DELETE   ->  remove

Every endpoint here requires login, and users can only ever see and change
THEIR OWN tasks (we always filter by owner_id).
"""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Priority, Task, User
from app.schemas import TaskCreate, TaskList, TaskOut, TaskUpdate
from app.security import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_own_task(task_id: int, db: Session, user: User) -> Task:
    """
    Fetch a task that belongs to the current user, or raise 404.

    We return 404 (not 403) for other users' tasks so we don't even reveal
    that the task exists.
    """
    task = db.scalar(select(Task).where(Task.id == task_id, Task.owner_id == user.id))
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a task for the logged-in user."""
    # model_dump() turns the Pydantic object into a dict of its fields.
    task = Task(**task_in.model_dump(), owner_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=TaskList)
def list_tasks(
    # Query parameters: /tasks?completed=false&priority=high&search=report
    completed: bool | None = Query(None, description="Filter by done / not done"),
    priority: Priority | None = Query(None, description="Filter by priority"),
    search: str | None = Query(None, description="Search in title and description"),
    due_before: date | None = Query(None, description="Only tasks due on/before this date"),
    # Pagination: never return unlimited rows.
    skip: int = Query(0, ge=0, description="How many tasks to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max tasks to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List your tasks with optional filters and pagination."""
    query = select(Task).where(Task.owner_id == current_user.id)

    # Build the query step by step — only add filters the client asked for.
    if completed is not None:
        query = query.where(Task.completed == completed)
    if priority is not None:
        query = query.where(Task.priority == priority)
    if search:
        pattern = f"%{search}%"
        query = query.where(Task.title.ilike(pattern) | Task.description.ilike(pattern))
    if due_before is not None:
        query = query.where(Task.due_date <= due_before)

    # Count all matches (before pagination) so the client knows the total.
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    items = db.scalars(query.order_by(Task.created_at.desc()).offset(skip).limit(limit)).all()
    return TaskList(total=total, items=items)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get one task by its id."""
    return get_own_task(task_id, db, current_user)


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update only the fields you send."""
    task = get_own_task(task_id, db, current_user)

    # exclude_unset=True -> only fields the client actually sent.
    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a task. Returns 204 No Content on success."""
    task = get_own_task(task_id, db, current_user)
    db.delete(task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
