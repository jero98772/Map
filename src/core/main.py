from pathlib import Path

from fastapi import FastAPI, Request, Query
from fastapi import HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from core.tools.constans import (
    SUPPORTED_LANGUAGES,
    SUPPORTED_PROGRAMING_LANGUAGES,
    PROGRAMING_LANGUAGE_NAMES,
    HIGHLIGHT_CLASSES,
    DEFAULT_PROGRAMING_LANGUAGE,
    DEFAULT_LANGUAGE,
    LANGUAGES_FOLDER,
    PROGRAMING_LANGUAGES_FOLDER,
    SHARED_FOLDER,
    TESTS_FOLDER,
    STATIC_FOLDER,
    THEMES,
)
from core.tools.tools import read_json_content, snippet_for, read_shared, read_tests, themed_media
from core.tools.runner import run_map

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_FOLDER), name="static")
templates = Jinja2Templates(directory="core/templates")


def resolve_block(block: dict, prog_lang: str) -> dict:
    """Attach the code a content block refers to, in the chosen interpreter."""
    block = dict(block)
    kind = block["t"]
    if kind == "code":
        block["snippet"] = snippet_for(
            block["id"], prog_lang, PROGRAMING_LANGUAGES_FOLDER, DEFAULT_PROGRAMING_LANGUAGE
        )
        block["hl"] = HIGHLIGHT_CLASSES[block["snippet"]["lang"]]
    elif kind == "shared":
        block["snippet"] = read_shared(block["id"], SHARED_FOLDER)
    elif kind == "shared_html":
        block["html"] = (Path(SHARED_FOLDER) / f"{block['id']}.html").read_text(encoding="utf-8")
    elif kind == "anim":
        block["media"] = themed_media(block["file"], STATIC_FOLDER, THEMES)
    elif kind == "cols":
        block["blocks"] = [resolve_block(b, prog_lang) for b in block["blocks"]]
    elif kind == "errgrid":
        block["items"] = [
            {**item, "snippet": read_shared(item["id"], SHARED_FOLDER)} for item in block["items"]
        ]
    return block


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
    chapters = [
        {
            **ch,
            "blocks": [resolve_block(b, prog_lang) for b in ch["blocks"]],
            "videos": [
                {**v, "media": themed_media(v["file"], STATIC_FOLDER, THEMES)}
                for v in ch.get("videos", [])
            ],
        }
        for ch in content["chapters"]
    ]
    tests = {ch["id"]: read_tests(ch["id"], TESTS_FOLDER) for ch in chapters}

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "lang": lang,
            "prog_lang": prog_lang,
            "prog_name": PROGRAMING_LANGUAGE_NAMES[prog_lang],
            "prog_names": PROGRAMING_LANGUAGE_NAMES,
            "content": content,
            "chapters": chapters,
            "tests": tests,
            "languages": SUPPORTED_LANGUAGES,
            "code_languages": SUPPORTED_PROGRAMING_LANGUAGES,
        },
    )


@app.post("/run/example/{snippet}")
def run_example(snippet: str):
    meta = read_json_content("index", SHARED_FOLDER).get(snippet, {})
    if not meta.get("runnable"):
        raise HTTPException(status_code=404)
    return {"output": run_map(read_shared(snippet, SHARED_FOLDER)["code"])}


@app.post("/run/tests/{chapter}")
def run_tests(chapter: str):
    cases = read_tests(chapter, TESTS_FOLDER)
    if cases is None:
        raise HTTPException(status_code=404)
    results = []
    for case in cases:
        output = run_map(case["source"])
        results.append({"name": case["name"], "expected": case["expected"],
                        "output": output, "passed": output == case["expected"]})
    return results


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        lang = request.url.path.strip("/").split("/")[0]
        if lang not in SUPPORTED_LANGUAGES:
            lang = DEFAULT_LANGUAGE
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={
                "request": request,
                "path": request.url.path,
                "lang": lang,
                "content": read_json_content(lang, LANGUAGES_FOLDER),
            },
            status_code=404,
        )

    return HTMLResponse(
        content=f"<h1>{exc.status_code}</h1><p>{exc.detail}</p>",
        status_code=exc.status_code,
    )
