import time
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.database.models import AlertRecord

class AlertEngine:
    """
    Evaluates system metrics against configured thresholds, manages alert lifecycle
    (ACTIVE -> ACKNOWLEDGED -> RESOLVED), automatically resolves alerts when conditions return to normal,
    and prevents duplicate alert creation.
    """
    def __init__(self):
        self._cpu_high_since = None

    def evaluate_snapshot(self, db: Session, snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
        current_issues: List[Dict[str, Any]] = []
        now = snapshot.get("timestamp", time.time())

        # 1. CPU Evaluation (CPU > 90% for sustained duration)
        cpu_usage = snapshot.get("cpu", {}).get("usage_percent", 0.0)
        if cpu_usage >= 90.0:
            if self._cpu_high_since is None:
                self._cpu_high_since = now
            elif now - self._cpu_high_since >= 30: # 30 seconds threshold
                current_issues.append({
                    "target_key": "cpu:high",
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
            current_issues.append({
                "target_key": "mem:high",
                "subsystem": "Memory",
                "severity": "CRITICAL" if ram_usage > 95.0 else "WARNING",
                "title": "High Memory Utilization",
                "message": f"RAM usage is at {ram_usage}% (threshold: 90%)"
            })

        # 3. Storage Evaluation (Disk > 85%, > 95%)
        partitions = snapshot.get("storage", {}).get("partitions", [])
        for p in partitions:
            mount = p.get("mount_point", "")
            pct = p.get("usage_percent", 0.0)
            if pct >= 95.0:
                current_issues.append({
                    "target_key": f"storage:{mount}",
                    "subsystem": "Storage",
                    "severity": "CRITICAL",
                    "title": f"Disk Usage Critical on {mount}",
                    "message": f"{mount} disk usage is at {pct}%"
                })
            elif pct >= 85.0:
                current_issues.append({
                    "target_key": f"storage:{mount}",
                    "subsystem": "Storage",
                    "severity": "WARNING",
                    "title": f"Disk Usage Warning on {mount}",
                    "message": f"{mount} disk usage is at {pct}%"
                })

        # 4. SMART Health
        disks = snapshot.get("storage", {}).get("disks", [])
        for d in disks:
            smart_health = d.get("smart_health", "")
            dev = d.get("device", "")
            if smart_health == "FAILED":
                current_issues.append({
                    "target_key": f"smart:{dev}",
                    "subsystem": "SMART",
                    "severity": "CRITICAL",
                    "title": f"SMART Drive Health Failure on {dev}",
                    "message": f"Physical disk {dev} ({d.get('model')}) failed SMART diagnostics!"
                })

        # 5. Temperature (Temp > 80°C warning, > 90°C critical)
        cpu_temp = snapshot.get("temperature", {}).get("cpu_temp_celsius")
        if isinstance(cpu_temp, (int, float)):
            if cpu_temp >= 90.0:
                current_issues.append({
                    "target_key": "temp:cpu",
                    "subsystem": "Temperature",
                    "severity": "CRITICAL",
                    "title": "CPU Overheating Critical",
                    "message": f"CPU temperature is {cpu_temp}°C (critical > 90°C)"
                })
            elif cpu_temp >= 80.0:
                current_issues.append({
                    "target_key": "temp:cpu",
                    "subsystem": "Temperature",
                    "severity": "WARNING",
                    "title": "CPU High Temperature",
                    "message": f"CPU temperature is {cpu_temp}°C (warning > 80°C)"
                })

        # 6. Services Evaluation (nginx, docker, sshd, etc.)
        services = snapshot.get("services", {}).get("services", [])
        for svc in services:
            name = svc.get("name")
            state = svc.get("state")
            if state in ["STOPPED", "FAILED"]:
                severity = "CRITICAL" if name in ["nginx", "docker", "sshd", "server-monitor-backend"] else "WARNING"
                current_issues.append({
                    "target_key": f"service:{name}",
                    "subsystem": "Services",
                    "severity": severity,
                    "title": f"Service {name} is {state}",
                    "message": f"Systemd service '{name}' is currently {state}"
                })

        # 7. DuckDNS & IPv6 Mismatch
        duckdns = snapshot.get("duckdns", {})
        if duckdns.get("mismatch"):
            current_issues.append({
                "target_key": "duckdns:mismatch",
                "subsystem": "DuckDNS",
                "severity": "WARNING",
                "title": "DuckDNS IPv6 Mismatch",
                "message": f"Current IPv6 ({duckdns.get('current_ipv6')}) does not match DuckDNS AAAA ({duckdns.get('duckdns_aaaa')})"
            })

        # 8. Internet & Wi-Fi Connectivity Evaluation
        connectivity = snapshot.get("network", {}).get("connectivity", {})
        wifi = snapshot.get("wifi", {})

        if wifi.get("status") == "Available":
            if not wifi.get("connected") or wifi.get("state") == "Disconnected":
                current_issues.append({
                    "target_key": "wifi:disconnected",
                    "subsystem": "Network",
                    "severity": "WARNING",
                    "title": "Wi-Fi Disconnected",
                    "message": f"Wi-Fi interface {wifi.get('interface', 'wlp2s0')} is disconnected"
                })
            elif wifi.get("signal_percent", 100) < 30:
                current_issues.append({
                    "target_key": "wifi:signal_low",
                    "subsystem": "Network",
                    "severity": "WARNING",
                    "title": "Wi-Fi Signal Low",
                    "message": f"Wi-Fi signal strength has fallen to {wifi.get('signal_percent')}%"
                })

        if not connectivity.get("ipv4") and not connectivity.get("ipv6") and not connectivity.get("internet", True):
            current_issues.append({
                "target_key": "network:offline",
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
                current_issues.append({
                    "target_key": "battery:low",
                    "subsystem": "Battery",
                    "severity": "WARNING",
                    "title": "Low Battery Warning",
                    "message": f"Battery charge is down to {cap}% while discharging"
                })

        active_keys = {issue["target_key"] for issue in current_issues}

        # Query all existing unresolved alerts from SQLite
        existing_unresolved = db.query(AlertRecord).filter(AlertRecord.resolved == False).all()
        existing_map = {alt.target_key: alt for alt in existing_unresolved if alt.target_key}

        # A. Process current issues -> create new alert or update existing
        for issue in current_issues:
            t_key = issue["target_key"]
            if t_key in existing_map:
                # Issue persists: update message/severity if changed, do not duplicate!
                alt = existing_map[t_key]
                alt.severity = issue["severity"]
                alt.message = issue["message"]
            else:
                # New issue detected: insert new ACTIVE alert
                db.add(AlertRecord(
                    target_key=t_key,
                    timestamp=now,
                    started_at=now,
                    subsystem=issue["subsystem"],
                    severity=issue["severity"],
                    title=issue["title"],
                    message=issue["message"],
                    status="ACTIVE",
                    resolved=False
                ))

        # B. Automatic Resolution: For unresolved alerts whose target_key is NO LONGER in active_keys
        for alt in existing_unresolved:
            if alt.target_key and alt.target_key not in active_keys:
                alt.status = "RESOLVED"
                alt.resolved = True
                alt.resolved_at = now

        db.commit()

        # Return currently active/acknowledged unresolved alerts
        return [
            {
                "id": a.id,
                "target_key": a.target_key,
                "subsystem": a.subsystem,
                "severity": a.severity,
                "title": a.title,
                "message": a.message,
                "status": a.status,
                "started_at": a.started_at or a.timestamp
            }
            for a in db.query(AlertRecord).filter(AlertRecord.resolved == False).all()
        ]

alert_engine = AlertEngine()
