"""Integration tests for start/stop time tracking and its rules."""
import pytest


@pytest.fixture()
def task_id(client, auth_headers):
    pid = client.post("/projects", json={"name": "P"}, headers=auth_headers).json()["id"]
    return client.post(
        f"/projects/{pid}/tasks", json={"title": "T"}, headers=auth_headers
    ).json()["id"]


def test_start_creates_running_entry(client, auth_headers, task_id):
    resp = client.post(
        "/time-entries/start", json={"task_id": task_id}, headers=auth_headers
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["task_id"] == task_id
    assert body["stopped_at"] is None
    assert body["duration_seconds"] is None


def test_cannot_start_second_timer_while_one_runs(client, auth_headers, task_id):
    client.post("/time-entries/start", json={"task_id": task_id}, headers=auth_headers)
    resp = client.post(
        "/time-entries/start", json={"task_id": task_id}, headers=auth_headers
    )
    assert resp.status_code == 400


def test_stop_sets_duration(client, auth_headers, task_id):
    entry_id = client.post(
        "/time-entries/start", json={"task_id": task_id}, headers=auth_headers
    ).json()["id"]

    resp = client.post(f"/time-entries/{entry_id}/stop", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["stopped_at"] is not None
    assert body["duration_seconds"] is not None
    assert body["duration_seconds"] >= 0


def test_cannot_stop_already_stopped_entry(client, auth_headers, task_id):
    entry_id = client.post(
        "/time-entries/start", json={"task_id": task_id}, headers=auth_headers
    ).json()["id"]
    client.post(f"/time-entries/{entry_id}/stop", headers=auth_headers)

    resp = client.post(f"/time-entries/{entry_id}/stop", headers=auth_headers)
    assert resp.status_code == 400


def test_list_returns_only_current_users_entries(client, auth_headers, task_id):
    client.post("/time-entries/start", json={"task_id": task_id}, headers=auth_headers)

    resp = client.get("/time-entries", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
