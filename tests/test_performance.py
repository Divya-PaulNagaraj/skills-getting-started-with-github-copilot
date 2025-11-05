"""
Performance and load tests for the Activities API.
"""

import pytest
import time
from fastapi.testclient import TestClient


class TestPerformance:
    """Basic performance tests."""
    
    def test_get_activities_response_time(self, client: TestClient, reset_activities):
        """Test that getting activities has reasonable response time."""
        start_time = time.time()
        response = client.get("/activities")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 1.0  # Should respond within 1 second
    
    def test_signup_response_time(self, client: TestClient, reset_activities):
        """Test that signup has reasonable response time."""
        start_time = time.time()
        response = client.post("/activities/Chess Club/signup?email=perf.test@mergington.edu")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 1.0  # Should respond within 1 second
    
    def test_multiple_rapid_requests(self, client: TestClient, reset_activities):
        """Test handling of multiple rapid requests."""
        emails = [f"load.test.{i}@mergington.edu" for i in range(10)]
        
        start_time = time.time()
        responses = []
        
        for email in emails:
            response = client.post(f"/activities/Programming Class/signup?email={email}")
            responses.append(response)
        
        end_time = time.time()
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
        
        # Total time should be reasonable
        total_time = end_time - start_time
        assert total_time < 5.0  # Should complete within 5 seconds
        
        # Verify all participants were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        programming_participants = activities_data["Programming Class"]["participants"]
        
        for email in emails:
            assert email in programming_participants


class TestStressScenarios:
    """Test stress scenarios and edge conditions."""
    
    def test_activity_near_capacity(self, client: TestClient, reset_activities):
        """Test behavior when activity is near or at capacity."""
        # Math Olympiad has max 10 participants, currently has 2
        math_olympiad_emails = [f"math.student.{i}@mergington.edu" for i in range(8)]
        
        # Fill up to capacity
        for email in math_olympiad_emails:
            response = client.post(f"/activities/Math Olympiad/signup?email={email}")
            assert response.status_code == 200
        
        # Verify we're at capacity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert len(activities_data["Math Olympiad"]["participants"]) == 10
        
        # Note: The current API doesn't enforce capacity limits, but we test the data integrity
        # In a real application, you might want to add capacity validation
    
    def test_large_participant_list_handling(self, client: TestClient, reset_activities):
        """Test handling activities with large numbers of participants."""
        # Add many participants to Gym Class (has max 30)
        gym_emails = [f"gym.student.{i}@mergington.edu" for i in range(25)]
        
        for email in gym_emails:
            response = client.post(f"/activities/Gym Class/signup?email={email}")
            assert response.status_code == 200
        
        # Test that we can still retrieve activities efficiently
        start_time = time.time()
        response = client.get("/activities")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 2.0  # Should still be fast even with many participants
        
        # Verify data integrity
        activities_data = response.json()
        gym_participants = activities_data["Gym Class"]["participants"]
        assert len(gym_participants) >= 27  # Original 2 + 25 new ones


class TestConcurrencySimulation:
    """Simulate concurrent operations that might happen in real usage."""
    
    def test_concurrent_signup_and_removal(self, client: TestClient, reset_activities):
        """Test concurrent signups and removals."""
        # Add several participants
        test_emails = [f"concurrent.{i}@mergington.edu" for i in range(5)]
        
        for email in test_emails:
            response = client.post(f"/activities/Drama Club/signup?email={email}")
            assert response.status_code == 200
        
        # Now remove some while adding others
        removal_emails = test_emails[:2]  # Remove first 2
        addition_emails = [f"new.concurrent.{i}@mergington.edu" for i in range(3)]  # Add 3 new
        
        # Remove participants
        for email in removal_emails:
            response = client.delete(f"/activities/Drama Club/participants/{email}")
            assert response.status_code == 200
        
        # Add new participants
        for email in addition_emails:
            response = client.post(f"/activities/Drama Club/signup?email={email}")
            assert response.status_code == 200
        
        # Verify final state
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        drama_participants = activities_data["Drama Club"]["participants"]
        
        # Should not contain removed emails
        for email in removal_emails:
            assert email not in drama_participants
        
        # Should contain new emails
        for email in addition_emails:
            assert email in drama_participants
    
    def test_rapid_state_changes(self, client: TestClient, reset_activities):
        """Test rapid state changes on the same activity."""
        test_email = "rapid.change@mergington.edu"
        activity = "Science Club"
        
        # Rapidly add and remove participant multiple times
        for i in range(5):
            # Add
            add_response = client.post(f"/activities/{activity}/signup?email={test_email}")
            assert add_response.status_code == 200
            
            # Verify added
            activities_response = client.get("/activities")
            activities_data = activities_response.json()
            assert test_email in activities_data[activity]["participants"]
            
            # Remove
            remove_response = client.delete(f"/activities/{activity}/participants/{test_email}")
            assert remove_response.status_code == 200
            
            # Verify removed
            activities_response = client.get("/activities")
            activities_data = activities_response.json()
            assert test_email not in activities_data[activity]["participants"]