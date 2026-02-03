import pytest

from logs.config import HOSConfig
from logs.feasibility import validate_trip_feasibility
from logs.logbook_generator import LogbookGenerator

@pytest.fixture
def config()-> HOSConfig:
    """Fixture to provide HOSConfig instance for tests."""
    return HOSConfig()

def test_valid_trip_feasibility(config: HOSConfig):
    """
    Test that a feasible trip is correctly identified.
    """
    total_dist = 300.0  # miles
    total_time_mins = 300.0  # minutes (5 hours)
    current_cycle_hour = 20.0  # hours used in cycle

    is_possible, error_msg = validate_trip_feasibility(
        total_dist=total_dist,
        total_time_mins=total_time_mins,
        config=config,
        current_cycle_hour=current_cycle_hour
    )

    assert is_possible is True
    assert error_msg == ""

def test_cycle_limit_violation(config: HOSConfig):
    """
    Test that an infeasible trip due to cycle limits is correctly identified.
    """
    total_dist = 1000.0  # miles
    total_time_mins = 1200.0  # minutes (20 hours)
    current_cycle_hour = 60.0  # hours used in cycle, close to max

    is_possible, error_msg = validate_trip_feasibility(
        total_dist=total_dist,
        total_time_mins=total_time_mins,
        config=config,
        current_cycle_hour=current_cycle_hour
    )

    assert is_possible is False
    assert "Insufficient cycle hours" in error_msg

def test_edge_case_exact_cycle_limit(config: HOSConfig):
    """
    Test a trip that exactly matches the remaining cycle hours,
    accounting for driving, fixed tasks, and mandatory breaks.
    """
    total_dist = 400.0 
    driving_hrs = 10.0
    total_time_mins = driving_hrs * 60  # 600 mins
    
    predicted_on_duty = (
        driving_hrs + 
        config.FIXED_ON_DUTY_HOURS + 
        0.5 # One 30-min break triggered after 8h
    )

    current_cycle_hour = config.MAX_WEEKLY_CYCLE - predicted_on_duty

    is_possible, error_msg = validate_trip_feasibility(
        total_dist=total_dist,
        total_time_mins=total_time_mins,
        config=config,
        current_cycle_hour=current_cycle_hour
    )

    assert is_possible is True, f"Trip should be possible. Error: {error_msg}"
    assert error_msg == ""


@pytest.mark.parametrize("distance, expected_stops", [
    (500.0, 0),    # Below threshold
    (1000.0, 1),   # Just over first threshold (980)
    (2000.0, 2),   # Multiple stops
    (3000.0, 3),   # Long haul
])
def test_refuel_stop_calculation(config, distance, expected_stops):
    """
    Verify that feasibility logic correctly predicts the number of 
    refuel stops based on distance.
    """
    current_cycle_hour = 0.0
    driving_hrs = 10.0 
    
    is_possible, _ = validate_trip_feasibility(
        total_dist=distance,
        total_time_mins=driving_hrs * 60,
        config=config,
        current_cycle_hour=current_cycle_hour
    )
   
    fueling_time = expected_stops * config.REFUEL_DURATION
    fixed_time = config.FIXED_ON_DUTY_HOURS
    
    subtotal = driving_hrs + fixed_time + fueling_time
    num_breaks = int(subtotal // config.BREAK_REQUIRED_AFTER)
    expected_on_duty = subtotal + (num_breaks * config.MANDATORY_BREAK_DURATION)
    
    tight_cycle = config.MAX_WEEKLY_CYCLE - (expected_on_duty - 0.1)
    
    possible_with_tight_cycle, _ = validate_trip_feasibility(
        total_dist=distance,
        total_time_mins=driving_hrs * 60,
        config=config,
        current_cycle_hour=tight_cycle
    )
    
    assert possible_with_tight_cycle is False, f"Should fail at {distance} miles due to {expected_stops} fuel stops."

def test_feasibility_zero_values(config):
    """Verify feasibility service handles zero distance/time safely (Prevent ZeroDivisionError)."""
    # Should not crash; 0 miles/time simply requires 0 cycle hours.
    is_possible, error_msg = validate_trip_feasibility(
        total_dist=0,
        total_time_mins=0,
        config=config,
        current_cycle_hour=0
    )
    assert is_possible is True
    assert error_msg == ""

def test_generator_zero_values(config):
    """Verify logbook generator doesn't raise ZeroDivisionError."""
    # This specifically targets: self.mph = total_dist / total_driving_required_hrs
    generator = LogbookGenerator(
        total_dist=0,
        total_time_mins=0,
        config=config
    )
    
    # We expect the MPH to be 0 rather than a crash
    assert generator.mph == 0
    
    # Ensure it can still generate a 'minimal' logbook (Pre-trip/Post-trip)
    logbooks = generator.generate(pickup_time_mins=0)
    assert len(logbooks) > 0
    assert "logbook" in logbooks[0]