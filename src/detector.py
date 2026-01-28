from src.models import FlightSample, FaultEvent, DetectionResult
from src.rules import (
    range_check_airspeed, range_check_altitude, range_check_vertical_speed, range_check_oat,
    spike_check, consistency_check_alt_vs_vs
)


def _to_fault(timestamp: str, hit):
    sensor, status, fault_type, value_str, message = hit
    return FaultEvent(
        timestamp=timestamp,
        sensor=sensor,
        status=status,
        fault_type=fault_type,
        value=value_str,
        message=message
    )


def detect_faults(samples: list[FlightSample]):
    overall_statuses = []
    all_faults: list[FaultEvent] = []

    # for stuck detection
    airspeed_stuck_count = 0
    last_airspeed = None

    for i in range(len(samples)):
        s = samples[i]
        faults_this_sample: list[FaultEvent] = []

        # --- Range checks (FAILED) ---
        for hit in [
            range_check_airspeed(s.airspeed_kt),
            range_check_altitude(s.altitude_ft),
            range_check_vertical_speed(s.vertical_speed_fpm),
            range_check_oat(s.oat_c),
        ]:
            if hit is not None:
                faults_this_sample.append(_to_fault(s.timestamp, hit))

        # --- Spike checks (SUSPECT), needs previous sample ---
        if i > 0:
            p = samples[i - 1]
            # max allowed per-sample jumps (simplified)
            hit = spike_check(p.airspeed_kt, s.airspeed_kt, max_delta=60.0, sensor_name="Airspeed", unit="kt")
            if hit is not None:
                faults_this_sample.append(_to_fault(s.timestamp, hit))

            hit = spike_check(p.altitude_ft, s.altitude_ft, max_delta=3000.0, sensor_name="Altitude", unit="ft")
            if hit is not None:
                faults_this_sample.append(_to_fault(s.timestamp, hit))

            hit = spike_check(p.oat_c, s.oat_c, max_delta=10.0, sensor_name="OAT", unit="°C")
            if hit is not None:
                faults_this_sample.append(_to_fault(s.timestamp, hit))

            # Consistency check between altitude change and vertical speed
            hit = consistency_check_alt_vs_vs(p.altitude_ft, s.altitude_ft, s.vertical_speed_fpm, dt_sec=1.0)
            if hit is not None:
                faults_this_sample.append(_to_fault(s.timestamp, hit))

        # --- Stuck detection for airspeed (FAILED) ---
        # If airspeed equals the previous reading repeatedly, suspect a stuck sensor.
        if last_airspeed is None:
            last_airspeed = s.airspeed_kt
            airspeed_stuck_count = 0
        else:
            if s.airspeed_kt == last_airspeed:
                airspeed_stuck_count += 1
            else:
                airspeed_stuck_count = 0
                last_airspeed = s.airspeed_kt

            if airspeed_stuck_count >= 5:
                hit = ("Airspeed", "FAILED", "STUCK", f"{s.airspeed_kt:.1f} kt", "Airspeed appears stuck (unchanged for 6 consecutive samples).")
                faults_this_sample.append(_to_fault(s.timestamp, hit))

        # Determine overall status for this sample
        status = "HEALTHY"
        if any(f.status == "FAILED" for f in faults_this_sample):
            status = "FAILED"
        elif any(f.status == "SUSPECT" for f in faults_this_sample):
            status = "SUSPECT"

        overall_statuses.append(status)
        all_faults.extend(faults_this_sample)

    return overall_statuses, all_faults


def summarize_faults(faults: list[FaultEvent]):
    summary = {
        "total": len(faults),
        "suspect": 0,
        "failed": 0,
        "by_sensor": {},
        "by_type": {},
    }

    for f in faults:
        if f.status == "SUSPECT":
            summary["suspect"] += 1
        elif f.status == "FAILED":
            summary["failed"] += 1

        summary["by_sensor"][f.sensor] = summary["by_sensor"].get(f.sensor, 0) + 1
        summary["by_type"][f.fault_type] = summary["by_type"].get(f.fault_type, 0) + 1

    return summary


def summarize_statuses(statuses: list[str]):
    summary = {"HEALTHY": 0, "SUSPECT": 0, "FAILED": 0}
    for s in statuses:
        if s in summary:
            summary[s] += 1
    return summary
