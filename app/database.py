"""
Database setup with SQLAlchemy.

SQLAlchemy is an ORM (Object-Relational Mapper): instead of writing raw SQL,
we work with Python classes and objects, and SQLAlchemy turns them into SQL.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import DATABASE_URL

# The engine is the connection to the database.
# `check_same_thread=False` is needed only for SQLite, because FastAPI may
# use the same connection from different threads.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# A "session" is a short conversation with the database: we open one per
# request, do our reads/writes, then close it.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """All database models inherit from this class."""


def get_db():
    """
    FastAPI dependency that gives each request its own database session.

    `yield` hands the session to the endpoint; the code after `yield` runs
    once the request is finished, so the session is always closed — even
    if an error happened.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
