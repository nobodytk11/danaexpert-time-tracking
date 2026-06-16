"""Business rules for time tracking.

Rules enforced here:
- You can only track time on a task that belongs to one of your projects.
- Only one timer may run at a time per user.
- A stopped entry cannot be stopped again.
On stop we compute the duration and fire an (optional) Slack notification.
"""
from datetime import datetime, timezone

from app.models import TimeEntry
from app.repositories.time_entry_repository import TimeEntryRepository
from app.services.slack_notifier import SlackNotifier


class TaskNotFound(Exception):
    """Task does not exist for this user."""


class TimerAlreadyRunning(Exception):
    """The user already has a running timer."""


class EntryNotFound(Exception):
    """Time entry does not exist for this user."""


class EntryAlreadyStopped(Exception):
    """The entry has already been stopped."""


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TimeEntryService:
    def __init__(self, entries: TimeEntryRepository, notifier: SlackNotifier | None = None):
        self.entries = entries
        self.notifier = notifier or SlackNotifier()

    def start(self, user_id: int, task_id: int) -> TimeEntry:
        if not self.entries.task_belongs_to_user(task_id, user_id):
            raise TaskNotFound(task_id)
        if self.entries.get_running_for_user(user_id) is not None:
            raise TimerAlreadyRunning()
        return self.entries.create(user_id=user_id, task_id=task_id)

    def stop(self, user_id: int, entry_id: int) -> TimeEntry:
        entry = self.entries.get_for_user(entry_id, user_id)
        if entry is None:
            raise EntryNotFound(entry_id)
        if entry.stopped_at is not None:
            raise EntryAlreadyStopped(entry_id)

        entry.stopped_at = _utcnow()
        entry.duration_seconds = int((entry.stopped_at - entry.started_at).total_seconds())
        saved = self.entries.save(entry)

        self.notifier.notify_session_finished(
            task_id=saved.task_id, duration_seconds=saved.duration_seconds or 0
        )
        return saved

    def list_for_user(self, user_id: int) -> list[TimeEntry]:
        return self.entries.list_for_user(user_id)
