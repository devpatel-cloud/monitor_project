import os
import re
import subprocess
from typing import Dict, Any, Optional

def run_cmd(cmd: list, timeout: int = 4) -> str:
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return ""

def parse_iw_link(iface: str) -> Dict[str, Any]:
    """
    Parses 'iw dev <iface> link' output to extract SSID, freq, signal dBm/pct, bitrates, and RX/TX bytes.
    Example iw link output:
    Connected to 00:11:22:33:44:55 (on wlp2s0)
        SSID: AKSHAR BHUVAN_2.4g
        freq: 2422.0
        RX: 257315490 bytes (792783 packets)
        TX: 55150744 bytes (187869 packets)
        signal: -41 dBm
        rx bitrate: 39.0 MBit/s
        tx bitrate: 58.5 MBit/s
    """
    out = run_cmd(["iw", "dev", iface, "link"])
    if not out or "Not connected" in out or "command failed" in out:
        return {
            "connected": False,
            "ssid": "",
            "freq_mhz": 0,
            "signal_dbm": 0.0,
            "signal_pct": 0,
            "bitrate_mbps": 0,
            "rx_bytes": 0,
            "tx_bytes": 0
        }

    connected = "Connected to" in out or "SSID:" in out
    ssid = ""
    freq_mhz = 0
    signal_dbm = 0.0
    signal_pct = 0
    bitrate_mbps = 0
    rx_bytes = 0
    tx_bytes = 0

    for line in out.splitlines():
        line_str = line.strip()
        if line_str.startswith("SSID:"):
            ssid = line_str.split("SSID:", 1)[1].strip()
        elif line_str.startswith("freq:"):
            try:
                freq_val = line_str.split("freq:", 1)[1].strip().split()[0]
                freq_mhz = int(float(freq_val))
            except Exception:
                pass
        elif line_str.startswith("signal:"):
            try:
                sig_val = line_str.split("signal:", 1)[1].strip().split()[0]
                signal_dbm = float(sig_val)
                # Convert dBm (-100 to -50) to 0-100% range
                signal_pct = max(0, min(100, int(2 * (signal_dbm + 100))))
            except Exception:
                pass
        elif "bitrate:" in line_str:
            try:
                # e.g. tx bitrate: 58.5 MBit/s or rx bitrate: 39.0 MBit/s
                rate_str = line_str.split("bitrate:", 1)[1].strip().split()[0]
                rate_val = int(float(rate_str))
                if rate_val > bitrate_mbps:
                    bitrate_mbps = rate_val
            except Exception:
                pass
        elif line_str.startswith("RX:"):
            # e.g. RX: 257315490 bytes (792783 packets)
            m = re.search(r"RX:\s*(\d+)\s*bytes", line_str)
            if m:
                rx_bytes = int(m.group(1))
        elif line_str.startswith("TX:"):
            # e.g. TX: 55150744 bytes (187869 packets)
            m = re.search(r"TX:\s*(\d+)\s*bytes", line_str)
            if m:
                tx_bytes = int(m.group(1))

    return {
        "connected": connected,
        "ssid": ssid,
        "freq_mhz": freq_mhz,
        "signal_dbm": signal_dbm,
        "signal_pct": signal_pct,
        "bitrate_mbps": bitrate_mbps,
        "rx_bytes": rx_bytes,
        "tx_bytes": tx_bytes
    }

