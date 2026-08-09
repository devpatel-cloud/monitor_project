import subprocess
from typing import Dict, Any, List

DEFAULT_SERVICES = [
    "nginx",
    "docker",
    "sshd",
    "NetworkManager",
    "chronyd",
    "firewalld",
    "server-monitor",
    "duckdns-ipv6"
]

def check_service_status(service_name: str) -> Dict[str, Any]:
    """
    Queries systemctl is-active and systemctl is-failed for a systemd service.
    """
    state = "UNKNOWN"
    sub_state = "unknown"
    enabled = False

    try:
        res = subprocess.run(
            ["systemctl", "is-active", service_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3
        )
        stdout = res.stdout.strip()
        if stdout == "active":
            state = "RUNNING"
        elif stdout == "inactive":
            state = "STOPPED"
        elif stdout == "failed":
            state = "FAILED"
        elif stdout == "activating" or stdout == "reloading":
            state = "STARTING"
        else:
            state = "STOPPED"

        # Check if enabled
        res_en = subprocess.run(
            ["systemctl", "is-enabled", service_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3
        )
        if res_en.stdout.strip() == "enabled":
            enabled = True
    except Exception:
        state = "UNKNOWN"

    return {
        "name": service_name,
        "state": state,
        "enabled": enabled
    }

def get_services_info(custom_services: List[str] = None) -> Dict[str, Any]:
    """
    Monitors list of systemd services and returns detailed status map.
    """
    service_list = custom_services if custom_services else DEFAULT_SERVICES
    services: List[Dict[str, Any]] = []

    running_count = 0
    stopped_count = 0
    failed_count = 0

    for svc in service_list:
        info = check_service_status(svc)
        services.append(info)
        if info["state"] == "RUNNING":
            running_count += 1
        elif info["state"] == "FAILED":
            failed_count += 1
        else:
            stopped_count += 1

    return {
        "total": len(services),
        "running": running_count,
        "stopped": stopped_count,
        "failed": failed_count,
        "services": services
    }
