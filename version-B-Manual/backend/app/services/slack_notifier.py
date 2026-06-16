"""Optional Slack notifier.

Designed to fail safe: if no webhook URL is configured it does nothing and reports
False, so the core application keeps working without any Slack setup.
"""
import requests

from app.core.config import settings


class SlackNotifier:
    def __init__(self, webhook_url: str | None = None):
        self.webhook_url = webhook_url if webhook_url is not None else settings.slack_webhook_url

    def notify_session_finished(self, task_id: int, duration_seconds: int) -> bool:
        if not self.webhook_url:
            return False
        minutes = duration_seconds // 60
        text = f"Finished a focus session on task #{task_id} ({minutes} min)."
        try:
            requests.post(self.webhook_url, json={"text": text}, timeout=5)
        except requests.RequestException:
            # A notification failure must never break stopping a timer.
            return False
        return True
