from fastapi import APIRouter
from backend.app.agent_bridge import get_latest_snapshot

router = APIRouter(prefix="/network", tags=["network"])

@router.get("")
def get_network():
    snapshot = get_latest_snapshot()
    return {
        "network": snapshot.get("network", {}),
        "wifi": snapshot.get("wifi", {})
    }
