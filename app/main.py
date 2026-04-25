from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.routes.health import router as health_router
from app.routes.sources import router as sources_router
from app.routes.pipeline import router as pipeline_router
from app.routes.articles import router as articles_router
from app.routes.debug import router as debug_router
from app.routes.stories import router as stories_router
from app.routes.reporter import router as reporter_router
from app.routes.editor import router as editor_router
from app.routes.control import router as control_router
from app.routes.publisher import router as publisher_router
from app.routes.orchestrator import router as orchestrator_router
from app.routes.community import router as community_router
from app.routes.ui import router as ui_router
from app.db.session import Base, engine
from app.models import (
    Source,
    Story,
    RawArticle,
    ReporterReport,
    EditorDraft,
    ControlAlert,
    BlogPost,
    SocialPost,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Diario IA")

_HERE = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(_HERE / "static")), name="static")

app.include_router(health_router)
app.include_router(sources_router)
app.include_router(pipeline_router)
app.include_router(articles_router)
app.include_router(debug_router)
app.include_router(stories_router)
app.include_router(reporter_router)
app.include_router(editor_router)
app.include_router(control_router)
app.include_router(publisher_router)
app.include_router(orchestrator_router)
app.include_router(community_router)
app.include_router(ui_router)


@app.get("/")
def root():
    return {"ok": True, "app": "Diario IA"}
