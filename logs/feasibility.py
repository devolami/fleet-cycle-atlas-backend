from .config import HOSConfig

def validate_trip_feasibility(
    total_dist: float, 
    total_time_mins: float, 
    config: HOSConfig, 
    current_cycle_hour: float
) -> tuple[bool, str]:
    """
    Service to predict if a trip is legal under HOS cycle limits 
    before the detailed log is generated.
    """
    
    total_driving_required_hrs = total_time_mins / config.MINUTES_PER_HOUR
    remaining_cycle_hrs = config.MAX_WEEKLY_CYCLE - current_cycle_hour
    
    fixed_on_duty_hrs = config.FIXED_ON_DUTY_HOURS    
    # Refueling stops calculation
    num_fueling_stops = total_dist // config.REFUEL_THRESHOLD_MILES
    fueling_duration_hrs = num_fueling_stops * config.REFUEL_DURATION
    
    # Work duration for 30-min break calculation
    subtotal_work_hrs = total_driving_required_hrs + fixed_on_duty_hrs + fueling_duration_hrs
    
    # FMCSA Rule: Break required after 8 hours of work
    num_breaks = int(subtotal_work_hrs // config.BREAK_REQUIRED_AFTER)
    break_duration_hrs = num_breaks * config.MANDATORY_BREAK_DURATION
    
    total_predicted_on_duty = subtotal_work_hrs + break_duration_hrs
    
    if total_predicted_on_duty > remaining_cycle_hrs:
        return False, (
            f"Insufficient cycle hours. Trip requires ~{total_predicted_on_duty:.1f}h "
            f"on-duty. You only have {remaining_cycle_hrs:.1f}h left in your cycle."
        )
    
    return True, ""