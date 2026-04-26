from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.control_alert import ControlAlert
from app.schemas import ControlAlertSchema
from app.services.control import run_control_checks

router = APIRouter(prefix="/control", tags=["control"])


@router.post("/run")
def run_control(db: Session = Depends(get_db)):
    return run_control_checks(db)


@router.get("/alerts", response_model=list[ControlAlertSchema])
def list_alerts(db: Session = Depends(get_db)):
    alerts = db.query(ControlAlert).all()
    return alerts