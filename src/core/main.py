# main.py
from fastapi import FastAPI, Request, Query, Cookie
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from i18n import t, normalize_language, parse_accept_language, SUPPORTED_LANGUAGES
from code_i18n import (
    get_snippet,
    normalize_code_language,
    SUPPORTED_CODE_LANGUAGES,
    CODE_LANGUAGE_LABELS,
)
from articles import get_article

app = FastAPI()
app.mount("/static", StaticFiles(directory="core/static"), name="static")
templates = Jinja2Templates(directory="core/templates")


@app.get("/{lang}/make-a-python/")
async def index(
    request: Request,
    lang: str | None = Query(default="en"),
    code_lang: Optional[str] = Query(default="py"),
):
    resolved_lang = normalize_language(
        lang or parse_accept_language(request.headers.get("accept-language"))
    )
    resolved_code_lang = normalize_code_language(code_lang)

    response = templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "lang": resolved_lang,
            "code_lang": resolved_code_lang,
        },
    )

    return response
