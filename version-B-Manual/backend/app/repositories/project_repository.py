"""Data-access for projects and tasks."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project, Task


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, owner_id: int, name: str) -> Project:
        project = Project(owner_id=owner_id, name=name)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def list_for_owner(self, owner_id: int) -> list[Project]:
        return list(
            self.db.execute(
                select(Project).where(Project.owner_id == owner_id).order_by(Project.id)
            ).scalars()
        )

    def get_owned(self, project_id: int, owner_id: int) -> Project | None:
        return self.db.execute(
            select(Project).where(
                Project.id == project_id, Project.owner_id == owner_id
            )
        ).scalar_one_or_none()

    def add_task(self, project_id: int, title: str) -> Task:
        task = Task(project_id=project_id, title=title)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def list_tasks(self, project_id: int) -> list[Task]:
        return list(
            self.db.execute(
                select(Task).where(Task.project_id == project_id).order_by(Task.id)
            ).scalars()
        )
