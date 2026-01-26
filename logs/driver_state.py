from dataclasses import dataclass, field

@dataclass
class DriverState:
    # Clock & Movement tracking
    current_hour_of_day: float = 0.0
    total_trip_time_elapsed_hrs: float = 0.0
    miles_since_refuel: float = 0.0
    
    # HOS Regulatory Accumulators
    daily_driving_hrs: float = 0.0
    daily_duty_hrs: float = 0.0
    hrs_since_last_break: float = 0.0
    
    # Daily Summaries (Reset every midnight/rotate)
    day_off_duty: float = 0.0
    day_on_duty: float = 0.0
    day_driving: float = 0.0
    day_sleeper: float = 0.0

    def reset_daily_counters(self):
        self.day_off_duty = 0.0
        self.day_on_duty = 0.0
        self.day_driving = 0.0
        self.day_sleeper = 0.0