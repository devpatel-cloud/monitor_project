import time
import subprocess
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from backend.app.agent_bridge import get_latest_snapshot
from backend.app.database.database import get_db
from backend.app.database.models import AuditLogRecord
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

def execute_systemctl(action: str, service_name: str, db: Session, user: dict, req: Request) -> dict:
    clean_name = validate_service_name(service_name)
    username = user.get("username", "admin")
    client_ip = req.client.host if req.client else "127.0.0.1"
    now = time.time()

    cmd = ["sudo", "systemctl", action, f"{clean_name}.service"]
    res_code = -1
    err_msg = ""

    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        res_code = res.returncode
        if res_code != 0:
            # Fallback direct systemctl if running as root
            cmd = ["systemctl", action, f"{clean_name}.service"]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            res_code = res.returncode
            err_msg = res.stderr.strip()
    except Exception as e:
        err_msg = str(e)

    res_status = "success" if res_code == 0 else "failed"

    # Persist audit record in SQLite
    audit = AuditLogRecord(
        timestamp=now,
        user=username,
        action=action,
        service=clean_name,
        result=res_status,
        ip_address=client_ip
    )
    db.add(audit)
    db.commit()

    if res_code == 0:
        return {
            "success": True,
            "status": "success",
            "action": action,
            "service": clean_name,
            "message": f"Service {clean_name} {action}ed successfully"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to {action} {clean_name}: {err_msg}"
        )

@router.get("")
def get_services():
    snapshot = get_latest_snapshot()
    return snapshot.get("services", {})

@router.post("/{service}/start")
def start_service(service: str, req: Request, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    return execute_systemctl("start", service, db, current_user, req)

@router.post("/{service}/stop")
def stop_service(service: str, req: Request, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    return execute_systemctl("stop", service, db, current_user, req)

@router.post("/{service}/restart")
def restart_service(service: str, req: Request, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    return execute_systemctl("restart", service, db, current_user, req)

@router.post("/{service}/enable")
def enable_service(service: str, req: Request, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    return execute_systemctl("enable", service, db, current_user, req)

@router.post("/{service}/disable")
def disable_service(service: str, req: Request, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    return execute_systemctl("disable", service, db, current_user, req)

@router.get("/audit-logs")
def get_audit_logs(db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    records = db.query(AuditLogRecord).order_by(AuditLogRecord.timestamp.desc()).limit(50).all()
    return [{
        "id": r.id,
        "timestamp": r.timestamp,
        "user": r.user,
        "action": r.action,
        "service": r.service,
        "result": r.result,
        "ip_address": r.ip_address
    } for r in records]

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
