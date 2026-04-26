from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.blog_post import BlogPost
from app.schemas import BlogPostSchema
from app.services.publisher import publish_drafts

router = APIRouter(prefix="/publisher", tags=["publisher"])


@router.post("/publish")
def run_publisher(db: Session = Depends(get_db)):
    return publish_drafts(db)


@router.get("/posts", response_model=list[BlogPostSchema])
def list_posts(db: Session = Depends(get_db)):
    posts = db.query(BlogPost).all()
    return posts