from datetime import datetime
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from app.models.raw_article import RawArticle
from app.models.story import Story


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_matching_story(db: Session, article: RawArticle) -> Story | None:
    if not article.category_hint:
        return None

    stories = db.query(Story).filter(Story.category == article.category_hint).all()

    best_match = None
    best_score = 0.0

    for story in stories:
        score = similarity(article.title, story.title)
        if score > best_score:
            best_score = score
            best_match = story

    if best_match and best_score >= 0.80:
        return best_match

    return None


def assign_articles_to_stories(db: Session) -> dict:
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
            category=article.category_hint,
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

    return {
        "status": "ok",
        "unassigned_articles_processed": len(articles),
        "stories_existing_before": existing_stories_before,
        "stories_created": created_stories,
        "articles_linked": linked_articles,
        "articles_matched_to_existing_stories": matched_existing_stories,
        "stories_existing_after": existing_stories_after,
    }