import pytest
from rest_framework import status
from rest_framework.test import APIClient

from logs.config import HOSConfig
from logs.logbook_generator import LogbookGenerator

pytestmark = pytest.mark.django_db

@pytest.fixture
def config() -> HOSConfig:
    """Fixture to provide HOSConfig instance for tests."""
    return HOSConfig()

@pytest.fixture
def api_url():
    return "/api/logs/generate_logbook/"

@pytest.fixture
def api_client():
    return APIClient()


def test_generate_logbook_success(api_client, api_url):
    """Verify 200 OK and valid structure for a standard trip."""
    payload = {
        "total_distance_miles": 500,
        "total_driving_time": 480,  # 8 hours
        "current_cycle_hour": 10,
        "pickup_time": 30
    }
    response = api_client.post(api_url, data=payload, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)

    assert "logbook" in response.data[0]
    assert "timeSpentInDriving" in response.data[0]

def test_generate_logbook_feasibility_rejection(api_client, api_url):
    """Verify 400 Bad Request when cycle hours are insufficient."""
    payload = {
        "total_distance_miles": 1000,
        "total_driving_time": 1200,  # 20 hours
        "current_cycle_hour": 65,    # 70 - 65 = 5 hours left (Impossible)
        "pickup_time": 30
    }
    response = api_client.post(api_url, data=payload, format='json')
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in response.data
    assert "Insufficient cycle hours" in response.data["error"]


@pytest.mark.parametrize("missing_field", [
    "total_distance_miles", 
    "total_driving_time", 
    "current_cycle_hour"
])

def test_input_validation_missing_fields(api_client, api_url, missing_field):
    """Verify the API returns 400 if required fields are missing."""
    payload = {
        "total_distance_miles": 100,
        "total_driving_time": 480,
        "current_cycle_hour": 10,
        "pickup_time": 30
    }
    payload.pop(missing_field)  
    
    response = api_client.post(api_url, data=payload, format='json')
    
    # Assertions
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Missing required fields" in response.data["error"]
    assert missing_field in response.data["error"]

def test_input_validation_non_numeric(api_client, api_url):
    """Verify 400 error when sending garbage strings."""
    payload = {
        "total_distance_miles": "five hundred miles", # Invalid
        "total_driving_time": 480,
        "current_cycle_hour": 10,  
        "pickup_time": 30          
    }
    response = api_client.post(api_url, data=payload, format='json')
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
   
    assert "Invalid input format" in response.data["error"]

def test_input_zero_values_no_crash(api_client, api_url):
    """Ensure 0 distance/time doesn't trigger a ZeroDivisionError (500)."""
    payload = {
        "total_distance_miles": 0,
        "total_driving_time": 0,
        "current_cycle_hour": 0,
        "pickup_time": 0 
    }
    response = api_client.post(api_url, data=payload, format='json')
    
   
    assert response.status_code == status.HTTP_200_OK

def test_mandatory_break_insertion(config):
    """
    Verify that a 30-minute break is inserted after 8 hours of work.
    """
    generator = LogbookGenerator(
        total_dist=500,
        total_time_mins=600, # 10 hours
        config=config
    )
    
    logbooks = generator.generate(pickup_time_mins=0)
    day_log = logbooks[0]["logbook"]

    break_events = [entry for entry in day_log if entry.get("action") == "30-minute break"]
    
    assert len(break_events) > 0, "A mandatory break should have been inserted."
    
    break_start_time = break_events[0]["hour"]
    assert break_start_time >= 8.0


def test_input_validation_non_numeric(api_client, api_url):
    """Verify 400 error when sending garbage strings."""
    payload = {
        "total_distance_miles": "five hundred miles", # Invalid
        "total_driving_time": 480,
        "current_cycle_hour": 10,  
        "pickup_time": 30          
    }
    response = api_client.post(api_url, data=payload, format='json')
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    assert "Invalid input format" in response.data["error"]

def test_input_zero_values_no_crash(api_client, api_url):
    """Ensure 0 distance/time doesn't trigger a ZeroDivisionError (500)."""
    payload = {
        "total_distance_miles": 0,
        "total_driving_time": 0,
        "current_cycle_hour": 0,
        "pickup_time": 0  
    }
    response = api_client.post(api_url, data=payload, format='json')
    
    assert response.status_code == status.HTTP_200_OK