def detect_wifi_interface() -> Optional[str]:
    """
    Dynamically finds the Wi-Fi interface name (e.g. wlp2s0, wlan0).
    """
    # Method 1: nmcli dev
    nm_out = run_cmd(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE", "dev"])
    if nm_out:
        for line in nm_out.splitlines():
            parts = line.split(":")
            if len(parts) >= 2 and parts[1].lower() == "wifi":
                return parts[0]

    # Method 2: iw dev
    iw_out = run_cmd(["iw", "dev"])
    if iw_out:
        for line in iw_out.splitlines():
            line_str = line.strip()
            if line_str.startswith("Interface "):
                return line_str.split("Interface ", 1)[1].strip()

    # Method 3: /sys/class/net
    if os.path.exists("/sys/class/net"):
        try:
            for iface in os.listdir("/sys/class/net"):
                if os.path.exists(f"/sys/class/net/{iface}/wireless") or iface.startswith("wlp") or iface.startswith("wlan"):
                    return iface
        except Exception:
            pass

    return None

def chan_to_freq_mhz(chan_str: str) -> int:
    try:
        chan = int(chan_str)
        if 1 <= chan <= 13:
            return 2407 + (chan * 5)
        elif chan == 14:
            return 2484
        elif 36 <= chan <= 165:
            return 5000 + (chan * 5)
    except Exception:
        pass
    return 0

def get_wifi_info() -> Dict[str, Any]:
    """
    Collects Wi-Fi details (interface, SSID, signal %, frequency MHz, link speed Mbps, state)
    dynamically using nmcli and iw enrichment/fallback.
    """
    iface = detect_wifi_interface()

    if not iface:
        return {
            "status": "Unavailable",
            "connected": False,
            "interface": "Unavailable",
            "ssid": "Unavailable",
            "signal_percent": 0,
            "frequency_mhz": 0,
            "frequency_str": "Unavailable",
            "link_speed_mbps": 0,
            "state": "Unavailable"
        }

    connected = False
    ssid = "Unavailable"
    signal_pct = 0
    freq_mhz = 0
    freq_str = "Unavailable"
    link_speed_mbps = 0
    state = "Disconnected"

    # Step 1: Check iw link for the interface
    iw_data = parse_iw_link(iface)
    if iw_data["connected"]:
        connected = True
        state = "Connected"
        if iw_data["ssid"]:
            ssid = iw_data["ssid"]
        freq_mhz = iw_data["freq_mhz"]
        signal_pct = iw_data["signal_pct"]
        link_speed_mbps = iw_data["bitrate_mbps"]

    # Step 2: Enrich/Fallback via nmcli dev status
    nm_dev_out = run_cmd(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "dev"])
    if nm_dev_out:
        for line in nm_dev_out.splitlines():
            parts = line.split(":")
            if len(parts) >= 4 and parts[0] == iface and parts[1].lower() == "wifi":
                if parts[2].lower() == "connected":
                    connected = True
                    state = "Connected"
                    if parts[3] and parts[3] != "--" and (ssid == "Unavailable" or not ssid):
                        ssid = parts[3]

    # Step 3: Enrich via nmcli dev wifi (handling format active,ssid,signal,chan,rate)
    nm_wifi_out = run_cmd(["nmcli", "-t", "-f", "ACTIVE,SSID,SIGNAL,CHAN,RATE", "dev", "wifi"])
    if nm_wifi_out:
        for line in nm_wifi_out.splitlines():
            if line.startswith("yes:") or line.startswith("*:") or line.startswith("active:yes"):
                parts = line.split(":")
                if len(parts) >= 5:
                    nm_active = parts[0]
                    nm_ssid = parts[1]
                    nm_sig = parts[2]
                    nm_chan = parts[3]
                    nm_rate = parts[4]

                    connected = True
                    state = "Connected"

                    if nm_ssid and nm_ssid != "--" and (ssid == "Unavailable" or not ssid):
                        ssid = nm_ssid
                    if nm_sig.isdigit() and int(nm_sig) > 0:
                        signal_pct = int(nm_sig)

                    # Extract frequency from channel if freq_mhz is not yet known
                    if freq_mhz == 0 and nm_chan.isdigit():
                        freq_mhz = chan_to_freq_mhz(nm_chan)

                    # Extract rate e.g. "130 Mbit/s"
                    rate_clean = nm_rate.replace("Mbit/s", "").replace("Mbps", "").strip()
                    try:
                        rate_val = int(float(rate_clean))
                        if rate_val > link_speed_mbps:
                            link_speed_mbps = rate_val
                    except Exception:
                        pass
                    break

    # Determine frequency string
    if freq_mhz >= 4900:
        freq_str = "5 GHz"
    elif freq_mhz > 0:
        freq_str = "2.4 GHz"
    else:
        freq_str = "Unavailable"

    return {
        "status": "Available",
        "connected": connected,
        "interface": iface,
        "ssid": ssid if connected else "Unavailable",
        "signal_percent": signal_pct if connected else 0,
        "frequency_mhz": freq_mhz if connected else 0,
        "frequency_str": freq_str if connected else "Unavailable",
        "link_speed_mbps": link_speed_mbps if connected else 0,
        "state": state
    }
