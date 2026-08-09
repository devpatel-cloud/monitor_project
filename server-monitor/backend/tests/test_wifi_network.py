import os
import sys
import time
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agent.collectors.wifi import get_wifi_info
from agent.collectors.network import get_network_info
from backend.app.main import app

client = TestClient(app)

def test_wifi_info_collector():
    data = get_wifi_info()
    assert "status" in data
    assert "connected" in data
    assert "interface" in data
    assert "ssid" in data
    assert "signal_percent" in data
    assert "frequency_mhz" in data
    assert "frequency_str" in data
    assert "link_speed_mbps" in data
    assert "state" in data
    assert isinstance(data["connected"], bool)
    assert isinstance(data["signal_percent"], int)
    assert isinstance(data["link_speed_mbps"], int)

def test_network_info_collector_and_throughput():
    # First snapshot
    info1 = get_network_info()
    assert "interfaces" in info1
    assert "connectivity" in info1
    assert "traffic" in info1
    assert "download_mbps" in info1["traffic"]
    assert "upload_mbps" in info1["traffic"]

    # Sleep 1 second to test throughput delta calculation
    time.sleep(1.0)

    # Second snapshot
    info2 = get_network_info()
    assert "traffic" in info2
    assert isinstance(info2["traffic"]["download_mbps"], float)
    assert isinstance(info2["traffic"]["upload_mbps"], float)
    assert info2["traffic"]["download_mbps"] >= 0.0
    assert info2["traffic"]["upload_mbps"] >= 0.0

def test_api_network_endpoint():
    res = client.get("/api/v1/network")
    assert res.status_code == 200
    data = res.json()
    assert "wifi" in data
    assert "connectivity" in data
    assert "traffic" in data
    assert "interfaces" in data

def test_api_health_endpoint():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["online", "healthy", "warning", "critical"]
