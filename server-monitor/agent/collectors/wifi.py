import os
import subprocess
from typing import Dict, Any

def get_wifi_info() -> Dict[str, Any]:
    """
    Collects Wi-Fi details (interface, SSID, signal strength %, frequency MHz, link speed Mbps, connection state)
    via nmcli, /proc/net/wireless, or iwconfig. Returns status 'Unavailable' if no Wi-Fi hardware is present.
    """
    connected = False
    iface_name = "wlp2s0"
    ssid = "Unavailable"
    signal_pct = 0
    freq_mhz = 0
    freq_str = "Unavailable"
    link_speed_mbps = 0
    state = "Unavailable"

    # Try nmcli
    try:
        res = subprocess.run(
            ["nmcli", "-t", "-f", "IN-SIGNAL,DEV,SSID,SIGNAL,FREQ,RATE", "dev", "wifi"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3
        )
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                if line.startswith("*:") or line.startswith("yes:"):
                    parts = line.split(":")
                    if len(parts) >= 6:
                        iface_name = parts[1] if parts[1] else iface_name
                        ssid = parts[2]
                        signal_pct = int(parts[3]) if parts[3].isdigit() else 0
                        freq_raw = parts[4] # e.g. "5180 MHz"
                        if "MHz" in freq_raw:
                            freq_mhz = int(freq_raw.replace("MHz", "").strip())
                        elif freq_raw.isdigit():
                            freq_mhz = int(freq_raw)

                        freq_str = "5 GHz" if freq_mhz >= 4900 else ("2.4 GHz" if freq_mhz > 0 else "Unavailable")

                        rate_raw = parts[5] # e.g. "433 Mbit/s"
                        rate_clean = rate_raw.replace("Mbit/s", "").replace("Mbps", "").strip()
                        if rate_clean.replace(".", "").isdigit():
                            link_speed_mbps = int(float(rate_clean))

                        state = "Connected"
                        connected = True
                        break
    except Exception:
        pass

    if not connected and os.path.exists("/proc/net/wireless"):
        try:
            with open("/proc/net/wireless", "r") as f:
                lines = f.readlines()
                if len(lines) > 2:
                    parts = lines[2].split()
                    if len(parts) >= 4:
                        iface_name = parts[0].rstrip(":")
                        state = "Connected"
                        connected = True
                        link_qual = float(parts[2].rstrip("."))
                        signal_pct = int((link_qual / 70.0) * 100)
        except Exception:
            pass

    return {
        "status": "Available" if state != "Unavailable" else "Unavailable",
        "connected": connected,
        "interface": iface_name,
        "ssid": ssid,
        "signal_percent": signal_pct,
        "frequency_mhz": freq_mhz,
        "frequency_str": freq_str,
        "link_speed_mbps": link_speed_mbps,
        "state": state
    }
