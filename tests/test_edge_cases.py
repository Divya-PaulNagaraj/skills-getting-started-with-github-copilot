"""
Test cases for edge cases and error handling in the Activities API.
"""

import pytest
from fastapi.testclient import TestClient


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_special_characters_in_email(self, client: TestClient, reset_activities):
        """Test signup with special characters in email."""
        import urllib.parse
        
        special_emails = [
            "test.student@mergington.edu",
            "test+tag@mergington.edu",
            "test_underscore@mergington.edu",
            "test-dash@mergington.edu"
        ]
        
        for email in special_emails:
            # URL encode the email to handle special characters properly
            encoded_email = urllib.parse.quote(email, safe='@')
            response = client.post(
                f"/activities/Chess Club/signup?email={encoded_email}"
            )
            assert response.status_code == 200
            
            # Verify participant was added (check for the original email)
            activities_response = client.get("/activities")
            activities_data = activities_response.json()
            assert email in activities_data["Chess Club"]["participants"]
    
    def test_case_sensitivity_activity_names(self, client: TestClient, reset_activities):
        """Test that activity names are case sensitive."""
        # This should fail because "chess club" != "Chess Club"
        response = client.post(
            "/activities/chess club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unicode_characters_in_activity_name(self, client: TestClient, reset_activities):
        """Test handling of unicode characters in activity names."""
        # Test with URL-encoded unicode characters
        response = client.post(
            "/activities/Café%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404  # Activity doesn't exist
    
    def test_very_long_email(self, client: TestClient, reset_activities):
        """Test signup with very long email address."""
        long_email = "a" * 100 + "@mergington.edu"
        response = client.post(
            f"/activities/Chess Club/signup?email={long_email}"
        )
        assert response.status_code in [200, 422]  # Either succeeds or validation error
    
    def test_empty_activity_name(self, client: TestClient, reset_activities):
        """Test with empty activity name."""
        response = client.post(
            "/activities/ /signup?email=test@mergington.edu"
        )
        assert response.status_code == 404


class TestDataConsistency:
    """Test data consistency and state management."""
    
    def test_participant_count_consistency(self, client: TestClient, reset_activities):
        """Test that participant counts remain consistent after operations."""
        # Get initial count
        activities_response = client.get("/activities")
        initial_data = activities_response.json()
        initial_count = len(initial_data["Chess Club"]["participants"])
        
        # Add a participant
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        # Check count increased by 1
        activities_response = client.get("/activities")
        updated_data = activities_response.json()
        new_count = len(updated_data["Chess Club"]["participants"])
        assert new_count == initial_count + 1
        
        # Remove the participant
        client.delete("/activities/Chess Club/participants/newstudent@mergington.edu")
        
        # Check count is back to original
        activities_response = client.get("/activities")
        final_data = activities_response.json()
        final_count = len(final_data["Chess Club"]["participants"])
        assert final_count == initial_count
    
    def test_activity_data_immutability_except_participants(self, client: TestClient, reset_activities):
        """Test that only participants list changes, other data remains immutable."""
        # Get initial activity data
        activities_response = client.get("/activities")
        initial_data = activities_response.json()
        chess_initial = initial_data["Chess Club"]
        
        # Perform signup
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        # Get updated data
        activities_response = client.get("/activities")
        updated_data = activities_response.json()
        chess_updated = updated_data["Chess Club"]
        
        # Check that non-participant fields are unchanged
        assert chess_updated["description"] == chess_initial["description"]
        assert chess_updated["schedule"] == chess_initial["schedule"]
        assert chess_updated["max_participants"] == chess_initial["max_participants"]
        
        # Check that participants list has changed
        assert len(chess_updated["participants"]) == len(chess_initial["participants"]) + 1


class TestConcurrentOperations:
    """Test scenarios that might occur with concurrent requests."""
    
    def test_multiple_signups_same_student(self, client: TestClient, reset_activities):
        """Test multiple signup attempts for the same student and activity."""
        email = "duplicate.test@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response2.status_code == 400
        assert response2.json()["detail"] == "Student already signed up for this activity"
        
        # Verify only one instance exists
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participant_count = activities_data["Chess Club"]["participants"].count(email)
        assert participant_count == 1
    
    def test_remove_then_add_same_participant(self, client: TestClient, reset_activities):
        """Test removing and then re-adding the same participant."""
        email = "michael@mergington.edu"  # Already exists in Chess Club
        
        # Remove participant
        remove_response = client.delete(f"/activities/Chess Club/participants/{email}")
        assert remove_response.status_code == 200
        
        # Verify removal
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Chess Club"]["participants"]
        
        # Re-add participant
        add_response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert add_response.status_code == 200
        
        # Verify re-addition
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]


class TestErrorHandling:
    """Test error handling and HTTP status codes."""
    
    def test_invalid_http_methods(self, client: TestClient):
        """Test that invalid HTTP methods return appropriate errors."""
        # PUT on signup endpoint
        response = client.put("/activities/Chess Club/signup?email=test@mergington.edu")
        assert response.status_code == 405  # Method not allowed
        
        # PATCH on activities endpoint
        response = client.patch("/activities")
        assert response.status_code == 405  # Method not allowed
    
    def test_malformed_urls(self, client: TestClient):
        """Test handling of malformed URLs."""
        # Missing activity name
        response = client.post("/activities//signup?email=test@mergington.edu")
        assert response.status_code in [404, 422]
        
        # Missing participants segment
        response = client.delete("/activities/Chess Club//test@mergington.edu")
        assert response.status_code in [404, 422]
    
    def test_content_type_handling(self, client: TestClient, reset_activities):
        """Test that the API handles different content types appropriately."""
        # Test with JSON body (should still work as we use query params)
        response = client.post(
            "/activities/Chess Club/signup?email=json.test@mergington.edu",
            json={"extra": "data"}
        )
        assert response.status_code == 200
        
        # Test with form data
        response = client.post(
            "/activities/Chess Club/signup?email=form.test@mergington.edu",
            data={"extra": "data"}
        )
        assert response.status_code == 200


class TestDataValidation:
    """Test data validation and sanitization."""
    
    def test_email_validation_patterns(self, client: TestClient, reset_activities):
        """Test various email patterns to ensure proper validation."""
        valid_emails = [
            "simple@mergington.edu",
            "with.dots@mergington.edu",
            "with+plus@mergington.edu",
            "with_underscore@mergington.edu",
            "with-dash@mergington.edu"
        ]
        
        for email in valid_emails:
            response = client.post(f"/activities/Chess Club/signup?email={email}")
            # Should either succeed or fail gracefully
            assert response.status_code in [200, 400, 422]
    
    def test_sql_injection_attempts(self, client: TestClient, reset_activities):
        """Test that SQL injection attempts are handled safely."""
        malicious_inputs = [
            "'; DROP TABLE activities; --",
            "' OR '1'='1",
            "admin@mergington.edu'; DELETE FROM participants; --"
        ]
        
        for malicious_input in malicious_inputs:
            response = client.post(
                f"/activities/Chess Club/signup?email={malicious_input}"
            )
            # Should not crash the server
            assert response.status_code in [200, 400, 422]
            
            # Verify activities still exist
            activities_response = client.get("/activities")
            assert activities_response.status_code == 200
            assert len(activities_response.json()) > 0