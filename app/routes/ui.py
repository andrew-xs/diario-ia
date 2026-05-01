from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/ui", tags=["ui"])

_HERE = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(_HERE.parent / "templates"))


@router.get("", response_class=HTMLResponse)
def ui(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Diario IA",
        },
    )