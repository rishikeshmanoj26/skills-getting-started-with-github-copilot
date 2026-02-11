"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test"""
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team and practice",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis training and friendly matches",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 16,
            "participants": ["lucas@mergington.edu", "natalie@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and visual arts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Learn instruments and perform in concerts",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["gabriel@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 14,
            "participants": ["james@mergington.edu"]
        },
        "Science Lab": {
            "description": "Hands-on experiments and scientific research",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["benjamin@mergington.edu", "charlotte@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_includes_activity_details(self, client):
        """Test that activities include all required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_includes_participants(self, client):
        """Test that activities include participant list"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "michael@mergington.edu" in activity["participants"]
        assert "daniel@mergington.edu" in activity["participants"]
        assert len(activity["participants"]) == 2


class TestSignUp:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_adds_participant(self, client):
        """Test that signup successfully adds a participant"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
    
    def test_signup_appears_in_activity(self, client):
        """Test that signed up student appears in activity participants"""
        client.post(
            "/activities/Programming%20Class/signup?email=newstudent@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        activity = data["Programming Class"]
        
        assert "newstudent@mergington.edu" in activity["participants"]
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_duplicate_returns_400(self, client):
        """Test that signing up twice returns 400 error"""
        email = "michael@mergington.edu"
        response = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_different_students(self, client):
        """Test that multiple different students can signup"""
        client.post(
            "/activities/Basketball%20Team/signup?email=student1@mergington.edu"
        )
        client.post(
            "/activities/Basketball%20Team/signup?email=student2@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        participants = data["Basketball Team"]["participants"]
        
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants
        assert len(participants) == 3  # alex + 2 new


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister successfully removes a participant"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_appears_in_activity(self, client):
        """Test that unregistered student no longer appears in activity"""
        client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "michael@mergington.edu" not in activity["participants"]
        assert "daniel@mergington.edu" in activity["participants"]
    
    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_non_participant_returns_400(self, client):
        """Test that unregistering someone not signed up returns 400"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=notstudent@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_then_signup_again(self, client):
        """Test that student can signup after unregistering"""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Unregister
        client.delete(f"/activities/{activity}/unregister?email={email}")
        
        # Signup again
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify they're registered
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity]["participants"]


class TestRoot:
    """Tests for root endpoint"""
    
    def test_root_redirects_to_index(self, client):
        """Test that root endpoint redirects to index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
