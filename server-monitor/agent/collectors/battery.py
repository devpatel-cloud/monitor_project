import os
import glob
from typing import Dict, Any

def get_battery_info() -> Dict[str, Any]:
    """
    Collects battery percentage, state, power draw, and health from /sys/class/power_supply/BAT*.
    Gracefully returns status 'Unavailable' if no battery exists (e.g. standard server hardware).
    """
    bat_dirs = glob.glob("/sys/class/power_supply/BAT*")
    if not bat_dirs:
        return {
            "status": "Unavailable",
            "capacity_percent": 0,
            "state": "No Battery",
            "health": "N/A",
            "power_draw_watts": 0.0
        }

    bat_dir = bat_dirs[0]
    capacity = 0
    state = "Unknown"
    health = "Good"
    power_watts = 0.0

    try:
        cap_file = os.path.join(bat_dir, "capacity")
        if os.path.exists(cap_file):
            with open(cap_file, "r") as f:
                capacity = int(f.read().strip())

        status_file = os.path.join(bat_dir, "status")
        if os.path.exists(status_file):
            with open(status_file, "r") as f:
                state = f.read().strip()

        health_file = os.path.join(bat_dir, "health")
        if os.path.exists(health_file):
            with open(health_file, "r") as f:
                health = f.read().strip()

        # Voltage & Current / Power
        power_now_file = os.path.join(bat_dir, "power_now")
        if os.path.exists(power_now_file):
            with open(power_now_file, "r") as f:
                power_watts = round(float(f.read().strip()) / 1_000_000.0, 2)
    except Exception:
        pass

    return {
        "status": "Available",
        "capacity_percent": capacity,
        "state": state,
        "health": health,
        "power_draw_watts": power_watts
    }
