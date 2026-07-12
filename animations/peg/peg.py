"""
PEG Parser By Hand — Manim animations
======================================

Two scenes:

  PEGTrace      - traces parsing "3+4*2" against:
                    Expr   <- Term (('+' / '-') Term)*
                    Term   <- Factor (('*' / '/') Factor)*
                    Factor <- Number / '(' Expr ')'
                  Shows the call stack growing/shrinking and precedence
                  falling out of call structure (no precedence table needed).

  PEGBacktrack  - shows TRUE backtracking: grammar  Rule <- "ab" / "ac"
                  parsing "ac". The parser tentatively consumes 'a', tries
                  to match 'b', fails, restores the cursor to where it was
                  saved, then retries the second alternative from scratch.

Render with (ManimCE):
    pip install manim --break-system-packages
    manim -pql peg_parser_manim.py PEGTrace
    manim -pql peg_parser_manim.py PEGBacktrack

    (-pql = preview, quality low/fast. Use -pqh for a high quality render.)
"""

from manim import *

CHAR_W = 0.9


def char_boxes(s, y=0.5):
    """Build a centered row of boxes (one per character) with index labels
    underneath. Returns (full_group, boxes_vgroup)."""
    n = len(s)
    boxes = VGroup(
        *[
            Square(side_length=CHAR_W, stroke_color=GREY_B).shift(
                RIGHT * (i - (n - 1) / 2) * CHAR_W
            )
            for i in range(n)
        ]
    )
    boxes.move_to(UP * y)

    labels = VGroup(
        *[
            Text(ch, font_size=36).move_to(boxes[i].get_center())
            for i, ch in enumerate(s)
        ]
    )

    idx = VGroup(
        *[
            Text(str(i), font_size=18, color=GREY).next_to(boxes[i], DOWN, buff=0.15)
            for i in range(n)
        ]
    )

    group = VGroup(boxes, labels, idx)
    return group, boxes


def boundary_point(boxes, pos, lift=0.75):
    """Point above the boundary BEFORE character `pos` (pos may equal
    len(boxes), meaning 'end of string')."""
    if pos < len(boxes):
        return boxes[pos].get_left() + UP * lift + RIGHT * (CHAR_W / 2 - CHAR_W / 2)
    else:
        return boxes[-1].get_right() + UP * lift


def make_cursor():
    tri = Triangle(color=YELLOW, fill_color=YELLOW, fill_opacity=1).scale(0.15)
    tri.rotate(PI)  # point downward
    return tri


class PEGTrace(Scene):
    """Trace parsing '3+4*2', showing precedence come from call structure."""

    def construct(self):
        s = "3+4*2"

        title = Text("PEG Parsing by Hand:  3 + 4 * 2", font_size=32).to_edge(UP)
        self.play(Write(title))

        grammar = (
            VGroup(
                Text("Expr   <- Term (('+' / '-') Term)*", font_size=22),
                Text("Term   <- Factor (('*' / '/') Factor)*", font_size=22),
                Text("Factor <- Number / '(' Expr ')'", font_size=22),
            )
            .arrange(DOWN, aligned_edge=LEFT)
            .to_corner(UL)
            .shift(DOWN * 0.9)
        )
        self.play(FadeIn(grammar))

        chargroup, boxes = char_boxes(s, y=0.9)
        self.play(FadeIn(chargroup))

        cursor = make_cursor()
        cursor.move_to(boundary_point(boxes, 0))
        self.play(FadeIn(cursor))

        caption = Text("", font_size=26).to_edge(DOWN, buff=1.6)
        self.add(caption)

        stack_label = Text("call stack", font_size=20, color=GREY)
        stack_label.to_edge(RIGHT, buff=1.0).shift(UP * 2.6)
        self.add(stack_label)
        stack = VGroup()

        # ---- helpers ----
        def set_caption(txt, color=WHITE):
            new = Text(txt, font_size=26, color=color).move_to(caption.get_center())
            self.play(Transform(caption, new), run_time=0.6)

        def push(name):
            rect = Rectangle(width=2.0, height=0.5, color=BLUE, fill_opacity=0.15)
            lbl = Text(name, font_size=20).move_to(rect)
            frame = VGroup(rect, lbl)
            if len(stack) == 0:
                frame.next_to(stack_label, DOWN, buff=0.25)
            else:
                frame.next_to(stack[-1], DOWN, buff=0.15)
            stack.add(frame)
            self.play(FadeIn(frame), run_time=0.35)

        def pop():
            frame = stack[-1]
            stack.remove(frame)
            self.play(FadeOut(frame), run_time=0.25)

        def move_cursor(pos):
            self.play(cursor.animate.move_to(boundary_point(boxes, pos)), run_time=0.45)

        def consume(i):
            self.play(boxes[i].animate.set_fill(GREEN, opacity=0.4), run_time=0.3)
            move_cursor(i + 1)

        # ---------------- trace ----------------
        set_caption("parse_expr() calls parse_term()")
        push("Expr")
        push("Term")

        set_caption("parse_term() calls parse_factor()")
        push("Factor")

        set_caption("Factor: try Number -> matches '3'")
        consume(0)
        pop()  # Factor -> 3

        set_caption("Term loop: peek '*' -> sees '+', stop (nothing consumed)")
        self.play(Indicate(boxes[1], color=RED), run_time=0.5)

        set_caption("Term returns 3, control back in Expr")
        pop()  # Term -> 3

        set_caption("Expr loop: match '+'")
        consume(1)

        set_caption("Expr calls parse_term() again")
        push("Term")
        push("Factor")

        set_caption("Factor: Number matches '4'")
        consume(2)
        pop()

        set_caption("Term loop: match '*'")
        self.play(boxes[3].animate.set_fill(GREEN, opacity=0.4), run_time=0.3)
        move_cursor(4)
        push("Factor")

        set_caption("Factor: Number matches '2'")
        consume(4)
        pop()

        set_caption("Term computes 4 * 2 = 8")
        pop()  # Term -> 8

        set_caption("Expr computes 3 + 8 = 11")
        pop()  # Expr -> 11

        result = Text("result = 11", font_size=36, color=YELLOW)
        result.next_to(chargroup, DOWN, buff=2.4)
        self.play(Write(result))
        self.wait(2)


