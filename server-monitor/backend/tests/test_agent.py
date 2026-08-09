import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agent.collector import MetricsCollector

def test_collector_returns_valid_snapshot():
    collector = MetricsCollector()
    snapshot = collector.collect_all(use_cache=False)
    
    assert "timestamp" in snapshot
    assert "cpu" in snapshot
    assert "memory" in snapshot
    assert "storage" in snapshot
    assert "network" in snapshot
    assert "duckdns" in snapshot
    assert snapshot["duckdns"].get("domain") == "sanjaya-server.duckdns.org"
