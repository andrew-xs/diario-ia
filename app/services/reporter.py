from sqlalchemy.orm import Session

from app.models.story import Story
from app.models.raw_article import RawArticle
from app.models.reporter_report import ReporterReport
from app.models.source import Source


def build_report_body(story: Story, articles: list[RawArticle], source_names: list[str]) -> str:
    source_list = ", ".join(source_names)

    lines = [
        f"Historia: {story.title}",
        f"Categoría: {story.category}",
        f"Cantidad de fuentes relacionadas: {len(source_names)}",
        f"Fuentes: {source_list}",
        "",
        "Resumen informativo:",
        story.summary or "Sin resumen disponible.",
        "",
        "Artículos asociados:",
    ]

    for article in articles:
        lines.append(f"- {article.title} | {article.url}")

    return "\n".join(lines)


def generate_reports(db: Session) -> dict:
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

    return {
        "status": "ok",
        "stories_processed": len(stories),
        "reports_created": created_reports,
    }