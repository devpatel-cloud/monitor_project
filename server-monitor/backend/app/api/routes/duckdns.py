from fastapi import APIRouter
from backend.app.agent_bridge import get_latest_snapshot

router = APIRouter(prefix="/duckdns", tags=["duckdns"])

@router.get("")
def get_duckdns():
    snapshot = get_latest_snapshot()
    data = snapshot.get("duckdns", {})
    # Ensure token is never included in response
    data.pop("token", None)
    return data
