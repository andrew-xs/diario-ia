from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.reporter_report import ReporterReport
from app.models.editor_draft import EditorDraft

logger = get_logger(__name__)

def clean_title(title: str) -> str:
    t = title.strip()

    # cortar títulos compuestos típicos de RSS
    separators = [";", " y ", " | ", " – ", " - "]

    for sep in separators:
        if sep in t:
            t = t.split(sep)[0]

    return t.strip()

def slugify(text: str) -> str:
    return (
        text.lower()
        .replace(" ", "-")
        .replace(",", "")
        .replace(".", "")
        .replace(":", "")
        .replace(";", "")
    )


def build_content(report: ReporterReport) -> str:
    title=clean_title(report.title),

    intro = f"{title}."

    body = report.report_body or ""

    summary = report.summary or ""

    content = f"""{intro}

{summary}

{body}

Fuentes consolidadas: {report.source_count}
"""

    return content.strip()

def process_reports(db: Session) -> dict:
    logger.info("Editor iniciado")

    try:
        reports = db.query(ReporterReport).all()
        created_drafts = 0

        for report in reports:
            exists = db.query(EditorDraft).filter(
                EditorDraft.reporter_report_id == report.id
            ).first()

            if exists:
                continue

            draft = EditorDraft(
                story_id=report.story_id,
                reporter_report_id=report.id,
                title=report.title,
                slug=slugify(report.title),
                content=build_content(report),
                action="create",
                status="draft",
            )

            db.add(draft)
            created_drafts += 1

        db.commit()

        logger.info(
            "Editor finalizado | reports_processed=%s drafts_created=%s",
            len(reports),
            created_drafts,
        )

        return {
            "status": "ok",
            "reports_processed": len(reports),
            "drafts_created": created_drafts,
        }

    except Exception as exc:
        db.rollback()
        logger.exception("Editor fallo: %s", exc)

        return {
            "status": "error",
            "error": str(exc),
            "reports_processed": 0,
            "drafts_created": 0,
        }