import os
import subprocess
from typing import Dict, Any

def get_wifi_info() -> Dict[str, Any]:
    """
    Collects Wi-Fi details (SSID, signal strength, frequency, bitrate, connection state)
    via nmcli or /proc/net/wireless. Returns status 'Unavailable' if no Wi-Fi hardware is present.
    """
    ssid = "Unavailable"
    signal_pct = 0
    frequency = "Unavailable"
    bitrate = "Unavailable"
    state = "Unavailable"

    # Try nmcli
    try:
        res = subprocess.run(
            ["nmcli", "-t", "-f", "ACTIVE,SSID,SIGNAL,FREQ,RATE", "dev", "wifi"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3
        )
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                if line.startswith("yes:"):
                    parts = line.split(":")
                    if len(parts) >= 5:
                        ssid = parts[1]
                        signal_pct = int(parts[2]) if parts[2].isdigit() else 0
                        frequency = parts[3]
                        bitrate = parts[4]
                        state = "Connected"
                        break
    except Exception:
        pass

    if state == "Unavailable" and os.path.exists("/proc/net/wireless"):
        try:
            with open("/proc/net/wireless", "r") as f:
                lines = f.readlines()
                if len(lines) > 2:
                    parts = lines[2].split()
                    if len(parts) >= 4:
                        state = "Connected"
                        # Link quality estimation
                        link_qual = float(parts[2].rstrip("."))
                        signal_pct = int((link_qual / 70.0) * 100)
        except Exception:
            pass

    return {
        "status": "Available" if state != "Unavailable" else "Unavailable",
        "ssid": ssid,
        "signal_percent": signal_pct,
        "frequency": frequency,
        "bitrate": bitrate,
        "state": state
    }
