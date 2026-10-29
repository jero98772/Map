"""Render the site to static HTML for GitHub Pages.

Usage (from src/):  uv run python freeze.py [out_dir] [base_path]
Defaults: out_dir=site, base_path=/Map  (served at https://<user>.github.io/Map/)

Every language x interpreter page becomes <base>/<lang>/<interpreter>/index.html;
the ?prog_lang= links of the selectors are rewritten to those paths.
"""
import asyncio
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import unquote

from starlette.requests import Request

import core.main as site
from core.tools.constans import (
    SUPPORTED_LANGUAGES,
    SUPPORTED_PROGRAMING_LANGUAGES,
    DEFAULT_LANGUAGE,
    DEFAULT_PROGRAMING_LANGUAGE,
    LANGUAGES_FOLDER,
    STATIC_FOLDER,
)
from core.tools.tools import read_json_content

HOST = "http://freeze"
# "c++" is not a comfortable directory name in a URL
SLUGS = {"c++": "cpp"}


def slug(prog_lang: str) -> str:
    return SLUGS.get(prog_lang, prog_lang)


def request(path: str) -> Request:
    return Request({"type": "http", "scheme": "http", "server": ("freeze", 80), "method": "GET",
                    "path": path, "headers": [], "query_string": b"", "root_path": "", "app": site.app})


def rewrite(html: str, base: str) -> str:
    html = html.replace(f"{HOST}/static/", f"{base}/static/")

    def page(m):
        prog = unquote(m.group(2)) if m.group(2) else DEFAULT_PROGRAMING_LANGUAGE
        return f"{base}/{m.group(1)}/{slug(prog)}/"

    return re.sub(r"/([a-z]{2})/make-a-python/(?:\?prog_lang=([^\"'&]+))?", page, html)


def redirect(target: str) -> str:
    return (f'<!DOCTYPE html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={target}">'
            f'<link rel="canonical" href="{target}"><a href="{target}">{target}</a>\n')


async def freeze(out: Path, base: str):
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(STATIC_FOLDER, out / "static")

    for lang in SUPPORTED_LANGUAGES:
        for prog in SUPPORTED_PROGRAMING_LANGUAGES:
            response = await site.index(request(f"/{lang}/make-a-python/"), lang, prog)
            page = out / lang / slug(prog) / "index.html"
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text(rewrite(response.body.decode(), base), encoding="utf-8")
        (out / lang / "index.html").write_text(
            redirect(f"{base}/{lang}/{slug(DEFAULT_PROGRAMING_LANGUAGE)}/"), encoding="utf-8")

    (out / "index.html").write_text(
        redirect(f"{base}/{DEFAULT_LANGUAGE}/{slug(DEFAULT_PROGRAMING_LANGUAGE)}/"), encoding="utf-8")

    not_found = site.templates.get_template("404.html").render(
        request=request("/404"), path="", lang=DEFAULT_LANGUAGE,
        content=read_json_content(DEFAULT_LANGUAGE, LANGUAGES_FOLDER))
    (out / "404.html").write_text(rewrite(not_found, base), encoding="utf-8")
    # GitHub Pages must not run Jekyll over the output
    (out / ".nojekyll").write_text("")


if __name__ == "__main__":
    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
    base_path = (sys.argv[2] if len(sys.argv) > 2 else "/Map").rstrip("/")
    asyncio.run(freeze(out_dir, base_path))
    print(f"wrote {out_dir}/ for base path '{base_path or '/'}'")
