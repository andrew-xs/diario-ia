from sqlalchemy.orm import Session

from app.models.reporter_report import ReporterReport
from app.models.editor_draft import EditorDraft


def slugify(text: str) -> str:
    return text.lower().replace(" ", "-")


def build_content(report: ReporterReport) -> str:
    return f"""
{report.title}

{report.report_body}

Fuentes consolidadas: {report.source_count}
"""


def process_reports(db: Session) -> dict:
    reports = db.query(ReporterReport).all()

    created_drafts = 0

    for report in reports:
        exists = db.query(EditorDraft).filter(EditorDraft.reporter_report_id == report.id).first()
        if exists:
            continue

        action = "create"  # luego será lógica real

        draft = EditorDraft(
            story_id=report.story_id,
            reporter_report_id=report.id,
            title=report.title,
            slug=slugify(report.title),
            content=build_content(report),
            action=action,
            status="draft",
        )

        db.add(draft)
        created_drafts += 1

    db.commit()

    return {
        "status": "ok",
        "reports_processed": len(reports),
        "drafts_created": created_drafts,
    }