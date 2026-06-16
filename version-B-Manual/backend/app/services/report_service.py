"""Assemble the productivity summary from the aggregation repository."""
from app.repositories.report_repository import ReportRepository
from app.schemas.report import DayTotal, ProjectTotal, Summary


class ReportService:
    def __init__(self, reports: ReportRepository):
        self.reports = reports

    def summary(self, user_id: int) -> Summary:
        by_project = [
            ProjectTotal(project_id=pid, project_name=name, total_seconds=total)
            for pid, name, total in self.reports.totals_by_project(user_id)
        ]
        by_day = [
            DayTotal(day=day, total_seconds=total)
            for day, total in self.reports.totals_by_day(user_id)
        ]
        return Summary(by_project=by_project, by_day=by_day)
