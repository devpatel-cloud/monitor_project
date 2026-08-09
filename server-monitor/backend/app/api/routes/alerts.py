from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.database import get_db
from backend.app.database.models import AlertRecord
from backend.app.agent_bridge import get_latest_snapshot
from backend.app.services.alerts import alert_engine

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("")
def get_alerts(db: Session = Depends(get_db)):
    snapshot = get_latest_snapshot()
    # Evaluate current active alerts
    alert_engine.evaluate_snapshot(db, snapshot)

    records = db.query(AlertRecord).order_by(AlertRecord.timestamp.desc()).limit(100).all()
    return [{
        "id": r.id,
        "timestamp": r.timestamp,
        "subsystem": r.subsystem,
        "severity": r.severity,
        "title": r.title,
        "message": r.message,
        "resolved": r.resolved,
        "resolved_at": r.resolved_at
    } for r in records]

@router.post("/{alert_id}/resolve")
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    record = db.query(AlertRecord).filter(AlertRecord.id == alert_id).first()
    if record:
        record.resolved = True
        import time
        record.resolved_at = time.time()
        db.commit()
        return {"status": "success", "id": alert_id}
    return {"status": "not_found", "id": alert_id}
