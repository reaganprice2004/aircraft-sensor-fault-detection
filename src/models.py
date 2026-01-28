from dataclasses import dataclass


@dataclass
class FlightSample:
    timestamp: str
    airspeed_kt: float      # knots
    altitude_ft: float      # feet
    vertical_speed_fpm: float  # feet per minute
    oat_c: float            # outside air temperature (°C)


@dataclass
class FaultEvent:
    timestamp: str
    sensor: str             # "Airspeed", "Altitude", "Vertical Speed", "OAT"
    status: str             # "SUSPECT" or "FAILED"
    fault_type: str         # "OUT_OF_RANGE", "SPIKE", "STUCK", "INCONSISTENT"
    value: str
    message: str


@dataclass
class DetectionResult:
    overall_status: str     # "HEALTHY", "SUSPECT", "FAILED"
    faults: list[FaultEvent]
