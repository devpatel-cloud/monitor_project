import os
import sys
import time
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.database.models import Base, CpuMetric, MemoryMetric, NetworkMetric, DiskIOMetric
from backend.app.database.repository import save_snapshot_to_db
from backend.app.services.history import (
    get_cpu_history, get_memory_history, get_network_history, get_disk_io_history, parse_range_to_seconds
)
from agent.collectors.services import check_service_status
from agent.collectors.storage import get_storage_info

@pytest.fixture
def db_session(tmp_path):
    db_file = tmp_path / "test_grafana.db"
    engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_snapshot_persistence_and_history(db_session):
    now = time.time()
    s1 = {
        "timestamp": now - 20,
        "cpu": {"usage_percent": 12.5, "load_1m": 0.5},
        "memory": {"used_bytes": 4000000000, "total_bytes": 8000000000, "usage_percent": 50.0},
        "network": {"interfaces": [{"rx_bytes": 1000000, "tx_bytes": 500000}]},
        "disk_io": {"total_read_bytes": 2000000, "total_write_bytes": 1000000}
    }
    s2 = {
        "timestamp": now - 10,
        "cpu": {"usage_percent": 25.0, "load_1m": 0.8},
        "memory": {"used_bytes": 4400000000, "total_bytes": 8000000000, "usage_percent": 55.0},
        "network": {"interfaces": [{"rx_bytes": 2000000, "tx_bytes": 1000000}]},
        "disk_io": {"total_read_bytes": 4000000, "total_write_bytes": 2000000}
    }

    save_snapshot_to_db(db_session, s1)
    save_snapshot_to_db(db_session, s2)

    cpu_hist = get_cpu_history(db_session, range_str="15m")
    assert len(cpu_hist) == 2
    assert cpu_hist[1]["usage_percent"] == 25.0

    net_hist = get_network_history(db_session, range_str="15m")
    assert len(net_hist) == 2
    assert net_hist[1]["download_mbps"] > 0.0
    assert net_hist[1]["upload_mbps"] > 0.0

    disk_hist = get_disk_io_history(db_session, range_str="15m")
    assert len(disk_hist) == 2
    assert disk_hist[1]["read_mb_s"] > 0.0

def test_parse_range_to_seconds():
    assert parse_range_to_seconds("15m") == 900.0
    assert parse_range_to_seconds("1h") == 3600.0
    assert parse_range_to_seconds("24h") == 86400.0

def test_service_classification():
    ssh_info = check_service_status("sshd")
    assert ssh_info["is_default"] == True

    custom_info = check_service_status("server-monitor-backend")
    assert custom_info["is_default"] == False

def test_primary_storage_root_selection():
    storage = get_storage_info()
    partitions = storage.get("partitions", [])
    if partitions:
        assert partitions[0]["mount_point"] == "/"
        assert partitions[0]["is_root"] == True
