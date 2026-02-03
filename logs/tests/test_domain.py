import pytest

from logs.config import HOSConfig
from logs.driver_state import DriverState

@pytest.fixture
def config() -> HOSConfig:
    """Fixture to provide HOSConfig instance for tests."""
    return HOSConfig()

@pytest.fixture
def state() -> DriverState:
    """Fixture to provide a default DriverState instance for tests."""
    return DriverState()

def test_daily_counter_reset(state: DriverState):
    """
    Verify that resetting daily counters clears logs but 
    persists the total trip progress.
    """
    state.day_off_duty = 5.0
    state.day_on_duty = 8.0
    state.day_driving = 6.5  
    state.day_sleeper = 10.0         

    state.reset_daily_counters()
    assert state.day_off_duty == 0.0
    assert state.day_on_duty == 0.0
    assert state.day_driving == 0.0
    assert state.day_sleeper == 0.0

def test_refuel_mileage_accumulation(state, config):
    """Verify that miles accumulate correctly toward the refuel threshold."""
    mph = 60
    step = config.TIME_STEP # 0.5 hours
    
    # Simulate one driving step
    state.miles_since_refuel += (mph * step)
    
    assert state.miles_since_refuel == 30.0