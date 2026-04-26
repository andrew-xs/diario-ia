from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SourceSchema(BaseModel):
    id: int
    name: str
    base_url: str
    category_hint: str | None = None
    active: bool

    model_config = ConfigDict(from_attributes=True)


class RawArticleSchema(BaseModel):
    id: int
    source_id: int
    story_id: int | None = None
    title: str
    url: str
    summary: str | None = None
    body: str | None = None
    category_hint: str | None = None
    extraction_quality: str
    extraction_notes: str | None = None
    published_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StorySchema(BaseModel):
    id: int
    title: str
    category: str | None = None
    summary: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReporterReportSchema(BaseModel):
    id: int
    story_id: int
    title: str
    category: str | None = None
    summary: str | None = None
    source_count: int
    report_body: str | None = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EditorDraftSchema(BaseModel):
    id: int
    story_id: int
    reporter_report_id: int
    title: str
    slug: str
    content: str
    action: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ControlAlertSchema(BaseModel):
    id: int
    story_id: int
    reporter_report_id: int
    editor_draft_id: int
    severity: str
    field_name: str
    message: str
    suggested_fix: str | None = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BlogPostSchema(BaseModel):
    id: int
    story_id: int
    editor_draft_id: int
    title: str
    slug: str
    content: str
    status: str
    published_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SocialPostSchema(BaseModel):
    id: int
    blog_post_id: int
    platform: str
    post_copy: str
    status: str
    published_at: datetime

    model_config = ConfigDict(from_attributes=True)