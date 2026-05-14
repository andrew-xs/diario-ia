from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

from app.db.session import Base


class EditorDraft(Base):
    __tablename__ = "editor_drafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"), nullable=False)
    reporter_report_id: Mapped[int] = mapped_column(ForeignKey("reporter_reports.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    action: Mapped[str] = mapped_column(String(50), nullable=False)  # create | update
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    story = relationship("Story")

    editorial_score = Column(Integer, nullable=True)

    editorial_priority = Column(String, nullable=True)