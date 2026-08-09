import time
import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.database.models import AlertRecord

class AlertEngine:
    """
    Evaluates system metrics against configured thresholds and generates/resolves alerts.
    Supports hysteresis to prevent false alarms from temporary spikes.
    """
    def __init__(self):
        self._cpu_high_since = None
        self._ram_high_since = None

    def evaluate_snapshot(self, db: Session, snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
        active_alerts: List[Dict[str, Any]] = []
        now = snapshot.get("timestamp", time.time())

        # 1. CPU Evaluation (CPU > 90% for sustained duration)
        cpu_usage = snapshot.get("cpu", {}).get("usage_percent", 0.0)
        if cpu_usage >= 90.0:
            if self._cpu_high_since is None:
                self._cpu_high_since = now
            elif now - self._cpu_high_since >= 30: # 30 seconds threshold
                active_alerts.append({
                    "subsystem": "CPU",
                    "severity": "CRITICAL" if cpu_usage > 95.0 else "WARNING",
                    "title": "High CPU Utilization",
                    "message": f"CPU usage is at {cpu_usage}% (threshold: 90%)"
                })
        else:
            self._cpu_high_since = None

        # 2. RAM Evaluation (RAM > 90%)
        ram_usage = snapshot.get("memory", {}).get("usage_percent", 0.0)
        if ram_usage >= 90.0:
            active_alerts.append({
                "subsystem": "Memory",
                "severity": "CRITICAL" if ram_usage > 95.0 else "WARNING",
                "title": "High Memory Utilization",
                "message": f"RAM usage is at {ram_usage}% (threshold: 90%)"
            })

        # 3. Storage & Inode Evaluation (Disk > 85%, > 95%)
        partitions = snapshot.get("storage", {}).get("partitions", [])
        for p in partitions:
            mount = p.get("mount_point", "")
            pct = p.get("usage_percent", 0.0)
            if pct >= 95.0:
                active_alerts.append({
                    "subsystem": "Storage",
                    "severity": "CRITICAL",
                    "title": f"Disk Usage Critical on {mount}",
                    "message": f"{mount} disk usage is at {pct}%"
                })
            elif pct >= 85.0:
                active_alerts.append({
                    "subsystem": "Storage",
                    "severity": "WARNING",
                    "title": f"Disk Usage Warning on {mount}",
                    "message": f"{mount} disk usage is at {pct}%"
                })

        # 4. SMART Health
        disks = snapshot.get("storage", {}).get("disks", [])
        for d in disks:
            smart_health = d.get("smart_health", "")
            if smart_health == "FAILED":
                active_alerts.append({
                    "subsystem": "SMART",
                    "severity": "CRITICAL",
                    "title": f"SMART Drive Health Failure on {d.get('device')}",
                    "message": f"Physical disk {d.get('device')} ({d.get('model')}) failed SMART diagnostics!"
                })

        # 5. Temperature (Temp > 80°C warning, > 90°C critical)
        cpu_temp = snapshot.get("temperature", {}).get("cpu_temp_celsius")
        if isinstance(cpu_temp, (int, float)):
            if cpu_temp >= 90.0:
                active_alerts.append({
                    "subsystem": "Temperature",
                    "severity": "CRITICAL",
                    "title": "CPU Overheating Critical",
                    "message": f"CPU temperature is {cpu_temp}°C (critical > 90°C)"
                })
            elif cpu_temp >= 80.0:
                active_alerts.append({
                    "subsystem": "Temperature",
                    "severity": "WARNING",
                    "title": "CPU High Temperature",
                    "message": f"CPU temperature is {cpu_temp}°C (warning > 80°C)"
                })

        # 6. Services Evaluation (nginx, docker, sshd)
        services = snapshot.get("services", {}).get("services", [])
        for svc in services:
            name = svc.get("name")
            state = svc.get("state")
            if state in ["STOPPED", "FAILED"]:
                severity = "CRITICAL" if name in ["nginx", "docker", "sshd"] else "WARNING"
                active_alerts.append({
                    "subsystem": "Services",
                    "severity": severity,
                    "title": f"Service {name} is {state}",
                    "message": f"Systemd service '{name}' is currently {state}"
                })

        # 7. DuckDNS & IPv6 Mismatch
        duckdns = snapshot.get("duckdns", {})
        if duckdns.get("mismatch"):
            active_alerts.append({
                "subsystem": "DuckDNS",
                "severity": "WARNING",
                "title": "DuckDNS IPv6 Mismatch",
                "message": f"Current IPv6 ({duckdns.get('current_ipv6')}) does not match DuckDNS AAAA ({duckdns.get('duckdns_aaaa')})"
            })

        # 8. Internet Connectivity
        connectivity = snapshot.get("network", {}).get("connectivity", {})
        if not connectivity.get("ipv4_online") and not connectivity.get("ipv6_online"):
            active_alerts.append({
                "subsystem": "Network",
                "severity": "CRITICAL",
                "title": "Internet Connection Lost",
                "message": "Both IPv4 and IPv6 internet connectivity tests failed"
            })

        # 9. Battery < 20%
        battery = snapshot.get("battery", {})
        if battery.get("status") == "Available":
            cap = battery.get("capacity_percent", 100)
            b_state = battery.get("state", "")
            if cap < 20 and b_state == "Discharging":
                active_alerts.append({
                    "subsystem": "Battery",
                    "severity": "WARNING",
                    "title": "Low Battery Warning",
                    "message": f"Battery charge is down to {cap}% while discharging"
                })

        # Record active alerts into SQLite if not already recorded
        for alt in active_alerts:
            existing = db.query(AlertRecord).filter(
                AlertRecord.title == alt["title"],
                AlertRecord.resolved == False
            ).first()
            if not existing:
                db.add(AlertRecord(
                    timestamp=now,
                    subsystem=alt["subsystem"],
                    severity=alt["severity"],
                    title=alt["title"],
                    message=alt["message"],
                    resolved=False
                ))
        db.commit()

        return active_alerts

alert_engine = AlertEngine()
