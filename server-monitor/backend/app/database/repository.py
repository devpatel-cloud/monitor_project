import json
import time
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.database.models import (
    User, CpuMetric, MemoryMetric, TemperatureMetric, StorageMetric,
    DiskIOMetric, NetworkMetric, BatteryMetric, DockerMetric,
    ServiceStatusMetric, SystemEvent, AlertRecord, DuckDNSStatus
)
from backend.app.core.security import hash_password

def init_db_seeds(db: Session):
    """Seed initial default admin and viewer accounts if table is empty."""
    user_count = db.query(User).count()
    if user_count == 0:
        admin_user = User(
            username="admin",
            hashed_password=hash_password("admin123"),
            role="admin"
        )
        viewer_user = User(
            username="viewer",
            hashed_password=hash_password("viewer123"),
            role="viewer"
        )
        db.add(admin_user)
        db.add(viewer_user)
        db.commit()

def save_snapshot_to_db(db: Session, snapshot: Dict[str, Any]):
    ts = snapshot.get("timestamp", time.time())

    # CPU
    cpu = snapshot.get("cpu", {})
    db.add(CpuMetric(
        timestamp=ts,
        usage_percent=cpu.get("usage_percent", 0.0),
        per_core_json=json.dumps(cpu.get("per_core_usage", [])),
        load_1m=cpu.get("load_1m", 0.0),
        load_5m=cpu.get("load_5m", 0.0),
        load_15m=cpu.get("load_15m", 0.0),
        frequency_mhz=cpu.get("frequency_mhz", 0.0)
    ))

    # Memory
    mem = snapshot.get("memory", {})
    db.add(MemoryMetric(
        timestamp=ts,
        total_bytes=mem.get("total_bytes", 0),
        used_bytes=mem.get("used_bytes", 0),
        available_bytes=mem.get("available_bytes", 0),
        free_bytes=mem.get("free_bytes", 0),
        cached_bytes=mem.get("cached_bytes", 0),
        buffers_bytes=mem.get("buffers_bytes", 0),
        usage_percent=mem.get("usage_percent", 0.0),
        swap_total_bytes=mem.get("swap_total_bytes", 0),
        swap_used_bytes=mem.get("swap_used_bytes", 0),
        swap_percent=mem.get("swap_percent", 0.0)
    ))

    # Temperature
    temp = snapshot.get("temperature", {})
    c_temp = temp.get("cpu_temp_celsius")
    c_temp_val = float(c_temp) if isinstance(c_temp, (int, float)) else None
    f_speed = temp.get("fan_speed_rpm")
    f_speed_val = int(f_speed) if isinstance(f_speed, (int, float)) else None

    db.add(TemperatureMetric(
        timestamp=ts,
        cpu_temp_celsius=c_temp_val,
        fan_speed_rpm=f_speed_val,
        sensors_json=json.dumps(temp.get("sensors", []))
    ))

    # Storage
    storage = snapshot.get("storage", {})
    db.add(StorageMetric(
        timestamp=ts,
        disks_json=json.dumps(storage.get("disks", [])),
        partitions_json=json.dumps(storage.get("partitions", [])),
        lvm_json=json.dumps(storage.get("lvm", {}))
    ))

    # Disk IO
    disk_io = snapshot.get("disk_io", {})
    db.add(DiskIOMetric(
        timestamp=ts,
        total_read_bytes=disk_io.get("total_read_bytes", 0),
        total_write_bytes=disk_io.get("total_write_bytes", 0),
        total_read_ops=disk_io.get("total_read_ops", 0),
        total_write_ops=disk_io.get("total_write_ops", 0),
        devices_json=json.dumps(disk_io.get("devices", []))
    ))

    # Network
    net = snapshot.get("network", {})
    rx_tot = sum(i.get("rx_bytes", 0) for i in net.get("interfaces", []))
    tx_tot = sum(i.get("tx_bytes", 0) for i in net.get("interfaces", []))
    rx_p_tot = sum(i.get("rx_packets", 0) for i in net.get("interfaces", []))
    tx_p_tot = sum(i.get("tx_packets", 0) for i in net.get("interfaces", []))

    db.add(NetworkMetric(
        timestamp=ts,
        rx_bytes_total=rx_tot,
        tx_bytes_total=tx_tot,
        rx_packets_total=rx_p_tot,
        tx_packets_total=tx_p_tot,
        interfaces_json=json.dumps(net.get("interfaces", [])),
        connectivity_json=json.dumps(net.get("connectivity", {}))
    ))

    # Battery
    bat = snapshot.get("battery", {})
    db.add(BatteryMetric(
        timestamp=ts,
        status=bat.get("status", "Unavailable"),
        capacity_percent=float(bat.get("capacity_percent", 0)),
        state=str(bat.get("state", "")),
        health=str(bat.get("health", "")),
        power_draw_watts=float(bat.get("power_draw_watts", 0.0))
    ))

    # Docker
    doc = snapshot.get("docker", {})
    db.add(DockerMetric(
        timestamp=ts,
        daemon_status=doc.get("daemon_status", "STOPPED"),
        containers_total=doc.get("containers_total", 0),
        containers_running=doc.get("containers_running", 0),
        containers_stopped=doc.get("containers_stopped", 0),
        images_total=doc.get("images_total", 0),
        volumes_total=doc.get("volumes_total", 0),
        containers_json=json.dumps(doc.get("containers", []))
    ))

    # Services
    svc = snapshot.get("services", {})
    db.add(ServiceStatusMetric(
        timestamp=ts,
        total=svc.get("total", 0),
        running=svc.get("running", 0),
        stopped=svc.get("stopped", 0),
        failed=svc.get("failed", 0),
        services_json=json.dumps(svc.get("services", []))
    ))

    # DuckDNS
    ddns = snapshot.get("duckdns", {})
    db.add(DuckDNSStatus(
        timestamp=ts,
        domain=ddns.get("domain", ""),
        current_ipv6=ddns.get("current_ipv6", ""),
        duckdns_aaaa=ddns.get("duckdns_aaaa", ""),
        status=ddns.get("status", ""),
        last_update_status=ddns.get("last_update_status", "")
    ))

    db.commit()
