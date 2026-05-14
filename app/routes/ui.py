from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.blog_post import BlogPost
from app.models.control_alert import ControlAlert
from app.models.editor_draft import EditorDraft
from app.models.raw_article import RawArticle

router = APIRouter(prefix="/ui", tags=["ui"])

_HERE = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(_HERE.parent / "templates"))


def extract_editorial_score(content: str | None) -> str:
    if not content:
        return "—"

    for line in content.splitlines():
        if line.startswith("Puntaje editorial:"):
            return line.replace("Puntaje editorial:", "").strip()

    return "—"


def extract_editorial_priority(content: str | None) -> str:
    if not content:
        return "—"

    for line in content.splitlines():
        if line.startswith("Prioridad editorial:"):
            return line.replace("Prioridad editorial:", "").strip()

    return "—"


@router.get("", response_class=HTMLResponse)
def ui(request: Request, db: Session = Depends(get_db)):
    category = request.query_params.get("category")

    articles_query = db.query(RawArticle)

    if category:
        articles_query = articles_query.filter(RawArticle.category_hint == category)

    articles = (
        articles_query.order_by(RawArticle.published_at.desc())
        .limit(20)
        .all()
    )

    posts = db.query(BlogPost).order_by(BlogPost.id.desc()).limit(10).all()

    drafts = db.query(EditorDraft).order_by(EditorDraft.id.desc()).limit(15).all()

    draft_rows = []
    for draft in drafts:
        open_alerts = (
            db.query(ControlAlert)
            .filter(
                ControlAlert.editor_draft_id == draft.id,
                ControlAlert.status == "open",
            )
            .count()
        )

        draft_rows.append(
            {
                "id": draft.id,
                "title": draft.title,
                "status": draft.status,
                "priority": draft.editorial_priority or "—",
                "score": draft.editorial_score if draft.editorial_score is not None else "—",
                "open_alerts": open_alerts,
            }
        )

    categories = db.query(RawArticle.category_hint).distinct().all()
    categories = [c[0] for c in categories if c[0]]

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Diario IA",
            "articles": articles,
            "posts": posts,
            "drafts": draft_rows,
            "categories": categories,
            "selected_category": category,
        },
    )