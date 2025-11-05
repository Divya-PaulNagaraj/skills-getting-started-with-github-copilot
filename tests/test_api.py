"""
Test cases for the Mergington High School Activities API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Test cases for the root endpoint."""
    
    def test_root_redirects_to_static_html(self, client: TestClient):
        """Test that root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Test cases for the activities endpoints."""
    
    def test_get_activities_success(self, client: TestClient, reset_activities):
        """Test successful retrieval of all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check that required fields are present for each activity
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)
    
    def test_get_activities_contains_expected_activities(self, client: TestClient, reset_activities):
        """Test that the response contains expected activities."""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", 
            "Soccer Team", "Basketball Club", "Art Workshop",
            "Drama Club", "Math Olympiad", "Science Club"
        ]
        
        for activity in expected_activities:
            assert activity in data
    
    def test_activities_data_structure(self, client: TestClient, reset_activities):
        """Test the structure of activity data."""
        response = client.get("/activities")
        data = response.json()
        
        # Test Chess Club specifically
        chess_club = data["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Test cases for the signup endpoint."""
    
    def test_signup_success(self, client: TestClient, reset_activities):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify the participant was actually added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_activity_not_found(self, client: TestClient, reset_activities):
        """Test signup for non-existent activity."""
        response = client.post(
            "/activities/Non-existent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_student(self, client: TestClient, reset_activities):
        """Test signup when student is already registered."""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"
    
    def test_signup_url_encoding(self, client: TestClient, reset_activities):
        """Test signup with URL-encoded activity name and email."""
        response = client.post(
            "/activities/Programming%20Class/signup?email=test%40mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify the participant was actually added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test@mergington.edu" in activities_data["Programming Class"]["participants"]
    
    def test_signup_missing_email(self, client: TestClient, reset_activities):
        """Test signup without email parameter."""
        response = client.post("/activities/Chess Club/signup")
        assert response.status_code == 422  # Validation error
    
    def test_signup_empty_email(self, client: TestClient, reset_activities):
        """Test signup with empty email."""
        response = client.post("/activities/Chess Club/signup?email=")
        # FastAPI currently accepts empty emails, but in a real app you'd want validation
        assert response.status_code in [200, 422]  # Either succeeds or validation error


class TestRemoveParticipantEndpoint:
    """Test cases for the remove participant endpoint."""
    
    def test_remove_participant_success(self, client: TestClient, reset_activities):
        """Test successful removal of a participant."""
        # First verify the participant exists
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" in activities_data["Chess Club"]["participants"]
        
        # Remove the participant
        response = client.delete(
            "/activities/Chess Club/participants/michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify the participant was actually removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_remove_participant_activity_not_found(self, client: TestClient, reset_activities):
        """Test removing participant from non-existent activity."""
        response = client.delete(
            "/activities/Non-existent Activity/participants/test@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_remove_participant_not_found(self, client: TestClient, reset_activities):
        """Test removing participant who is not signed up."""
        response = client.delete(
            "/activities/Chess Club/participants/nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Participant is not signed up for this activity"
    
    def test_remove_participant_url_encoding(self, client: TestClient, reset_activities):
        """Test removing participant with URL-encoded names."""
        response = client.delete(
            "/activities/Programming%20Class/participants/emma%40mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify the participant was actually removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "emma@mergington.edu" not in activities_data["Programming Class"]["participants"]


class TestIntegrationScenarios:
    """Integration test scenarios combining multiple operations."""
    
    def test_signup_and_remove_workflow(self, client: TestClient, reset_activities):
        """Test complete workflow of signup and removal."""
        test_email = "integration.test@mergington.edu"
        activity_name = "Chess Club"
        
        # Initial state - participant should not exist
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email not in activities_data[activity_name]["participants"]
        
        # Sign up participant
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        assert signup_response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email in activities_data[activity_name]["participants"]
        
        # Remove participant
        remove_response = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )
        assert remove_response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email not in activities_data[activity_name]["participants"]
    
    def test_multiple_signups_different_activities(self, client: TestClient, reset_activities):
        """Test signing up for multiple different activities."""
        test_email = "multi.signup@mergington.edu"
        activities = ["Chess Club", "Programming Class", "Art Workshop"]
        
        # Sign up for multiple activities
        for activity in activities:
            response = client.post(
                f"/activities/{activity}/signup?email={test_email}"
            )
            assert response.status_code == 200
        
        # Verify participant is in all activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        for activity in activities:
            assert test_email in activities_data[activity]["participants"]
    
    def test_activity_capacity_tracking(self, client: TestClient, reset_activities):
        """Test that we can track how many spots are left in activities."""
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        # Check Math Olympiad (max 10, currently has 2)
        math_olympiad = activities_data["Math Olympiad"]
        spots_taken = len(math_olympiad["participants"])
        spots_available = math_olympiad["max_participants"] - spots_taken
        
        assert spots_taken == 2
        assert spots_available == 8
        assert math_olympiad["max_participants"] == 10