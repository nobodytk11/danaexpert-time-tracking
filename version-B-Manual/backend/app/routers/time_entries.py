"""Time-tracking endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.repositories.time_entry_repository import TimeEntryRepository
from app.schemas.time_entry import StartRequest, TimeEntryOut
from app.services.time_entry_service import (
    EntryAlreadyStopped,
    EntryNotFound,
    TaskNotFound,
    TimeEntryService,
    TimerAlreadyRunning,
)

router = APIRouter(prefix="/time-entries", tags=["time-entries"])


def _service(db: Session) -> TimeEntryService:
    return TimeEntryService(TimeEntryRepository(db))


@router.post("/start", response_model=TimeEntryOut, status_code=status.HTTP_201_CREATED)
def start(
    payload: StartRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return _service(db).start(user.id, payload.task_id)
    except TaskNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    except TimerAlreadyRunning:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A timer is already running. Stop it first.",
        )


@router.post("/{entry_id}/stop", response_model=TimeEntryOut)
def stop(
    entry_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return _service(db).stop(user.id, entry_id)
    except EntryNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    except EntryAlreadyStopped:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Entry already stopped"
        )


@router.get("", response_model=list[TimeEntryOut])
def list_entries(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return _service(db).list_for_user(user.id)
