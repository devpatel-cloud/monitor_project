from fastapi import APIRouter
from backend.app.agent_bridge import get_latest_snapshot

router = APIRouter(prefix="/storage", tags=["storage"])

@router.get("")
def get_storage():
    snapshot = get_latest_snapshot()
    return {
        "storage": snapshot.get("storage", {}),
        "disk_io": snapshot.get("disk_io", {})
    }
