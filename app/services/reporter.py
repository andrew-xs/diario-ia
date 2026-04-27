from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.story import Story
from app.models.raw_article import RawArticle
from app.models.reporter_report import ReporterReport
from app.models.source import Source

logger = get_logger(__name__)


def build_report_body(story: Story, articles: list[RawArticle], source_names: list[str]) -> str:
    source_list = ", ".join(source_names)

    return f"""
Titulo: {story.title}

Resumen:
{story.summary}

Fuentes consolidadas: {source_list}

Cantidad de fuentes: {len(source_names)}
"""


def generate_reports(db: Session) -> dict:
    logger.info("Reporter iniciado")

    try:
        stories = db.query(Story).all()
        created_reports = 0

        for story in stories:
            exists = db.query(ReporterReport).filter(ReporterReport.story_id == story.id).first()
            if exists:
                continue

            articles = db.query(RawArticle).filter(RawArticle.story_id == story.id).all()

            source_names = []
            for article in articles:
                source = db.query(Source).filter(Source.id == article.source_id).first()
                if source:
                    source_names.append(source.name)

            source_names = list(dict.fromkeys(source_names))

            report = ReporterReport(
                story_id=story.id,
                title=story.title,
                category=story.category,
                summary=story.summary,
                source_count=len(source_names),
                report_body=build_report_body(story, articles, source_names),
                status="generated",
            )

            db.add(report)
            created_reports += 1

        db.commit()

        logger.info(
            "Reporter finalizado | stories_processed=%s reports_created=%s",
            len(stories),
            created_reports,
        )

        return {
            "status": "ok",
            "stories_processed": len(stories),
            "reports_created": created_reports,
        }

    except Exception as exc:
        db.rollback()
        logger.exception("Reporter fallo: %s", exc)

        return {
            "status": "error",
            "error": str(exc),
            "stories_processed": 0,
            "reports_created": 0,
        }