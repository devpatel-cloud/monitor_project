from fastapi import APIRouter
from backend.app.agent_bridge import get_latest_snapshot

router = APIRouter(prefix="/battery", tags=["battery"])

@router.get("")
def get_battery():
    snapshot = get_latest_snapshot()
    return snapshot.get("battery", {})
