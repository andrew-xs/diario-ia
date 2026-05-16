from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.raw_article import RawArticle
from app.schemas import RawArticleSchema

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=list[RawArticleSchema])
def list_articles(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    category: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(RawArticle)

    if category:
        query = query.filter(RawArticle.category_hint == category)

    articles = (
        query.order_by(RawArticle.published_at.desc().nullslast(), RawArticle.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return articles