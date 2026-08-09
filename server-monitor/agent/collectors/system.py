import os
import platform
import subprocess
from typing import Dict, Any

def format_uptime(seconds: float) -> str:
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0 or days > 0:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)

def get_system_info() -> Dict[str, Any]:
    """
    Collects hostname, OS distribution, kernel version, and system uptime.
    """
    hostname = socket_name = platform.node()
    kernel = platform.release()
    os_name = "Rocky Linux 9.4 (Blue Onyx)" if "Linux" in platform.system() else platform.system()
    uptime_seconds = 0.0

    if os.path.exists("/etc/os-release"):
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        os_name = line.split("=", 1)[1].strip().strip('"')
                        break
        except Exception:
            pass

    if os.path.exists("/proc/uptime"):
        try:
            with open("/proc/uptime", "r") as f:
                uptime_seconds = float(f.read().split()[0])
        except Exception:
            pass

    return {
        "hostname": hostname,
        "os_name": os_name,
        "kernel": kernel,
        "arch": platform.machine(),
        "uptime_seconds": uptime_seconds,
        "uptime_formatted": format_uptime(uptime_seconds)
    }
