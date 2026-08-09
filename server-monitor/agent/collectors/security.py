import os
import subprocess
from typing import Dict, Any, List

def run_cmd(cmd: List[str]) -> str:
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=4)
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return ""

def get_firewalld_status() -> Dict[str, Any]:
    state = "INACTIVE"
    active_zones = []
    output = run_cmd(["firewall-cmd", "--state"])
    if output == "running":
        state = "RUNNING"
        zones_out = run_cmd(["firewall-cmd", "--get-active-zones"])
        if zones_out:
            active_zones = zones_out.splitlines()

    return {
        "status": state,
        "active_zones": active_zones
    }

def get_selinux_status() -> Dict[str, Any]:
    status = "Disabled"
    mode = "disabled"

    out = run_cmd(["getenforce"])
    if out:
        mode = out.lower()
        if mode == "enforcing":
            status = "Enforcing"
        elif mode == "permissive":
            status = "Permissive"

    return {
        "status": status,
        "mode": mode
    }

def get_logged_in_users() -> List[Dict[str, Any]]:
    users = []
    out = run_cmd(["who"])
    if out:
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 3:
                user = parts[0]
                tty = parts[1]
                login_time = " ".join(parts[2:4])
                ip = parts[4].strip("()") if len(parts) >= 5 else "local"
                users.append({
                    "username": user,
                    "terminal": tty,
                    "login_time": login_time,
                    "remote_host": ip
                })
    return users

def get_journal_events() -> Dict[str, Any]:
    failed_ssh_count = 0
    successful_ssh_count = 0
    oom_events_count = 0
    critical_errors: List[str] = []

    # Check journalctl for SSH failed attempts
    ssh_failed = run_cmd(["journalctl", "-u", "sshd", "-g", "Failed password", "--since", "24 hours ago", "-o", "cat"])
    if ssh_failed:
        failed_ssh_count = len(ssh_failed.splitlines())

    ssh_accepted = run_cmd(["journalctl", "-u", "sshd", "-g", "Accepted", "--since", "24 hours ago", "-o", "cat"])
    if ssh_accepted:
        successful_ssh_count = len(ssh_accepted.splitlines())

    # Check for OOM events in journal
    oom_out = run_cmd(["journalctl", "-k", "-g", "Out of memory", "--since", "24 hours ago", "-o", "cat"])
    if oom_out:
        oom_events_count = len(oom_out.splitlines())

    # Check critical kernel/system journal errors
    err_out = run_cmd(["journalctl", "-p", "3", "-n", "10", "--since", "1 hour ago", "-o", "cat"])
    if err_out:
        critical_errors = err_out.splitlines()[:5]

    return {
        "failed_ssh_24h": failed_ssh_count,
        "successful_ssh_24h": successful_ssh_count,
        "oom_events_24h": oom_events_count,
        "recent_critical_errors": critical_errors
    }

def get_security_info() -> Dict[str, Any]:
    """
    Collects security posture: firewalld, SELinux, logged-in users, SSH audit, OOM/journal errors.
    """
    fw = get_firewalld_status()
    selinux = get_selinux_status()
    users = get_logged_in_users()
    events = get_journal_events()

    return {
        "firewalld": fw,
        "selinux": selinux,
        "logged_in_users": users,
        "events": events
    }
