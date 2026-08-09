import os
import json
import socket
import subprocess
from typing import Dict, Any, List

def run_cmd(cmd: List[str]) -> str:
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return ""

def check_internet_connectivity() -> Dict[str, Any]:
    """
    Checks external IPv4 and IPv6 internet connectivity and DNS resolution.
    """
    ipv4_online = False
    ipv6_online = False
    dns_ok = False
    latency_ms = 0.0

    # Test IPv4 connectivity & latency
    try:
        start = socket.get_addrinfo("1.1.1.1", 53, socket.AF_INET)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        t0 = socket.get_addrinfo("1.1.1.1", 80, socket.AF_INET)
        s.connect(("1.1.1.1", 80))
        s.close()
        ipv4_online = True
    except Exception:
        pass

    # Test IPv6 connectivity (Google IPv6 DNS / Cloudflare IPv6 DNS)
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
        t_start = socket.get_addrinfo("duckdns.org", 80)
        dns_ok = True
    except Exception:
        pass

    return {
        "ipv4_online": ipv4_online,
        "ipv6_online": ipv6_online,
        "dns_resolution": dns_ok
    }

def get_listening_ports() -> List[Dict[str, Any]]:
    """
    Parses listening TCP/UDP ports via ss -tuln.
    """
    ports = []
    output = run_cmd(["ss", "-tuln"])
    if output:
        lines = output.splitlines()
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 5:
                proto = parts[0]
                local_addr = parts[4]
                ports.append({"proto": proto, "address": local_addr})
    return ports

def get_network_info() -> Dict[str, Any]:
    """
    Monitors all network interfaces (wlp2s0, enp*, docker0, lo, veth*),
    IP addresses, RX/TX counters, drops, listening ports, and internet availability.
    """
    interfaces: List[Dict[str, Any]] = []

    # Read /proc/net/dev for RX/TX metrics
    proc_net_dev: Dict[str, Dict[str, int]] = {}
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
        except Exception:
            pass

    # Gather interface addresses via ip -j addr
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
    listening_ports = get_listening_ports()

    return {
        "interfaces": interfaces,
        "connectivity": connectivity,
        "listening_ports": listening_ports
    }
