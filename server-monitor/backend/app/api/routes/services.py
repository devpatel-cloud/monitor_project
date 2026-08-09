from fastapi import APIRouter
from backend.app.agent_bridge import get_latest_snapshot

router = APIRouter(prefix="/services", tags=["services"])

@router.get("")
def get_services():
    snapshot = get_latest_snapshot()
    return snapshot.get("services", {})
