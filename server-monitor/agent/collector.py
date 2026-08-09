import time
from typing import Dict, Any

from agent.collectors.cpu import get_cpu_info
from agent.collectors.memory import get_memory_info
from agent.collectors.temperature import get_temperature_info
from agent.collectors.storage import get_storage_info
from agent.collectors.disk_io import get_disk_io_info
from agent.collectors.network import get_network_info
from agent.collectors.wifi import get_wifi_info
from agent.collectors.battery import get_battery_info
from agent.collectors.docker import get_docker_info
from agent.collectors.services import get_services_info
from agent.collectors.security import get_security_info
from agent.collectors.processes import get_top_processes
from agent.collectors.system import get_system_info
from agent.collectors.duckdns import get_duckdns_info
from agent.cache import MetricsCache

class MetricsCollector:
    """
    Master collector that coordinates subsystem metrics gathering.
    """
    def __init__(self, cache_ttl: float = 5.0):
        self.cache = MetricsCache(default_ttl_seconds=cache_ttl)

    def collect_all(self, use_cache: bool = True) -> Dict[str, Any]:
        if use_cache:
            cached = self.cache.get("full_snapshot")
            if cached:
                return cached

        timestamp = time.time()

        system_data = get_system_info()
        cpu_data = get_cpu_info()
        memory_data = get_memory_info()
        temperature_data = get_temperature_info()
        storage_data = get_storage_info()
        disk_io_data = get_disk_io_info()
        network_data = get_network_info()
        wifi_data = get_wifi_info()
        battery_data = get_battery_info()
        docker_data = get_docker_info()
        services_data = get_services_info()
        security_data = get_security_info()
        processes_data = get_top_processes()
        duckdns_data = get_duckdns_info()

        snapshot = {
            "timestamp": timestamp,
            "system": system_data,
            "cpu": cpu_data,
            "memory": memory_data,
            "temperature": temperature_data,
            "storage": storage_data,
            "disk_io": disk_io_data,
            "network": network_data,
            "wifi": wifi_data,
            "battery": battery_data,
            "docker": docker_data,
            "services": services_data,
            "security": security_data,
            "processes": processes_data,
            "duckdns": duckdns_data
        }

        self.cache.set("full_snapshot", snapshot)
        return snapshot
