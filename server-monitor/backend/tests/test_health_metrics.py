import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.services.metrics import calculate_health_score

def test_health_score_with_working_internet():
    snapshot = {
        "cpu": {"usage_percent": 15.0},
        "memory": {"usage_percent": 30.0},
        "storage": {"partitions": [{"mount_point": "/", "usage_percent": 20.0}], "disks": []},
        "temperature": {"cpu_temp_celsius": 45.0},
        "services": {"failed": 0},
        "duckdns": {"mismatch": False},
        "network": {
            "connectivity": {
                "ipv4": True,
                "ipv6": True,
                "gateway": True,
                "internet": True,
                "dns_resolution": True
            }
        }
    }
    result = calculate_health_score(snapshot)
    assert result["score"] == 100
    assert result["status"] == "HEALTHY"
    # Ensure "Internet" deduction is NOT present in breakdown
    internet_factors = [f for f in result["breakdown"] if f.get("name") == "Internet"]
    assert len(internet_factors) == 0

def test_health_score_with_failed_internet():
    snapshot = {
        "cpu": {"usage_percent": 15.0},
        "memory": {"usage_percent": 30.0},
        "storage": {"partitions": [{"mount_point": "/", "usage_percent": 20.0}], "disks": []},
        "temperature": {"cpu_temp_celsius": 45.0},
        "services": {"failed": 0},
        "duckdns": {"mismatch": False},
        "network": {
            "connectivity": {
                "ipv4": False,
                "ipv6": False,
                "gateway": False,
                "internet": False,
                "dns_resolution": False
            }
        }
    }
    result = calculate_health_score(snapshot)
    assert result["score"] == 70
    assert result["status"] == "DEGRADED"
    internet_factors = [f for f in result["breakdown"] if f.get("name") == "Internet"]
    assert len(internet_factors) == 1
    assert internet_factors[0]["impact"] == -30
    assert internet_factors[0]["reason"] == "No public internet connectivity"
