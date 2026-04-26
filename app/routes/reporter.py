from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.reporter_report import ReporterReport
from app.schemas import ReporterReportSchema
from app.services.reporter import generate_reports

router = APIRouter(prefix="/reporter", tags=["reporter"])


@router.post("/generate")
def run_reporter(db: Session = Depends(get_db)):
    return generate_reports(db)


@router.get("/reports", response_model=list[ReporterReportSchema])
def list_reports(db: Session = Depends(get_db)):
    reports = db.query(ReporterReport).all()
    return reports