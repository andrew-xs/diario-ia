from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.source import Source
from app.schemas import SourceSchema

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=list[SourceSchema])
def list_sources(db: Session = Depends(get_db)):
    sources = db.query(Source).all()
    return sources