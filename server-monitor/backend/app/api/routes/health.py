from fastapi import APIRouter
from backend.app.agent_bridge import get_latest_snapshot
from backend.app.services.metrics import calculate_health_score

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
def get_health_status():
    snapshot = get_latest_snapshot()
    health_score = calculate_health_score(snapshot)
    return {
        "status": "online",
        "health_score": health_score,
        "timestamp": snapshot.get("timestamp")
    }
