from fastapi import APIRouter
from backend.app.agent_bridge import get_latest_snapshot

router = APIRouter(prefix="/docker", tags=["docker"])

@router.get("")
def get_docker():
    snapshot = get_latest_snapshot()
    return snapshot.get("docker", {})
