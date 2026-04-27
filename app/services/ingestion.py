from datetime import datetime

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.source import Source
from app.models.raw_article import RawArticle

logger = get_logger(__name__)


def build_mock_title(source_name: str) -> tuple[str, str]:
    if source_name in ["latercera", "emol", "24horas"]:
        return "Gobierno anuncia nueva medida economica", "economia"
    return "Evento relevante en la agenda nacional", "general"


def run_mock_ingestion(db: Session) -> dict:
    logger.info("Ingestion iniciada")

    try:
        sources = db.query(Source).filter(Source.active == True).all()
        created = 0

        for source in sources:
            sample_url = f"{source.base_url.rstrip('/')}/mock-article-{source.id}"

            exists = db.query(RawArticle).filter(RawArticle.url == sample_url).first()
            if exists:
                continue

            title, category = build_mock_title(source.name)

            article = RawArticle(
                source_id=source.id,
                title=title,
                url=sample_url,
                summary=f"Resumen de prueba para la fuente {source.name}.",
                body=f"Cuerpo de prueba generado para la fuente {source.name}.",
                category_hint=category,
                extraction_quality="metadata_only",
                extraction_notes="Articulo simulado para validar el pipeline inicial.",
                published_at=datetime.utcnow(),
            )

            db.add(article)
            created += 1

        db.commit()

        logger.info(
            "Ingestion finalizada | sources_processed=%s articles_created=%s",
            len(sources),
            created,
        )

        return {
            "status": "ok",
            "sources_processed": len(sources),
            "articles_created": created,
        }

    except Exception as exc:
        db.rollback()
        logger.exception("Ingestion fallo: %s", exc)

        return {
            "status": "error",
            "error": str(exc),
            "sources_processed": 0,
            "articles_created": 0,
        }