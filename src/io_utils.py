import csv
import random

from src.models import FlightSample


def read_flight_csv(path: str):
    samples = []

    with open(path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            samples.append(
                FlightSample(
                    timestamp=row["timestamp"],
                    airspeed_kt=float(row["airspeed_kt"]),
                    altitude_ft=float(row["altitude_ft"]),
                    vertical_speed_fpm=float(row["vertical_speed_fpm"]),
                    oat_c=float(row["oat_c"]),
                )
            )

    return samples


def generate_sample_flight_csv(path: str, n: int = 120):
    """
    Generates simplified commercial-flight-like data with injected sensor faults:
      - airspeed spike
      - altitude spike
      - OAT out-of-range
      - airspeed stuck segment
      - altitude/vs inconsistency
    """
    random.seed(11)

    fieldnames = ["timestamp", "airspeed_kt", "altitude_ft", "vertical_speed_fpm", "oat_c"]

    rows = []

    # Basic flight profile: climb then cruise
    airspeed = 140.0
    altitude = 0.0
    vs = 1500.0  # fpm
    oat = 15.0

    for i in range(n):
        t = f"t{i:03d}"

        # simple phases
        if i < 40:  # takeoff/climb
            airspeed += random.uniform(1.0, 3.0)
            vs = 1500.0 + random.uniform(-150, 150)
            altitude += vs / 60.0
            oat -= random.uniform(0.05, 0.15)  # cooling as altitude increases
        else:  # cruise-ish
            airspeed += random.uniform(-1.5, 1.5)
            vs = random.uniform(-200, 200)
            altitude += vs / 60.0
            oat += random.uniform(-0.05, 0.05)

        # add noise
        airspeed_meas = airspeed + random.uniform(-2.0, 2.0)
        altitude_meas = altitude + random.uniform(-25.0, 25.0)
        vs_meas = vs + random.uniform(-80.0, 80.0)
        oat_meas = oat + random.uniform(-0.5, 0.5)

        rows.append({
            "timestamp": t,
            "airspeed_kt": round(airspeed_meas, 1),
            "altitude_ft": round(altitude_meas, 1),
            "vertical_speed_fpm": round(vs_meas, 1),
            "oat_c": round(oat_meas, 1),
        })

    # Inject faults
    if n >= 100:
        # 1) Airspeed spike (suspect)
        rows[30]["airspeed_kt"] = rows[29]["airspeed_kt"] + 120.0

        # 2) Altitude spike (suspect)
        rows[55]["altitude_ft"] = rows[54]["altitude_ft"] + 8000.0

        # 3) OAT out-of-range (failed)
        rows[70]["oat_c"] = 95.0

        # 4) Airspeed stuck (failed): same value for 6 samples
        stuck_val = rows[80]["airspeed_kt"]
        for k in range(81, 87):
            rows[k]["airspeed_kt"] = stuck_val

        # 5) Altitude/VS inconsistency (suspect)
        rows[95]["vertical_speed_fpm"] = 5000.0  # implies big climb
        # but keep altitude almost unchanged -> inconsistency
        rows[95]["altitude_ft"] = rows[94]["altitude_ft"] + 50.0

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
