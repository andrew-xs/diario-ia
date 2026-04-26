from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.raw_article import RawArticle
from app.schemas import RawArticleSchema

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=list[RawArticleSchema])
def list_articles(db: Session = Depends(get_db)):
    articles = db.query(RawArticle).all()
    return articles