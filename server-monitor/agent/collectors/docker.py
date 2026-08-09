import os
import json
import subprocess
from typing import Dict, Any, List

def run_cmd(cmd: List[str]) -> str:
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return ""

def get_docker_info() -> Dict[str, Any]:
    """
    Monitors Docker daemon status, container states, CPU/Memory usage, images, volumes, and networks.
    Returns daemon_status 'STOPPED' or 'UNAVAILABLE' if Docker is not running.
    """
    docker_sock = "/var/run/docker.sock"
    if not os.path.exists(docker_sock):
        # Also check docker binary presence
        if not run_cmd(["which", "docker"]):
            return {
                "daemon_status": "NOT_INSTALLED",
                "containers_total": 0,
                "containers_running": 0,
                "containers_stopped": 0,
                "images_total": 0,
                "volumes_total": 0,
                "containers": []
            }

    # Query docker info
    info_json = run_cmd(["docker", "info", "--format", "{{json .}}"])
    if not info_json:
        return {
            "daemon_status": "STOPPED",
            "containers_total": 0,
            "containers_running": 0,
            "containers_stopped": 0,
            "images_total": 0,
            "volumes_total": 0,
            "containers": []
        }

    containers_total = 0
    containers_running = 0
    containers_stopped = 0
    images_total = 0

    try:
        info_data = json.loads(info_json)
        containers_total = info_data.get("Containers", 0)
        containers_running = info_data.get("ContainersRunning", 0)
        containers_stopped = info_data.get("ContainersStopped", 0)
        images_total = info_data.get("Images", 0)
    except Exception:
        pass

    # Query volumes
    volumes_total = 0
    vols_json = run_cmd(["docker", "volume", "ls", "--format", "{{json .}}"])
    if vols_json:
        volumes_total = len(vols_json.splitlines())

    # Query container metrics via docker stats
    containers_list: List[Dict[str, Any]] = []
    stats_json = run_cmd(["docker", "stats", "--no-stream", "--format", "{{json .}}"])
    if stats_json:
        for line in stats_json.splitlines():
            try:
                c_stat = json.loads(line)
                name = c_stat.get("Name", "")
                cpu_pct = float(c_stat.get("CPUPerc", "0%").rstrip("%"))
                mem_usage_str = c_stat.get("MemUsage", "0B / 0B")
                mem_parts = mem_usage_str.split("/")
                mem_used = mem_parts[0].strip() if len(mem_parts) > 0 else "0B"
                mem_limit = mem_parts[1].strip() if len(mem_parts) > 1 else "0B"
                net_io = c_stat.get("NetIO", "0B / 0B")
                net_parts = net_io.split("/")
                net_rx = net_parts[0].strip() if len(net_parts) > 0 else "0B"
                net_tx = net_parts[1].strip() if len(net_parts) > 1 else "0B"

                containers_list.append({
                    "id": c_stat.get("ID", ""),
                    "name": name,
                    "image": c_stat.get("Container", ""),
                    "status": "RUNNING",
                    "cpu_percent": cpu_pct,
                    "memory_used": mem_used,
                    "memory_limit": mem_limit,
                    "network_rx": net_rx,
                    "network_tx": net_tx,
                    "restart_count": 0
                })
            except Exception:
                pass

    return {
        "daemon_status": "RUNNING",
        "containers_total": containers_total,
        "containers_running": containers_running,
        "containers_stopped": containers_stopped,
        "images_total": images_total,
        "volumes_total": volumes_total,
        "containers": containers_list
    }
