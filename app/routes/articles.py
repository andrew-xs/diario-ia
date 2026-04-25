from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.raw_article import RawArticle

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("")
def list_articles(db: Session = Depends(get_db)):
    articles = db.query(RawArticle).all()
    return articles