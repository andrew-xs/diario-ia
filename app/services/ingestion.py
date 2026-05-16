from datetime import datetime, timedelta

import re
from html import unescape

import feedparser
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.source import Source
from app.models.raw_article import RawArticle
from app.services.stories import similarity, token_overlap

logger = get_logger(__name__)

RECENT_DUPLICATE_DAYS = 7
SEMANTIC_DUPLICATE_THRESHOLD = 0.78

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


def _is_more_complete(new_text: str | None, existing_text: str | None) -> bool:
    return bool(new_text) and len(new_text.strip()) > len((existing_text or "").strip())


def _update_article_seen(article: RawArticle, seen_at: datetime) -> None:
    article.last_seen_at = seen_at


def _update_article_content_if_better(
    article: RawArticle,
    summary: str | None,
    body: str | None,
    updated_at: datetime,
) -> bool:
    changed = False

    if _is_more_complete(summary, article.summary):
        article.summary = summary
        changed = True

    if _is_more_complete(body, article.body):
        article.body = body
        changed = True

    if changed:
        article.updated_at = updated_at

    return changed


def _find_recent_semantic_duplicate(
    db: Session,
    title: str,
    seen_at: datetime,
) -> RawArticle | None:
    cutoff = seen_at - timedelta(days=RECENT_DUPLICATE_DAYS)

    recent_articles = (
        db.query(RawArticle)
        .filter(
            or_(
                RawArticle.published_at >= cutoff,
                RawArticle.created_at >= cutoff,
                RawArticle.last_seen_at >= cutoff,
            )
        )
        .all()
    )

    best_article = None
    best_score = 0.0

    for article in recent_articles:
        sequence_score = similarity(title, article.title)
        overlap_score = token_overlap(title, article.title)
        combined_score = (sequence_score * 0.55) + (overlap_score * 0.45)

        if combined_score > best_score:
            best_score = combined_score
            best_article = article

    if best_article and best_score >= SEMANTIC_DUPLICATE_THRESHOLD:
        logger.info(
            "Semantic duplicate detected | incoming='%s' existing='%s' score=%.2f",
            title,
            best_article.title,
            best_score,
        )
        return best_article

    return None


def run_rss_ingestion(db: Session) -> dict:
    logger.info("Ingestion RSS iniciada")

    try:
        sources = db.query(Source).filter(Source.active == True).all()
        created = 0
        sources_processed = 0
        entries_seen = 0
        url_duplicates = 0
        semantic_duplicates = 0
        articles_updated = 0

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

                seen_at = datetime.utcnow()
                title = entry.get("title") or "Sin titulo"
                raw_summary = entry.get("summary") or entry.get("description") or ""
                summary = clean_html(raw_summary)
                body = summary[:2000]

                exists = db.query(RawArticle).filter(RawArticle.url == url).first()
                if exists:
                    _update_article_seen(exists, seen_at)
                    if _update_article_content_if_better(
                        article=exists,
                        summary=summary[:500],
                        body=body,
                        updated_at=seen_at,
                    ):
                        articles_updated += 1
                    url_duplicates += 1
                    continue

                duplicate = _find_recent_semantic_duplicate(db, title, seen_at)
                if duplicate:
                    _update_article_seen(duplicate, seen_at)
                    semantic_duplicates += 1
                    continue

                article = RawArticle(
                    source_id=source.id,
                    title=title.strip(),
                    url=url.strip(),
                    summary=summary[:500],
                    body=body,
                    category_hint=_detect_category(source, entry),
                    extraction_quality="rss",
                    extraction_notes="Ingestion RSS desde feed",
                    published_at=_parse_published(entry),
                    last_seen_at=seen_at,
                    updated_at=seen_at,
                )

                db.add(article)
                created += 1

        db.commit()

        logger.info(
            "Ingestion RSS finalizada | sources_processed=%s entries_seen=%s articles_created=%s url_duplicates=%s semantic_duplicates=%s articles_updated=%s",
            sources_processed,
            entries_seen,
            created,
            url_duplicates,
            semantic_duplicates,
            articles_updated,
        )

        return {
            "status": "ok",
            "sources_processed": sources_processed,
            "entries_seen": entries_seen,
            "articles_created": created,
            "url_duplicates": url_duplicates,
            "semantic_duplicates": semantic_duplicates,
            "articles_updated": articles_updated,
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
            "url_duplicates": 0,
            "semantic_duplicates": 0,
            "articles_updated": 0,
        }


# Alias temporal para no romper rutas antiguas que importan run_mock_ingestion.
run_mock_ingestion = run_rss_ingestion
