"""Integration tests for projects and tasks (scoped to the current user)."""


def test_create_and_list_project(client, auth_headers):
    resp = client.post("/projects", json={"name": "Thesis"}, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["name"] == "Thesis"

    listed = client.get("/projects", headers=auth_headers)
    assert listed.status_code == 200
    assert [p["name"] for p in listed.json()] == ["Thesis"]


def test_projects_are_scoped_to_owner(client, auth_headers):
    # First user creates a project.
    client.post("/projects", json={"name": "Private"}, headers=auth_headers)

    # A second, different user must not see it.
    client.post("/auth/register", json={"email": "other@u.com", "password": "pw12345"})
    token = client.post(
        "/auth/login", json={"email": "other@u.com", "password": "pw12345"}
    ).json()["access_token"]
    other = {"Authorization": f"Bearer {token}"}

    listed = client.get("/projects", headers=other)
    assert listed.json() == []


def test_create_and_list_tasks_under_project(client, auth_headers):
    project_id = client.post(
        "/projects", json={"name": "App"}, headers=auth_headers
    ).json()["id"]

    resp = client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Write tests"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "Write tests"

    listed = client.get(f"/projects/{project_id}/tasks", headers=auth_headers)
    assert [t["title"] for t in listed.json()] == ["Write tests"]


def test_cannot_add_task_to_another_users_project(client, auth_headers):
    project_id = client.post(
        "/projects", json={"name": "Mine"}, headers=auth_headers
    ).json()["id"]

    client.post("/auth/register", json={"email": "x@u.com", "password": "pw12345"})
    token = client.post(
        "/auth/login", json={"email": "x@u.com", "password": "pw12345"}
    ).json()["access_token"]
    other = {"Authorization": f"Bearer {token}"}

    resp = client.post(
        f"/projects/{project_id}/tasks", json={"title": "Sneaky"}, headers=other
    )
    assert resp.status_code == 404


def test_endpoints_require_authentication(client):
    assert client.get("/projects").status_code in (401, 403)
