"""Aggregation queries for reporting.

Only finished entries (those with a duration) contribute to totals.
"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Project, Task, TimeEntry


class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def totals_by_project(self, user_id: int) -> list[tuple[int, str, int]]:
        rows = self.db.execute(
            select(
                Project.id,
                Project.name,
                func.coalesce(func.sum(TimeEntry.duration_seconds), 0),
            )
            .join(Task, Task.project_id == Project.id)
            .join(TimeEntry, TimeEntry.task_id == Task.id)
            .where(
                TimeEntry.user_id == user_id,
                TimeEntry.duration_seconds.is_not(None),
            )
            .group_by(Project.id, Project.name)
            .order_by(Project.id)
        ).all()
        return [(r[0], r[1], int(r[2])) for r in rows]

    def totals_by_day(self, user_id: int) -> list[tuple[str, int]]:
        day = func.date(TimeEntry.started_at)
        rows = self.db.execute(
            select(day, func.coalesce(func.sum(TimeEntry.duration_seconds), 0))
            .where(
                TimeEntry.user_id == user_id,
                TimeEntry.duration_seconds.is_not(None),
            )
            .group_by(day)
            .order_by(day)
        ).all()
        return [(str(r[0]), int(r[1])) for r in rows]
