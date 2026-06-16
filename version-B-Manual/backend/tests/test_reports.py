"""Integration test for the productivity summary report."""
import pytest


@pytest.fixture()
def task_id(client, auth_headers):
    pid = client.post("/projects", json={"name": "Reporting"}, headers=auth_headers).json()["id"]
    return client.post(
        f"/projects/{pid}/tasks", json={"title": "T"}, headers=auth_headers
    ).json()["id"]


def test_summary_groups_totals_by_project_and_day(client, auth_headers, task_id):
    entry_id = client.post(
        "/time-entries/start", json={"task_id": task_id}, headers=auth_headers
    ).json()["id"]
    client.post(f"/time-entries/{entry_id}/stop", headers=auth_headers)

    resp = client.get("/reports/summary", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()

    assert "by_project" in body and "by_day" in body
    assert len(body["by_project"]) == 1
    assert body["by_project"][0]["project_name"] == "Reporting"
    assert body["by_project"][0]["total_seconds"] >= 0
    assert len(body["by_day"]) == 1


def test_summary_is_empty_for_user_without_entries(client, auth_headers):
    resp = client.get("/reports/summary", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == {"by_project": [], "by_day": []}
