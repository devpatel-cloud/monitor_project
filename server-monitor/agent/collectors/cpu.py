import os
import time
import subprocess
from typing import Dict, Any, List

def get_cpu_info() -> Dict[str, Any]:
    """
    Collects CPU model, core counts, per-core CPU %, total CPU %, load averages,
    frequency, and CPU temperature.
    Uses Linux native /proc/stat, /proc/loadavg, /proc/cpuinfo, /sys/devices/system/cpu.
    """
    cpu_model = "Unknown CPU"
    cores_physical = os.cpu_count() or 1
    threads = os.cpu_count() or 1

    # Read /proc/cpuinfo for model name and physical core estimation
    if os.path.exists("/proc/cpuinfo"):
        try:
            with open("/proc/cpuinfo", "r") as f:
                core_ids = set()
                for line in f:
                    if line.startswith("model name"):
                        cpu_model = line.split(":")[1].strip()
                    elif line.startswith("core id"):
                        core_ids.add(line.split(":")[1].strip())
                if core_ids:
                    cores_physical = len(core_ids)
        except Exception:
            pass

    # Read load averages from /proc/loadavg
    load_1m, load_5m, load_15m = 0.0, 0.0, 0.0
    if os.path.exists("/proc/loadavg"):
        try:
            with open("/proc/loadavg", "r") as f:
                parts = f.read().split()
                load_1m = float(parts[0])
                load_5m = float(parts[1])
                load_15m = float(parts[2])
        except Exception:
            pass

    # Read per-core CPU usage from /proc/stat
    overall_usage = 0.0
    per_core_usage: List[float] = []

    if os.path.exists("/proc/stat"):
        try:
            # We sample twice quickly to compute delta CPU utilization if needed,
            # or read delta from snapshot. Here we do snapshot computation.
            def read_proc_stat():
                stats = []
                with open("/proc/stat", "r") as f:
                    for line in f:
                        if line.startswith("cpu"):
                            fields = line.split()
                            name = fields[0]
                            values = [float(x) for x in fields[1:]]
                            # user, nice, system, idle, iowait, irq, softirq, steal
                            idle = values[3] + (values[4] if len(values) > 4 else 0)
                            total = sum(values)
                            stats.append((name, idle, total))
                return stats

            s1 = read_proc_stat()
            time.sleep(0.1)
            s2 = read_proc_stat()

            s1_dict = {item[0]: (item[1], item[2]) for item in s1}
            for item in s2:
                name, idle2, total2 = item
                if name in s1_dict:
                    idle1, total1 = s1_dict[name]
                    idle_delta = idle2 - idle1
                    total_delta = total2 - total1
                    pct = 0.0
                    if total_delta > 0:
                        pct = round(100.0 * (1.0 - (idle_delta / total_delta)), 1)
                    if name == "cpu":
                        overall_usage = pct
                    else:
                        per_core_usage.append(pct)
        except Exception:
            pass

    # Read CPU frequency (MHz)
    freq_mhz = 0.0
    freq_path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
    if os.path.exists(freq_path):
        try:
            with open(freq_path, "r") as f:
                freq_mhz = round(float(f.read().strip()) / 1000.0, 1)
        except Exception:
            pass
    elif os.path.exists("/proc/cpuinfo"):
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("cpu MHz"):
                        freq_mhz = float(line.split(":")[1].strip())
                        break
        except Exception:
            pass

    return {
        "model": cpu_model,
        "cores_physical": cores_physical,
        "threads": threads,
        "usage_percent": overall_usage,
        "per_core_usage": per_core_usage,
        "load_1m": load_1m,
        "load_5m": load_5m,
        "load_15m": load_15m,
        "frequency_mhz": freq_mhz
    }
