from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database.database import get_db
from backend.app.services.history import (
    get_cpu_history, get_memory_history, get_temperature_history, get_network_history
)

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/cpu")
def history_cpu(range_hours: float = Query(24.0, ge=0.1, le=8760.0), db: Session = Depends(get_db)):
    return get_cpu_history(db, range_hours=range_hours)

@router.get("/memory")
def history_memory(range_hours: float = Query(24.0, ge=0.1, le=8760.0), db: Session = Depends(get_db)):
    return get_memory_history(db, range_hours=range_hours)

@router.get("/temperature")
def history_temperature(range_hours: float = Query(24.0, ge=0.1, le=8760.0), db: Session = Depends(get_db)):
    return get_temperature_history(db, range_hours=range_hours)

@router.get("/network")
def history_network(range_hours: float = Query(24.0, ge=0.1, le=8760.0), db: Session = Depends(get_db)):
    return get_network_history(db, range_hours=range_hours)
