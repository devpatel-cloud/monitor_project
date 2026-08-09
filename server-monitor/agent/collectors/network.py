import os
import json
import socket
import time
import subprocess
from typing import Dict, Any, List

_last_network_snapshot = {
    "timestamp": 0.0,
    "rx_bytes": 0,
    "tx_bytes": 0
}

def run_cmd(cmd: List[str]) -> str:
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return ""

def get_default_gateway() -> str:
    out = run_cmd(["ip", "route", "show", "default"])
    if out:
        parts = out.split()
        if len(parts) >= 3 and parts[0] == "default" and parts[1] == "via":
            return parts[2]
    return "Unavailable"

def get_dns_servers() -> List[str]:
    dns = []
    if os.path.exists("/etc/resolv.conf"):
        try:
            with open("/etc/resolv.conf", "r") as f:
                for line in f:
                    if line.startswith("nameserver"):
                        parts = line.split()
                        if len(parts) >= 2:
                            dns.append(parts[1])
        except Exception:
            pass
    return dns if dns else ["1.1.1.1", "8.8.8.8"]

def check_internet_connectivity() -> Dict[str, Any]:
    """
    Checks external IPv4 and IPv6 internet connectivity and DNS resolution.
    """
    ipv4_online = False
    ipv6_online = False
    dns_ok = False

    # Test IPv4 connectivity
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect(("1.1.1.1", 53))
        s.close()
        ipv4_online = True
    except Exception:
        pass

    # Test IPv6 connectivity
    try:
        s6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s6.settimeout(2.0)
        s6.connect(("2606:4700:4700::1111", 53))
        s6.close()
        ipv6_online = True
    except Exception:
        pass

    # Test DNS resolution
    try:
        socket.getaddrinfo("duckdns.org", 80)
        dns_ok = True
    except Exception:
        pass

    return {
        "ipv4": ipv4_online,
        "ipv6": ipv6_online,
        "gateway": get_default_gateway() != "Unavailable",
        "internet": ipv4_online or ipv6_online,
        "dns_resolution": dns_ok
    }

def get_listening_ports() -> List[Dict[str, Any]]:
    ports = []
    output = run_cmd(["ss", "-tuln"])
    if output:
        lines = output.splitlines()
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 5:
                ports.append({"proto": parts[0], "address": parts[4]})
    return ports

def get_network_info() -> Dict[str, Any]:
    """
    Monitors network interfaces, IP addresses, RX/TX counters, default gateway, DNS,
    and calculates live real-time network traffic throughput.
    """
    global _last_network_snapshot

    interfaces: List[Dict[str, Any]] = []
    proc_net_dev: Dict[str, Dict[str, int]] = {}

    total_rx_bytes = 0
    total_tx_bytes = 0

    if os.path.exists("/proc/net/dev"):
        try:
            with open("/proc/net/dev", "r") as f:
                lines = f.readlines()
                for line in lines[2:]:
                    if ":" in line:
                        iface, data = line.split(":", 1)
                        iface = iface.strip()
                        fields = [int(x) for x in data.split()]
                        if len(fields) >= 16:
                            proc_net_dev[iface] = {
                                "rx_bytes": fields[0],
                                "rx_packets": fields[1],
                                "rx_errs": fields[2],
                                "rx_drop": fields[3],
                                "tx_bytes": fields[8],
                                "tx_packets": fields[9],
                                "tx_errs": fields[10],
                                "tx_drop": fields[11],
                            }
                            if iface != "lo":
                                total_rx_bytes += fields[0]
                                total_tx_bytes += fields[8]
        except Exception:
            pass

    # Calculate real-time traffic throughput (MB/s)
    now = time.time()
    download_mbps = 0.0
    upload_mbps = 0.0

    if _last_network_snapshot["timestamp"] > 0:
        dt = now - _last_network_snapshot["timestamp"]
        if dt > 0:
            rx_delta = max(0, total_rx_bytes - _last_network_snapshot["rx_bytes"])
            tx_delta = max(0, total_tx_bytes - _last_network_snapshot["tx_bytes"])
            download_mbps = round((rx_delta / dt) / (1024 * 1024), 2) # MB/s
            upload_mbps = round((tx_delta / dt) / (1024 * 1024), 2)   # MB/s

    _last_network_snapshot = {
        "timestamp": now,
        "rx_bytes": total_rx_bytes,
        "tx_bytes": total_tx_bytes
    }

    # Gather interfaces via ip -j addr
    ip_json = run_cmd(["ip", "-j", "addr"])
    if ip_json:
        try:
            ifaces_data = json.loads(ip_json)
            for if_info in ifaces_data:
                ifname = if_info.get("ifname", "")
                operstate = if_info.get("operstate", "DOWN").upper()
                mac = if_info.get("address", "")

                ipv4_addrs = []
                ipv6_addrs = []
                for addr_info in if_info.get("addr_info", []):
                    family = addr_info.get("family")
                    local_ip = addr_info.get("local")
                    if family == "inet":
                        ipv4_addrs.append(f"{local_ip}/{addr_info.get('prefixlen', 32)}")
                    elif family == "inet6":
                        ipv6_addrs.append(f"{local_ip}/{addr_info.get('prefixlen', 128)}")

                dev_metrics = proc_net_dev.get(ifname, {
                    "rx_bytes": 0, "rx_packets": 0, "rx_errs": 0, "rx_drop": 0,
                    "tx_bytes": 0, "tx_packets": 0, "tx_errs": 0, "tx_drop": 0
                })

                interfaces.append({
                    "name": ifname,
                    "state": operstate,
                    "mac": mac,
                    "ipv4": ipv4_addrs,
                    "ipv6": ipv6_addrs,
                    "rx_bytes": dev_metrics["rx_bytes"],
                    "tx_bytes": dev_metrics["tx_bytes"],
                    "rx_packets": dev_metrics["rx_packets"],
                    "tx_packets": dev_metrics["tx_packets"],
                    "rx_errors": dev_metrics["rx_errs"],
                    "tx_errors": dev_metrics["tx_errs"],
                    "rx_drops": dev_metrics["rx_drop"],
                    "tx_drops": dev_metrics["tx_drop"],
                })
        except Exception:
            pass

    connectivity = check_internet_connectivity()
    gateway = get_default_gateway()
    dns = get_dns_servers()
    ports = get_listening_ports()

    return {
        "interfaces": interfaces,
        "connectivity": connectivity,
        "gateway": gateway,
        "dns": dns,
        "traffic": {
            "download_mbps": download_mbps,
            "upload_mbps": upload_mbps
        },
        "listening_ports": ports
    }
