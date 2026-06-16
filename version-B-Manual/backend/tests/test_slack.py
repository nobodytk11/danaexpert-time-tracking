"""Unit tests for the optional Slack notifier."""
from app.services.slack_notifier import SlackNotifier


def test_notifier_is_noop_when_url_unset():
    notifier = SlackNotifier(webhook_url="")
    assert notifier.notify_session_finished(task_id=1, duration_seconds=120) is False


def test_notifier_posts_when_url_set(monkeypatch):
    calls = {}

    def fake_post(url, json, timeout):
        calls["url"] = url
        calls["json"] = json
        class _Resp:
            status_code = 200
        return _Resp()

    monkeypatch.setattr("app.services.slack_notifier.requests.post", fake_post)

    notifier = SlackNotifier(webhook_url="https://hooks.slack.test/abc")
    result = notifier.notify_session_finished(task_id=7, duration_seconds=180)

    assert result is True
    assert calls["url"] == "https://hooks.slack.test/abc"
    assert "#7" in calls["json"]["text"]
