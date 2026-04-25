from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.raw_article import RawArticle
from app.models.story import Story
from app.models.reporter_report import ReporterReport
from app.models.editor_draft import EditorDraft
from app.models.control_alert import ControlAlert
from app.models.blog_post import BlogPost
from app.models.social_post import SocialPost
from app.db.seed import seed_sources

router = APIRouter(prefix="/debug", tags=["debug"])


@router.delete("/articles")
def delete_articles(db: Session = Depends(get_db)):
    deleted = db.query(RawArticle).delete()
    db.commit()
    return {"status": "ok", "deleted_articles": deleted}


@router.delete("/posts")
def delete_posts(db: Session = Depends(get_db)):
    deleted = db.query(BlogPost).delete()
    db.commit()
    return {"status": "ok", "deleted_posts": deleted}


@router.post("/seed-sources")
def seed_default_sources(db: Session = Depends(get_db)):
    return seed_sources(db)


@router.delete("/reset")
def reset_pipeline_data(db: Session = Depends(get_db)):
    deleted_social_posts = db.query(SocialPost).delete()
    deleted_alerts = db.query(ControlAlert).delete()
    deleted_posts = db.query(BlogPost).delete()
    deleted_drafts = db.query(EditorDraft).delete()
    deleted_reports = db.query(ReporterReport).delete()
    deleted_stories = db.query(Story).delete()
    deleted_articles = db.query(RawArticle).delete()

    db.commit()

    return {
        "status": "ok",
        "deleted_articles": deleted_articles,
        "deleted_stories": deleted_stories,
        "deleted_reports": deleted_reports,
        "deleted_drafts": deleted_drafts,
        "deleted_alerts": deleted_alerts,
        "deleted_posts": deleted_posts,
        "deleted_social_posts": deleted_social_posts,
    }
