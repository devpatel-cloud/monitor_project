import time
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.database.models import (
    CpuMetric, MemoryMetric, TemperatureMetric, StorageMetric, DiskIOMetric, NetworkMetric, BatteryMetric
)
from backend.app.core.config import settings

def parse_range_to_seconds(range_str: str) -> float:
    """
    Parses range string (e.g. '15m', '30m', '1h', '3h', '6h', '12h', '24h') to seconds.
    Falls back to hours if float is passed.
    """
    if not range_str:
        return 900.0 # Default 15 minutes

    s = str(range_str).strip().lower()
    if s.endswith("m") and s[:-1].isdigit():
        return float(s[:-1]) * 60.0
    elif s.endswith("h") and s[:-1].isdigit():
        return float(s[:-1]) * 3600.0
    elif s.endswith("d") and s[:-1].isdigit():
        return float(s[:-1]) * 86400.0
    else:
        try:
            return float(s) * 3600.0
        except ValueError:
            return 900.0

def get_downsample_step(seconds: float) -> float:
    """
    Returns downsampling interval step in seconds based on time range:
    - <= 30 mins (1800s): raw ~10s (step = 0)
    - 1 hour (3600s): step ~30s
    - 3 hours (10800s): step ~60s (1m)
    - 6 hours (21600s): step ~120s (2m)
    - 12 hours (43200s): step ~300s (5m)
    - 24 hours (86400s): step ~600s (10m)
    """
    if seconds <= 1800.0:
        return 0.0
    elif seconds <= 3600.0:
        return 30.0
    elif seconds <= 10800.0:
        return 60.0
    elif seconds <= 21600.0:
        return 120.0
    elif seconds <= 43200.0:
        return 300.0
    else:
        return 600.0

def downsample_records(records: List[Any], step_seconds: float) -> List[Any]:
    if step_seconds <= 0 or not records:
        return records

    sampled = []
    last_ts = 0.0
    for r in records:
        ts = getattr(r, "timestamp", 0.0)
        if ts - last_ts >= step_seconds or not sampled:
            sampled.append(r)
            last_ts = ts
    return sampled

def cleanup_old_metrics(db: Session):
    """
    Cleans metrics older than retention policies.
    """
    now = time.time()
    cutoff_24h = now - (settings.RETENTION_10S_HOURS * 3600)

    db.query(CpuMetric).filter(CpuMetric.timestamp < cutoff_24h).delete()
    db.query(MemoryMetric).filter(MemoryMetric.timestamp < cutoff_24h).delete()
    db.query(TemperatureMetric).filter(TemperatureMetric.timestamp < cutoff_24h).delete()
    db.query(StorageMetric).filter(StorageMetric.timestamp < cutoff_24h).delete()
    db.query(DiskIOMetric).filter(DiskIOMetric.timestamp < cutoff_24h).delete()
    db.query(NetworkMetric).filter(NetworkMetric.timestamp < cutoff_24h).delete()
    db.query(BatteryMetric).filter(BatteryMetric.timestamp < cutoff_24h).delete()

    db.commit()

def get_cpu_history(db: Session, range_str: str = "15m") -> List[Dict[str, Any]]:
    seconds = parse_range_to_seconds(range_str)
    cutoff = time.time() - seconds
    raw_records = db.query(CpuMetric).filter(CpuMetric.timestamp >= cutoff).order_by(CpuMetric.timestamp.asc()).all()
    step = get_downsample_step(seconds)
    records = downsample_records(raw_records, step)
    return [{
        "timestamp": r.timestamp,
        "usage_percent": r.usage_percent,
        "load_1m": r.load_1m,
        "load_5m": r.load_5m,
        "load_15m": r.load_15m,
        "frequency_mhz": r.frequency_mhz
    } for r in records]

