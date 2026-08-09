from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.app.database.database import Base

class Host(Base):
    __tablename__ = "hosts"
    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, unique=True, index=True)
    os_name = Column(String)
    kernel = Column(String)
    arch = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="viewer") # "admin" or "viewer"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CpuMetric(Base):
    __tablename__ = "cpu_metrics"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, index=True, nullable=False)
    usage_percent = Column(Float)
    per_core_json = Column(Text)
    load_1m = Column(Float)
    load_5m = Column(Float)
    load_15m = Column(Float)
    frequency_mhz = Column(Float)

class MemoryMetric(Base):
    __tablename__ = "memory_metrics"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, index=True, nullable=False)
    total_bytes = Column(Integer)
    used_bytes = Column(Integer)
    available_bytes = Column(Integer)
    free_bytes = Column(Integer)
    cached_bytes = Column(Integer)
    buffers_bytes = Column(Integer)
    usage_percent = Column(Float)
    swap_total_bytes = Column(Integer)
    swap_used_bytes = Column(Integer)
    swap_percent = Column(Float)

class TemperatureMetric(Base):
    __tablename__ = "temperature_metrics"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, index=True, nullable=False)
    cpu_temp_celsius = Column(Float, nullable=True)
    fan_speed_rpm = Column(Integer, nullable=True)
    sensors_json = Column(Text)

class StorageMetric(Base):
    __tablename__ = "storage_metrics"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, index=True, nullable=False)
    disks_json = Column(Text)
    partitions_json = Column(Text)
    lvm_json = Column(Text)

class DiskIOMetric(Base):
    __tablename__ = "disk_io_metrics"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, index=True, nullable=False)
    total_read_bytes = Column(Integer)
    total_write_bytes = Column(Integer)
    total_read_ops = Column(Integer)
    total_write_ops = Column(Integer)
    devices_json = Column(Text)

class NetworkMetric(Base):
    __tablename__ = "network_metrics"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, index=True, nullable=False)
    rx_bytes_total = Column(Integer)
    tx_bytes_total = Column(Integer)
    rx_packets_total = Column(Integer)
    tx_packets_total = Column(Integer)
    interfaces_json = Column(Text)
    connectivity_json = Column(Text)

class BatteryMetric(Base):
    __tablename__ = "battery_metrics"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, index=True, nullable=False)
    status = Column(String)
    capacity_percent = Column(Float)
    state = Column(String)
    health = Column(String)
    power_draw_watts = Column(Float)

class DockerMetric(Base):
    __tablename__ = "docker_metrics"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, index=True, nullable=False)
    daemon_status = Column(String)
    containers_total = Column(Integer)
    containers_running = Column(Integer)
    containers_stopped = Column(Integer)
    images_total = Column(Integer)
    volumes_total = Column(Integer)
    containers_json = Column(Text)

class ServiceStatusMetric(Base):
    __tablename__ = "service_status"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, index=True, nullable=False)
    total = Column(Integer)
    running = Column(Integer)
    stopped = Column(Integer)
    failed = Column(Integer)
    services_json = Column(Text)

class SystemEvent(Base):
    __tablename__ = "system_events"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, index=True, nullable=False)
    category = Column(String) # security, service, OOM, kernel
    severity = Column(String) # INFO, WARNING, CRITICAL
    message = Column(Text)

class AlertRecord(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, index=True, nullable=False)
    subsystem = Column(String) # CPU, RAM, Storage, Temp, SMART, Docker, Services, IPv6, DuckDNS
    severity = Column(String) # INFO, WARNING, CRITICAL
    title = Column(String)
    message = Column(Text)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(Float, nullable=True)

class DuckDNSStatus(Base):
    __tablename__ = "duckdns_status"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, index=True, nullable=False)
    domain = Column(String)
    current_ipv6 = Column(String)
    duckdns_aaaa = Column(String)
    status = Column(String) # MATCH, MISMATCH, NO_IPV6, DNS_FAILURE
    last_update_status = Column(Text)
