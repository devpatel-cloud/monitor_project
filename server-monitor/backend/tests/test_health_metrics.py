import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.services.metrics import calculate_health_score

def base_snapshot(conn_dict):
    return {
        "cpu": {"usage_percent": 15.0},
        "memory": {"usage_percent": 30.0},
        "storage": {"partitions": [{"mount_point": "/", "usage_percent": 20.0}], "disks": []},
        "temperature": {"cpu_temp_celsius": 45.0},
        "services": {"failed": 0},
        "duckdns": {"mismatch": False},
        "network": {"connectivity": conn_dict}
    }

def test_internet_true_no_deduction():
    snapshot = base_snapshot({"internet": True, "ipv4": False, "ipv6": False})
    res = calculate_health_score(snapshot)
    assert res["score"] == 100
    assert not any(f["name"] == "Internet" for f in res["breakdown"])

def test_ipv4_true_no_deduction():
    snapshot = base_snapshot({"internet": False, "ipv4": True, "ipv6": False})
    res = calculate_health_score(snapshot)
    assert res["score"] == 100
    assert not any(f["name"] == "Internet" for f in res["breakdown"])

def test_ipv6_true_no_deduction():
    snapshot = base_snapshot({"internet": False, "ipv4": False, "ipv6": True})
    res = calculate_health_score(snapshot)
    assert res["score"] == 100
    assert not any(f["name"] == "Internet" for f in res["breakdown"])

def test_all_false_triggers_deduction():
    snapshot = base_snapshot({"internet": False, "ipv4": False, "ipv6": False})
    res = calculate_health_score(snapshot)
    assert res["score"] == 70
    assert res["status"] == "DEGRADED"
    factors = [f for f in res["breakdown"] if f["name"] == "Internet"]
    assert len(factors) == 1
    assert factors[0]["impact"] == -30
    assert factors[0]["reason"] == "No public internet connectivity"
