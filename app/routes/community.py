from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.social_post import SocialPost
from app.services.community import publish_social_posts

router = APIRouter(prefix="/community", tags=["community"])


@router.post("/publish")
def run_community_manager(db: Session = Depends(get_db)):
    return publish_social_posts(db)


@router.get("/posts")
def list_social_posts(db: Session = Depends(get_db)):
    posts = db.query(SocialPost).all()
    return posts