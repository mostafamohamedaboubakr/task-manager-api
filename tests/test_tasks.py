from tests.conftest import register_and_login


def create_task(client, headers, **fields):
    body = {"title": "Write report", **fields}
    response = client.post("/tasks", json=body, headers=headers)
    assert response.status_code == 201
    return response.json()


def test_tasks_require_login(client):
    assert client.get("/tasks").status_code == 401
    assert client.post("/tasks", json={"title": "x"}).status_code == 401


def test_create_and_get_task(client, auth_headers):
    task = create_task(client, auth_headers, priority="high", due_date="2026-12-01")
    assert task["title"] == "Write report"
    assert task["completed"] is False
    assert task["priority"] == "high"

    response = client.get(f"/tasks/{task['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == task["id"]


def test_create_task_validation(client, auth_headers):
    # Empty title and an invalid priority are both rejected.
    assert client.post("/tasks", json={"title": ""}, headers=auth_headers).status_code == 422
    response = client.post(
        "/tasks", json={"title": "ok", "priority": "urgent"}, headers=auth_headers
    )
    assert response.status_code == 422


def test_list_tasks_with_filters(client, auth_headers):
    create_task(client, auth_headers, title="Buy milk", priority="low")
    create_task(client, auth_headers, title="Finish project", priority="high")
    done = create_task(client, auth_headers, title="Call mom", priority="high")
    client.patch(f"/tasks/{done['id']}", json={"completed": True}, headers=auth_headers)

    all_tasks = client.get("/tasks", headers=auth_headers).json()
    assert all_tasks["total"] == 3

    high = client.get("/tasks?priority=high", headers=auth_headers).json()
    assert high["total"] == 2

    open_high = client.get("/tasks?priority=high&completed=false", headers=auth_headers).json()
    assert open_high["total"] == 1
    assert open_high["items"][0]["title"] == "Finish project"

    search = client.get("/tasks?search=milk", headers=auth_headers).json()
    assert search["total"] == 1


def test_pagination(client, auth_headers):
    for i in range(5):
        create_task(client, auth_headers, title=f"Task {i}")
    page = client.get("/tasks?skip=0&limit=2", headers=auth_headers).json()
    assert page["total"] == 5
    assert len(page["items"]) == 2


def test_partial_update(client, auth_headers):
    task = create_task(client, auth_headers, description="draft")
    response = client.patch(
        f"/tasks/{task['id']}", json={"completed": True}, headers=auth_headers
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["completed"] is True
    # Fields we didn't send stay the same.
    assert updated["title"] == "Write report"
    assert updated["description"] == "draft"


def test_delete_task(client, auth_headers):
    task = create_task(client, auth_headers)
    assert client.delete(f"/tasks/{task['id']}", headers=auth_headers).status_code == 204
    assert client.get(f"/tasks/{task['id']}", headers=auth_headers).status_code == 404


def test_users_cannot_access_each_others_tasks(client, auth_headers):
    task = create_task(client, auth_headers)
    other_headers = register_and_login(client, username="mallory")

    assert client.get(f"/tasks/{task['id']}", headers=other_headers).status_code == 404
    assert (
        client.patch(f"/tasks/{task['id']}", json={"title": "hacked"}, headers=other_headers)
        .status_code
        == 404
    )
    assert client.delete(f"/tasks/{task['id']}", headers=other_headers).status_code == 404
    assert client.get("/tasks", headers=other_headers).json()["total"] == 0
