from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database.database import get_db
from backend.app.services.history import (
    get_cpu_history, get_memory_history, get_temperature_history, get_network_history, get_disk_io_history
)

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/cpu")
def history_cpu(
    range: Optional[str] = Query("15m", description="Time range string (e.g. 15m, 30m, 1h, 3h, 6h, 12h, 24h)"),
    range_hours: Optional[float] = Query(None, description="Legacy fallback range in hours"),
    db: Session = Depends(get_db)
):
    selected_range = range if range else (f"{range_hours}h" if range_hours else "15m")
    return get_cpu_history(db, range_str=selected_range)

@router.get("/memory")
def history_memory(
    range: Optional[str] = Query("15m", description="Time range string (e.g. 15m, 30m, 1h, 3h, 6h, 12h, 24h)"),
    range_hours: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    selected_range = range if range else (f"{range_hours}h" if range_hours else "15m")
    return get_memory_history(db, range_str=selected_range)

@router.get("/temperature")
def history_temperature(
    range: Optional[str] = Query("15m", description="Time range string (e.g. 15m, 30m, 1h, 3h, 6h, 12h, 24h)"),
    range_hours: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    selected_range = range if range else (f"{range_hours}h" if range_hours else "15m")
    return get_temperature_history(db, range_str=selected_range)

@router.get("/network")
def history_network(
    range: Optional[str] = Query("15m", description="Time range string (e.g. 15m, 30m, 1h, 3h, 6h, 12h, 24h)"),
    range_hours: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    selected_range = range if range else (f"{range_hours}h" if range_hours else "15m")
    return get_network_history(db, range_str=selected_range)

@router.get("/disk")
def history_disk(
    range: Optional[str] = Query("15m", description="Time range string (e.g. 15m, 30m, 1h, 3h, 6h, 12h, 24h)"),
    range_hours: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    selected_range = range if range else (f"{range_hours}h" if range_hours else "15m")
    return get_disk_io_history(db, range_str=selected_range)
