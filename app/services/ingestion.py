from datetime import datetime

from sqlalchemy.orm import Session

from app.models.source import Source
from app.models.raw_article import RawArticle


def build_mock_title(source_name: str) -> tuple[str, str]:
    if source_name in ["latercera", "emol", "24horas"]:
        return (
            "Gobierno anuncia nuevas medidas económicas",
            "economia",
        )
    if source_name in ["biobiochile", "ciperchile"]:
        return (
            "Investigan irregularidades en organismo público",
            "actualidad",
        )
    return (
        f"Artículo de prueba desde {source_name}",
        "actualidad",
    )


def run_mock_ingestion(db: Session) -> dict:
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
            extraction_notes="Artículo simulado para validar el pipeline inicial.",
            published_at=datetime.utcnow(),
        )
        db.add(article)
        created += 1

    db.commit()

    return {
        "status": "ok",
        "sources_processed": len(sources),
        "articles_created": created,
    }