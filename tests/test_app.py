from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(original_activities)


client = TestClient(app)


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    email = "alex@mergington.edu"
    activity_name = "Chess Club"
    response = client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    email = "michael@mergington.edu"
    activity_name = "Chess Club"
    response = client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_for_missing_activity_returns_404():
    email = "alex@mergington.edu"
    activity_name = "Nonexistent Club"
    response = client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_from_activity():
    email = "daniel@mergington.edu"
    activity_name = "Chess Club"
    response = client.delete(f"/activities/{quote(activity_name)}/participants/{quote(email)}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    email = "not-a-user@mergington.edu"
    activity_name = "Chess Club"
    response = client.delete(f"/activities/{quote(activity_name)}/participants/{quote(email)}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not registered"


def test_remove_participant_from_missing_activity_returns_404():
    email = "alex@mergington.edu"
    activity_name = "Nonexistent Club"
    response = client.delete(f"/activities/{quote(activity_name)}/participants/{quote(email)}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
