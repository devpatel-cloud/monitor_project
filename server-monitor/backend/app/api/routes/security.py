from fastapi import APIRouter
from backend.app.agent_bridge import get_latest_snapshot

router = APIRouter(prefix="/security", tags=["security"])

@router.get("")
def get_security():
    snapshot = get_latest_snapshot()
    return snapshot.get("security", {})
