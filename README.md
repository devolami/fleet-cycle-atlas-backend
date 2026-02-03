# 🚛 Hours of Service (HOS) Logbook Generator

An automated logic engine and Django API designed to generate FMCSA-compliant driver logbooks. This system simulates real-world trucking constraints, including driving limits, mandatory rest periods, and refueling stops.

---

## 📖 Project Overview

This application takes trip parameters (distance, time, cycle hours) and simulates a driver's logbook across multiple days. It strictly adheres to Federal Motor Carrier Safety Administration (FMCSA) regulations to ensure trip feasibility and legal compliance.

### Core Regulations Handled

- **11-Hour Driving Limit:** Maximum allowed driving time per shift.
- **14-Hour Duty Window:** No work allowed after 14 hours since the start of the shift.
- **10-Hour Reset:** Automatically triggers sleeper berth periods to reset daily clocks.
- **30-Minute Break:** Enforces a mandatory rest break after 8 hours of work.
- **70-Hour Rule:** A pre-trip feasibility check against the 8-day cycle limit.

---

## 🚀 Installation & Setup

### 1. Prerequisites

This project uses **uv** for high-performance Python package management. [Install uv here](https://docs.astral.sh/uv/getting-started/installation/).

### 2. Setup the Environment

Clone the repository and sync the dependencies (this creates your virtual environment automatically):

```bash
git clone <your-repo-url>
cd trip-backend-recent
uv sync

### 3. Run the Server

uv run python manage.py migrate
uv run python manage.py runserver
```

### 4. Run all tests:

uv run pytest

### Endpoint: POST /api/logs/generate_logbook/

### Required JSON Body:

{
"total_distance_miles": 1200.0,
"total_driving_time": 1080.0,
"current_cycle_hour": 15.0,
"pickup_time": 60.0
}
