"""Response schemas for the productivity report."""
from pydantic import BaseModel


class ProjectTotal(BaseModel):
    project_id: int
    project_name: str
    total_seconds: int


class DayTotal(BaseModel):
    day: str
    total_seconds: int


class Summary(BaseModel):
    by_project: list[ProjectTotal]
    by_day: list[DayTotal]
