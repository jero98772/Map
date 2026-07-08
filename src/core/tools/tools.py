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
