from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.orchestrator import run_full_pipeline

router = APIRouter(prefix="/orchestrator", tags=["orchestrator"])


@router.post("/run")
def run_orchestrator(db: Session = Depends(get_db)):
    return run_full_pipeline(db)