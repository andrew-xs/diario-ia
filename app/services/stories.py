from datetime import datetime
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.raw_article import RawArticle
from app.models.story import Story

logger = get_logger(__name__)


STOPWORDS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "de", "del", "en", "por", "para", "con", "sin", "sobre",
    "y", "o", "que", "a", "al", "se", "su", "sus", "lo",
    "tras", "ante", "desde", "hasta", "como",
}


def normalize_title(title: str) -> str:
    text = title.lower()

    for ch in [":", ";", ",", ".", "¿", "?", "¡", "!", "\"", "'", "“", "”", "(", ")"]:
        text = text.replace(ch, " ")

    words = [
        word.strip()
        for word in text.split()
        if len(word.strip()) > 2 and word.strip() not in STOPWORDS
    ]

    return " ".join(words)


def similarity(a: str, b: str) -> float:
    a_norm = normalize_title(a)
    b_norm = normalize_title(b)

    if not a_norm or not b_norm:
        return 0.0

    return SequenceMatcher(None, a_norm, b_norm).ratio()


def token_overlap(a: str, b: str) -> float:
    a_tokens = set(normalize_title(a).split())
    b_tokens = set(normalize_title(b).split())

    if not a_tokens or not b_tokens:
        return 0.0

    intersection = a_tokens.intersection(b_tokens)
    union = a_tokens.union(b_tokens)

    return len(intersection) / len(union)


def find_matching_story(db: Session, article: RawArticle) -> Story | None:
    stories_query = db.query(Story)

    if article.category_hint:
        stories_query = stories_query.filter(Story.category == article.category_hint)

    stories = stories_query.all()

    best_story = None
    best_score = 0.0

    for story in stories:
        sequence_score = similarity(article.title, story.title)
        overlap_score = token_overlap(article.title, story.title)

        combined_score = (sequence_score * 0.6) + (overlap_score * 0.4)

        if combined_score > best_score:
            best_score = combined_score
            best_story = story

    if best_story and best_score >= 0.62:
        logger.info(
            "Articulo vinculado a story existente | article='%s' story='%s' score=%.2f",
            article.title,
            best_story.title,
            best_score,
        )
        return best_story

    return None


def assign_articles_to_stories(db: Session) -> dict:
    logger.info("Stories resolver iniciado")

    try:
        existing_stories_before = db.query(Story).count()
        articles = db.query(RawArticle).filter(RawArticle.story_id.is_(None)).all()

        created_stories = 0
        linked_articles = 0
        matched_existing_stories = 0

        for article in articles:
            matched_story = find_matching_story(db, article)

            if matched_story:
                article.story_id = matched_story.id
                matched_story.updated_at = datetime.utcnow()
                matched_existing_stories += 1
                linked_articles += 1
                continue

            new_story = Story(
                title=article.title,
                category=article.category_hint or "general",
                summary=article.summary,
                status="open",
            )

            db.add(new_story)
            db.flush()

            article.story_id = new_story.id
            created_stories += 1
            linked_articles += 1

        db.commit()

        existing_stories_after = db.query(Story).count()

        logger.info(
            "Stories resolver finalizado | processed=%s created=%s linked=%s matched_existing=%s",
            len(articles),
            created_stories,
            linked_articles,
            matched_existing_stories,
        )

        return {
            "status": "ok",
            "unassigned_articles_processed": len(articles),
            "stories_existing_before": existing_stories_before,
            "stories_created": created_stories,
            "articles_linked": linked_articles,
            "articles_matched_to_existing_stories": matched_existing_stories,
            "stories_existing_after": existing_stories_after,
        }

    except Exception as exc:
        db.rollback()
        logger.exception("Stories resolver fallo: %s", exc)

        return {
            "status": "error",
            "error": str(exc),
            "unassigned_articles_processed": 0,
            "stories_existing_before": 0,
            "stories_created": 0,
            "articles_linked": 0,
            "articles_matched_to_existing_stories": 0,
            "stories_existing_after": 0,
        }