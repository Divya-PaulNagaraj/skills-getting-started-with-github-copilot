"""
Test configuration and fixtures for the Mergington High School Activities API.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add src directory to path so we can import the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test."""
    # Store original activities
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
        "Soccer Team": {
            "description": "Join the school soccer team and compete in matches",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["alex@mergington.edu", "lucas@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice basketball skills and play friendly games",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["mia@mergington.edu", "noah@mergington.edu"]
        },
        "Art Workshop": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["ava@mergington.edu", "liam@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act in plays and learn stage performance skills",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ella@mergington.edu", "jack@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Prepare for math competitions and solve challenging problems",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 10,
            "participants": ["ethan@mergington.edu", "isabella@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["benjamin@mergington.edu", "charlotte@mergington.edu"]
        }
    }
    
    # Reset activities to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test (reset again)
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def sample_activity_data():
    """Sample activity data for testing."""
    return {
        "name": "Test Activity",
        "description": "A test activity for unit testing",
        "schedule": "Test Schedule",
        "max_participants": 5,
        "participants": ["test1@mergington.edu", "test2@mergington.edu"]
    }