from pathlib import Path

from core.tools.tools import read_folders, read_json_files

PROGRAMING_LANGUAGES_FOLDER = "core/codesnippets/"
LANGUAGES_FOLDER = "core/content/"
SHARED_FOLDER = "core/shared/"
# Display order of the interpreters; only those with a snippet folder are offered.
PROGRAMING_LANGUAGES_ORDER = ["python", "rust", "c++", "java", "clojure", "llvm"]
SUPPORTED_PROGRAMING_LANGUAGES = [
    p for p in PROGRAMING_LANGUAGES_ORDER if p in read_folders(PROGRAMING_LANGUAGES_FOLDER)
]
PROGRAMING_LANGUAGE_NAMES = {
    "python": "Python",
    "rust": "Rust",
    "c++": "C++",
    "java": "Java",
    "clojure": "Clojure",
    "llvm": "LLVM",
}
# highlight.js language for each interpreter (the llvm port is written in Python)
HIGHLIGHT_CLASSES = {
    "python": "python",
    "rust": "rust",
    "c++": "cpp",
    "java": "java",
    "clojure": "clojure",
    "llvm": "python",
}
LANGUAGES_ORDER = ["en", "es", "ru"]
SUPPORTED_LANGUAGES = sorted(
    read_json_files(LANGUAGES_FOLDER),
    key=lambda l: LANGUAGES_ORDER.index(l) if l in LANGUAGES_ORDER else len(LANGUAGES_ORDER),
)
DEFAULT_PROGRAMING_LANGUAGE = "python"
DEFAULT_LANGUAGE = "en"
TESTS_FOLDER = "core/tests/"
# Reference interpreter the Run buttons execute
MAP_INTERPRETER = (
    Path(__file__).resolve().parents[3]
    / "animations/full_process/python_interpreter_in_python/main.py"
)
RUN_TIMEOUT = 3
STATIC_FOLDER = "core/static/"
# Site themes; each animation may have a render per theme in video/<theme>/
THEMES = ["dark", "light"]
