import os
import sys
import time
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.main import app
from backend.app.database.database import Base, engine, SessionLocal
from backend.app.database.models import CpuMetric, MemoryMetric

client = TestClient(app)

@pytest.fixture
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    now = time.time()
    # Insert 100 historical metric snapshots spanning past 2 hours
    for i in range(100):
        ts = now - (i * 72) # 72 seconds apart
        session.add(CpuMetric(timestamp=ts, usage_percent=20.0 + (i % 10), load_1m=0.5))
        session.add(MemoryMetric(timestamp=ts, usage_percent=50.0 + (i % 5)))
    session.commit()
    session.close()

    yield
    Base.metadata.drop_all(bind=engine)

def test_history_ranges_and_downsampling(setup_db):
    # 1. Test 15 minutes range
    res_15m = client.get("/api/v1/history/cpu?range=15m")
    assert res_15m.status_code == 200
    data_15m = res_15m.json()
    assert isinstance(data_15m, list)
    if len(data_15m) > 0:
        assert "timestamp" in data_15m[0]
        assert "usage_percent" in data_15m[0]

    # 2. Test 24 hours range with downsampling
    res_24h = client.get("/api/v1/history/cpu?range=24h")
    assert res_24h.status_code == 200
    data_24h = res_24h.json()
    assert isinstance(data_24h, list)
    assert len(data_24h) <= 100
