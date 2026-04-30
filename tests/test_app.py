import copy

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
original_activities = copy.deepcopy(activities)


def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities():
    reset_activities()

    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["description"].startswith("Learn strategies")


def test_signup_new_participant():
    reset_activities()

    email = "test.student@mergington.edu"
    response = client.post(
        "/activities/Chess%20Club/signup?email=test.student%40mergington.edu"
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"

    activities_response = client.get("/activities").json()
    assert email in activities_response["Chess Club"]["participants"]


def test_duplicate_signup_returns_400():
    reset_activities()

    email = "michael@mergington.edu"
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael%40mergington.edu"
    )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_remove_participant():
    reset_activities()

    email = "michael@mergington.edu"
    response = client.delete(
        "/activities/Chess%20Club/participants?email=michael%40mergington.edu"
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"

    activities_response = client.get("/activities").json()
    assert email not in activities_response["Chess Club"]["participants"]


def test_remove_nonexistent_participant_returns_404():
    reset_activities()

    response = client.delete(
        "/activities/Chess%20Club/participants?email=nope%40mergington.edu"
    )

    assert response.status_code == 404
    assert "is not registered" in response.json()["detail"]


def test_remove_from_invalid_activity_returns_404():
    reset_activities()

    response = client.delete(
        "/activities/Unknown%20Club/participants?email=test%40mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
