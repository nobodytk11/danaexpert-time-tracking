"""Request/response schemas for time entries."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StartRequest(BaseModel):
    task_id: int


class TimeEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    started_at: datetime
    stopped_at: datetime | None
    duration_seconds: int | None
