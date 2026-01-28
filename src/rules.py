def _mk(sensor: str, status: str, fault_type: str, value_str: str, message: str):
    return (sensor, status, fault_type, value_str, message)


def range_check_airspeed(airspeed_kt: float):
    # Commercial aviation plausible range (very simplified)
    if airspeed_kt < 0:
        return _mk("Airspeed", "FAILED", "OUT_OF_RANGE", f"{airspeed_kt:.1f} kt", "Airspeed is negative (physically impossible).")
    if airspeed_kt > 650:
        return _mk("Airspeed", "FAILED", "OUT_OF_RANGE", f"{airspeed_kt:.1f} kt", "Airspeed exceeds plausible commercial aircraft range (> 650 kt).")
    return None


def range_check_altitude(altitude_ft: float):
    if altitude_ft < -1000:
        return _mk("Altitude", "FAILED", "OUT_OF_RANGE", f"{altitude_ft:.1f} ft", "Altitude is implausibly low (< -1000 ft).")
    if altitude_ft > 60000:
        return _mk("Altitude", "FAILED", "OUT_OF_RANGE", f"{altitude_ft:.1f} ft", "Altitude exceeds plausible commercial aircraft range (> 60,000 ft).")
    return None


def range_check_vertical_speed(vertical_speed_fpm: float):
    # Very simplified plausible vertical speed for commercial aircraft
    if vertical_speed_fpm < -12000 or vertical_speed_fpm > 12000:
        return _mk("Vertical Speed", "FAILED", "OUT_OF_RANGE", f"{vertical_speed_fpm:.0f} fpm", "Vertical speed exceeds plausible limits (>|12,000| fpm).")
    return None

def range_check_oat(oat_c: float):
    # Outside air temperature plausible range (very broad)
    if oat_c < -90 or oat_c > 60:
        return _mk("OAT", "FAILED", "OUT_OF_RANGE", f"{oat_c:.1f}°C", "Outside air temperature is outside plausible atmospheric range.")
    return None


def spike_check(prev_val: float, curr_val: float, max_delta: float, sensor_name: str, unit: str):
    delta = abs(curr_val - prev_val)
    if delta > max_delta:
        return _mk(
            sensor_name,
            "SUSPECT",
            "SPIKE",
            f"{curr_val:.1f} {unit}",
            f"Detected abrupt change: Δ={delta:.1f} {unit} exceeds max allowed Δ={max_delta:.1f} {unit} per sample."
        )
    return None


def consistency_check_alt_vs_vs(prev_alt_ft: float, curr_alt_ft: float, vertical_speed_fpm: float, dt_sec: float = 1.0):
    # vertical_speed_fpm implies expected altitude change approx (fpm * minutes)
    expected_delta = vertical_speed_fpm * (dt_sec / 60.0)
    actual_delta = curr_alt_ft - prev_alt_ft

    # Allow some tolerance for noise/rounding
    tolerance_ft = 300.0

    if abs(actual_delta - expected_delta) > tolerance_ft:
        return _mk(
            "Altitude/Vertical Speed",
            "SUSPECT",
            "INCONSISTENT",
            f"Δalt={actual_delta:.1f} ft, VS={vertical_speed_fpm:.0f} fpm",
            "Altitude change is inconsistent with reported vertical speed (exceeds tolerance)."
        )
    return None