class PEGBacktrack(Scene):
    """Genuine backtracking: Rule <- "ab" / "ac", parsing "ac"."""

    def construct(self):
        s = "ac"

        title = Text("PEG Ordered-Choice Backtracking", font_size=32).to_edge(UP)
        self.play(Write(title))

        rule = Text('Rule <- "ab" / "ac"', font_size=28).next_to(title, DOWN, buff=0.5)
        self.play(FadeIn(rule))

        chargroup, boxes = char_boxes(s, y=0.8)
        self.play(FadeIn(chargroup))

        cursor = make_cursor()
        cursor.move_to(boundary_point(boxes, 0))
        self.play(FadeIn(cursor))

        caption = Text("", font_size=26).to_edge(DOWN, buff=2.0)
        self.add(caption)

        pos_label = Text("pos = 0", font_size=22, color=GREY)
        pos_label.next_to(chargroup, DOWN, buff=0.6)
        self.add(pos_label)

        def set_caption(txt, color=WHITE):
            new = Text(txt, font_size=26, color=color).move_to(caption.get_center())
            self.play(Transform(caption, new), run_time=0.6)

        def set_pos(p):
            new = Text(f"pos = {p}", font_size=22, color=GREY).move_to(
                pos_label.get_center()
            )
            self.play(Transform(pos_label, new), run_time=0.3)

        def move_cursor(pos):
            self.play(cursor.animate.move_to(boundary_point(boxes, pos)), run_time=0.4)

        # ---------------- alt 1: "ab" ----------------
        set_caption('Try alt 1: "ab"  ->  save pos = 0')
        saved_marker = Text("saved pos = 0", font_size=20, color=ORANGE)
        saved_marker.next_to(boxes[0], UP, buff=1.0)
        self.play(FadeIn(saved_marker))

        set_caption("Tentatively match 'a' against input[0]")
        self.play(boxes[0].animate.set_fill(ORANGE, opacity=0.5), run_time=0.3)
        move_cursor(1)
        set_pos(1)

        set_caption("Now need 'b' against input[1] = 'c'  ->  FAILS", color=RED)
        self.play(Flash(boxes[1], color=RED, flash_radius=0.6))

        set_caption("Backtrack: restore pos to the SAVED value (0)", color=RED)
        self.play(boxes[0].animate.set_fill(opacity=0), run_time=0.3)
        move_cursor(0)
        set_pos(0)
        self.play(FadeOut(saved_marker))

        # ---------------- alt 2: "ac" ----------------
        set_caption('Ordered choice moves on: try alt 2: "ac"')
        self.wait(0.3)

        set_caption("Match 'a' against input[0]  ->  OK")
        self.play(boxes[0].animate.set_fill(GREEN, opacity=0.4), run_time=0.3)
        move_cursor(1)
        set_pos(1)

        set_caption("Match 'c' against input[1]  ->  OK")
        self.play(boxes[1].animate.set_fill(GREEN, opacity=0.4), run_time=0.3)
        move_cursor(2)
        set_pos(2)

        set_caption('Rule matches: "ac"', color=GREEN)
        result = Text(
            'Rule -> "ac"  (alt 1 was tried and abandoned)', font_size=28, color=YELLOW
        )
        result.next_to(chargroup, DOWN, buff=2.6)
        self.play(Write(result))
        self.wait(2)
