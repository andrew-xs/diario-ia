from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class SocialPost(Base):
    __tablename__ = "social_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    blog_post_id: Mapped[int] = mapped_column(ForeignKey("blog_posts.id"), nullable=False)

    platform: Mapped[str] = mapped_column(String(50), nullable=False)  # facebook | instagram
    post_copy: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="published", nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    blog_post = relationship("BlogPost")