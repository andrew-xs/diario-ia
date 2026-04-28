from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.reporter_report import ReporterReport
from app.models.editor_draft import EditorDraft
from app.models.control_alert import ControlAlert

logger = get_logger(__name__)


def compare_report_and_draft(report: ReporterReport, draft: EditorDraft) -> list[dict]:
    alerts = []

    if report.title != draft.title:
        alerts.append(
            {
                "severity": "medium",
                "field_name": "title",
                "message": "El titulo del draft difiere del titulo del reporte.",
                "suggested_fix": "Revisar si el cambio es editorialmente correcto.",
            }
        )

    if "Fuentes consolidadas" not in draft.content:
        alerts.append(
            {
                "severity": "low",
                "field_name": "content",
                "message": "El draft no menciona explicitamente la cantidad de fuentes consolidadas.",
                "suggested_fix": "Agregar una mencion a la consolidacion de fuentes.",
            }
        )

    if not report.summary or len(report.summary) < 20:
        alerts.append(
            {
                "severity": "low",
                "field_name": "summary",
                "message": "El reporte tiene un resumen debil o ausente.",
                "suggested_fix": "Revisar la calidad del resumen generado.",
            }
        )

    return alerts


def run_control_checks(db: Session) -> dict:
    logger.info("Control iniciado")

    try:
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

        logger.info(
            "Control finalizado | drafts_checked=%s drafts_skipped_already_approved=%s alerts_created=%s drafts_approved=%s drafts_blocked=%s",
            drafts_checked,
            drafts_skipped_already_approved,
            alerts_created,
            drafts_approved,
            drafts_blocked,
        )

        return {
            "status": "ok",
            "drafts_checked": drafts_checked,
            "drafts_skipped_already_approved": drafts_skipped_already_approved,
            "alerts_created": alerts_created,
            "drafts_approved": drafts_approved,
            "drafts_blocked": drafts_blocked,
        }

    except Exception as exc:
        db.rollback()
        logger.exception("Control fallo: %s", exc)

        return {
            "status": "error",
            "error": str(exc),
            "drafts_checked": 0,
            "drafts_skipped_already_approved": 0,
            "alerts_created": 0,
            "drafts_approved": 0,
            "drafts_blocked": 0,
        }