def get_memory_history(db: Session, range_str: str = "15m") -> List[Dict[str, Any]]:
    seconds = parse_range_to_seconds(range_str)
    cutoff = time.time() - seconds
    raw_records = db.query(MemoryMetric).filter(MemoryMetric.timestamp >= cutoff).order_by(MemoryMetric.timestamp.asc()).all()
    step = get_downsample_step(seconds)
    records = downsample_records(raw_records, step)
    return [{
        "timestamp": r.timestamp,
        "usage_percent": r.usage_percent,
        "used_bytes": r.used_bytes,
        "total_bytes": r.total_bytes,
        "swap_percent": r.swap_percent
    } for r in records]

def get_temperature_history(db: Session, range_str: str = "15m") -> List[Dict[str, Any]]:
    seconds = parse_range_to_seconds(range_str)
    cutoff = time.time() - seconds
    raw_records = db.query(TemperatureMetric).filter(TemperatureMetric.timestamp >= cutoff).order_by(TemperatureMetric.timestamp.asc()).all()
    step = get_downsample_step(seconds)
    records = downsample_records(raw_records, step)
    return [{
        "timestamp": r.timestamp,
        "cpu_temp_celsius": r.cpu_temp_celsius,
        "fan_speed_rpm": r.fan_speed_rpm
    } for r in records]

def get_network_history(db: Session, range_str: str = "15m") -> List[Dict[str, Any]]:
    seconds = parse_range_to_seconds(range_str)
    cutoff = time.time() - seconds
    raw_records = db.query(NetworkMetric).filter(NetworkMetric.timestamp >= cutoff).order_by(NetworkMetric.timestamp.asc()).all()
    step = get_downsample_step(seconds)
    records = downsample_records(raw_records, step)

    result = []
    prev_r = None
    for r in records:
        down_mbps = 0.0
        up_mbps = 0.0
        if prev_r:
            dt = r.timestamp - prev_r.timestamp
            if dt > 0:
                rx_delta = max(0, r.rx_bytes_total - prev_r.rx_bytes_total)
                tx_delta = max(0, r.tx_bytes_total - prev_r.tx_bytes_total)
                down_mbps = round((rx_delta * 8.0) / (dt * 1_000_000.0), 2)
                up_mbps = round((tx_delta * 8.0) / (dt * 1_000_000.0), 2)
        prev_r = r

        result.append({
            "timestamp": r.timestamp,
            "rx_bytes_total": r.rx_bytes_total,
            "tx_bytes_total": r.tx_bytes_total,
            "rx_packets_total": r.rx_packets_total,
            "tx_packets_total": r.tx_packets_total,
            "download_mbps": down_mbps,
            "upload_mbps": up_mbps
        })
    return result

def get_disk_io_history(db: Session, range_str: str = "15m") -> List[Dict[str, Any]]:
    seconds = parse_range_to_seconds(range_str)
    cutoff = time.time() - seconds
    raw_records = db.query(DiskIOMetric).filter(DiskIOMetric.timestamp >= cutoff).order_by(DiskIOMetric.timestamp.asc()).all()
    step = get_downsample_step(seconds)
    records = downsample_records(raw_records, step)

    result = []
    prev_r = None
    for r in records:
        read_mb_s = 0.0
        write_mb_s = 0.0
        if prev_r:
            dt = r.timestamp - prev_r.timestamp
            if dt > 0:
                r_delta = max(0, r.total_read_bytes - prev_r.total_read_bytes)
                w_delta = max(0, r.total_write_bytes - prev_r.total_write_bytes)
                read_mb_s = round((r_delta / dt) / (1024.0 * 1024.0), 2)
                write_mb_s = round((w_delta / dt) / (1024.0 * 1024.0), 2)
        prev_r = r

        result.append({
            "timestamp": r.timestamp,
            "total_read_bytes": r.total_read_bytes,
            "total_write_bytes": r.total_write_bytes,
            "total_read_ops": r.total_read_ops,
            "total_write_ops": r.total_write_ops,
            "read_mb_s": read_mb_s,
            "write_mb_s": write_mb_s
        })
    return result
