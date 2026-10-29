from pathlib import Path
from functools import lru_cache
import json


def read_folders(path: str | Path) -> list[str]:
    path = Path(path)
    return [item.name for item in path.iterdir() if item.is_dir()]


def read_json_files(path: str | Path) -> list[str]:
    path = Path(path)
    return [
        str(file.stem).replace(".json", "")
        for file in path.glob("*.json")
        if file.is_file()
    ]


@lru_cache(maxsize=None)
def read_json_content(language: str, folder: str) -> dict:
    path = Path(folder) / f"{language}.json"
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def read_code_snippet(language: str, snippet: str, folder: str) -> str:
    path = Path(folder) / language
    file = next(path.glob(f"{snippet}.*"))
    return file.read_text(encoding="utf-8")


@lru_cache(maxsize=None)
def snippet_for(snippet: str, language: str, folder: str, fallback: str) -> dict:
    """Code of one concept in the chosen interpreter, or in `fallback` when it has none."""
    refs = read_json_content("index", folder)[snippet]
    shown = language if language in refs else fallback
    return {
        "code": read_code_snippet(shown, snippet, folder),
        "ref": refs[shown],
        "lang": shown,
        "fell_back": shown != language,
    }


@lru_cache(maxsize=None)
def read_shared(snippet: str, folder: str) -> dict:
    """A language-neutral block (example program, AST print, dis output, test)."""
    meta = read_json_content("index", folder).get(snippet, {})
    path = next(Path(folder).glob(f"{snippet}.*"))
    return {**meta, "code": path.read_text(encoding="utf-8")}


@lru_cache(maxsize=None)
def read_tests(chapter: str, folder: str) -> list | None:
    """Black-box cases of one chapter: MAP source and the output it must print."""
    path = Path(folder) / f"{chapter}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def themed_media(file: str, folder: str, themes: list[str]) -> dict:
    """GIF and video of one animation for each site theme, relative to the static folder.

    A theme without its own render falls back to the shared file."""
    media = {}
    for theme in themes:
        prefix = f"{theme}/" if (Path(folder) / "video" / theme / f"{file}.mp4").is_file() else ""
        media[theme] = {"gif": f"gif/{prefix}{file}.gif", "mp4": f"video/{prefix}{file}.mp4"}
    return media
