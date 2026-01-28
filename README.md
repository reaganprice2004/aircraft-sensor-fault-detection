# Aircraft Sensor Fault Detection System

A Python-based aviation diagnostics project that validates flight sensor data and detects common fault patterns using interpretable, rule-based checks. The system processes time-series flight data and classifies sensor health as **HEALTHY**, **SUSPECT**, or **FAILED** with fault-type attribution.

## Overview

Modern commercial aircraft rely on multiple sensors for navigation, control, and situational awareness. If a sensor becomes unreliable (e.g., due to spikes, stuck readings, or physically implausible values), downstream avionics and control systems may behave incorrectly.

This project simulates a sensor validation and fault detection pipeline using a simplified commercial flight profile with injected anomalies. The focus is on **sensor integrity and diagnostics**, not human-facing alerts.

## Signals Monitored

- Airspeed (knots)
- Altitude (feet)
- Vertical Speed (ft/min)
- Outside Air Temperature (°C)

## Fault Types Detected

- **OUT_OF_RANGE** — physically implausible sensor values
- **SPIKE** — abrupt rate-of-change exceeding allowed limits
- **STUCK** — unchanged sensor readings across multiple samples
- **INCONSISTENT** — cross-sensor inconsistency (e.g., altitude vs vertical speed)

Each time step is classified as:
- **HEALTHY**
- **SUSPECT**
- **FAILED**

## Example Output

```
=== Aircraft Sensor Fault Detection Summary ===
Samples processed: 120
Total fault events: 11
SUSPECT events: 8
FAILED events: 3

Status timeline (per sample):
  HEALTHY: 112
  SUSPECT: 5
  FAILED: 3
```

Detected fault events are logged for traceability:
```
data/fault_log.log
```

## Project Structure

```
aircraft-sensor-fault-detection/
  data/
    flight_data.csv
    fault_log.log
  src/
    __init__.py
    main.py
    models.py
    rules.py
    detector.py
    io_utils.py
    logger.py
```

### Key Components

- **models.py** — Data models for flight samples and fault events
- **rules.py** — Physics-based range, spike, and consistency checks
- **detector.py** — Core fault detection and classification logic
- **io_utils.py** — Flight data generation and CSV ingestion
- **logger.py** — Fault logging utilities
- **main.py** — Pipeline orchestration and summary output

## How to Run

From the project root:

```bash
python -m src.main
```

The program will:
1. Generate simulated commercial flight data (if not already present)
2. Inject representative sensor faults
3. Apply validation and fault detection logic
4. Print a diagnostic summary and log fault events

## Design Philosophy

This project emphasizes transparent, rule-based diagnostics rather than black-box machine learning. Such approaches are commonly used in aerospace systems where interpretability, validation, and traceability are essential for certification and safety analysis.

## Technologies Used

- Python
- Time-series data processing
- Sensor validation and fault detection logic
- Modular system architecture

## Potential Extensions

- Additional avionics signals (e.g., heading, barometric vs GPS altitude)
- Fault persistence and confidence scoring
- Visualization of sensor data with fault windows
- Unit testing and CI integration

## Author

Reagan Price
