from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.story import Story
from app.schemas import StorySchema
from app.services.stories import assign_articles_to_stories

router = APIRouter(prefix="/stories", tags=["stories"])


@router.post("/resolve")
def resolve_stories(db: Session = Depends(get_db)):
    return assign_articles_to_stories(db)


@router.get("", response_model=list[StorySchema])
def list_stories(db: Session = Depends(get_db)):
    stories = db.query(Story).all()
    return stories