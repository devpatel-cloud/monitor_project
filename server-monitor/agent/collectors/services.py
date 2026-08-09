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
    Queries systemctl is-active and is-enabled for a systemd service.
    Special handling: if service is oneshot (e.g. duckdns-ipv6), checks duckdns-ipv6.timer.
    """
    state = "UNKNOWN"
    enabled = False
    is_timer_active = False

    # Special handling for oneshot timer services
    if service_name == "duckdns-ipv6" or service_name == "duckdns-ipv6.service":
        try:
            res_timer = subprocess.run(
                ["systemctl", "is-active", "duckdns-ipv6.timer"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3
            )
            if res_timer.stdout.strip() in ["active", "activating"]:
                is_timer_active = True
        except Exception:
            pass

    try:
        res = subprocess.run(
            ["systemctl", "is-active", service_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3
        )
        stdout = res.stdout.strip()
        if stdout == "active":
            state = "RUNNING"
        elif stdout == "inactive":
            # If oneshot service is inactive but its timer is active, treat as RUNNING/SCHEDULED (Healthy!)
            state = "RUNNING" if is_timer_active else "STOPPED"
        elif stdout == "failed":
            state = "FAILED"
        elif stdout in ["activating", "reloading"]:
            state = "STARTING"
        else:
            state = "RUNNING" if is_timer_active else "STOPPED"

        res_en = subprocess.run(
            ["systemctl", "is-enabled", service_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3
        )
        if res_en.stdout.strip() in ["enabled", "linked", "static"]:
            enabled = True
    except Exception:
        state = "RUNNING" if is_timer_active else "UNKNOWN"

    return {
        "name": service_name,
        "state": state,
        "enabled": enabled,
        "timer_active": is_timer_active if service_name.startswith("duckdns") else None
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
