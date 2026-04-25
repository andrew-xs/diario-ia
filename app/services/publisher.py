from sqlalchemy.orm import Session

from app.models.editor_draft import EditorDraft
from app.models.blog_post import BlogPost


def publish_drafts(db: Session) -> dict:
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

    return {
        "status": "ok",
        "drafts_processed": len(drafts),
        "posts_published": published,
    }