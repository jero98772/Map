from manim import *

# ---------- palette: Docs/theme-light.md — "Blueprint textbook" ----------
NAME = "#1d5fbf"  # identifiers (--hl-name)
OP = "#16357a"  # operators (--hl-type)
TEXT = "#10213f"  # body text
MUTED = "#4a5a78"  # captions, sub-labels
COMMENT = "#6a7a94"  # grid lines, box strokes (--hl-comment)
ACCENT = "#16357a"  # structural / headers (--accent)
HILITE = "#9a6700"  # cursor, current step
BG_CARD = "#ffffff"
OK = "#2f7d3e"
MONO = "Monospace"

config.background_color = "#f5f8fc"

TOKEN_W = 1.3
TERM_COLOR = {"id": NAME, "+": OP, "$": MUTED}


def token_boxes(tokens, x=0, y=0.5):
    """Build a centered row of boxes (one per token) with index labels
    underneath. Returns (full_group, boxes_vgroup)."""
    n = len(tokens)
    boxes = VGroup(
        *[
            Rectangle(width=TOKEN_W, height=0.7, stroke_color=COMMENT).shift(
                RIGHT * (i - (n - 1) / 2) * TOKEN_W
            )
            for i in range(n)
        ]
    )
    boxes.move_to(RIGHT * x + UP * y)

    labels = VGroup(
        *[
            Text(tok, font=MONO, font_size=30, color=TERM_COLOR.get(tok, TEXT)).move_to(
                boxes[i].get_center()
            )
            for i, tok in enumerate(tokens)
        ]
    )

    idx = VGroup(
        *[
            Text(str(i), font_size=18, color=MUTED).next_to(boxes[i], DOWN, buff=0.15)
            for i in range(n)
        ]
    )

    group = VGroup(boxes, labels, idx)
    return group, boxes


def boundary_point(boxes, pos, lift=0.7):
    """Point above the boundary BEFORE token `pos` (pos may equal
    len(boxes), meaning 'end of input')."""
    if pos < len(boxes):
        return boxes[pos].get_left() + UP * lift
    else:
        return boxes[-1].get_right() + UP * lift


def make_cursor():
    tri = Triangle(color=HILITE, fill_color=HILITE, fill_opacity=1).scale(0.15)
    tri.rotate(PI)  # point downward
    return tri


def make_table_grid():
    """Builds the LL(1) parsing table as a grid of rectangles + text.
    Returns (group, cell_rects) where cell_rects[(nonterm, term)] gives the
    Rectangle mobject for that data cell, so it can be highlighted later."""
    nonterms = ["E", "E'", "T"]
    terms = ["id", "+", "$"]
    cell_w, cell_h = 1.35, 0.55

    entries = {
        ("E", "id"): "E→TE'",
        ("E'", "+"): "E'→+TE'",
        ("E'", "$"): "E'→ε",
        ("T", "id"): "T→id",
    }

    # header row: blank corner + one cell per terminal
    header_cells = VGroup(Rectangle(width=cell_w, height=cell_h, stroke_color=COMMENT))
    for t in terms:
        rect = Rectangle(width=cell_w, height=cell_h, stroke_color=COMMENT)
        txt = Text(t, font=MONO, font_size=22, color=TERM_COLOR[t]).move_to(rect)
        header_cells.add(VGroup(rect, txt))
    header_cells.arrange(RIGHT, buff=0)

    rows = VGroup()
    cell_rects = {}
    for nt in nonterms:
        row = VGroup()
        label_rect = Rectangle(width=cell_w, height=cell_h, stroke_color=COMMENT)
        label_txt = Text(nt, font=MONO, font_size=22, color=ACCENT).move_to(label_rect)
        row.add(VGroup(label_rect, label_txt))
        for t in terms:
            rect = Rectangle(width=cell_w, height=cell_h, stroke_color=COMMENT)
            content = entries.get((nt, t), "")
            txt = Text(content, font=MONO, font_size=16, color=TEXT).move_to(rect)
            row.add(VGroup(rect, txt))
            cell_rects[(nt, t)] = rect
        row.arrange(RIGHT, buff=0)
        rows.add(row)
    rows.arrange(DOWN, buff=0)
    header_cells.next_to(rows, UP, buff=0)

    full = VGroup(header_cells, rows)
    return full, cell_rects


