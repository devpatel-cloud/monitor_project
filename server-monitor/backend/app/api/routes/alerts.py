import time
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.database import get_db
from backend.app.database.models import AlertRecord
from backend.app.agent_bridge import get_latest_snapshot
from backend.app.services.alerts import alert_engine
from backend.app.core.security import get_current_user, require_admin

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("")
def get_alerts(
    include_resolved: bool = Query(False, description="Include resolved alerts from history"),
    db: Session = Depends(get_db)
):
    snapshot = get_latest_snapshot()
    # Evaluate snapshot to apply automatic resolution and deduplication
    alert_engine.evaluate_snapshot(db, snapshot)

    query = db.query(AlertRecord)
    if not include_resolved:
        query = query.filter(AlertRecord.resolved == False)

    records = query.order_by(AlertRecord.timestamp.desc()).limit(100).all()
    return [{
        "id": r.id,
        "target_key": r.target_key,
        "timestamp": r.timestamp,
        "started_at": r.started_at or r.timestamp,
        "subsystem": r.subsystem,
        "severity": r.severity,
        "title": r.title,
        "message": r.message,
        "status": r.status or ("RESOLVED" if r.resolved else "ACTIVE"),
        "resolved": r.resolved,
        "resolved_at": r.resolved_at,
        "acknowledged_at": r.acknowledged_at,
        "acknowledged_by": r.acknowledged_by
    } for r in records]

@router.post("/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    record = db.query(AlertRecord).filter(AlertRecord.id == alert_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_440_NOT_FOUND if hasattr(status, 'HTTP_440_NOT_FOUND') else 404, detail="Alert not found")

    record.status = "ACKNOWLEDGED"
    record.acknowledged_at = time.time()
    record.acknowledged_by = current_user.get("username", "admin")
    db.commit()
    return {"status": "success", "id": alert_id, "alert_status": record.status}

@router.post("/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    record = db.query(AlertRecord).filter(AlertRecord.id == alert_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Alert not found")

    record.status = "RESOLVED"
    record.resolved = True
    record.resolved_at = time.time()
    db.commit()
    return {"status": "success", "id": alert_id, "alert_status": record.status}
