from typing import Dict, Any, List

def calculate_health_score(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes an overall 0-100 Server Health Score based on weighted metrics & subsystem states.
    Returns overall score, status string ('HEALTHY', 'DEGRADED', 'CRITICAL'), and breakdown factors.
    """
    factors: List[Dict[str, Any]] = []
    deductions = 0.0

    # CPU penalty
    cpu_usage = snapshot.get("cpu", {}).get("usage_percent", 0.0)
    if cpu_usage > 95.0:
        deductions += 25
        factors.append({"name": "CPU Usage", "impact": -25, "reason": f"CPU usage critically high at {cpu_usage}%"})
    elif cpu_usage > 85.0:
        deductions += 10
        factors.append({"name": "CPU Usage", "impact": -10, "reason": f"CPU usage elevated at {cpu_usage}%"})

    # Memory penalty
    mem_usage = snapshot.get("memory", {}).get("usage_percent", 0.0)
    if mem_usage > 95.0:
        deductions += 25
        factors.append({"name": "Memory", "impact": -25, "reason": f"Memory usage critical at {mem_usage}%"})
    elif mem_usage > 85.0:
        deductions += 10
        factors.append({"name": "Memory", "impact": -10, "reason": f"Memory usage elevated at {mem_usage}%"})

    # Storage penalty
    partitions = snapshot.get("storage", {}).get("partitions", [])
    for p in partitions:
        pct = p.get("usage_percent", 0.0)
        mnt = p.get("mount_point", "")
        if pct > 95.0:
            deductions += 20
            factors.append({"name": f"Storage {mnt}", "impact": -20, "reason": f"{mnt} disk nearly full ({pct}%)"})
        elif pct > 85.0:
            deductions += 10
            factors.append({"name": f"Storage {mnt}", "impact": -10, "reason": f"{mnt} disk elevated ({pct}%)"})

    # Temperature penalty
    cpu_temp = snapshot.get("temperature", {}).get("cpu_temp_celsius")
    if isinstance(cpu_temp, (int, float)):
        if cpu_temp >= 90.0:
            deductions += 25
            factors.append({"name": "Temperature", "impact": -25, "reason": f"CPU overheating ({cpu_temp}°C)"})
        elif cpu_temp >= 80.0:
            deductions += 10
            factors.append({"name": "Temperature", "impact": -10, "reason": f"CPU warm ({cpu_temp}°C)"})

    # Services penalty
    services_failed = snapshot.get("services", {}).get("failed", 0)
    if services_failed > 0:
        deductions += (services_failed * 15)
        factors.append({"name": "Systemd Services", "impact": -(services_failed * 15), "reason": f"{services_failed} systemd service(s) failed"})

    # SMART penalty
    disks = snapshot.get("storage", {}).get("disks", [])
    for d in disks:
        if d.get("smart_health") == "FAILED":
            deductions += 30
            factors.append({"name": "SMART Health", "impact": -30, "reason": f"Disk {d.get('device')} failed SMART"})

    # DuckDNS Mismatch penalty
    if snapshot.get("duckdns", {}).get("mismatch"):
        deductions += 10
        factors.append({"name": "DuckDNS IPv6", "impact": -10, "reason": "IPv6 / DuckDNS AAAA mismatch"})

    # Internet Connectivity penalty
    conn = snapshot.get("network", {}).get("connectivity", {})
    if not conn.get("ipv4_online") and not conn.get("ipv6_online"):
        deductions += 30
        factors.append({"name": "Internet", "impact": -30, "reason": "No public internet connectivity"})

    score = max(0, int(round(100.0 - deductions)))

    if score >= 85:
        status_str = "HEALTHY"
    elif score >= 60:
        status_str = "DEGRADED"
    else:
        status_str = "CRITICAL"

    if not factors:
        factors.append({"name": "All Systems Nominal", "impact": 0, "reason": "All monitored subsystems operating within normal parameters"})

    return {
        "score": score,
        "status": status_str,
        "deductions": deductions,
        "breakdown": factors
    }
