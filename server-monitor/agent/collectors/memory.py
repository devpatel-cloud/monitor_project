import os
from typing import Dict, Any

def get_memory_info() -> Dict[str, Any]:
    """
    Collects RAM total, used, available, free, cached, buffers, and Swap stats from /proc/meminfo.
    """
    mem_info = {}
    if os.path.exists("/proc/meminfo"):
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    parts = line.split(":")
                    if len(parts) == 2:
                        key = parts[0].strip()
                        val_parts = parts[1].strip().split()
                        val = int(val_parts[0]) * 1024  # Convert kB to Bytes
                        mem_info[key] = val
        except Exception:
            pass

    total = mem_info.get("MemTotal", 0)
    free = mem_info.get("MemFree", 0)
    available = mem_info.get("MemAvailable", free)
    buffers = mem_info.get("Buffers", 0)
    cached = mem_info.get("Cached", 0) + mem_info.get("SReclaimable", 0)

    used = max(0, total - available) if total > 0 else 0
    usage_percent = round((used / total) * 100.0, 1) if total > 0 else 0.0

    swap_total = mem_info.get("SwapTotal", 0)
    swap_free = mem_info.get("SwapFree", 0)
    swap_used = max(0, swap_total - swap_free) if swap_total > 0 else 0
    swap_percent = round((swap_used / swap_total) * 100.0, 1) if swap_total > 0 else 0.0

    return {
        "total_bytes": total,
        "used_bytes": used,
        "available_bytes": available,
        "free_bytes": free,
        "cached_bytes": cached,
        "buffers_bytes": buffers,
        "usage_percent": usage_percent,
        "swap_total_bytes": swap_total,
        "swap_used_bytes": swap_used,
        "swap_percent": swap_percent
    }
