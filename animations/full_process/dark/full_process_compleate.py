"""
MAP — Make A Python : the interpreter tutorial as a manim-slides deck.

Every number, token, tree, frame and error message on screen comes from the
real interpreter in python_interpreter_in_python/main.py (via capture.py).

Render (run from this folder, the HTML expects ./slides/):
    cd tutorial
    manim-slides render -qm slides.py InterpreterTutorial      # -ql for a fast draft

Present:
    manim-slides present InterpreterTutorial

One slide = one video file in slides/files/InterpreterTutorial/.
Each slide carries notes "chNN|title"; build_html.py uses them to put
each video in the right chapter of index.html.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manim import *  # noqa: E402,F403
from manim_slides import Slide  # noqa: E402

import capture as C  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
import manim_slides.slide.base as _msb  # noqa: E402

# manim-slides concatenates each slide's clips with pyav, which fails with
# "Invalid argument" on some clip sets. Fall back to the ffmpeg CLI then.
_pyav_concat = _msb.concatenate_video_files


def _concat_with_fallback(files, dest):
    try:
        _pyav_concat(files, dest)
    except Exception:
        if os.path.exists(dest):
            os.unlink(dest)
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.writelines(f"file '{os.path.abspath(p)}'\n" for p in files)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
                        "-i", f.name, "-c:v", "libx264", "-pix_fmt", "yuv420p", str(dest)], check=True)
        os.unlink(f.name)


_msb.concatenate_video_files = _concat_with_fallback

# ---------- palette: Docs/theme-dark.md — "Night-shift terminal" ----------
KEYWORD = "#f5c02f"  # def / return (--hl-keyword)
NAME = "#7fd1ff"  # identifiers (--hl-name)
NUMBER = "#8be0a4"  # numeric literals (--hl-string)
OP = "#6fa8ff"  # operators (--hl-type)
TEXT = "#e6edf5"  # body text
MUTED = "#9fb0c8"  # captions, sub-labels, paths
PUNCT = MUTED  # punctuation
COMMENT = "#6c7fa3"  # line numbers, tree edges (--hl-comment)
ACCENT = "#7fd1ff"  # structural / headers (--accent)
HILITE = "#f5c02f"  # cursor, current step
ON_FILL = "#071633"  # text on solid fills
BG_CARD = "#0e1a33"
CODE_BG = "#071633"
BORDER = "#1b2c52"
ERR = "#ff7b7b"
OK = "#8be0a4"
LOGO_BLUE = "#2f6fd6"
LOGO_YELLOW = "#f5c02f"
NAVY_700 = "#16357a"
MONO = "Monospace"

config.background_color = "#0b1220"


# ---------- helpers reused from Map/animations ----------


def chip(label, color, sub=None, w=None, h=0.62, fs=26):
    """A small rounded rectangle token chip (from full_process.py)."""
    txt = Text(label, font=MONO, font_size=fs, color=TEXT, weight=BOLD)
    width = w if w else max(txt.width + 0.3, 0.45)
    box = RoundedRectangle(
        corner_radius=0.08, width=width, height=h,
        fill_color=color, fill_opacity=0.22, stroke_color=color, stroke_width=2,
    )
    txt.move_to(box.get_center())
    grp = VGroup(box, txt)
    if sub:
        sub_txt = Text(sub, font=MONO, font_size=12, color=color)
        sub_txt.next_to(box, DOWN, buff=0.06)
        grp.add(sub_txt)
    return grp


def card(text, color=ACCENT, w=4.6, h=0.65, fs=24):
    """Dark box with coloured border (from full_process.py)."""
    box = RoundedRectangle(
        corner_radius=0.08, width=w, height=h,
        fill_color=BG_CARD, fill_opacity=1, stroke_color=color, stroke_width=2.5,
    )
    txt = Text(text, font=MONO, font_size=fs, color=color, weight=BOLD)
    if txt.width > w - 0.2:
        txt.scale_to_fit_width(w - 0.2)
    txt.move_to(box)
    return VGroup(box, txt)


def make_cursor():
    """Yellow downward triangle (from peg/peg.py)."""
    tri = Triangle(color=HILITE, fill_color=HILITE, fill_opacity=1).scale(0.13)
    tri.rotate(PI)
    return tri


def mono(s, fs=18, color=TEXT, **kw):
    return Text(s, font=MONO, font_size=fs, color=color, **kw)


def caption(s, fs=22, color=MUTED):
    t = Text(s, font_size=fs, color=color)
    if t.width > 13:
        t.scale_to_fit_width(13)
    return t.to_edge(DOWN, buff=0.3)


def code_card(src, fs=16, title=None, color=ACCENT, ref=None):
    """A block of real code on a dark card, optional title and file:line ref."""
    body = VGroup(*[mono(l if l.strip() else ".", fs=fs,
                         color=TEXT if l.strip() else BG_CARD)
                    for l in src.rstrip("\n").split("\n")])
    # keep indentation: shift each line by its leading spaces
    cw = mono("M" * 10, fs=fs).width / 10
    lines = src.rstrip("\n").split("\n")
    for i, (t, l) in enumerate(zip(body, lines)):
        indent = len(l) - len(l.lstrip())
        t.move_to(ORIGIN, aligned_edge=LEFT).shift(RIGHT * indent * cw + DOWN * i * fs / 20 * 0.42)
    box = SurroundingRectangle(body, buff=0.2, corner_radius=0.08, color=color,
                               fill_color=BG_CARD, fill_opacity=1, stroke_width=2)
    g = VGroup(box, body)
    if title:
        tt = Text(title, font_size=16, color=color, weight=BOLD).next_to(box, UP, buff=0.08, aligned_edge=LEFT)
        g.add(tt)
    if ref:
        rr = mono(ref, fs=12, color=MUTED).next_to(box, DOWN, buff=0.06, aligned_edge=RIGHT)
        g.add(rr)
    return g


class Listing(VGroup):
    """
    Source code, one Text per line, indentation preserved.
    pos(line, col) gives the screen point of a 1-based (line, col), even after
    the listing is moved or scaled (two anchor points track the grid).
    """

    def __init__(self, src, fs=20, color=TEXT, numbers=False):
        super().__init__()
        self.src_lines = src.rstrip("\n").split("\n")
        cw = mono("M" * 10, fs=fs).width / 10
        lh = fs / 20 * 0.46
        self.rows = VGroup()
        for i, line in enumerate(self.src_lines):
            s = line.strip()
            if s:
                t = mono(s, fs=fs, color=color)
                indent = len(line) - len(line.lstrip())
                t.move_to(RIGHT * (indent * cw + t.width / 2) + DOWN * i * lh)
            else:
                t = VectorizedPoint(DOWN * i * lh)
            self.rows.add(t)
        self.add(self.rows)
        if numbers:
            self.nums = VGroup(*[
                mono(str(i + 1), fs=fs - 4, color=COMMENT).move_to(LEFT * 0.45 + DOWN * i * lh)
                for i in range(len(self.src_lines))])
            self.add(self.nums)
        self.a0 = VectorizedPoint(ORIGIN)
        self.a1 = VectorizedPoint(RIGHT * cw + DOWN * lh)
        self.add(self.a0, self.a1)

    def _unit(self):
        d = self.a1.get_center() - self.a0.get_center()
        return d[0], -d[1]

    def pos(self, line, col):
        """Left edge of character (line, col), vertically centred on the line."""
        cw, lh = self._unit()
        return self.a0.get_center() + RIGHT * (col - 1) * cw + DOWN * (line - 1) * lh

    def span(self, line, col, length, color=HILITE, pad=0.04):
        cw, lh = self._unit()
        w = max(length, 0.35) * cw
        r = Rectangle(width=w + 2 * pad, height=lh * 0.95, color=color, stroke_width=2.5)
        r.move_to(self.pos(line, col) + RIGHT * w / 2)
        return r

    def line_box(self, line, color=HILITE, width_chars=None):
        cw, lh = self._unit()
        n = width_chars or max(len(l) for l in self.src_lines)
        r = Rectangle(width=n * cw + 0.2, height=lh, color=color, stroke_width=0,
                      fill_color=color, fill_opacity=0.18)
        r.move_to(self.pos(line, 1) + RIGHT * (n * cw / 2))
        return r


# ---------- token colouring ----------

KEYWORDS = {"DEF", "IF", "ELSE", "ELIF", "RETURN", "FOR", "IN", "WHILE",
            "TRUE", "FALSE", "NONE", "AND", "OR", "NOT"}
LAYOUT = {"NEWLINE", "INDENT", "DEDENT", "EOF"}
PUNCTS = {"LPAREN", "RPAREN", "COLON", "COMMA", "LBRACKET", "RBRACKET", "DOT"}


def tok_color(kind):
    if kind in KEYWORDS:
        return KEYWORD
    if kind == "NAME":
        return NAME
    if kind in ("INTEGER", "FLOAT", "STRING"):
        return NUMBER
    if kind in LAYOUT:
        return ACCENT
    if kind in PUNCTS:
        return PUNCT
    return OP


def tok_label(t):
    kind, value = t[0], t[1]
    if kind == "NEWLINE":
        return "NL"
    if kind in ("INDENT", "DEDENT", "EOF"):
        return kind
    return str(value)


# ---------- tree layout (tidy, top-down) ----------

def kind_color(kind):
    if kind in ("Name",):
        return NAME
    if kind in ("IntLiteral", "BoolLiteral", "NoneLiteral"):
        return NUMBER
    if kind in ("BinOp", "Compare", "Call"):
        return OP
    return ACCENT


def build_tree(d, fs=16, hgap=0.22, vgap=0.85):
    """Returns (VGroup of everything, list of (node_dict) in pre-order)."""
    def measure(n):
        n["_lab"] = mono(n["label"], fs=fs, color=TEXT)
        n["_w"] = n["_lab"].width + 0.28
        for c in n["children"]:
            measure(c)
        if n["children"]:
            cw = sum(c["_sw"] for c in n["children"]) + hgap * (len(n["children"]) - 1)
        else:
            cw = 0
        n["_sw"] = max(n["_w"], cw)

    order = []

    def place(n, x0, depth):
        order.append(n)
        n["_x"], n["_y"] = x0 + n["_sw"] / 2, -depth * vgap
        if n["children"]:
            total = sum(c["_sw"] for c in n["children"]) + hgap * (len(n["children"]) - 1)
            x = n["_x"] - total / 2
            for c in n["children"]:
                place(c, x, depth + 1)
                x += c["_sw"] + hgap

    measure(d)
    place(d, 0, 0)
    everything = VGroup()
    for n in order:
        col = kind_color(n["kind"])
        box = RoundedRectangle(corner_radius=0.07, width=n["_w"], height=0.4,
                               stroke_color=col, stroke_width=2,
                               fill_color=col, fill_opacity=0.15)
        box.move_to([n["_x"], n["_y"], 0])
        n["_lab"].move_to(box)
        n["mob"] = VGroup(box, n["_lab"])
        everything.add(n["mob"])
    for n in order:
        n["edges"] = VGroup()
        for c in n["children"]:
            e = Line(n["mob"].get_bottom(), c["mob"].get_top(), stroke_width=1.5, color=MUTED)
            c["edge"] = e
            everything.add(e)
    return everything, order


def fit(m, w, h):
    if m.width > w:
        m.scale_to_fit_width(w)
    if m.height > h:
        m.scale_to_fit_height(h)
    return m


# ---------- Python-Tutor style memory view ----------

def tutor_frames(step, x_frames=0.15, x_objs=3.95, top=2.6, fs=17):
    """Frames column + Objects column + reference arrows for one trace step."""
    g = VGroup()
    heads = VGroup(
        Text("Frames", font_size=20, color=MUTED).move_to([x_frames + 1.6, top + 0.35, 0]),
        Text("Objects", font_size=20, color=MUTED).move_to([x_objs + 1.4, top + 0.35, 0]),
    )
    g.add(heads)
    objs = {}
    for fr in step["frames"]:
        for v in fr["vars"].values():
            if isinstance(v, dict) and v["ref"] not in objs:
                objs[v["ref"]] = None
    oy = top - 0.3
    for ref in objs:
        o = card(ref, color=NAME, w=3.0, h=0.5, fs=16)
        o.move_to([x_objs + 1.5, oy, 0])
        objs[ref] = o
        g.add(o)
        oy -= 0.7
    y = top
    n = len(step["frames"])
    for i, fr in enumerate(step["frames"]):
        active = i == n - 1
        rows = list(fr["vars"].items())
        if active and step["event"] == "return":
            rows.append(("Return value", step["ret"]))
        h = 0.42 + 0.36 * max(len(rows), 1)
        box = Rectangle(width=3.2, height=h,
                        stroke_color=NAME if active else MUTED,
                        stroke_width=2.5 if active else 1.5,
                        fill_color=BG_CARD, fill_opacity=1)
        box.move_to([x_frames + 1.6, y - h / 2, 0])
        title = Text(fr["name"], font_size=fs, color=TEXT if active else MUTED, weight=BOLD)
        title.next_to(box.get_top(), DOWN, buff=0.08).align_to(box, LEFT).shift(RIGHT * 0.12)
        g.add(box, title)
        ry = y - 0.55
        for k, v in rows:
            kt = mono(k, fs=fs - 1, color=ERR if k == "Return value" else NAME)
            kt.move_to([x_frames + 1.5, ry, 0], aligned_edge=RIGHT)
            cell = Rectangle(width=0.9, height=0.3, stroke_width=1, color=MUTED)
            cell.move_to([x_frames + 2.25, ry, 0])
            g.add(kt, cell)
            if isinstance(v, dict):
                dot = Dot(cell.get_center(), radius=0.05, color=NAME)
                target = objs[v["ref"]]
                arr = Arrow(dot.get_center(), target.get_left(), buff=0.05,
                            stroke_width=2, color=NAME, max_tip_length_to_length_ratio=0.08)
                g.add(dot, arr)
            else:
                vt = mono(v, fs=fs - 1, color=NUMBER)
                vt.move_to(cell)
                g.add(vt)
            ry -= 0.36
        y -= h + 0.12
    return g


# ════════════════════════════════════════════════════════════════════════════
class InterpreterTutorial(Slide):
    def construct(self):
        chapters = [
            self.ch01_overview, self.ch02_tokenizer, self.ch03_parser,
            self.ch04_ast, self.ch05_semantic, self.ch06_memory,
            self.ch07_errors, self.ch08_builtins, self.ch09_bytecode,
            self.ch10_out_of_scope,
        ]
        only = os.environ.get("MAP_CHAPTERS")  # e.g. MAP_CHAPTERS=2,3 for a test render
        for i, ch in enumerate(chapters, start=1):
            if not only or str(i) in only.split(","):
                ch()

    # ── utilities ────────────────────────────────────────────────────────────

    def slide(self, chap, label):
        """Start a new slide; notes tag it for build_html.py."""
        self.next_slide(notes=f"{chap}|{label}")

    def clear(self, keep=(), run_time=0.4):
        keep_ids = {id(m) for k in keep for m in k.get_family()}
        out = [m for m in self.mobjects if id(m) not in keep_ids]
        if out:
            self.play(*[FadeOut(m) for m in out], run_time=run_time)

    def title(self, text):
        t = Text(text, font_size=32, color=ACCENT, weight=BOLD).to_edge(UP, buff=0.3)
        line = Line(LEFT, RIGHT, color=ACCENT, stroke_width=1.5).match_width(t).scale(1.3)
        line.next_to(t, DOWN, buff=0.1)
        self.play(FadeIn(t, shift=DOWN * 0.2), Create(line), run_time=0.5)
        return VGroup(t, line)

    def set_cap(self, cap, text, color=MUTED):
        new = caption(text, color=color)
        if cap is None:
            self.play(FadeIn(new), run_time=0.3)
        else:
            self.play(Transform(cap, new), run_time=0.3)
            return cap
        return new

    # ═════════════════════════════════════════════════════════════ CHAPTER 1
    def ch01_overview(self):
        self.slide("ch01", "MAP: Make A Python")
        t = Text("MAP — Make A Python", font_size=54, weight=BOLD)
        t.set_color_by_gradient(NAME, ACCENT, NUMBER)
        sub = Text("Build a Python interpreter, one stage at a time", font_size=26, color=MUTED)
        VGroup(t, sub).arrange(DOWN, buff=0.3).to_edge(UP, buff=0.6)
        self.play(FadeIn(t, scale=1.1), FadeIn(sub, shift=UP * 0.2))
        la = Listing(C.PROGRAM_A, fs=15)
        lb = Listing(C.PROGRAM_B, fs=15)
        ca = VGroup(Text("Program A — recursive", font_size=20, color=NAME), la).arrange(DOWN, aligned_edge=LEFT)
        cb = VGroup(Text("Program B — iterative", font_size=20, color=NAME), lb).arrange(DOWN, aligned_edge=LEFT)
        VGroup(ca, cb).arrange(RIGHT, buff=1.0, aligned_edge=UP).next_to(sub, DOWN, buff=0.35)
        self.play(FadeIn(ca), FadeIn(cb))
        oa = mono("→ " + C.run(C.PROGRAM_A).strip(), fs=22, color=OK).next_to(la, DOWN, aligned_edge=LEFT)
        ob = mono("→ " + C.run(C.PROGRAM_B).strip(), fs=22, color=OK).next_to(lb, DOWN, aligned_edge=LEFT)
        self.play(Write(oa), Write(ob))
        self.wait(0.5)

        # ── pipeline
        self.slide("ch01", "The pipeline")
        self.clear()
        head = self.title("1 · The pipeline")
        stages = [
            ("Source", "str", TEXT),
            ("Tokens", "Lexer.tokenize()", NAME),
            ("Parser", "Parser.parse()", OP),
            ("AST", "Program(body=[...])", ACCENT),
            ("Semantic", "concept · ch.5", MUTED),
            ("Tree-walk\n+ memory", "Interpreter.run()", NUMBER),
            ("Output", "stdout", TEXT),
        ]
        boxes = VGroup()
        for name, fn, col in stages:
            b = RoundedRectangle(corner_radius=0.1, width=1.7, height=1.0, color=col,
                                 fill_color=BG_CARD, fill_opacity=1, stroke_width=2.5)
            lab = Text(name, font_size=20, color=col, weight=BOLD, line_spacing=0.8).move_to(b)
            f = mono(fn, fs=11, color=MUTED).next_to(b, DOWN, buff=0.1)
            if f.width > 1.9:
                f.scale_to_fit_width(1.9)
            boxes.add(VGroup(b, lab, f))
        boxes.arrange(RIGHT, buff=0.22).move_to(UP * 0.9)
        sem = boxes[4][0]
        dashed = DashedVMobject(sem.copy(), num_dashes=30).set_color(MUTED)
        boxes[4].remove(sem)
        boxes[4].add_to_back(dashed)
        arrows = VGroup(*[Arrow(boxes[i][0].get_right(), boxes[i + 1][0].get_left(), buff=0.03,
                                stroke_width=3, color=MUTED, max_tip_length_to_length_ratio=0.3)
                          for i in range(len(boxes) - 1)])
        for i, b in enumerate(boxes):
            self.play(FadeIn(b, shift=UP * 0.2), run_time=0.35)
            if i < len(arrows):
                self.play(GrowArrow(arrows[i]), run_time=0.2)
        dot = Dot(boxes[0][0].get_center(), color=HILITE, radius=0.1)
        self.play(FadeIn(dot))
        for b in boxes[1:]:
            self.play(dot.animate.move_to(b[0].get_center()), Indicate(b[0], color=HILITE, scale_factor=1.05), run_time=0.45)
        out = mono("3", fs=30, color=OK).next_to(boxes[-1], UP, buff=0.2)
        self.play(FadeOut(dot), FadeIn(out, shift=UP * 0.2))

        self.next_slide(notes="ch01|CPython takes another road")
        # CPython branch from AST
        cp = VGroup()
        cp_stages = [("compile", "ast → code object"), ("Bytecode", "dis.dis(...)"), ("PVM", "ceval.c loop")]
        for name, fn in cp_stages:
            b = RoundedRectangle(corner_radius=0.1, width=2.0, height=0.8, color=KEYWORD,
                                 fill_color=BG_CARD, fill_opacity=1, stroke_width=2)
            lab = Text(name, font_size=20, color=KEYWORD, weight=BOLD).move_to(b)
            f = mono(fn, fs=11, color=MUTED).next_to(b, DOWN, buff=0.08)
            cp.add(VGroup(b, lab, f))
        cp.arrange(RIGHT, buff=0.5).next_to(boxes, DOWN, buff=1.3).align_to(boxes[3], LEFT)
        branch = Arrow(boxes[3][2].get_bottom(), cp[0][0].get_top(), buff=0.05, color=KEYWORD, stroke_width=3)
        cp_ar = VGroup(*[Arrow(cp[i][0].get_right(), cp[i + 1][0].get_left(), buff=0.03, color=KEYWORD,
                               stroke_width=3, max_tip_length_to_length_ratio=0.25) for i in range(2)])
        lab = Text("real CPython (ch. 9): compiles to bytecode with jumps", font_size=18, color=KEYWORD)
        lab.next_to(cp, DOWN, buff=0.35)
        self.play(GrowArrow(branch))
        for i, b in enumerate(cp):
            self.play(FadeIn(b, shift=RIGHT * 0.2), run_time=0.35)
            if i < 2:
                self.play(GrowArrow(cp_ar[i]), run_time=0.2)
        self.play(Write(lab))
        note = caption("MAP walks the tree directly; CPython turns the AST into bytecode first.")
        self.play(FadeIn(note))

        # ── six languages
        self.slide("ch01", "Same pipeline in six languages")
        self.clear()
        self.title("Same pipeline, six interpreters")
        rows = [
            ("", "Tokens", "AST", "Dispatch", "return"),
            ("Python", "TT Enum + dataclass", "@dataclass nodes", "getattr _eval_X", "raise ReturnSignal"),
            ("Rust", "enum TokKind(payload)", "enum Expr/Stmt, Box", "match", "Err(Flow::Return)"),
            ("C++", "enum class TT", "fat ASTNode + tag", "switch(type)", "throw ReturnException"),
            ("Java", "enum TT + record", "sealed Node + records", "switch pattern", "throw ReturnSignal"),
            ("Clojure", "keywords + defrecord", "defrecord per node", "defmulti", "ex-info"),
            ("LLVM", "same as Python", "same as Python", "emit IR", "native ret"),
        ]
        grid = VGroup()
        for r, row in enumerate(rows):
            line = VGroup()
            for c, cell in enumerate(row):
                col = ACCENT if r == 0 else (NAME if c == 0 else TEXT)
                t = mono(cell, fs=13 if r else 15, color=col)
                line.add(t)
            grid.add(line)
        widths = [1.4, 3.0, 3.0, 2.3, 2.7]
        for r, line in enumerate(grid):
            x = -6.5
            for c, t in enumerate(line):
                t.move_to([x, 2.3 - r * 0.62, 0], aligned_edge=LEFT)
                x += widths[c]
        sep = Line([-6.7, 2.0, 0], [6.7, 2.0, 0], color=BORDER)
        self.play(FadeIn(grid[0]), Create(sep))
        for line in grid[1:]:
            self.play(FadeIn(line, shift=RIGHT * 0.2), run_time=0.35)
        common = caption("All six share: indent stack → INDENT/DEDENT, recursive descent, Environment{vars, parent}, PyError(msg, line)")
        self.play(FadeIn(common))
        self.wait(0.5)

    # ═════════════════════════════════════════════════════════════ CHAPTER 2
    def ch02_tokenizer(self):
        self.slide("ch02", "The scanner loop")
        self.clear()
        self.title("2 · Tokenizer — Lexer.tokenize()")
        loop = code_card(
            "def tokenize(self):\n"
            "    while self.pos < len(self.source):\n"
            "        self._next_token()\n"
            "    self._close_all_indents()\n"
            "    self.tokens.append(Token(TT.EOF, ...))",
            fs=17, title="main.py — the next_token loop", ref="python_interpreter_in_python/main.py:190")
        disp = code_card(
            "def _next_token(self):\n"
            "    if self.at_line_start: _handle_indentation()\n"
            "    ch = self._cur()\n"
            "    ' ' / '\\t'   → skip\n"
            "    '\\n'        → NEWLINE\n"
            "    '#'         → comment, skip\n"
            "    '\"' or \"'\"  → _read_string()\n"
            "    digit       → _read_number()\n"
            "    letter / _  → _read_name()  (keyword?)\n"
            "    otherwise   → _read_operator()",
            fs=15, title="dispatch on the current character", ref="main.py:234 (summarised)")
        tok = code_card("@dataclass\nclass Token:\n    type: TT    # DEF, NAME ...\n    value: Any\n    line: int\n    col: int",
                        fs=15, title="each token remembers where it came from", ref="main.py:138")
        left = VGroup(loop, tok).arrange(DOWN, buff=0.55, aligned_edge=LEFT)
        VGroup(left, disp).arrange(RIGHT, buff=0.5, aligned_edge=UP)
        fit(VGroup(left, disp), 13.4, 6.2)
        VGroup(left, disp).move_to(DOWN * 0.45)
        self.play(FadeIn(loop, shift=UP * 0.2))
        self.play(FadeIn(disp, shift=UP * 0.2))
        self.play(FadeIn(tok, shift=UP * 0.2))

        # ── Program A token by token
        self.slide("ch02", "Program A token by token")
        self.clear()
        self.title("Scanning Program A")
        lst = Listing(C.PROGRAM_A, fs=20, numbers=True).to_corner(UL, buff=0.5).shift(DOWN * 0.75 + RIGHT * 0.4)
        self.play(FadeIn(lst))
        legend = VGroup(*[
            VGroup(Square(0.18, fill_color=c, fill_opacity=0.6, stroke_width=0), Text(n, font_size=14, color=c)).arrange(RIGHT, buff=0.1)
            for n, c in [("keyword", KEYWORD), ("NAME", NAME), ("INTEGER", NUMBER), ("operator", OP), ("punct", PUNCT), ("layout", ACCENT)]
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to([5.2, 1.9, 0], aligned_edge=LEFT)
        stack_lbl = mono("indent_stack", fs=15, color=ACCENT).next_to(legend, DOWN, buff=0.4).align_to(legend, LEFT)
        self.play(FadeIn(legend), FadeIn(stack_lbl))
        stack = VGroup()

        def stack_box(v, i):
            b = VGroup(Rectangle(width=0.8, height=0.32, color=ACCENT, fill_color=ACCENT, fill_opacity=0.15, stroke_width=2),
                       mono(str(v), fs=15))
            b[1].move_to(b[0])
            b.next_to(stack_lbl, DOWN, buff=0.15 + 0.34 * i).align_to(stack_lbl, LEFT)
            return b

        stack.add(stack_box(0, 0))
        self.play(FadeIn(stack[0]))
        toks = C.tokens(C.PROGRAM_A)
        cursor = lst.span(1, 1, 3)
        self.play(Create(cursor), run_time=0.3)
        x0, y0 = -6.6, -0.95
        x, y = x0, y0
        n_lines = len(lst.src_lines)
        for t in toks:
            kind, value, line, col = t
            line = min(line, n_lines)
            ln = len(C.token_text(t))
            if kind == "INDENT":
                target = lst.span(line, 1, value, color=ACCENT)
            elif kind in ("DEDENT", "EOF"):
                target = lst.span(line, 1, 0.4, color=ACCENT)
            elif kind == "NEWLINE":
                target = lst.span(line, col, 0.6, color=ACCENT)
            else:
                target = lst.span(line, col, ln)
            c = chip(tok_label(t), tok_color(kind), h=0.36, fs=14)
            if x + c.width > 6.7:
                x, y = x0, y - 0.48
            c.move_to([x + c.width / 2, y, 0])
            x += c.width + 0.08
            anims = [Transform(cursor, target), FadeIn(c, shift=DOWN * 0.1)]
            if kind == "INDENT":
                nb = stack_box(value, len(stack))
                stack.add(nb)
                anims.append(FadeIn(nb, shift=DOWN * 0.1))
            elif kind == "DEDENT":
                top = stack[-1]
                stack.remove(top)
                anims.append(FadeOut(top, shift=UP * 0.1))
            self.play(*anims, run_time=0.22)
        cap = caption(f"{len(toks)} tokens from Lexer(source).tokenize() — INDENT/DEDENT come from the indent stack")
        self.play(FadeIn(cap))

        # ── Program B: indentation focus
        self.slide("ch02", "INDENT and DEDENT in Program B")
        self.clear()
        self.title("Leading whitespace → INDENT / DEDENT")
        lst = Listing(C.PROGRAM_B, fs=19, numbers=True).to_corner(UL, buff=0.5).shift(DOWN * 0.7 + RIGHT * 0.4)
        self.play(FadeIn(lst))
        rule = code_card(
            "indent = count leading spaces\n"
            "if indent > stack[-1]:  push, emit INDENT\n"
            "while indent < stack[-1]: pop, emit DEDENT\n"
            "if indent != stack[-1]: IndentationError",
            fs=14, title="_handle_indentation", ref="main.py:271")
        rule.to_corner(UR, buff=0.4).shift(DOWN * 0.7)
        self.play(FadeIn(rule))
        stack_lbl = mono("indent_stack", fs=15, color=ACCENT).next_to(rule, DOWN, buff=0.35).align_to(rule, LEFT)
        emit_lbl = mono("emitted", fs=15, color=ACCENT).next_to(stack_lbl, RIGHT, buff=1.6)
        self.play(FadeIn(stack_lbl), FadeIn(emit_lbl))

        def sbox(v, i):
            b = VGroup(Rectangle(width=0.8, height=0.32, color=ACCENT, fill_color=ACCENT, fill_opacity=0.15, stroke_width=2),
                       mono(str(v), fs=15))
            b[1].move_to(b[0])
            b.next_to(stack_lbl, DOWN, buff=0.15 + 0.34 * i).align_to(stack_lbl, LEFT)
            return b

        stack = VGroup(sbox(0, 0))
        self.play(FadeIn(stack))
        toks = C.tokens(C.PROGRAM_B)
        hl = None
        emitted = VGroup()
        n_lines = len(lst.src_lines)
        for ln_no, text in enumerate(lst.src_lines, start=1):
            if not text.strip():
                continue
            box = lst.line_box(ln_no)
            ind = len(text) - len(text.lstrip())
            count = mono(f"indent = {ind}", fs=16, color=HILITE).next_to(lst, DOWN, buff=0.25).align_to(lst, LEFT)
            layout = [t for t in toks if t[2] == ln_no and t[0] in ("INDENT", "DEDENT")]
            anims = []
            if hl is None:
                hl = box
                anims.append(FadeIn(hl))
                cnt = count
                anims.append(FadeIn(cnt))
            else:
                anims.append(Transform(hl, box))
                anims.append(Transform(cnt, count))
            new_emit = VGroup(*[chip(t[0], ACCENT, h=0.32, fs=13) for t in layout]).arrange(DOWN, buff=0.06)
            if layout:
                new_emit.next_to(emit_lbl, DOWN, buff=0.15).align_to(emit_lbl, LEFT)
            else:
                new_emit = VGroup(mono("—", fs=14, color=MUTED).next_to(emit_lbl, DOWN, buff=0.15).align_to(emit_lbl, LEFT))
            anims.append(FadeOut(emitted))
            for t in layout:
                if t[0] == "INDENT":
                    nb = sbox(t[1], len(stack))
                    stack.add(nb)
                    anims.append(FadeIn(nb, shift=DOWN * 0.1))
                else:
                    top = stack[-1]
                    stack.remove(top)
                    anims.append(FadeOut(top, shift=UP * 0.1))
            anims.append(FadeIn(new_emit))
            emitted = new_emit
            self.play(*anims, run_time=0.5)
            self.wait(0.15)
        # EOF dedents
        eof = [t for t in toks if t[2] > n_lines and t[0] == "DEDENT"]
        if eof:
            new_emit = VGroup(*[chip("DEDENT", ACCENT, h=0.32, fs=13) for _ in eof]).arrange(DOWN, buff=0.06)
            new_emit.next_to(emit_lbl, DOWN, buff=0.15).align_to(emit_lbl, LEFT)
            self.play(FadeOut(emitted), FadeIn(new_emit), run_time=0.4)
        cap = caption("At EOF, _close_all_indents() pops what is left. Blank lines never change the stack.")
        self.play(FadeIn(cap))

    # ═════════════════════════════════════════════════════════════ CHAPTER 3
    def ch03_parser(self):
        self.slide("ch03", "MAP grammar")
        self.clear()
        self.title("3 · Parser — a PEG for MAP")
        grammar = [
            ("program", "stmt* EOF"),
            ("stmt", "func_def / if_stmt / for_stmt / simple_stmt"),
            ("simple_stmt", "(return_stmt / assign / expr_stmt) NEWLINE"),
            ("assign", "NAME '=' expr"),
            ("func_def", "'def' NAME '(' params? ')' ':' block"),
            ("if_stmt", "'if' expr ':' block ('else' ':' block)?"),
            ("for_stmt", "'for' NAME 'in' expr ':' block"),
            ("block", "NEWLINE INDENT stmt+ DEDENT"),
            ("expr", "comparison"),
            ("comparison", "sum (('<=' / '<' / '==') sum)*"),
            ("sum", "primary (('+' / '-') primary)*"),
            ("primary", "atom ('(' args? ')')*"),
            ("atom", "NAME / INT / 'True' / 'False' / 'None' / '(' expr ')'"),
        ]
        rows = VGroup()
        for lhs, rhs in grammar:
            l = mono(f"{lhs:<11}", fs=16, color=NAME)
            a = mono("<-", fs=16, color=MUTED)
            r = mono(rhs, fs=16, color=TEXT)
            rows.add(VGroup(l, a, r).arrange(RIGHT, buff=0.2))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.14).to_edge(LEFT, buff=0.6).shift(DOWN * 0.3)
        for r in rows:
            r[1].move_to([rows.get_left()[0] + 2.2, r.get_y(), 0])
            r[2].next_to(r[1], RIGHT, buff=0.2)
        for r in rows:
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.18)
        ops = VGroup(
            mono("e1 e2   sequence", fs=15), mono("e1 / e2 ordered choice", fs=15, color=OP),
            mono("e*  e+  e?", fs=15), mono("each rule → one method", fs=15, color=NUMBER),
            mono("_stmt, _if_stmt, _sum ...", fs=15, color=NUMBER),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        box = SurroundingRectangle(ops, buff=0.2, color=MUTED, corner_radius=0.08)
        VGroup(box, ops).to_corner(UR, buff=0.4).shift(DOWN * 0.9)
        self.play(FadeIn(box), FadeIn(ops))
        cap = caption("Grammar for MAP, taken from the EBNF comment in main.py:656 (with the extra features removed)")
        self.play(FadeIn(cap))

        # ── ordered choice + backtracking
        self.slide("ch03", "Ordered choice and backtracking")
        self.clear()
        self.title("Ordered choice + backtracking")
        rule = VGroup(mono("simple_stmt <- assign / expr_stmt", fs=22, color=TEXT),
                      mono("assign      <- NAME '=' expr", fs=18, color=MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        rule.to_corner(UL, buff=0.5).shift(DOWN * 0.8)
        self.play(FadeIn(rule))
        toks = [t for t in C.tokens("print(fib_rec(4))\n") if t[0] != "EOF"]
        chips = VGroup(*[chip(tok_label(t), tok_color(t[0]), h=0.55, fs=20) for t in toks]).arrange(RIGHT, buff=0.12)
        chips.move_to(DOWN * 0.3)
        idx = VGroup(*[mono(str(i), fs=13, color=MUTED).next_to(c, DOWN, buff=0.1) for i, c in enumerate(chips)])
        self.play(FadeIn(chips), FadeIn(idx))
        cur = make_cursor().next_to(chips[0], UP, buff=0.15)
        saved = make_cursor().set_color(MUTED).next_to(chips[0], UP, buff=0.45)
        saved_l = mono("saved pos=0", fs=13, color=MUTED).next_to(saved, UP, buff=0.05)
        cap = caption("try the FIRST alternative: assign.  Save pos = 0 first.")
        self.play(FadeIn(cur), FadeIn(saved), FadeIn(saved_l), FadeIn(cap))
        alt1 = SurroundingRectangle(rule[0][13:19], color=HILITE, buff=0.05)
        self.play(Create(alt1))
        self.play(chips[0][0].animate.set_fill(OK, 0.5), cur.animate.next_to(chips[1], UP, buff=0.15), run_time=0.5)
        cap = self.set_cap(cap, "NAME matched 'print'.  Next we need '=' ...")
        self.play(Indicate(chips[1], color=ERR), run_time=0.7)
        x = Cross(chips[1], stroke_color=ERR, stroke_width=4)
        self.play(Create(x))
        cap = self.set_cap(cap, "... but the token is '('.  assign FAILS → restore pos to 0 (backtrack)", color=ERR)
        self.play(cur.animate.next_to(chips[0], UP, buff=0.15), chips[0][0].animate.set_fill(NAME, 0.22), FadeOut(x), run_time=0.7)
        alt2 = SurroundingRectangle(rule[0][20:29], color=HILITE, buff=0.05)
        self.play(Transform(alt1, alt2))
        cap = self.set_cap(cap, "try the SECOND alternative from the same position: expr_stmt")
        for i in range(len(chips)):
            nxt = chips[i + 1] if i + 1 < len(chips) else chips[i]
            self.play(chips[i][0].animate.set_fill(OK, 0.5), cur.animate.next_to(nxt, UP, buff=0.15), run_time=0.18)
        node = card("ExprStmt(Call(print, [Call(fib_rec, [4])]))", color=OK, w=8.4, h=0.6, fs=18).next_to(chips, DOWN, buff=0.8)
        self.play(FadeIn(node, shift=UP * 0.2))
        cap = self.set_cap(cap, "main.py chooses without rewinding: _check(NAME) and _peek(1).type == EQUAL (main.py:770)")

        # ── packrat
        self.slide("ch03", "Packrat memoization")
        self.clear()
        self.title("Packrat: remember (rule, pos) → result")
        rule = mono("comparison <- sum '<=' sum / sum", fs=22).to_corner(UL, buff=0.5).shift(DOWN * 0.8)
        ctx = mono("context:  for i in range(2, n + 1):", fs=16, color=MUTED).next_to(rule, DOWN, aligned_edge=LEFT)
        self.play(FadeIn(rule), FadeIn(ctx))
        toks = [("NAME", "n"), ("PLUS", "+"), ("INTEGER", 1), ("RPAREN", ")")]
        chips = VGroup(*[chip(str(v), tok_color(k), h=0.55, fs=20) for k, v in toks]).arrange(RIGHT, buff=0.15)
        chips.move_to(LEFT * 3 + DOWN * 0.6)
        idx = VGroup(*[mono(str(i), fs=13, color=MUTED).next_to(c, DOWN, buff=0.1) for i, c in enumerate(chips)])
        self.play(FadeIn(chips), FadeIn(idx))
        memo_t = Text("memo table", font_size=20, color=ACCENT).move_to(RIGHT * 3.6 + UP * 1.2)
        hdr = mono("(rule, pos)     result        end", fs=15, color=MUTED).next_to(memo_t, DOWN, buff=0.2)
        self.play(FadeIn(memo_t), FadeIn(hdr))
        cur = make_cursor().next_to(chips[0], UP, buff=0.15)
        self.play(FadeIn(cur))
        cap = caption("alternative 1: parse sum at pos 0 ...")
        self.play(FadeIn(cap))
        for i in range(3):
            self.play(chips[i][0].animate.set_fill(OK, 0.5), cur.animate.next_to(chips[i + 1], UP, buff=0.15), run_time=0.3)
        row = mono("(sum, 0)        BinOp(+)      3", fs=15, color=OK).next_to(hdr, DOWN, buff=0.2, aligned_edge=LEFT)
        self.play(FadeIn(row, shift=LEFT * 0.3))
        cap = self.set_cap(cap, "... then '<=' is required, but pos 3 is ')'  → fail, rewind to 0", color=ERR)
        self.play(Indicate(chips[3], color=ERR))
        self.play(cur.animate.next_to(chips[0], UP, buff=0.15), *[chips[i][0].animate.set_fill(tok_color(toks[i][0]), 0.22) for i in range(3)])
        cap = self.set_cap(cap, "alternative 2: sum at pos 0 again — look it up instead of re-parsing")
        self.play(Circumscribe(row, color=HILITE))
        hit = mono("hit!", fs=16, color=HILITE).next_to(row, RIGHT, buff=0.2)
        self.play(FadeIn(hit), cur.animate.next_to(chips[3], UP, buff=0.15), *[chips[i][0].animate.set_fill(OK, 0.5) for i in range(3)])
        cap = self.set_cap(cap, "every (rule, pos) is parsed at most once → linear time.  main.py's _comparison parses _sum once, then peeks for '<='.")

        # ── real recursive descent
        self.slide("ch03", "Recursive descent in main.py")
        self.clear()
        self.title("main.py's recursive descent on:  n <= 1")
        events, ttoks = C.parse_calls("n <= 1\n")
        chips = VGroup(*[chip(str(v).replace("\n", "NL") if v is not None else k, tok_color(k), h=0.5, fs=18)
                         for k, v in ttoks]).arrange(RIGHT, buff=0.12)
        chips.move_to([2.0, 2.1, 0])
        self.play(FadeIn(chips))
        cur = make_cursor().next_to(chips[0], UP, buff=0.12)
        self.play(FadeIn(cur))
        st_lbl = Text("call stack", font_size=18, color=MUTED).move_to([-5.2, 2.0, 0])
        self.play(FadeIn(st_lbl))
        stack = []
        tree = {}
        tree_pos = {"Name n": [2.3, -2.2, 0], "Int 1": [5.3, -2.2, 0], "Compare <=": [3.8, -0.8, 0]}
        last = None
        for kind, meth, pos, lab in events:
            if kind == "enter":
                b = VGroup(Rectangle(width=2.7, height=0.34, color=NAME, fill_color=NAME, fill_opacity=0.15, stroke_width=1.5),
                           mono(meth, fs=14))
                b[1].move_to(b[0])
                b.move_to([-5.2, 1.6 - 0.37 * len(stack), 0])
                stack.append(b)
                self.play(FadeIn(b, shift=DOWN * 0.1), cur.animate.next_to(chips[min(pos, len(chips) - 1)], UP, buff=0.12), run_time=0.12)
            else:
                b = stack.pop()
                anims = [FadeOut(b, shift=UP * 0.1), cur.animate.next_to(chips[min(pos, len(chips) - 1)], UP, buff=0.12)]
                if lab and lab != last and lab in tree_pos and lab not in tree:
                    n = card(lab, color=OK, w=2.2, h=0.5, fs=18).move_to(tree_pos[lab])
                    tree[lab] = n
                    anims.append(FadeIn(n, scale=0.6))
                    if lab.startswith("Compare"):
                        anims += [Create(Line(n.get_bottom(), tree[k].get_top(), color=MUTED)) for k in ("Name n", "Int 1")]
                    made = mono(f"{meth} built {lab}", fs=15, color=OK).move_to([3.8, 0.5, 0])
                    anims.append(FadeIn(made))
                    self.play(*anims, run_time=0.35)
                    self.play(FadeOut(made), run_time=0.15)
                else:
                    self.play(*anims, run_time=0.12)
                last = lab
        cap = caption("_expr → _or_expr → _and_expr → _not_expr → _comparison → _sum → _term → _factor → _power → _primary → _atom")
        self.play(FadeIn(cap))

        # ── invalid programs
        bad = [
            ("parse_missing_colon.py", "parser"), ("parse_unclosed_paren.py", "parser"),
            ("parse_def_no_paren.py", "parser"), ("parse_double_equal.py", "parser"),
            ("parse_missing_indent.py", "parser"), ("parse_dangling_op.py", "parser"),
            ("lex_bad_dedent.py", "lexer"), ("lex_bad_char.py", "lexer"),
        ]
        for part in range(2):
            self.slide("ch03", f"Invalid programs ({part + 1}/2)")
            self.clear()
            self.title(f"Invalid programs and the SyntaxError each one raises ({part + 1}/2)")
            panels = VGroup()
            for fname, stage in bad[part * 4:(part + 1) * 4]:
                src = C.example("errors/" + fname)
                msg, line, col = C.parse_failure(src)
                cp = C.python314_error(src)
                p = VGroup()
                hd = mono(fname, fs=14, color=ACCENT)
                lst = Listing(src, fs=15, numbers=True)
                lst.next_to(hd, DOWN, buff=0.18, aligned_edge=LEFT).shift(RIGHT * 0.45)
                m1 = mono("MAP:  " + msg, fs=12, color=ERR)
                m2 = mono("3.14: " + cp, fs=12, color=MUTED)
                for m in (m1, m2):
                    if m.width > 6.2:
                        m.scale_to_fit_width(6.2)
                VGroup(m1, m2).arrange(DOWN, aligned_edge=LEFT, buff=0.08).next_to(lst, DOWN, buff=0.35).align_to(hd, LEFT)
                p.add(hd, lst, m1, m2)
                fit(VGroup(hd, lst, m1, m2), 6.3, 2.6)
                frame = Rectangle(width=6.6, height=2.9, color=BORDER, stroke_width=1)
                p.add(frame)
                frame.move_to(VGroup(hd, lst, m1, m2))
                p.fail = (line, col)
                panels.add(p)
            panels.arrange_in_grid(rows=2, cols=2, buff=(0.3, 0.25)).next_to(ORIGIN, DOWN, buff=-2.75)
            for p in panels:
                hd, lst, m1, m2, frame = p
                line, col = p.fail
                n_lines = len(lst.src_lines)
                if col is None:
                    mark = lst.line_box(min(line, n_lines), color=ERR)
                elif line > n_lines:
                    mark = mono("⏎ EOF", fs=13, color=ERR).next_to(lst, DOWN, buff=0.06, aligned_edge=LEFT)
                else:
                    cw, lh = lst._unit()
                    mark = mono("^", fs=18, color=ERR).move_to(lst.pos(line, col) + RIGHT * cw / 2 + DOWN * lh * 0.55)
                self.play(FadeIn(frame), FadeIn(hd), FadeIn(lst), run_time=0.4)
                self.play(FadeIn(mark, shift=UP * 0.1), Flash(mark.get_center(), color=ERR, line_length=0.15), run_time=0.5)
                self.play(Write(m1), FadeIn(m2), run_time=0.6)
            cap = caption("Messages captured by running main.py; the grey line is CPython 3.14 for comparison.")
            self.play(FadeIn(cap))

    # ═════════════════════════════════════════════════════════════ CHAPTER 4
    def ch04_ast(self):
        self.slide("ch04", "Node classes: Composite")
        self.clear()
        self.title("4 · AST — node classes (Composite pattern)")
        root = card("ASTNode(line)", color=ACCENT, w=3.2, h=0.55, fs=20).move_to(UP * 2.1)
        comp = ["Program", "FuncDef", "If", "For", "Return", "Assign", "ExprStmt", "BinOp", "Compare", "Call"]
        leaf = ["Name", "IntLiteral", "BoolLiteral", "NoneLiteral"]
        cg = VGroup(*[card(n, color=OP if n in ("BinOp", "Compare", "Call") else ACCENT, w=1.95, h=0.48, fs=16) for n in comp])
        cg.arrange_in_grid(rows=2, cols=5, buff=0.18).move_to(UP * 0.95)
        lg = VGroup(*[card(n, color=NUMBER if n != "Name" else NAME, w=2.2, h=0.48, fs=16) for n in leaf])
        lg.arrange(RIGHT, buff=0.2).move_to(DOWN * 0.35)
        self.play(FadeIn(root))
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.15) for c in cg], lag_ratio=0.08))
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.15) for c in lg], lag_ratio=0.1))
        l1 = Text("composite: holds child nodes (body, test, left/right, args)", font_size=18, color=ACCENT).next_to(cg, RIGHT, buff=0.1)
        fit(l1, 13, 1)
        l1.next_to(cg, DOWN, buff=0.12)
        l2 = Text("leaf: no children", font_size=18, color=NUMBER).next_to(lg, DOWN, buff=0.12)
        self.play(FadeIn(l1), FadeIn(l2))
        disp = code_card("def _exec(self, node, env):\n    name = type(node).__name__\n    method = getattr(self, f\"_exec_{name}\")\n    method(node, env)",
                         fs=14, title="Visitor-style dispatch  (Rust: match · Java: switch · Clojure: defmulti)", ref="main.py:1311")
        fit(disp, 12, 2.2)
        disp.to_edge(DOWN, buff=0.2)
        self.play(FadeIn(disp, shift=UP * 0.2))

        for name, src in (("A", C.PROGRAM_A), ("B", C.PROGRAM_B)):
            self.slide("ch04", f"Program {name}: tree construction")
            self.clear()
            self.title(f"Program {name} — the AST built by Parser.parse()")
            tree, order = build_tree(C.ast_tree(src), fs=17 if name == "A" else 16, vgap=0.85 if name == "A" else 1.35)
            fit(tree, 13.4, 6.0)
            tree.move_to(DOWN * 0.45)
            for n in order:
                anims = [FadeIn(n["mob"], scale=0.7)]
                if "edge" in n:
                    anims.append(Create(n["edge"]))
                self.play(*anims, run_time=0.14 if name == "A" else 0.09)
            cap = caption("Statements = purple, expressions = yellow, names = blue, literals = green")
            self.play(FadeIn(cap))

            self.slide("ch04", f"Program {name}: depth-first walk")
            ring = SurroundingRectangle(order[0]["mob"], color=HILITE, buff=0.04)
            cap = self.set_cap(cap, "_print_ast / a Visitor: visit node, then each child left → right (depth-first)")
            self.play(Create(ring), run_time=0.3)
            for i, n in enumerate(order):
                num = mono(str(i + 1), fs=12, color=HILITE).next_to(n["mob"], UP, buff=0.02)
                self.play(ring.animate.become(SurroundingRectangle(n["mob"], color=HILITE, buff=0.04)),
                          n["mob"][0].animate.set_fill(HILITE, 0.3), FadeIn(num),
                          run_time=0.16 if name == "A" else 0.1)
            self.wait(0.3)

    # ═════════════════════════════════════════════════════════════ CHAPTER 5
    def ch05_semantic(self):
        self.slide("ch05", "Scope resolution")
        self.clear()
        self.title("5 · Semantic analysis — which names are local?")
        lst = Listing(C.PROGRAM_B, fs=18, numbers=True).to_corner(UL, buff=0.5).shift(DOWN * 0.8 + RIGHT * 0.4)
        self.play(FadeIn(lst))
        rule = Text("Python rule: a name ASSIGNED anywhere in a function\nis local to the WHOLE function. Everything else is global/builtin.",
                    font_size=17, color=MUTED, line_spacing=0.9).next_to(lst, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(FadeIn(rule))
        table = C.scope_table(C.PROGRAM_B)
        x_tab = 1.8
        heads = {}
        y = 2.3
        tabs = VGroup()
        for scope in ("global", "fib_iter"):
            h = Text(f"scope: {scope}", font_size=18, color=ACCENT, weight=BOLD).move_to([x_tab, y, 0], aligned_edge=LEFT)
            tabs.add(h)
            heads[scope] = y
            self.play(FadeIn(h), run_time=0.3)
            y -= 0.45
            for name, kind in table[scope].items():
                line_no = None
                for i, l in enumerate(lst.src_lines, start=1):
                    if re.search(rf"\b{name}\s*=(?!=)", l) or re.search(rf"for\s+{name}\b", l) or \
                       re.search(rf"def\s+\w+\(.*\b{name}\b", l) or re.search(rf"def\s+{name}\b", l):
                        line_no = i
                        break
                col = OK if kind.startswith("local") else (OP if kind == "builtin" else NAME)
                row = VGroup(mono(name, fs=17, color=TEXT), mono(kind, fs=15, color=col)).arrange(RIGHT, buff=0.3)
                row[1].move_to([x_tab + 2.0, y, 0], aligned_edge=LEFT)
                row[0].move_to([x_tab + 0.3, y, 0], aligned_edge=LEFT)
                anims = [FadeIn(row, shift=LEFT * 0.2)]
                if line_no:
                    hl = lst.line_box(line_no, color=col)
                    anims.append(FadeIn(hl))
                    self.play(*anims, run_time=0.4)
                    self.play(FadeOut(hl), run_time=0.15)
                else:
                    self.play(*anims, run_time=0.3)
                y -= 0.38
            y -= 0.25
        ta = C.scope_table(C.PROGRAM_A)
        note = mono(f"Program A: n is {ta['fib_rec']['n']}; fib_rec itself is global", fs=13, color=MUTED)
        fit(note, 5.2, 1).move_to([x_tab, y - 0.1, 0], aligned_edge=LEFT)
        self.play(FadeIn(note))
        cap = caption("MAP has no separate semantic pass — this table is computed from the real AST to show the idea.")
        self.play(FadeIn(cap))

        self.slide("ch05", "Errors before running vs at runtime")
        self.clear()
        self.title("Compile-time errors vs runtime errors")
        cases = [
            ("sem_return_outside.py", "CPython rejects it before running anything"),
            ("sem_duplicate_param.py", "CPython rejects it before running anything"),
            ("sem_unbound_local.py", "x is assigned later in f, so x is local to all of f"),
        ]
        panels = VGroup()
        for fname, why in cases:
            src = C.example("errors/" + fname)
            lst = Listing(src, fs=14, numbers=True)
            import textwrap
            m1 = VGroup(*[mono(l, fs=12, color=KEYWORD) for l in
                          textwrap.wrap("CPython 3.14: " + C.python314_error(src), 44)]).arrange(DOWN, aligned_edge=LEFT, buff=0.05)
            m2 = mono("MAP: " + C.run(src).strip().splitlines()[-1], fs=14, color=ERR)
            w = mono(why, fs=12, color=MUTED)
            for m in (m1, m2, w):
                fit(m, 4.1, 1.2)
            g = VGroup(mono(fname, fs=13, color=ACCENT), lst, m1, m2, w).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
            lst.shift(RIGHT * 0.4)
            panels.add(VGroup(SurroundingRectangle(g, buff=0.15, color=BORDER, stroke_width=1), g))
        panels.arrange(RIGHT, buff=0.25, aligned_edge=UP)
        fit(panels, 13.6, 5)
        panels.to_edge(UP, buff=1.15)
        for p in panels:
            self.play(FadeIn(p, shift=UP * 0.2), run_time=0.6)
            self.play(Indicate(p[1][3], color=ERR), run_time=0.5)
        cap = caption("A semantic pass would catch the first two before running. MAP does not have one, so it runs them anyway.")
        self.play(FadeIn(cap))

        self.slide("ch05", "Why NameError must wait for runtime")
        self.clear()
        self.title("Why NameError can only be detected at runtime")
        src = C.example("errors/sem_late_binding.py")
        lst = Listing(src, fs=20, numbers=True).move_to(LEFT * 3.2 + DOWN * 0.2)
        self.play(FadeIn(lst))
        steps = [
            (1, "def f: body mentions g — g does not exist yet", MUTED),
            (4, "def g: now g exists in the global scope", NAME),
            (7, "f() runs → looks up g at THIS moment → found", OK),
        ]
        y = 1.4
        for line, text, col in steps:
            hl = lst.line_box(line, color=col)
            t = Text(text, font_size=18, color=col).move_to([3.4, y, 0])
            fit(t, 6.4, 1)
            self.play(FadeIn(hl), FadeIn(t, shift=LEFT * 0.2), run_time=0.6)
            self.wait(0.3)
            self.play(FadeOut(hl), run_time=0.2)
            y -= 0.8
        out = mono("output: " + C.run(src).strip(), fs=20, color=OK).move_to([3.4, y, 0])
        self.play(Write(out))
        cap = caption("Whether a global exists depends on what has run so far, so the check happens in Environment.get (main.py:1030).")
        self.play(FadeIn(cap))

    # ═════════════════════════════════════════════════════════════ CHAPTER 6
    def ch06_memory(self):
        self.slide("ch06", "Environments and calls")
        self.clear()
        self.title("6 · Evaluation — Environment frames and calls")
        g = card("Global Environment", color=NAME, w=4.2, h=0.55, fs=18).move_to(LEFT * 3.5 + UP * 1.6)
        gv = mono("fib_rec → <function>   print, range → builtins", fs=13, color=MUTED).next_to(g, DOWN, buff=0.12)
        self.play(FadeIn(g), FadeIn(gv))
        f = card("Environment  n = 4", color=OK, w=4.2, h=0.55, fs=18).move_to(LEFT * 3.5 + DOWN * 0.6)
        par = Arrow(f.get_top(), gv.get_bottom(), buff=0.08, color=MUTED, stroke_width=2.5)
        pl = mono("parent", fs=13, color=MUTED).next_to(par, RIGHT, buff=0.1)
        self.play(FadeIn(f, shift=UP * 0.2), GrowArrow(par), FadeIn(pl))
        code = code_card(
            "call_env = Environment(parent=callee.closure)\n"
            "for param, val in zip(fn.params, args):\n"
            "    call_env.set(param, val)\n"
            "try:\n"
            "    self._exec_stmts(fn.body, call_env)\n"
            "except ReturnSignal as ret:\n"
            "    result = ret.value",
            fs=14, title="Interpreter._eval_Call", ref="main.py:1588")
        code.move_to(RIGHT * 3.2 + UP * 0.9)
        self.play(FadeIn(code))
        look = mono("lookup 'fib_rec':", fs=16, color=HILITE).move_to(LEFT * 3.5 + DOWN * 1.7)
        self.play(FadeIn(look))
        self.play(Indicate(f, color=ERR), run_time=0.6)
        miss = mono("not in vars → ask parent", fs=14, color=ERR).next_to(look, DOWN, buff=0.1)
        self.play(FadeIn(miss))
        self.play(Indicate(g, color=OK), run_time=0.6)
        hit = mono("found in global", fs=14, color=OK).next_to(miss, DOWN, buff=0.1)
        self.play(FadeIn(hit))
        get = code_card("def get(self, name, line=None):\n    if name in self.vars: return self.vars[name]\n    if self.parent: return self.parent.get(name, line)\n    raise PyRuntimeError(\"NameError: ...\")",
                        fs=13, title="Environment.get", ref="main.py:1030")
        get.move_to(RIGHT * 3.2 + DOWN * 2.0)
        self.play(FadeIn(get))

        for name, src in (("A", C.PROGRAM_A), ("B", C.PROGRAM_B)):
            self.slide("ch06", f"Program {name} step by step (memory view)")
            self.clear()
            self.title(f"Program {name} — memory, one step per executed line")
            self.tutor(src, fast=(name == "A"))

    def tutor(self, src, fast=False, stop_at_exception=False):
        steps = C.trace(src)
        lst = Listing(src, fs=16, numbers=True).move_to([-5.0, 0.6, 0], aligned_edge=UP)
        lst.to_edge(LEFT, buff=0.7).align_to(UP * 2.65, UP)
        self.play(FadeIn(lst), run_time=0.4)
        out_lbl = Text("Print output", font_size=16, color=MUTED).next_to(lst, DOWN, buff=0.45, aligned_edge=LEFT).shift(LEFT * 0.4)
        out_box = Rectangle(width=4.4, height=0.9, color=MUTED, stroke_width=1).next_to(out_lbl, DOWN, buff=0.08, aligned_edge=LEFT)
        out_txt = mono(" ", fs=16).move_to(out_box)
        counter = mono(f"step 1 / {len(steps)}", fs=14, color=MUTED).next_to(out_box, DOWN, buff=0.2, aligned_edge=LEFT)
        self.play(FadeIn(out_lbl), FadeIn(out_box), FadeIn(counter), run_time=0.3)
        arrow = Arrow(LEFT * 0.5, ORIGIN, buff=0, color=OK, stroke_width=5, max_tip_length_to_length_ratio=0.5)
        cw, lh = lst._unit()
        first = steps[0]
        arrow.move_to(lst.pos(first["line"] or 1, 1) + LEFT * 0.75)
        mem = tutor_frames(first)
        self.play(FadeIn(arrow), FadeIn(mem), run_time=0.4)
        rt = 0.32 if fast else 0.45
        shown = ""
        for i, st in enumerate(steps[1:], start=2):
            new_mem = tutor_frames(st)
            anims = [Transform(mem, new_mem), Transform(counter, mono(f"step {i} / {len(steps)}  ({st['event']})", fs=14, color=MUTED).move_to(counter, aligned_edge=LEFT))]
            if st["line"]:
                col = ERR if st["event"] in ("return", "exception") else OK
                anims.append(arrow.animate.move_to(lst.pos(st["line"], 1) + LEFT * 0.75).set_color(col))
            outs = st["stdout"].strip()
            if outs and outs != shown:
                shown = outs
                new_out = mono(" ".join(outs.split()), fs=18, color=OK).move_to(out_box)
                anims.append(Transform(out_txt, new_out))
                self.add(out_txt)
            self.play(*anims, run_time=rt)
        self.wait(0.4)
        return lst, mem

    # ═════════════════════════════════════════════════════════════ CHAPTER 7
    def ch07_errors(self):
        self.slide("ch07", "Every error and where it is raised")
        self.clear()
        self.title("7 · Errors — what, where, and the real message")
        rows = [
            ("stage", "error", "raised in (main.py)", "message"),
            ("lexer", "IndentationError", "Lexer._handle_indentation", C.run(C.example("errors/lex_bad_dedent.py")).strip()),
            ("lexer", "SyntaxError", "Lexer._read_operator", C.run(C.example("errors/lex_bad_char.py")).strip()),
            ("parser", "SyntaxError", "Parser._expect / _err", C.run(C.example("errors/parse_missing_colon.py")).strip()),
            ("semantic", "'return' outside", "(no pass) → InternalError", C.run(C.example("errors/sem_return_outside.py")).strip()),
            ("runtime", "NameError", "Environment.get", C.run(C.example("errors/rt_name_error.py")).strip()),
            ("runtime", "TypeError", "_apply_binop", C.run(C.example("errors/rt_type_error_add.py")).strip()),
            ("runtime", "TypeError", "_eval_Call (arity)", C.run(C.example("errors/rt_type_error_arity.py")).strip()),
            ("runtime", "RecursionError", "host Python stack", C.run(C.example("errors/rt_recursion.py")).strip()),
            ("runtime", "ZeroDivisionError", "_apply_binop (// %)", "unreachable: MAP has no / // %"),
        ]
        grid = VGroup()
        xs = [-6.8, -5.3, -3.2, -0.2]
        for r, row in enumerate(rows):
            for c, cell in enumerate(row):
                col = ACCENT if r == 0 else [MUTED, ERR, NAME, TEXT][c]
                t = mono(cell, fs=13 if r else 14, color=col)
                if c == 3:
                    fit(t, 6.9, 1)
                t.move_to([xs[c], 2.3 - r * 0.47, 0], aligned_edge=LEFT)
                grid.add(t)
        self.play(FadeIn(grid[:4]))
        for r in range(1, len(rows)):
            self.play(FadeIn(grid[4 * r:4 * r + 4], shift=RIGHT * 0.2), run_time=0.3)
        cap = caption("PyError.plain() → 'Kind: message [line N]'. Tokens carry a column, but the error reports only the line.")
        self.play(FadeIn(cap))

        self.slide("ch07", "An error travels up the call stack")
        self.clear()
        self.title("NameError raised 4 frames deep, caught in main()")
        src = C.example("errors/rt_name_error_deep.py")
        steps = C.trace(src)
        last = steps[-1]
        lst = Listing(src, fs=16, numbers=True).to_corner(UL, buff=0.6).shift(DOWN * 0.7 + RIGHT * 0.3)
        self.play(FadeIn(lst))
        hl = lst.line_box(3, color=ERR)
        self.play(FadeIn(hl))
        frames = VGroup()
        for i, fr in enumerate(last["frames"]):
            vs = ", ".join(f"{k}={v if not isinstance(v, dict) else '→fn'}" for k, v in fr["vars"].items())
            b = card(f"{fr['name']}   {vs}", color=NAME if i else MUTED, w=4.8, h=0.5, fs=15)
            b.move_to([3.2, 2.2 - i * 0.62, 0])
            frames.add(b)
        for b in frames:
            self.play(FadeIn(b, shift=DOWN * 0.15), run_time=0.25)
        exc = card("NameError: name 'm' is not defined", color=ERR, w=4.6, h=0.5, fs=15)
        exc.move_to(frames[-1].get_center() + DOWN * 0.75)
        self.play(FadeIn(exc, scale=1.2), Flash(frames[-1].get_center(), color=ERR))
        for b in reversed(list(frames[1:])):
            self.play(exc.animate.move_to(b.get_center() + DOWN * 0.05), b[0].animate.set_stroke(ERR), run_time=0.35)
            self.play(FadeOut(b, shift=RIGHT * 0.3), run_time=0.25)
        handler = code_card("except (LexerError, ParseError, PyRuntimeError) as e:\n    print(e)\n    sys.exit(1)",
                            fs=14, title="main()", ref="main.py:1883")
        handler.move_to([3.2, -1.2, 0])
        self.play(FadeIn(handler))
        self.play(exc.animate.move_to(handler.get_center() + UP * 1.45), FadeOut(frames[0]), run_time=0.5)
        out = mono(last["error"], fs=14, color=ERR).next_to(lst, DOWN, buff=0.6, aligned_edge=LEFT)
        fit(out, 6.5, 1)
        self.play(Write(out))
        cp = C.python314_error(src)
        cpt = mono("CPython 3.14 adds a traceback + ^ carets:  " + cp, fs=12, color=MUTED).next_to(out, DOWN, buff=0.2, aligned_edge=LEFT)
        fit(cpt, 4.8, 1)
        self.play(FadeIn(cpt))
        cap = caption("The exception unwinds every _eval_Call (no except clause catches PyRuntimeError) until main() prints it.")
        self.play(FadeIn(cap))

    # ═════════════════════════════════════════════════════════════ CHAPTER 8
    def ch08_builtins(self):
        self.slide("ch08", "BUILTINS seeded into globals")
        self.clear()
        self.title("8 · Builtins — native functions in the global scope")
        names = list(C.M.BUILTINS)
        dict_box = code_card("BUILTINS = {\n" + "\n".join(f'    "{n}": _builtin_{n},' for n in names[:7]) + "\n    ...\n}",
                             fs=13, title="main.py:1209", ref="14 entries")
        dict_box.to_corner(UL, buff=0.5).shift(DOWN * 0.7)
        self.play(FadeIn(dict_box))
        init = code_card("def __init__(self):\n    self.globals = Environment()\n    for name, fn in BUILTINS.items():\n        self.globals.set(name, fn)",
                         fs=14, title="Interpreter.__init__", ref="main.py:1284")
        init.next_to(dict_box, DOWN, buff=0.45, aligned_edge=LEFT)
        self.play(FadeIn(init))
        glob = Rectangle(width=5.6, height=4.6, color=NAME, stroke_width=2).move_to(RIGHT * 3.4 + DOWN * 0.3)
        gl = Text("Global Environment", font_size=18, color=NAME).next_to(glob, UP, buff=0.1)
        self.play(Create(glob), FadeIn(gl))
        chips_ = VGroup()
        for n in names:
            used = n in ("print", "range")
            chips_.add(chip(n, OK if used else MUTED, h=0.42, fs=16, w=1.6))
        chips_.arrange_in_grid(rows=5, cols=3, buff=0.18).move_to(glob)
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.5) for c in chips_], lag_ratio=0.1), run_time=2)
        cap = caption("All 14 get registered; MAP programs use only print and range (green).")
        self.play(FadeIn(cap))

        self.slide("ch08", "Crossing into native code")
        self.clear()
        self.title("print(...) and range(...) cross into host Python")
        border = DashedLine(UP * 2.6, DOWN * 3.0, color=MUTED).move_to(RIGHT * 1.6 + DOWN * 0.2)
        lm = Text("MAP world (AST + Environment)", font_size=16, color=NAME).move_to(LEFT * 3 + UP * 2.4)
        rn = Text("host Python (native)", font_size=16, color=KEYWORD).move_to(RIGHT * 4.4 + UP * 2.4)
        self.play(Create(border), FadeIn(lm), FadeIn(rn))
        flow1 = [
            (LEFT * 3 + UP * 1.5, "Call(Name print, [Call fib_rec 4])", NAME),
            (LEFT * 3 + UP * 0.6, "callee = env.get('print')", NAME),
            (LEFT * 3 + DOWN * 0.3, "callable(callee) and not PyFunction", NAME),
            (RIGHT * 4.4 + DOWN * 0.3, "_builtin_print(args)", KEYWORD),
            (RIGHT * 4.4 + DOWN * 1.2, "print(*(_ep_str(a) ...))", KEYWORD),
        ]
        prev = None
        for p, t, col in flow1:
            c = card(t, color=col, w=4.8, h=0.5, fs=15).move_to(p)
            self.play(FadeIn(c), *( [GrowArrow(Arrow(prev.get_bottom() if abs(prev.get_x()-c.get_x())<0.1 else prev.get_right(), c.get_top() if abs(prev.get_x()-c.get_x())<0.1 else c.get_left(), buff=0.05, color=MUTED, stroke_width=2.5))] if prev else []), run_time=0.45)
            prev = c
        out = mono("stdout:  " + C.run(C.PROGRAM_A).strip(), fs=20, color=OK).move_to(RIGHT * 4.4 + DOWN * 2.1)
        self.play(Write(out))
        rng = code_card("def _builtin_range(args):\n    ...\n    return list(range(*iargs))   # eager list",
                        fs=13, title="range(2, n + 1) with n = 6", ref="main.py:1090")
        rng.move_to(LEFT * 3 + DOWN * 1.8)
        lst_val = mono("→ [" + ", ".join(map(str, range(2, 7))) + "]", fs=18, color=NUMBER).next_to(rng, DOWN, buff=0.15)
        self.play(FadeIn(rng))
        self.play(Write(lst_val))
        cap = caption("A builtin is just a host function stored in the global Environment like any other value.")
        self.play(FadeIn(cap))

    # ═════════════════════════════════════════════════════════════ CHAPTER 9
    def ch09_bytecode(self):
        for name, src, func in (("A", C.PROGRAM_A, "fib_rec"), ("B", C.PROGRAM_B, "fib_iter")):
            self.slide("ch09", f"CPython bytecode for Program {name}")
            self.clear()
            self.title(f"9 · Bonus — CPython 3.14 bytecode for {func}")
            instrs = parse_dis(C.dis_text(src, func))
            fs = 14 if len(instrs) < 22 else 12
            rows = VGroup()
            for ins in instrs:
                t = mono(f"{(ins['label'] or ''):>3} {ins['op']:<34} {ins['arg']}", fs=fs,
                         color=KEYWORD if "JUMP" in ins["op"] or "FOR_ITER" in ins["op"] else TEXT)
                rows.add(t)
            rows.arrange(DOWN, aligned_edge=LEFT, buff=0.06)
            fit(rows, 6.2, 5.5)
            rows.to_edge(RIGHT, buff=2.0).shift(DOWN * 0.15)
            # left: AST statement nodes, one per source line
            stmts = stmt_nodes(C.parse(src).body[0])
            palette = [NAME, OK, OP, ACCENT, KEYWORD, ERR, MUTED, COMMENT, LOGO_BLUE, LOGO_YELLOW]
            cards = VGroup()
            for i, (line, lab) in enumerate(stmts):
                cards.add(card(f"L{line}  {lab}", color=palette[i % len(palette)], w=4.8, h=0.42, fs=14))
            cards.arrange(DOWN, buff=0.12, aligned_edge=LEFT)
            fit(cards, 5.2, 6.0)
            cards.to_edge(LEFT, buff=0.5).shift(DOWN * 0.3)
            self.play(FadeIn(cards), FadeIn(rows, lag_ratio=0.02), run_time=1)
            for i, (line, lab) in enumerate(stmts):
                idxs = [k for k, ins in enumerate(instrs) if ins["line"] == line]
                if not idxs:
                    continue
                col = palette[i % len(palette)]
                grp = VGroup(*[rows[k] for k in idxs])
                br = SurroundingRectangle(grp, color=col, buff=0.04, stroke_width=2)
                link = Line(cards[i].get_right(), br.get_left(), color=col, stroke_width=1.5)
                self.play(Create(br), Create(link), Indicate(cards[i], color=col, scale_factor=1.03), run_time=0.5)
                self.play(FadeOut(link), run_time=0.15)
            # jump arrows
            labels = {ins["label"]: k for k, ins in enumerate(instrs) if ins["label"]}
            x_edge = rows.get_right()[0] + 0.15
            lane = 0
            for k, ins in enumerate(instrs):
                m = re.search(r"to (L\d+)", ins["arg"])
                if m and m.group(1) in labels:
                    tgt = labels[m.group(1)]
                    x = x_edge + 0.25 + 0.3 * lane
                    lane += 1
                    y0, y1 = rows[k].get_y(), rows[tgt].get_y()
                    path = VGroup(
                        Line([x_edge, y0, 0], [x, y0, 0]),
                        Line([x, y0, 0], [x, y1, 0]),
                        Arrow([x, y1, 0], [x_edge - 0.05, y1, 0], buff=0, max_tip_length_to_length_ratio=0.15,
                              tip_length=0.12),
                    ).set_color(KEYWORD).set_stroke(width=2.5)
                    tag = mono(("forward " if tgt > k else "back ") + m.group(1), fs=11, color=KEYWORD)
                    tag.move_to([x + 0.08, y0, 0], aligned_edge=LEFT)
                    self.play(Create(path), FadeIn(tag), Indicate(rows[k], color=KEYWORD), run_time=0.8)
            cap = caption("Bytecode differs between Python versions (this is 3.14). Orange = jumps: that is how CPython does if/for.")
            self.play(FadeIn(cap))

        self.slide("ch09", "MAP uses no jumps")
        self.clear()
        self.title("MAP is a tree-walker: no jumps anywhere")
        a = code_card("def _exec_If(self, node, env):\n    if _ep_bool(self._eval(node.test, env)):\n        self._exec_stmts(node.body, env)\n    elif node.orelse:\n        self._exec_stmts(node.orelse, env)",
                      fs=15, title="if → a host-language if", ref="main.py:1340")
        b = code_card("def _exec_For(self, node, env):\n    iterable = self._eval(node.iter, env)\n    for item in iterable:\n        env.set(node.target, item)\n        self._exec_stmts(node.body, env)",
                      fs=15, title="for → a host-language for", ref="main.py:1350 (trimmed)")
        VGroup(a, b).arrange(DOWN, buff=0.5).move_to(LEFT * 2.6 + DOWN * 0.2)
        self.play(FadeIn(a), FadeIn(b))
        vs = VGroup(mono("CPython", fs=20, color=KEYWORD), mono("POP_JUMP_IF_FALSE", fs=16, color=KEYWORD),
                    mono("FOR_ITER / JUMP_BACKWARD", fs=16, color=KEYWORD), mono("vs", fs=18, color=MUTED),
                    mono("MAP", fs=20, color=OK), mono("Python's own if / for", fs=16, color=OK),
                    mono("+ recursion on the AST", fs=16, color=OK)).arrange(DOWN, buff=0.18)
        vs.move_to(RIGHT * 4.3)
        self.play(LaggedStart(*[FadeIn(v) for v in vs], lag_ratio=0.15))
        cap = caption("The host language's control flow IS our control flow. Only a compiler (CPython, the llvm/ port) needs jumps.")
        self.play(FadeIn(cap))

    # ════════════════════════════════════════════════════════════ CHAPTER 10
    def ch10_out_of_scope(self):
        self.slide("ch10", "Out of scope")
        self.clear()
        self.title("10 · Not in MAP")
        items = ["standard library (math, os, sys, ...)", "import / modules", "classes and objects",
                 "OS APIs: files, sockets, processes", "strings, lists, dicts, floats (in the full ports, not in MAP)",
                 "try / except, while, break, / // %"]
        g = VGroup(*[VGroup(mono("✗", fs=22, color=ERR), Text(s, font_size=22, color=MUTED)).arrange(RIGHT, buff=0.3)
                     for s in items]).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(UP * 0.2)
        self.play(LaggedStart(*[FadeIn(i, shift=RIGHT * 0.2) for i in g], lag_ratio=0.2))
        end = Text("ints · bools · None · = · + - < <= == · if/else · def/return · for range · print",
                   font_size=20, color=OK).to_edge(DOWN, buff=0.6)
        self.play(Write(end))
        self.wait(0.5)


# ---------- chapter 9 helpers ----------

def parse_dis(text):
    out, line = [], None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("Disassembly"):
            continue
        parts = raw.split()
        if parts[0].isdigit():
            line = int(parts.pop(0))
        label = None
        if parts and re.fullmatch(r"L\d+:", parts[0]):
            label = parts.pop(0)[:-1]
        op = parts.pop(0)
        out.append({"line": line, "label": label, "op": op, "arg": " ".join(parts)})
    return out


def stmt_nodes(fn):
    """[(line, label)] for each statement of a FuncDef, nested blocks included."""
    M = C.M
    res = [(fn.line, f"FuncDef {fn.name}")]

    def walk(stmts):
        for s in stmts:
            if isinstance(s, M.If):
                res.append((s.line, f"If ({C._label(s.test)})"))
                walk(s.body)
                walk(s.orelse)
            elif isinstance(s, M.For):
                res.append((s.line, f"For {s.target} in Call range"))
                walk(s.body)
            elif isinstance(s, M.Return):
                res.append((s.line, f"Return ({C._label(s.value)})"))
            elif isinstance(s, M.Assign):
                res.append((s.line, f"Assign {s.target} ({C._label(s.value)})"))
            else:
                res.append((s.line, C._label(s)))

    walk(fn.body)
    return res
