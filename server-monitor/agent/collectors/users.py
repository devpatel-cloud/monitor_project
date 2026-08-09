import subprocess
from typing import List, Dict, Any

def get_logged_in_users() -> List[Dict[str, Any]]:
    """
    Collects currently logged-in system users.
    """
    users = []
    try:
        res = subprocess.run(["who"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3)
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 3:
                    users.append({
                        "username": parts[0],
                        "tty": parts[1],
                        "login_time": f"{parts[2]} {parts[3]}",
                        "ip": parts[4].strip("()") if len(parts) >= 5 else "local"
                    })
    except Exception:
        pass
    return users
