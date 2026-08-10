import os
import re
import glob
import json
import subprocess
from typing import Dict, Any, List

def run_cmd(cmd: List[str]) -> str:
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3)
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return ""

def get_temperature_info() -> Dict[str, Any]:
    """
    Collects actual system temperatures (CPU Package, Cores, ACPI, NVMe sensors) and fan speeds.
    Prioritizes real CPU hardware core/package sensors (coretemp, k10temp, Tctl, Tdie, Package id 0)
    over generic ACPI thermal zones.
    """
    sensors: List[Dict[str, Any]] = []
    cpu_temp = None
    fan_speed = None

    # Priority 1: Parse 'sensors -j' or 'sensors' output if lm_sensors is installed
    sensors_json = run_cmd(["sensors", "-j"])
    if sensors_json:
        try:
            data = json.loads(sensors_json)
            for chip_name, chip_data in data.items():
                if isinstance(chip_data, dict):
                    for label, subdata in chip_data.items():
                        if isinstance(subdata, dict):
                            for subkey, val in subdata.items():
                                if subkey.endswith("_input") and isinstance(val, (int, float)):
                                    t_val = round(float(val), 1)
                                    sensors.append({
                                        "name": chip_name,
                                        "label": label,
                                        "temp_celsius": t_val
                                    })
                                    label_lower = label.lower()
                                    chip_lower = chip_name.lower()
                                    if "package" in label_lower or "tctl" in label_lower or "tdie" in label_lower:
                                        cpu_temp = t_val
                                    elif cpu_temp is None and ("coretemp" in chip_lower or "k10temp" in chip_lower or "zenpower" in chip_lower or "cpu" in chip_lower):
                                        cpu_temp = t_val
        except Exception:
            pass

    # Priority 2: Scan /sys/class/hwmon/hwmon*
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
                    t_raw = float(tf.read().strip())
                    t_val = round(t_raw / 1000.0, 1) if t_raw > 1000 else round(t_raw, 1)
                    
                    # Avoid duplicates
                    if not any(s["label"] == label and s["name"] == hw_name for s in sensors):
                        sensors.append({
                            "name": hw_name,
                            "label": label,
                            "temp_celsius": t_val
                        })

                    label_lower = label.lower()
                    hw_lower = hw_name.lower()

                    # High priority match for real CPU package / Tctl sensor
                    if "package" in label_lower or "tctl" in label_lower or "tdie" in label_lower or "x86_pkg_temp" in label_lower:
                        cpu_temp = t_val
                    elif cpu_temp is None and ("coretemp" in hw_lower or "k10temp" in hw_lower or "zenpower" in hw_lower or "cpu" in hw_lower or "core 0" in label_lower):
                        cpu_temp = t_val

            # Find fan inputs
            fan_inputs = glob.glob(os.path.join(hwmon, "fan*_input"))
            for f_in in fan_inputs:
                with open(f_in, "r") as ff:
                    fan_speed = int(ff.read().strip())
        except Exception:
            pass

    # Priority 3: Scan /sys/class/thermal/thermal_zone*
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
                    t_raw = float(f.read().strip())
                    temp_val = round(t_raw / 1000.0, 1) if t_raw > 1000 else round(t_raw, 1)
                    
                    if not any(s["label"] == os.path.basename(zone) for s in sensors):
                        sensors.append({
                            "name": sensor_type,
                            "label": os.path.basename(zone),
                            "temp_celsius": temp_val
                        })
                    
                    if cpu_temp is None and ("x86_pkg_temp" in sensor_type.lower() or "cpu" in sensor_type.lower()):
                        cpu_temp = temp_val
        except Exception:
            pass

    # Priority 4: Windows WMI Fallback (for Windows dev hosts)
    if cpu_temp is None and os.name == "nt":
        wmi_out = run_cmd(["wmic", "/namespace:\\\\root\\wmi", "PATH", "MSAcpi_ThermalZoneTemperature", "get", "CurrentTemperature"])
        if wmi_out:
            lines = wmi_out.splitlines()
            for line in lines[1:]:
                val = line.strip()
                if val.isdigit():
                    t_kelvin = float(val) / 10.0
                    t_cel = round(t_kelvin - 273.15, 1)
                    if 0 < t_cel < 120:
                        cpu_temp = t_cel
                        sensors.append({"name": "WMI Thermal Zone", "label": "CPU", "temp_celsius": t_cel})
                        break

    # Fallback overall CPU temp
    if cpu_temp is None and sensors:
        cpu_temp = sensors[0]["temp_celsius"]

    status = "Available" if sensors or cpu_temp is not None else "Unavailable"

    return {
        "status": status,
        "cpu_temp_celsius": cpu_temp if cpu_temp is not None else "Unavailable",
        "fan_speed_rpm": fan_speed if fan_speed is not None else "Unavailable",
        "sensors": sensors
    }
