import time
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.database.models import (
    CpuMetric, MemoryMetric, TemperatureMetric, StorageMetric, NetworkMetric, BatteryMetric
)
from backend.app.core.config import settings

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
    db.query(NetworkMetric).filter(NetworkMetric.timestamp < cutoff_24h).delete()
    db.query(BatteryMetric).filter(BatteryMetric.timestamp < cutoff_24h).delete()

    db.commit()

def get_cpu_history(db: Session, range_hours: float = 24.0) -> List[Dict[str, Any]]:
    cutoff = time.time() - (range_hours * 3600)
    records = db.query(CpuMetric).filter(CpuMetric.timestamp >= cutoff).order_by(CpuMetric.timestamp.asc()).all()
    return [{
        "timestamp": r.timestamp,
        "usage_percent": r.usage_percent,
        "load_1m": r.load_1m,
        "load_5m": r.load_5m,
        "load_15m": r.load_15m,
        "frequency_mhz": r.frequency_mhz
    } for r in records]

def get_memory_history(db: Session, range_hours: float = 24.0) -> List[Dict[str, Any]]:
    cutoff = time.time() - (range_hours * 3600)
    records = db.query(MemoryMetric).filter(MemoryMetric.timestamp >= cutoff).order_by(MemoryMetric.timestamp.asc()).all()
    return [{
        "timestamp": r.timestamp,
        "usage_percent": r.usage_percent,
        "used_bytes": r.used_bytes,
        "total_bytes": r.total_bytes,
        "swap_percent": r.swap_percent
    } for r in records]

def get_temperature_history(db: Session, range_hours: float = 24.0) -> List[Dict[str, Any]]:
    cutoff = time.time() - (range_hours * 3600)
    records = db.query(TemperatureMetric).filter(TemperatureMetric.timestamp >= cutoff).order_by(TemperatureMetric.timestamp.asc()).all()
    return [{
        "timestamp": r.timestamp,
        "cpu_temp_celsius": r.cpu_temp_celsius,
        "fan_speed_rpm": r.fan_speed_rpm
    } for r in records]

def get_network_history(db: Session, range_hours: float = 24.0) -> List[Dict[str, Any]]:
    cutoff = time.time() - (range_hours * 3600)
    records = db.query(NetworkMetric).filter(NetworkMetric.timestamp >= cutoff).order_by(NetworkMetric.timestamp.asc()).all()
    return [{
        "timestamp": r.timestamp,
        "rx_bytes_total": r.rx_bytes_total,
        "tx_bytes_total": r.tx_bytes_total,
        "rx_packets_total": r.rx_packets_total,
        "tx_packets_total": r.tx_packets_total
    } for r in records]
