<div align="center">

# MAP — Make A Python (under process)

<img src="Docs/logo.png" alt="Logo" width="50%">

</div>

A tutorial on how to write a Python interpreter: a website (English, Spanish and Russian) that walks through the lexer, parser, AST, semantic checks, evaluator, builtins and errors, showing the code of the same interpreter written in Python, Rust, C++, Java, Clojure and LLVM, plus the manim animations used to explain each step.

## Layout

```
src/           the tutorial site (FastAPI + Jinja2)
  map.py       entry point
  core/        app, templates, static files, texts (content/{en,es,ru}.json), code snippets
  scripts/     regenerate snippets and GIFs
animations/    manim scenes and the manim-slides deck
  ll1/  peg/  peg2parsetree/  full_process/{dark,light}/
Docs/          planning notes, logo, site theme palettes
```

## Requirements

Site:

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (dependencies are in `src/pyproject.toml` / `src/uv.lock`: fastapi, jinja2, uvicorn)

Animations (only to re-render videos):

- Python 3.13+ and the packages in `animations/requirements.txt` (manim, manim-slides, PyQt6)
- System libraries for manim: cairo, pango, pkg-config and ffmpeg
  (Debian/Ubuntu: `sudo apt install build-essential pkg-config libcairo2-dev libpango1.0-dev ffmpeg`)
- `python3.14` on the `PATH` for the bytecode slides of `full_process` (they show CPython 3.14 `dis` output)

## Run the site

```
cd src
uv sync
uv run python map.py
```

Open http://127.0.0.1:9602/en/make-a-python/ (also `/es/` and `/ru/`). Pick the interpreter language with `?prog_lang=python|rust|c++|java|clojure|llvm`.

The Run buttons on the page execute the examples and chapter tests with the reference interpreter in `animations/full_process/python_interpreter_in_python/main.py` (in a subprocess, stopped after 3 seconds), so keep that file in place.

## Render the animations

```
python3 -m venv env
. env/bin/activate
pip install -r animations/requirements.txt
```

Single scenes (`-p` opens the video, `-ql` is a fast low-quality draft, `-qh` for the final one):

```
manim -pql animations/ll1/ll1.py LL1Trace
manim -pql animations/peg/peg.py PEGTrace
manim -pql animations/peg/peg.py PEGBacktrack
manim -pql animations/peg2parsetree/peg2parsetree.py PEGParseTree
manim -pql animations/full_process/dark/full_process.py PythonExecutionJourney
```

The full interpreter deck (run from `dark/` or `light/`, one per site theme):

```
cd animations/full_process/dark
manim-slides render -qm full_process_compleate.py InterpreterTutorial   # MAP_CHAPTERS=2,3 renders only those chapters
manim-slides present InterpreterTutorial
```

Videos are written to `media/videos/...`. To use them on the site, copy them to `src/core/static/video/` and regenerate the GIFs (see `src/README.md`).

## License

See [LICENSE](LICENSE).
