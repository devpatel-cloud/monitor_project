import os
import sys
import pytest
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.database.database import Base, engine, SessionLocal
from backend.app.database.models import AlertRecord
from backend.app.services.alerts import alert_engine

@pytest.fixture
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

def test_automatic_alert_resolution(db: Session):
    # 1. Snapshot with stopped service (triggers ACTIVE alert)
    stopped_snapshot = {
        "timestamp": 1000.0,
        "cpu": {"usage_percent": 10.0},
        "memory": {"usage_percent": 20.0},
        "storage": {"partitions": []},
        "temperature": {"cpu_temp_celsius": 45.0},
        "services": {"services": [{"name": "duckdns-ipv6", "state": "STOPPED"}]},
        "duckdns": {},
        "network": {"connectivity": {"ipv4_online": True, "ipv6_online": True}},
        "battery": {}
    }

    active_alerts = alert_engine.evaluate_snapshot(db, stopped_snapshot)
    assert len(active_alerts) == 1
    assert active_alerts[0]["target_key"] == "service:duckdns-ipv6"
    assert active_alerts[0]["status"] == "ACTIVE"

    # Query DB record
    record = db.query(AlertRecord).filter(AlertRecord.target_key == "service:duckdns-ipv6").first()
    assert record is not None
    assert record.resolved is False

    # 2. Next snapshot where service returns to RUNNING (should automatically resolve)
    running_snapshot = {
        "timestamp": 1010.0,
        "cpu": {"usage_percent": 10.0},
        "memory": {"usage_percent": 20.0},
        "storage": {"partitions": []},
        "temperature": {"cpu_temp_celsius": 45.0},
        "services": {"services": [{"name": "duckdns-ipv6", "state": "RUNNING"}]},
        "duckdns": {},
        "network": {"connectivity": {"ipv4_online": True, "ipv6_online": True}},
        "battery": {}
    }

    active_alerts_after = alert_engine.evaluate_snapshot(db, running_snapshot)
    assert len(active_alerts_after) == 0

    # Query DB record -> status should now be RESOLVED and resolved=True
    db.refresh(record)
    assert record.resolved is True
    assert record.status == "RESOLVED"
    assert record.resolved_at == 1010.0
