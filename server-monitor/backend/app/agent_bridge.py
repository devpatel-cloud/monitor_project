from agent.collector import MetricsCollector

_collector = MetricsCollector(cache_ttl=3.0)

def get_latest_snapshot():
    return _collector.collect_all(use_cache=True)
