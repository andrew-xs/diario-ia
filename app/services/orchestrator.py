from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.services.ingestion import run_mock_ingestion
from app.services.stories import assign_articles_to_stories
from app.services.reporter import generate_reports
from app.services.editor import process_reports
from app.services.control import run_control_checks
from app.services.publisher import publish_drafts
from app.services.community import publish_social_posts

logger = get_logger(__name__)


def run_full_pipeline(db: Session) -> dict:
    logger.info("Orchestrator iniciado")

    results = {}

    stages = [
        ("ingestion", run_mock_ingestion),
        ("stories", assign_articles_to_stories),
        ("reporter", generate_reports),
        ("editor", process_reports),
        ("control", run_control_checks),
        ("publisher", publish_drafts),
        ("community", publish_social_posts),
    ]

    for stage_name, stage_fn in stages:
        logger.info("Ejecutando etapa: %s", stage_name)

        try:
            result = stage_fn(db)
            results[stage_name] = result

            if result.get("status") == "error":
                logger.error("Etapa %s retorno error controlado", stage_name)
            else:
                logger.info("Etapa %s finalizada correctamente", stage_name)

        except Exception as exc:
            logger.exception("Etapa %s lanzo excepcion: %s", stage_name, exc)
            results[stage_name] = {
                "status": "error",
                "error": str(exc),
            }

    pipeline_status = "ok"

    if any(item.get("status") == "error" for item in results.values()):
        pipeline_status = "partial_error"

    logger.info("Orchestrator finalizado | status=%s", pipeline_status)

    return {
        "status": pipeline_status,
        "pipeline_results": results,
    }