class LL1Trace(Scene):
    """Trace parsing 'id + id' with the table-driven LL(1) algorithm,
    grammar: E -> T E' | E' -> + T E' / eps | T -> id."""

    def construct(self):
        tokens = ["id", "+", "id"]

        title = Text("LL(1) Table-Driven Parsing:  id + id", font_size=32, color=TEXT).to_edge(UP)
        self.play(Write(title))

        grammar = (
            VGroup(
                Text("E  →  T E'", font=MONO, font_size=24, color=TEXT),
                Text("E' →  + T E'  |  ε", font=MONO, font_size=24, color=TEXT),
                Text("T  →  id", font=MONO, font_size=24, color=TEXT),
            )
            .arrange(DOWN, aligned_edge=LEFT)
            .to_corner(UL)
            .shift(DOWN * 0.9)
        )
        self.play(FadeIn(grammar))

        table, cell_rects = make_table_grid()
        table.scale(0.9).to_corner(UR).shift(DOWN * 0.7)
        self.play(FadeIn(table))

        # sits left of the table so the two never overlap
        chargroup, boxes = token_boxes(tokens, x=-0.9, y=1.1)
        self.play(FadeIn(chargroup))

        cursor = make_cursor()
        cursor.move_to(boundary_point(boxes, 0))
        self.play(FadeIn(cursor))

        caption = Text("", font_size=26).to_edge(DOWN, buff=1.7)
        self.add(caption)

        stack_label = Text("parse stack (grows downward)", font_size=18, color=MUTED)
        stack_label.to_edge(LEFT, buff=0.6).shift(DOWN * 0.6)
        self.add(stack_label)
        stack = VGroup()

        # ---- helpers ----
        def set_caption(txt, color=TEXT):
            new = Text(txt, font_size=26, color=color).move_to(caption.get_center())
            self.play(Transform(caption, new), run_time=0.6)

        def push(name):
            rect = Rectangle(
                width=1.6, height=0.5, stroke_color=ACCENT, fill_color=BG_CARD, fill_opacity=1
            )
            lbl = Text(name, font=MONO, font_size=20, color=TERM_COLOR.get(name, ACCENT)).move_to(rect)
            frame = VGroup(rect, lbl)
            if len(stack) == 0:
                frame.next_to(stack_label, DOWN, buff=0.25, aligned_edge=LEFT)
            else:
                frame.next_to(stack[-1], DOWN, buff=0.1, aligned_edge=LEFT)
            stack.add(frame)
            self.play(FadeIn(frame), run_time=0.3)

        def pop():
            frame = stack[-1]
            stack.remove(frame)
            self.play(FadeOut(frame), run_time=0.25)

        def move_cursor(pos):
            self.play(cursor.animate.move_to(boundary_point(boxes, pos)), run_time=0.4)

        def consume(i):
            self.play(boxes[i].animate.set_fill(OK, opacity=0.3), run_time=0.3)
            move_cursor(i + 1)

        def flash_cell(nt, t):
            rect = cell_rects[(nt, t)]
            self.play(rect.animate.set_fill(HILITE, opacity=0.5), run_time=0.4)
            self.play(rect.animate.set_fill(opacity=0), run_time=0.4)

        # ---------------- trace ----------------
        set_caption("Push start symbol E onto the stack")
        push("E")

        set_caption("Top = E, lookahead = id  →  M[E, id] = E → T E'")
        flash_cell("E", "id")
        pop()
        push("E'")
        push("T")

        set_caption("Top = T, lookahead = id  →  M[T, id] = T → id")
        flash_cell("T", "id")
        pop()
        push("id")

        set_caption("Top = 'id' matches input 'id'  →  match & advance")
        consume(0)
        pop()

        set_caption("Top = E', lookahead = +  →  M[E', +] = E' → + T E'")
        flash_cell("E'", "+")
        pop()
        push("E'")
        push("T")
        push("+")

        set_caption("Top = '+' matches input '+'  →  match & advance")
        consume(1)
        pop()

        set_caption("Top = T, lookahead = id  →  M[T, id] = T → id")
        flash_cell("T", "id")
        pop()
        push("id")

        set_caption("Top = 'id' matches input 'id'  →  match & advance")
        consume(2)
        pop()

        set_caption("Top = E', lookahead = $  →  M[E', $] = E' → ε")
        flash_cell("E'", "$")
        pop()

        set_caption("Stack empty & input = $  →  ACCEPT ✅", color=OK)
        result = Text('Input "id + id" accepted!', font_size=32, color=OK)
        result.next_to(chargroup, DOWN, buff=3.4)
        result.set_x(0)
        self.play(Write(result))
        self.wait(2)
