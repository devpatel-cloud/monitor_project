from fastapi import APIRouter
from backend.app.agent_bridge import get_latest_snapshot

router = APIRouter(prefix="/memory", tags=["memory"])

@router.get("")
def get_memory():
    snapshot = get_latest_snapshot()
    return snapshot.get("memory", {})
