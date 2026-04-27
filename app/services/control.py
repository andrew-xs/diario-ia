from sqlalchemy.orm import Session

from app.models.reporter_report import ReporterReport
from app.models.editor_draft import EditorDraft
from app.models.control_alert import ControlAlert


def compare_report_and_draft(report: ReporterReport, draft: EditorDraft) -> list[dict]:
    alerts = []

    if report.title.strip() != draft.title.strip():
        alerts.append(
            {
                "severity": "medium",
                "field_name": "title",
                "message": "El título del draft difiere del título del reporte.",
                "suggested_fix": "Revisar si el cambio es editorialmente correcto.",
            }
        )

    if str(report.source_count) not in draft.content:
        alerts.append(
            {
                "severity": "low",
                "field_name": "content",
                "message": "El draft no menciona explícitamente la cantidad de fuentes consolidadas.",
                "suggested_fix": "Agregar una mención a la consolidación de fuentes.",
            }
        )

    if not report.summary or report.summary == "Sin resumen disponible.":
        alerts.append(
            {
                "severity": "low",
                "field_name": "summary",
                "message": "El reporte tiene un resumen débil o ausente.",
                "suggested_fix": "Mejorar el resumen antes de publicar.",
            }
        )

    return alerts


def run_control_checks(db: Session) -> dict:
    drafts_to_check = (
        db.query(EditorDraft)
        .filter(EditorDraft.status.in_(["draft", "needs_review"]))
        .all()
    )

    drafts_skipped_already_approved = (
        db.query(EditorDraft)
        .filter(EditorDraft.status == "approved")
        .count()
    )

    drafts_checked = 0
    alerts_created = 0
    drafts_approved = 0
    drafts_blocked = 0

    for draft in drafts_to_check:
        report = (
            db.query(ReporterReport)
            .filter(ReporterReport.id == draft.reporter_report_id)
            .first()
        )

        if not report:
            continue

        drafts_checked += 1

        existing_alerts = (
            db.query(ControlAlert)
            .filter(ControlAlert.editor_draft_id == draft.id)
            .count()
        )

        if existing_alerts > 0:
            continue

        alerts = compare_report_and_draft(report, draft)

        if alerts:
            for item in alerts:
                db.add(
                    ControlAlert(
                        story_id=report.story_id,
                        reporter_report_id=report.id,
                        editor_draft_id=draft.id,
                        severity=item["severity"],
                        field_name=item["field_name"],
                        message=item["message"],
                        suggested_fix=item["suggested_fix"],
                        status="open",
                    )
                )
                alerts_created += 1

            draft.status = "needs_review"
            drafts_blocked += 1
        else:
            draft.status = "approved"
            drafts_approved += 1

    db.commit()

    return {
        "status": "ok",
        "drafts_checked": drafts_checked,
        "drafts_skipped_already_approved": drafts_skipped_already_approved,
        "alerts_created": alerts_created,
        "drafts_approved": drafts_approved,
        "drafts_blocked": drafts_blocked,
    }
