import os
import subprocess
from typing import Dict, Any, List

def get_top_processes(limit: int = 10) -> Dict[str, Any]:
    """
    Collects top CPU and Memory consuming processes via ps aux.
    """
    top_cpu: List[Dict[str, Any]] = []
    top_memory: List[Dict[str, Any]] = []

    try:
        res = subprocess.run(
            ["ps", "-eo", "pid,user,%cpu,%mem,comm", "--sort=-%cpu"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3
        )
        if res.returncode == 0:
            lines = res.stdout.splitlines()[1:limit+1]
            for line in lines:
                parts = line.split(maxsplit=4)
                if len(parts) >= 5:
                    top_cpu.append({
                        "pid": int(parts[0]),
                        "user": parts[1],
                        "cpu_percent": float(parts[2]),
                        "mem_percent": float(parts[3]),
                        "command": parts[4]
                    })

        res_mem = subprocess.run(
            ["ps", "-eo", "pid,user,%cpu,%mem,comm", "--sort=-%mem"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3
        )
        if res_mem.returncode == 0:
            lines = res_mem.stdout.splitlines()[1:limit+1]
            for line in lines:
                parts = line.split(maxsplit=4)
                if len(parts) >= 5:
                    top_memory.append({
                        "pid": int(parts[0]),
                        "user": parts[1],
                        "cpu_percent": float(parts[2]),
                        "mem_percent": float(parts[3]),
                        "command": parts[4]
                    })
    except Exception:
        pass

    return {
        "top_cpu": top_cpu,
        "top_memory": top_memory
    }
