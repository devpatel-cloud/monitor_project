import subprocess
from fastapi import APIRouter, Depends, HTTPException, Query, status
from backend.app.agent_bridge import get_latest_snapshot
from backend.app.core.security import get_current_user, require_admin

router = APIRouter(prefix="/services", tags=["services"])

APPROVED_SERVICES = {
    "nginx",
    "docker",
    "sshd",
    "NetworkManager",
    "chronyd",
    "firewalld",
    "server-monitor",
    "server-monitor-backend",
    "server-monitor-collector",
    "duckdns-ipv6",
    "sanjaya"
}

def validate_service_name(service_name: str):
    clean_name = service_name.replace(".service", "")
    if clean_name not in APPROVED_SERVICES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Service '{service_name}' is not on the approved management whitelist."
        )
    return clean_name

def execute_systemctl(action: str, service_name: str) -> dict:
    clean_name = validate_service_name(service_name)
    cmd = ["sudo", "systemctl", action, f"{clean_name}.service"]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        if res.returncode == 0:
            return {"status": "success", "action": action, "service": clean_name}
        else:
            # Try without sudo fallback if already root
            cmd = ["systemctl", action, f"{clean_name}.service"]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            if res.returncode == 0:
                return {"status": "success", "action": action, "service": clean_name}
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to {action} {clean_name}: {res.stderr.strip()}"
            )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
def get_services():
    snapshot = get_latest_snapshot()
    return snapshot.get("services", {})

@router.post("/{service}/start")
def start_service(service: str, current_user: dict = Depends(require_admin)):
    return execute_systemctl("start", service)

@router.post("/{service}/stop")
def stop_service(service: str, current_user: dict = Depends(require_admin)):
    return execute_systemctl("stop", service)

@router.post("/{service}/restart")
def restart_service(service: str, current_user: dict = Depends(require_admin)):
    return execute_systemctl("restart", service)

@router.post("/{service}/enable")
def enable_service(service: str, current_user: dict = Depends(require_admin)):
    return execute_systemctl("enable", service)

@router.post("/{service}/disable")
def disable_service(service: str, current_user: dict = Depends(require_admin)):
    return execute_systemctl("disable", service)

@router.get("/{service}/logs")
def get_service_logs(
    service: str,
    lines: int = Query(50, ge=5, le=500),
    current_user: dict = Depends(get_current_user)
):
    clean_name = validate_service_name(service)
    cmd = ["journalctl", "-u", f"{clean_name}.service", "-n", str(lines), "--no-pager", "-o", "cat"]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        log_content = res.stdout.strip() if res.returncode == 0 else f"No logs retrieved for {clean_name}"
        return {
            "service": clean_name,
            "lines": lines,
            "logs": log_content.splitlines()
        }
    except Exception as e:
        return {"service": clean_name, "lines": lines, "logs": [f"Error reading journal logs: {str(e)}"]}
