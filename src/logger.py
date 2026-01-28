from src.models import FaultEvent


def write_fault_log(path: str, faults: list[FaultEvent]):
    file = open(path, "w", encoding="utf-8")
    file.write("timestamp\tstatus\tsensor\tfault_type\tvalue\tmessage\n")

    for f in faults:
        file.write(f"{f.timestamp}\t{f.status}\t{f.sensor}\t{f.fault_type}\t{f.value}\t{f.message}\n")

    file.close()
