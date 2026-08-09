import os
import socket
import subprocess
from typing import Dict, Any

def run_cmd(cmd: list) -> str:
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return ""

def get_duckdns_info(domain: str = "sanjaya-server.duckdns.org") -> Dict[str, Any]:
    """
    Inspects existing DuckDNS IPv6 setup, current host IPv6, DuckDNS AAAA DNS record,
    and checks for IPv6 vs DuckDNS record mismatch.
    Never exposes DuckDNS auth tokens.
    """
    service_exists = os.path.exists("/etc/systemd/system/duckdns-ipv6.service") or os.path.exists("/usr/lib/systemd/system/duckdns-ipv6.service")
    script_exists = os.path.exists("/usr/local/bin/duckdns-ipv6.sh")

    current_ipv6 = "Unavailable"
    duckdns_aaaa = "Unavailable"
    mismatch = False
    status = "OK"
    last_update_status = "UNKNOWN"

    # Get local primary IPv6 address
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        s.connect(("2001:4860:4860::8888", 80))
        current_ipv6 = s.getsockname()[0]
        s.close()
    except Exception:
        # Fallback to ip addr
        ip_out = run_cmd(["ip", "-6", "addr", "show", "scope", "global"])
        if ip_out:
            for line in ip_out.splitlines():
                if "inet6" in line:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        current_ipv6 = parts[1].split("/")[0]
                        break

    # Resolve DuckDNS AAAA record
    try:
        addr_info = socket.getaddrinfo(domain, None, socket.AF_INET6)
        if addr_info:
            duckdns_aaaa = addr_info[0][4][0]
    except Exception:
        pass

    # Check mismatch
    if current_ipv6 != "Unavailable" and duckdns_aaaa != "Unavailable":
        if current_ipv6.lower() != duckdns_aaaa.lower():
            mismatch = True
            status = "MISMATCH"
            last_update_status = "DNS mismatch detected: IPv6 updated but DuckDNS record out of sync"
        else:
            status = "MATCH"
            last_update_status = "Synchronized"
    elif current_ipv6 == "Unavailable":
        status = "NO_IPV6"
        last_update_status = "Local IPv6 network unavailable"
    elif duckdns_aaaa == "Unavailable":
        status = "DNS_FAILURE"
        last_update_status = "Unable to resolve DuckDNS AAAA record"

    return {
        "domain": domain,
        "service_installed": service_exists,
        "script_installed": script_exists,
        "current_ipv6": current_ipv6,
        "duckdns_aaaa": duckdns_aaaa,
        "mismatch": mismatch,
        "status": status,
        "last_update_status": last_update_status
    }
