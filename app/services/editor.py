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

def calculate_editorial_score(report: ReporterReport) -> int:
    score = 0

    title = (report.title or "").lower()
    category = (report.category or "").lower()
    summary = (report.summary or "").lower()

    important_categories = {
        "politica": 25,
        "economia": 20,
        "seguridad": 20,
        "salud": 15,
        "internacional": 15,
        "tecnologia": 10,
        "general": 5,
    }

    score += important_categories.get(category, 5)

    high_impact_keywords = [
        "gobierno",
        "presidente",
        "ministro",
        "congreso",
        "ley",
        "hacienda",
        "salario",
        "crisis",
        "delito",
        "homicidio",
        "secuestro",
        "codelco",
        "corrupcion",
        "tribunal",
        "corte",
        "fiscalia",
        "migracion",
        "educacion",
        "salud",
    ]

    for keyword in high_impact_keywords:
        if keyword in title or keyword in summary:
            score += 5

    if report.source_count and report.source_count > 1:
        score += 10

    return min(score, 100)


def editorial_priority(score: int) -> str:
    if score >= 60:
        return "alta"
    if score >= 35:
        return "media"
    return "baja"

def build_content(report: ReporterReport) -> str:
    title = clean_title(report.title)

    score = calculate_editorial_score(report)
    priority = editorial_priority(score)

    intro = f"{title}."
    body = report.report_body or ""
    summary = report.summary or ""

    content = f"""{intro}

Prioridad editorial: {priority}
Puntaje editorial: {score}/100

Resumen:
{summary}

Desarrollo:
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

            score = calculate_editorial_score(report)
            priority = editorial_priority(score)

            raw_content = build_content(report)

            draft = EditorDraft(
                story_id=report.story_id,
                reporter_report_id=report.id,
                title=clean_title(report.title),
                slug=slugify(report.title),
                content=raw_content,
                raw_content=raw_content,
                action="create",
                status="draft",
                editorial_score=score,
                editorial_priority=priority,
                ai_status="not_processed",
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