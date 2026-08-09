import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "health_score" in data

def test_cpu_endpoint():
    response = client.get("/api/v1/cpu")
    assert response.status_code == 200
    data = response.json()
    assert "usage_percent" in data

def test_memory_endpoint():
    response = client.get("/api/v1/memory")
    assert response.status_code == 200
    data = response.json()
    assert "usage_percent" in data

def test_storage_endpoint():
    response = client.get("/api/v1/storage")
    assert response.status_code == 200
    data = response.json()
    assert "storage" in data

def test_duckdns_endpoint_does_not_expose_token():
    response = client.get("/api/v1/duckdns")
    assert response.status_code == 200
    data = response.json()
    assert "token" not in data
