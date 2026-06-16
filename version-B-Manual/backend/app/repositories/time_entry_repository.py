"""Data-access for time entries."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project, Task, TimeEntry


class TimeEntryRepository:
    def __init__(self, db: Session):
        self.db = db

    def task_belongs_to_user(self, task_id: int, user_id: int) -> bool:
        """True if the task exists and its project is owned by the user."""
        row = self.db.execute(
            select(Task.id)
            .join(Project, Task.project_id == Project.id)
            .where(Task.id == task_id, Project.owner_id == user_id)
        ).scalar_one_or_none()
        return row is not None

    def get_running_for_user(self, user_id: int) -> TimeEntry | None:
        return self.db.execute(
            select(TimeEntry).where(
                TimeEntry.user_id == user_id, TimeEntry.stopped_at.is_(None)
            )
        ).scalar_one_or_none()

    def get_for_user(self, entry_id: int, user_id: int) -> TimeEntry | None:
        return self.db.execute(
            select(TimeEntry).where(
                TimeEntry.id == entry_id, TimeEntry.user_id == user_id
            )
        ).scalar_one_or_none()

    def create(self, user_id: int, task_id: int) -> TimeEntry:
        entry = TimeEntry(user_id=user_id, task_id=task_id)
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def save(self, entry: TimeEntry) -> TimeEntry:
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def list_for_user(self, user_id: int) -> list[TimeEntry]:
        return list(
            self.db.execute(
                select(TimeEntry)
                .where(TimeEntry.user_id == user_id)
                .order_by(TimeEntry.started_at.desc())
            ).scalars()
        )
