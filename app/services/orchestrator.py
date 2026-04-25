from sqlalchemy.orm import Session

from app.services.ingestion import run_mock_ingestion
from app.services.stories import assign_articles_to_stories
from app.services.reporter import generate_reports
from app.services.editor import process_reports
from app.services.control import run_control_checks
from app.services.publisher import publish_drafts
from app.services.community import publish_social_posts


def run_full_pipeline(db: Session) -> dict:
    results = {}

    # 1. Ingesta
    results["ingestion"] = run_mock_ingestion(db)

    # 2. Agrupar en stories
    results["stories"] = assign_articles_to_stories(db)

    # 3. Generar reportes
    results["reporter"] = generate_reports(db)

    # 4. Procesar drafts editoriales
    results["editor"] = process_reports(db)

    # 5. Control de calidad
    results["control"] = run_control_checks(db)

    # 6. Publicación
    results["publisher"] = publish_drafts(db)

    # 7. RRSS
    results["community"] = publish_social_posts(db)

    return {
        "status": "ok",
        "pipeline_results": results,
    }