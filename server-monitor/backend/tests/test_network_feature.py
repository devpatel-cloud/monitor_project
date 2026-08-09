import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.main import app
from backend.app.database.database import Base, engine, SessionLocal
from backend.app.core.security import create_access_token

client = TestClient(app)

@pytest.fixture
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_get_network_schema(setup_db):
    response = client.get("/api/v1/network")
    assert response.status_code == 200
    data = response.json()
    assert "wifi" in data
    assert "connectivity" in data
    assert "traffic" in data
    assert "download_mbps" in data["traffic"]
    assert "upload_mbps" in data["traffic"]

def test_speed_test_rbac_and_rate_limiting(setup_db):
    admin_token = create_access_token({"sub": "admin", "role": "admin"})
    viewer_token = create_access_token({"sub": "viewer", "role": "viewer"})

    # 1. Viewer token should receive 403 Forbidden
    res_viewer = client.post(
        "/api/v1/network/speed-test",
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert res_viewer.status_code == 403

    # 2. Admin token should succeed on first test
    res_admin = client.post(
        "/api/v1/network/speed-test",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_admin.status_code == 200
    res_data = res_admin.json()
    assert res_data["status"] == "success"
    assert "download_mbps" in res_data

    # 3. Second test immediately after should trigger 429 Too Many Requests (Rate limit 60s)
    res_rate_limit = client.post(
        "/api/v1/network/speed-test",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_rate_limit.status_code == 429
