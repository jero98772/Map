"""
Copy the chapter animations out of a manim-slides render, for one site theme.

    cd src && python3 scripts/export_slides.py ../animations/full_process/slides/InterpreterTutorial.json dark

Every slide carries the notes "<chapter>|<title>". Each video listed in
core/content/en.json (chapters[].videos[] = {file, caption}) is the slide of
that chapter whose title is its caption; it is copied to
core/static/video/<theme>/<file>.mp4. Run scripts/videos_to_gif.sh afterwards.
"""

import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
CONTENT = os.path.join(SRC, "core", "content", "en.json")
VIDEO = os.path.join(SRC, "core", "static", "video")
THEMES = ("dark", "light")


def main():
    if len(sys.argv) != 3 or sys.argv[2] not in THEMES:
        sys.exit(f"usage: {sys.argv[0]} <slides json> <{'|'.join(THEMES)}>")
    deck, theme = sys.argv[1], sys.argv[2]
    # slide "file" paths are relative to the folder that holds slides/
    base = os.path.dirname(os.path.dirname(os.path.abspath(deck)))
    with open(deck, encoding="utf-8") as fh:
        slides = {
            tuple(s["notes"].split("|", 1)): os.path.join(base, s["file"])
            for s in json.load(fh)["slides"]
        }
    with open(CONTENT, encoding="utf-8") as fh:
        chapters = json.load(fh)["chapters"]

    out = os.path.join(VIDEO, theme)
    os.makedirs(out, exist_ok=True)
    missing = []
    for ch in chapters:
        for v in ch.get("videos", []):
            slide = slides.get((ch["id"], v["caption"]))
            if slide is None:
                missing.append(f"{ch['id']}|{v['caption']}")
                continue
            target = os.path.join(out, v["file"] + ".mp4")
            shutil.copyfile(slide, target)
            print(os.path.relpath(target, SRC))
    if missing:
        sys.exit("no slide for: " + ", ".join(missing))


if __name__ == "__main__":
    main()
