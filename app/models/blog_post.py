from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, DateTime, Text, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class BlogPost(Base):
    __tablename__ = "blog_posts"
    created_at = Column(DateTime, default=datetime.utcnow)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"), nullable=False)
    editor_draft_id: Mapped[int] = mapped_column(ForeignKey("editor_drafts.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(String(50), default="published", nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    story = relationship("Story")