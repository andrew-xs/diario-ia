from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.editor_draft import EditorDraft
from app.models.blog_post import BlogPost

logger = get_logger(__name__)


def publish_drafts(db: Session) -> dict:
    logger.info("Publisher iniciado")

    try:
        drafts = db.query(EditorDraft).filter(EditorDraft.status == "approved").all()
        published = 0

        for draft in drafts:
            exists = db.query(BlogPost).filter(BlogPost.editor_draft_id == draft.id).first()

            if exists:
                continue

            post = BlogPost(
                story_id=draft.story_id,
                editor_draft_id=draft.id,
                title=draft.title,
                slug=draft.slug,
                content=draft.content,
                status="published",
            )

            db.add(post)
            published += 1

        db.commit()

        logger.info(
            "Publisher finalizado | drafts_processed=%s posts_published=%s",
            len(drafts),
            published,
        )

        return {
            "status": "ok",
            "drafts_processed": len(drafts),
            "posts_published": published,
        }

    except Exception as exc:
        db.rollback()
        logger.exception("Publisher fallo: %s", exc)

        return {
            "status": "error",
            "error": str(exc),
            "drafts_processed": 0,
            "posts_published": 0,
        }