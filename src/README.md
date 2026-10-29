# Make a Python — tutorial site

The MAP tutorial as a FastAPI app, in English, Spanish and Russian, with the code of any of the six interpreters.

```
cd src
uv sync
uv run python map.py          # http://127.0.0.1:9602  →  /{en,es,ru}/make-a-python/?prog_lang=python|rust|c++|java|clojure|llvm
```

- `core/content/{en,es,ru}.json`: all text, chapter by chapter. Code blocks only name a snippet id.
- `core/codesnippets/<prog_lang>/<id>.*` and `core/shared/*` are generated from the interpreters and from `../index.html`. After changing an interpreter, run `python3 scripts/extract_snippets.py` again.
- `core/static/video/{dark,light}/`: the chapter animations in each site theme, cut from the manim-slides deck `animations/full_process/{dark,light}/full_process_compleate.py`. The page shows the one matching the selected theme. `core/static/video/ll1.mp4` (from `animations/ll1/ll1.py`, `LL1Trace`) has one version only and is used for both themes. To re-render and export one theme:

  ```
  cd animations/full_process
  manim-slides render -qm dark/full_process_compleate.py InterpreterTutorial
  cd ../../src && python3 scripts/export_slides.py ../animations/full_process/slides/InterpreterTutorial.json dark
  ```

  Repeat with `light`. Both themes write to the same `slides/` folder, so export each one before rendering the other.
- `core/static/gif/` (and `gif/{dark,light}/`): the GIFs shown on the page. Regenerate them from the videos with `sh scripts/videos_to_gif.sh` (`FPS=` and `WIDTH=` override the 12 fps / 720 px defaults).
- `../Docs/theme-dark.md`, `../Docs/theme-light.md`: color palette and personality of the two site themes (from `core/static/css/base.css`).
