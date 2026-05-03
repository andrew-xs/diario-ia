from datetime import datetime

import re
from html import unescape

import feedparser
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.source import Source
from app.models.raw_article import RawArticle

logger = get_logger(__name__)

def clean_html(text: str) -> str:
    if not text:
        return ""

    # decode entidades HTML
    text = unescape(text)

    # eliminar tags HTML
    text = re.sub(r"<.*?>", "", text)

    # eliminar espacios múltiples
    text = re.sub(r"\s+", " ", text)

    # limpiar basura común
    text = text.replace("Leer más", "")
    text = text.replace("Ver más", "")

    return text.strip()

def _parse_published(entry) -> datetime:
    published = entry.get("published_parsed") or entry.get("updated_parsed")

    if published:
        return datetime(*published[:6])

    return datetime.utcnow()


def classify_title(title: str) -> str:
    t = title.lower()

    if any(x in t for x in ["gobierno", "ministro", "presidente", "ley", "congreso", "diputado", "senado"]):
        return "politica"

    if any(x in t for x in ["economia", "inflacion", "salario", "hacienda", "pension", "sueldo", "mercado"]):
        return "economia"

    if any(x in t for x in ["ia", "tecnologia", "inteligencia artificial", "internet", "software", "digital"]):
        return "tecnologia"

    if any(x in t for x in ["internacional", "guerra", "eeuu", "china", "rusia", "ucrania", "israel"]):
        return "internacional"

    if any(x in t for x in ["salud", "hospital", "medico", "isapre", "fonasa", "licencia medica"]):
        return "salud"

    if any(x in t for x in ["delito", "carabinero", "pdi", "fiscalia", "robo", "homicidio", "narcotrafico"]):
        return "seguridad"

    if any(x in t for x in ["futbol", "deporte", "seleccion", "colo colo", "u de chile", "catolica"]):
        return "deportes"

    return "general"


def _detect_category(source: Source, entry) -> str | None:
    title = entry.get("title") or ""
    detected = classify_title(title)

    if detected != "general":
        return detected

    tags = entry.get("tags") or []

    if tags:
        first_tag = tags[0]
        term = first_tag.get("term") if isinstance(first_tag, dict) else None
        if term:
            return term.lower()

    return source.category_hint or "general"


def run_rss_ingestion(db: Session) -> dict:
    logger.info("Ingestion RSS iniciada")

    try:
        sources = db.query(Source).filter(Source.active == True).all()
        created = 0
        sources_processed = 0
        entries_seen = 0

        for source in sources:
            feed_url = source.base_url
            feed = feedparser.parse(feed_url)
            sources_processed += 1

            if feed.bozo:
                logger.warning(
                    "Feed con advertencia | source=%s url=%s error=%s",
                    source.name,
                    feed_url,
                    getattr(feed, "bozo_exception", "unknown"),
                )

            for entry in feed.entries[:15]:
                entries_seen += 1

                url = entry.get("link")
                if not url:
                    continue

                exists = db.query(RawArticle).filter(RawArticle.url == url).first()
                if exists:
                    continue

                title = entry.get("title") or "Sin titulo"
                raw_summary = entry.get("summary") or entry.get("description") or ""
                summary = clean_html(raw_summary)

                article = RawArticle(
                    source_id=source.id,
                    title=title.strip(),
                    url=url.strip(),
                    summary=summary[:500],
                    body=summary[:2000],
                    category_hint=_detect_category(source, entry),
                    extraction_quality="rss",
                    extraction_notes="Ingestion RSS desde feed",
                    published_at=_parse_published(entry),
                )

                db.add(article)
                created += 1

        db.commit()

        logger.info(
            "Ingestion RSS finalizada | sources_processed=%s entries_seen=%s articles_created=%s",
            sources_processed,
            entries_seen,
            created,
        )

        return {
            "status": "ok",
            "sources_processed": sources_processed,
            "entries_seen": entries_seen,
            "articles_created": created,
        }

    except Exception as exc:
        db.rollback()
        logger.exception("Ingestion RSS fallo: %s", exc)

        return {
            "status": "error",
            "error": str(exc),
            "sources_processed": 0,
            "entries_seen": 0,
            "articles_created": 0,
        }


# Alias temporal para no romper rutas antiguas que importan run_mock_ingestion.
run_mock_ingestion = run_rss_ingestion