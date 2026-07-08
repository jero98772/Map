from pathlib import Path


def load_snippets() -> None:
    for lang in SUPPORTED_CODE_LANGUAGES:
        lang_dir = CODESNIPPETS_DIR / lang
        _snippets[lang] = {}
        if not lang_dir.exists():
            continue
        for file in sorted(lang_dir.iterdir()):
            if file.is_file():
                _snippets[lang][file.stem] = file.read_text(encoding="utf-8")


def normalize_code_language(code_lang: str | None) -> str:
    if code_lang and code_lang.lower() in SUPPORTED_CODE_LANGUAGES:
        return code_lang.lower()
    return DEFAULT_CODE_LANGUAGE


def get_snippet(code_lang: str, snippet_id: str) -> str:
    code_lang = normalize_code_language(code_lang)
    table = _snippets.get(code_lang, {})
    return table.get(snippet_id, f"# '{snippet_id}' not translated to {code_lang} yet")


load_snippets()
