from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.ingestion import run_mock_ingestion

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run")
def run_pipeline(db: Session = Depends(get_db)):
    result = run_mock_ingestion(db)
    return result