import time
from typing import Dict, Any, Optional

class MetricsCache:
    """
    In-memory cache for collector metrics with TTL support.
    """
    def __init__(self, default_ttl_seconds: float = 5.0):
        self.default_ttl = default_ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["timestamp"] <= entry["ttl"]:
                return entry["data"]
        return None

    def set(self, key: str, data: Any, ttl: Optional[float] = None):
        self._cache[key] = {
            "data": data,
            "timestamp": time.time(),
            "ttl": ttl if ttl is not None else self.default_ttl
        }

    def clear(self):
        self._cache.clear()
