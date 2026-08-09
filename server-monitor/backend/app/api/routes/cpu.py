from fastapi import APIRouter
from backend.app.agent_bridge import get_latest_snapshot

router = APIRouter(prefix="/cpu", tags=["cpu"])

@router.get("")
def get_cpu():
    snapshot = get_latest_snapshot()
    return snapshot.get("cpu", {})
