from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.editor_draft import EditorDraft
from app.services.editor import process_reports

router = APIRouter(prefix="/editor", tags=["editor"])


@router.post("/process")
def run_editor(db: Session = Depends(get_db)):
    return process_reports(db)


@router.get("/drafts")
def list_drafts(db: Session = Depends(get_db)):
    drafts = db.query(EditorDraft).all()
    return drafts