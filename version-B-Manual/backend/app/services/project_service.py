"""Business rules for projects and tasks.

The key rule: a user may only see and modify their own projects. Asking for a
project that exists but belongs to someone else is treated as "not found" so we
don't reveal that it exists.
"""
from app.models import Project, Task
from app.repositories.project_repository import ProjectRepository


class ProjectNotFound(Exception):
    """Raised when a project does not exist for this owner."""


class ProjectService:
    def __init__(self, projects: ProjectRepository):
        self.projects = projects

    def create_project(self, owner_id: int, name: str) -> Project:
        return self.projects.create(owner_id=owner_id, name=name)

    def list_projects(self, owner_id: int) -> list[Project]:
        return self.projects.list_for_owner(owner_id)

    def _owned_or_404(self, project_id: int, owner_id: int) -> Project:
        project = self.projects.get_owned(project_id, owner_id)
        if project is None:
            raise ProjectNotFound(project_id)
        return project

    def add_task(self, owner_id: int, project_id: int, title: str) -> Task:
        self._owned_or_404(project_id, owner_id)
        return self.projects.add_task(project_id=project_id, title=title)

    def list_tasks(self, owner_id: int, project_id: int) -> list[Task]:
        self._owned_or_404(project_id, owner_id)
        return self.projects.list_tasks(project_id)
