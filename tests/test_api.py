from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # basic sanity check for one known activity
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    activity_e = quote(activity, safe="")
    email = "pytest_student@example.com"

    # Ensure clean state: remove if present
    resp = client.get(f"/activities")
    assert resp.status_code == 200
    participants_before = resp.json()[activity]["participants"]
    if email in participants_before:
        client.delete(f"/activities/{activity_e}/participants?email={quote(email, safe='')}")

    # Sign up
    resp = client.post(f"/activities/{activity_e}/signup?email={quote(email, safe='')}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify present
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email in resp.json()[activity]["participants"]

    # Duplicate signup should fail
    resp = client.post(f"/activities/{activity_e}/signup?email={quote(email, safe='')}")
    assert resp.status_code == 400

    # Unregister
    resp = client.delete(f"/activities/{activity_e}/participants?email={quote(email, safe='')}")
    assert resp.status_code == 200

    # Verify removed
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]


def test_unregister_nonexistent_returns_404():
    activity = "Chess Club"
    activity_e = quote(activity, safe="")
    resp = client.delete(f"/activities/{activity_e}/participants?email={quote('no-such-user@example.com', safe='')}")
    assert resp.status_code == 404
