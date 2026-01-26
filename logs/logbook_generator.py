from .config import HOSConfig
from .driver_state import DriverState

class LogbookGenerator:
    def __init__(self, total_dist: float, total_time_mins: float, config: HOSConfig, current_cycle_hour: float = 0.0):
        self.config = config
        self.state = DriverState()
        self.total_dist = total_dist
        self.total_driving_required_hrs = total_time_mins / self.config.MINUTES_PER_HOUR
        self.current_cycle_hour = current_cycle_hour
        self.mph = total_dist / self.total_driving_required_hrs if total_dist > 0 else 0
                
        self.logbooks = []
        self.current_day_log = self._initialize_new_day_dict()

    def _initialize_new_day_dict(self):
        return {
            "logbook": [],
            "currentHour": 0,
            "totalTimeTraveled": round(self.state.total_trip_time_elapsed_hrs * self.config.MINUTES_PER_HOUR, 2),
            "timeSpentInOffDuty": 0,
            "timeSpentInOnDuty": 0,
            "timeSpentInDriving": 0,
            "timeSpentInSleeperBerth": 0
        }

    def _finalize_day(self):
        """Helper to seal the summary values before pushing to the list."""
        self.current_day_log["timeSpentInOffDuty"] = round(self.state.day_off_duty, 2)
        self.current_day_log["timeSpentInOnDuty"] = round(self.state.day_on_duty, 2)
        self.current_day_log["timeSpentInDriving"] = round(self.state.day_driving, 2)
        self.current_day_log["timeSpentInSleeperBerth"] = round(self.state.day_sleeper, 2)
        self.logbooks.append(self.current_day_log)

    def _rotate_day(self):
        self._finalize_day()
        self.state.current_hour_of_day = 0.0
        self.state.reset_daily_counters()
        self.current_day_log = self._initialize_new_day_dict()

    def _log_sleeper(self, duration: float):
        remaining_in_day = self.config.HOURS_IN_DAY - self.state.current_hour_of_day
        
        if duration > remaining_in_day:
            # PART 1: Fill the rest of today
            self.current_day_log["logbook"].append({"hour": self.state.current_hour_of_day, "row": "sleeper"})
            self.state.day_sleeper += remaining_in_day
            self.state.current_hour_of_day = self.config.HOURS_IN_DAY
            self.current_day_log["logbook"].append({"hour": self.config.HOURS_IN_DAY, "row": "sleeper", "action": "10-hour Reset (Part 1)"})
            self._rotate_day()
            
            # PART 2: The remaining time in the new day
            remainder = duration - remaining_in_day
            self.current_day_log["logbook"].append({"hour": 0.0, "row": "sleeper"})
            self.state.current_hour_of_day += remainder
            self.state.day_sleeper += remainder
            self.current_day_log["logbook"].append({"hour": self.state.current_hour_of_day, "row": "sleeper", "action": "10-hour Reset (Part 2)"})
        else:
            # Normal logic if it fits in the current day
            self.current_day_log["logbook"].append({"hour": self.state.current_hour_of_day, "row": "sleeper"})
            self.state.current_hour_of_day += duration
            self.state.day_sleeper += duration
            self.current_day_log["logbook"].append({"hour": self.state.current_hour_of_day, "row": "sleeper", "action": "10-hour Reset"})

        # Resets for HOS
        self.state.daily_driving_hrs = 0
        self.state.daily_duty_hrs = 0
        self.state.hrs_since_last_break = 0

    def _log_off_duty(self, duration: float, action: str = None):
        remaining_in_day = self.config.HOURS_IN_DAY - self.state.current_hour_of_day
        
        if duration > remaining_in_day:
            # PART 1
            self.current_day_log["logbook"].append({"hour": self.state.current_hour_of_day, "row": "off-duty"})
            self.state.day_off_duty += remaining_in_day
            self.state.current_hour_of_day = self.config.HOURS_IN_DAY
            self.current_day_log["logbook"].append({"hour": self.config.HOURS_IN_DAY, "row": "off-duty", "action": action})
            
            self._rotate_day()
            
            # PART 2
            remainder = duration - remaining_in_day
            self.current_day_log["logbook"].append({"hour": 0.0, "row": "off-duty"})
            self.state.current_hour_of_day += remainder
            self.state.day_off_duty += remainder
            self.current_day_log["logbook"].append({"hour": self.state.current_hour_of_day, "row": "off-duty", "action": action})
        else:
            self.current_day_log["logbook"].append({"hour": self.state.current_hour_of_day, "row": "off-duty"})
            self.state.current_hour_of_day += duration
            self.state.day_off_duty += duration
            self.current_day_log["logbook"].append({"hour": self.state.current_hour_of_day, "row": "off-duty", "action": action})
        
        if duration >= self.config.MANDATORY_BREAK_DURATION: self.state.hrs_since_last_break = 0
    def _log_on_duty(self, duration: float, action: str):
        # On-duty tasks are usually short (0.5h), so they rarely cross midnight, 
        # but for robustness we check anyway.
        remaining_in_day = self.config.HOURS_IN_DAY - self.state.current_hour_of_day
        if duration > remaining_in_day:
            self.current_day_log["logbook"].append({"hour": self.state.current_hour_of_day, "row": "on-duty"})
            self.state.day_on_duty += remaining_in_day
            self.state.current_hour_of_day = self.config.HOURS_IN_DAY
            self.current_day_log["logbook"].append({"hour": self.config.HOURS_IN_DAY, "row": "on-duty", "action": action})
            self._rotate_day()
            remainder = duration - remaining_in_day
            self.current_day_log["logbook"].append({"hour": 0.0, "row": "on-duty"})
            self.state.current_hour_of_day += remainder
            self.state.day_on_duty += remainder
            self.current_day_log["logbook"].append({"hour": self.state.current_hour_of_day, "row": "on-duty", "action": action})
        else:
            self.current_day_log["logbook"].append({"hour": self.state.current_hour_of_day, "row": "on-duty"})
            self.state.current_hour_of_day += duration
            self.state.day_on_duty += duration
            self.current_day_log["logbook"].append({"hour": self.state.current_hour_of_day, "row": "on-duty", "action": action})
        
        self.state.daily_duty_hrs += duration
        self.state.hrs_since_last_break += duration

    def _log_drive_step(self, is_start: bool):
       
        step = self.config.TIME_STEP
        remaining_in_day = self.config.HOURS_IN_DAY - self.state.current_hour_of_day

        if remaining_in_day < step:
            # Log the sliver of driving left today
            if is_start: self.current_day_log["logbook"].append({"hour": self.state.current_hour_of_day, "row": "driving"})
            self.state.day_driving += remaining_in_day
            self.state.current_hour_of_day = self.config.HOURS_IN_DAY
            self.current_day_log["logbook"].append({"hour": self.config.HOURS_IN_DAY, "row": "driving"})
            
            self._rotate_day()
            
            # Log the rest in the next day
            remainder = step - remaining_in_day
            self.current_day_log["logbook"].append({"hour": 0.0, "row": "driving"})
            self.state.current_hour_of_day += remainder
            self.state.day_driving += remainder
            self.current_day_log["logbook"].append({"hour": self.state.current_hour_of_day, "row": "driving"})
        else:
            if is_start: self.current_day_log["logbook"].append({"hour": self.state.current_hour_of_day, "row": "driving"})
            self.state.current_hour_of_day += step
            self.state.day_driving += step
            self.current_day_log["logbook"].append({"hour": self.state.current_hour_of_day, "row": "driving"})

        self.state.daily_driving_hrs += step
        self.state.daily_duty_hrs += step
        self.state.hrs_since_last_break += step
        self.state.total_trip_time_elapsed_hrs += step
        self.state.miles_since_refuel += (self.mph * step)

    def generate(self, pickup_time_mins: float):
        pickup_time_hrs = pickup_time_mins / self.config.MINUTES_PER_HOUR
        has_performed_pickup = False
        
        self._log_off_duty(self.config.INITIAL_REST_DURATION) 
        self._log_on_duty(self.config.PRE_TRIP_DURATION, "Pre-trip/TIV")

        while self.state.total_trip_time_elapsed_hrs < self.total_driving_required_hrs:
            if self.state.daily_driving_hrs >= self.config.MAX_DRIVING_TIME or self.state.daily_duty_hrs >= self.config.MAX_DUTY_WINDOW:
                self._log_sleeper(self.config.SLEEPER_BERTH_REQUIRED)
                continue
            if self.state.hrs_since_last_break >= self.config.BREAK_REQUIRED_AFTER:
                self._log_off_duty(self.config.MANDATORY_BREAK_DURATION, "30-minute break")
                continue
            if self.state.miles_since_refuel >= self.config.REFUEL_THRESHOLD_MILES:
                self._log_on_duty(self.config.REFUEL_DURATION, "Refueling")
                self.state.miles_since_refuel = 0
                continue
            if not has_performed_pickup and (self.state.total_trip_time_elapsed_hrs >= pickup_time_hrs):
                self._log_on_duty(self.config.PICKUP_DURATION, "Pickup")
                has_performed_pickup = True
                continue

            is_new_block = (not self.current_day_log["logbook"] or 
                            self.current_day_log["logbook"][-1]["row"] != "driving")
            self._log_drive_step(is_start=is_new_block)

        self._log_on_duty(self.config.POST_TRIP_DURATION, "Drop-off")
        if self.state.current_hour_of_day < self.config.HOURS_IN_DAY:
            self._log_off_duty(self.config.HOURS_IN_DAY - self.state.current_hour_of_day)
        
        self._finalize_day()
        return self.logbooks
