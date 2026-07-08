from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from core.tools.constans import (
    SUPPORTED_LANGUAGES,
    SUPPORTED_PROGRAMING_LANGUAGES,
    DEFAULT_PROGRAMING_LANGUAGE,
    DEFAULT_LANGUAGE,
    LANGUAGES_FOLDER,
    PROGRAMING_LANGUAGES_FOLDER,
)
from core.tools.tools import read_json_content, read_code_snippet

app = FastAPI()
app.mount("/static", StaticFiles(directory="core/static"), name="static")
templates = Jinja2Templates(directory="core/templates")


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(
        url=f"/{DEFAULT_LANGUAGE}/make-a-python/?prog_lang={DEFAULT_PROGRAMING_LANGUAGE}"
    )


@app.get("/{lang}/make-a-python/", response_class=HTMLResponse)
async def index(
    request: Request,
    lang: str,
    prog_lang: str = Query(default=DEFAULT_PROGRAMING_LANGUAGE),
):
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    if prog_lang not in SUPPORTED_PROGRAMING_LANGUAGES:
        prog_lang = DEFAULT_PROGRAMING_LANGUAGE

    content = read_json_content(lang, LANGUAGES_FOLDER)
    snippet = read_code_snippet(prog_lang, "1", PROGRAMING_LANGUAGES_FOLDER)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "lang": lang,
            "prog_lang": prog_lang,
            "content": content,
            "snippet": snippet,
            "languages": SUPPORTED_LANGUAGES,
            "code_languages": SUPPORTED_PROGRAMING_LANGUAGES,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={
                "request": request,
                "path": request.url.path,
            },
            status_code=404,
        )

    return HTMLResponse(
        content=f"<h1>{exc.status_code}</h1><p>{exc.detail}</p>",
        status_code=exc.status_code,
    )
