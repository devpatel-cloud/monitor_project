import os
from typing import Dict, Any, List

def get_disk_io_info() -> Dict[str, Any]:
    """
    Parses /proc/diskstats for read/write operations, sectors, IO time, and IO wait.
    """
    devices: List[Dict[str, Any]] = []
    total_read_bytes = 0
    total_write_bytes = 0
    total_read_ops = 0
    total_write_ops = 0

    if os.path.exists("/proc/diskstats"):
        try:
            with open("/proc/diskstats", "r") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 14:
                        dev_name = parts[2]
                        # Filter out loop, ram, and partition devices (e.g. sda1 vs sda, nvme0n1p1 vs nvme0n1)
                        if dev_name.startswith("loop") or dev_name.startswith("ram") or dev_name.startswith("sr"):
                            continue

                        read_ops = int(parts[3])
                        read_sectors = int(parts[5])
                        write_ops = int(parts[7])
                        write_sectors = int(parts[9])
                        io_time_ms = int(parts[12])
                        weighted_io_time_ms = int(parts[13])

                        read_bytes = read_sectors * 512
                        write_bytes = write_sectors * 512

                        # Only include disk devices or significant devices
                        devices.append({
                            "device": dev_name,
                            "read_ops": read_ops,
                            "write_ops": write_ops,
                            "read_bytes": read_bytes,
                            "write_bytes": write_bytes,
                            "io_time_ms": io_time_ms,
                            "io_wait_ms": weighted_io_time_ms
                        })

                        total_read_ops += read_ops
                        total_write_ops += write_ops
                        total_read_bytes += read_bytes
                        total_write_bytes += write_bytes
        except Exception:
            pass

    return {
        "total_read_ops": total_read_ops,
        "total_write_ops": total_write_ops,
        "total_read_bytes": total_read_bytes,
        "total_write_bytes": total_write_bytes,
        "devices": devices
    }
