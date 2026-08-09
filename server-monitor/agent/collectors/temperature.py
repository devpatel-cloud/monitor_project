import os
import glob
from typing import Dict, Any, List

def get_temperature_info() -> Dict[str, Any]:
    """
    Collects system temperatures (CPU, ACPI, NVMe/drive sensors) and fan speeds from /sys/class/hwmon and /sys/class/thermal.
    Gracefully returns status 'Unavailable' if sensors are not present.
    """
    sensors: List[Dict[str, Any]] = []
    cpu_temp = None
    fan_speed = None

    # Check thermal zones
    thermal_zones = glob.glob("/sys/class/thermal/thermal_zone*")
    for zone in thermal_zones:
        try:
            type_file = os.path.join(zone, "type")
            temp_file = os.path.join(zone, "temp")
            if os.path.exists(temp_file):
                sensor_type = "Thermal Zone"
                if os.path.exists(type_file):
                    with open(type_file, "r") as tf:
                        sensor_type = tf.read().strip()
                with open(temp_file, "r") as f:
                    temp_val = float(f.read().strip()) / 1000.0
                    sensors.append({
                        "name": sensor_type,
                        "label": os.path.basename(zone),
                        "temp_celsius": round(temp_val, 1)
                    })
                    if "x86_pkg_temp" in sensor_type.lower() or "cpu" in sensor_type.lower():
                        cpu_temp = round(temp_val, 1)
        except Exception:
            pass

    # Check hwmon sensors
    hwmon_dirs = glob.glob("/sys/class/hwmon/hwmon*")
    for hwmon in hwmon_dirs:
        try:
            name_file = os.path.join(hwmon, "name")
            hw_name = "hwmon"
            if os.path.exists(name_file):
                with open(name_file, "r") as nf:
                    hw_name = nf.read().strip()

            # Find temperature inputs
            temp_inputs = glob.glob(os.path.join(hwmon, "temp*_input"))
            for t_in in temp_inputs:
                prefix = t_in.rsplit("_", 1)[0]
                label_file = f"{prefix}_label"
                label = os.path.basename(prefix)
                if os.path.exists(label_file):
                    with open(label_file, "r") as lf:
                        label = lf.read().strip()

                with open(t_in, "r") as tf:
                    t_val = float(tf.read().strip()) / 1000.0
                    sensors.append({
                        "name": hw_name,
                        "label": label,
                        "temp_celsius": round(t_val, 1)
                    })
                    if cpu_temp is None and ("core" in label.lower() or "package" in label.lower() or "k10temp" in hw_name.lower() or "coretemp" in hw_name.lower()):
                        cpu_temp = round(t_val, 1)

            # Find fan inputs
            fan_inputs = glob.glob(os.path.join(hwmon, "fan*_input"))
            for f_in in fan_inputs:
                with open(f_in, "r") as ff:
                    fan_speed = int(ff.read().strip())
        except Exception:
            pass

    # Fallback overall CPU temp
    if cpu_temp is None and sensors:
        cpu_temp = sensors[0]["temp_celsius"]

    status = "Available" if sensors else "Unavailable"

    return {
        "status": status,
        "cpu_temp_celsius": cpu_temp if cpu_temp is not None else "Unavailable",
        "fan_speed_rpm": fan_speed if fan_speed is not None else "Unavailable",
        "sensors": sensors
    }
