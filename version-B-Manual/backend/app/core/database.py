"""Database engine, session factory and the FastAPI session dependency.

Everything that talks to the database goes through a SQLAlchemy Session obtained
from `get_db`. Keeping this in one place means swapping the database (e.g. to
PostgreSQL) is a configuration change, not a code change.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# check_same_thread is a SQLite-only flag needed because FastAPI may use the
# connection from different threads. It is ignored by other databases.
_connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(settings.database_url, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Declarative base shared by every ORM model."""


def get_db() -> Generator[Session, None, None]:
    """Yield a session and guarantee it is closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
