import os

from src.io_utils import read_flight_csv, generate_sample_flight_csv
from src.detector import detect_faults, summarize_faults, summarize_statuses
from src.logger import write_fault_log


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    csv_path = os.path.join(data_dir, "flight_data.csv")
    log_path = os.path.join(data_dir, "fault_log.log")

    if not os.path.exists(csv_path):
        generate_sample_flight_csv(csv_path, n=120)
        print(f"Generated sample flight data at: {csv_path}")

    samples = read_flight_csv(csv_path)

    statuses, faults = detect_faults(samples)

    write_fault_log(log_path, faults)

    fault_summary = summarize_faults(faults)
    status_summary = summarize_statuses(statuses)

    print("\n=== Aircraft Sensor Fault Detection Summary ===")
    print(f"Samples processed: {len(samples)}")
    print(f"Total fault events: {fault_summary['total']}")
    print(f"SUSPECT events: {fault_summary['suspect']}")
    print(f"FAILED events: {fault_summary['failed']}")

    print("\nStatus timeline (per sample):")
    print(f"  HEALTHY: {status_summary['HEALTHY']}")
    print(f"  SUSPECT: {status_summary['SUSPECT']}")
    print(f"  FAILED: {status_summary['FAILED']}")

    print("\nFaults by sensor:")
    for sensor in fault_summary["by_sensor"]:
        print(f"  - {sensor}: {fault_summary['by_sensor'][sensor]}")

    print("\nFaults by type:")
    for t in fault_summary["by_type"]:
        print(f"  - {t}: {fault_summary['by_type'][t]}")

    print(f"\nFault log written to: {log_path}")

    if len(faults) > 0:
        print("\nFirst 10 fault events:")
        for f in faults[:10]:
            print(f"{f.timestamp} | {f.status} | {f.sensor} | {f.fault_type} | {f.value} | {f.message}")
    else:
        print("\nNo faults detected.")


if __name__ == "__main__":
    main()
