from fastapi import APIRouter
from backend.app.agent_bridge import get_latest_snapshot

router = APIRouter(prefix="/system", tags=["system"])

@router.get("")
def get_system():
    snapshot = get_latest_snapshot()
    return snapshot.get("system", {})
