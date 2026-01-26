from dataclasses import dataclass

@dataclass
class HOSConfig:
    """Hours of Service Regulation & Operational Constants."""

    # --- Regulatory Limits (FMCSA/HOS Rules in hours) ---
    MAX_DRIVING_TIME: float = 11.0         # Max hours driving per shift
    MAX_DUTY_WINDOW: float = 14.0          # Max hours on-duty per shift
    MAX_WEEKLY_CYCLE: float = 70.0         # 70-hour / 8-day rule
    BREAK_REQUIRED_AFTER: float = 8.0      # 30-min break required after 8h work
    MANDATORY_BREAK_DURATION: float = 0.5  # Duration of the required break
    SLEEPER_BERTH_REQUIRED: float = 10.0   # Required rest to reset shift clocks

    # --- Operational Durations (Trip Tasks) ---
    PRE_TRIP_DURATION: float = 0.5         # Inspection at start of day
    PICKUP_DURATION: float = 0.5           # Standard loading time
    POST_TRIP_DURATION: float = 0.5        # Inspection/Drop-off at end of day
    INITIAL_REST_DURATION: float = 6.5     # Forced rest before starting trip
    FIXED_ON_DUTY_HOURS: float = 1.5       # Combined static on-duty tasks (Pre+Pick+Drop)

    # --- Logistic & Threshold Rules ---
    REFUEL_THRESHOLD_MILES: float = 980.0  # Max miles before a refuel is forced
    REFUEL_DURATION: float = 0.5           # Time spent at the pump (in hours)

    # --- Mathematical & System Constants ---
    HOURS_IN_DAY: float = 24.0             # Grid/Clock cycle
    MINUTES_PER_HOUR: int = 60             # Conversion factor
    TIME_STEP: float = 0.5                 # Calculation resolution (30-min blocks)