"""
PEG Parser By Hand — Manim animations
======================================

Three scenes:

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

  PEGParseTree  - builds an actual parse tree, node by node, while parsing
                  "print(3+4*2)" against:
                    Call   <- Ident '(' Expr ')'
                    Expr   <- Term (('+' / '-') Term)*
                    Term   <- Factor (('*' / '/') Factor)*
                    Factor <- Number / '(' Expr ')'
                    Ident  <- [a-zA-Z]+
                    Number <- [0-9]+
                  Each tree node appears the instant its rule is called /
                  matches, wired to its parent with an edge, in lock-step
                  with the cursor consuming the input above it.

Render with (ManimCE):
    pip install manim --break-system-packages
    manim -pql peg_parser_manim.py PEGTrace
    manim -pql peg_parser_manim.py PEGBacktrack
    manim -pql peg_parser_manim.py PEGParseTree

    (-pql = preview, quality low/fast. Use -pqh for a high quality render.
     Use "manim -qh -a peg_parser_manim.py" to render every scene at once.)
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


class PEGParseTree(Scene):
    """Build an actual parse tree, node by node, while parsing
    'print(3+4*2)' against:

        Call   <- Ident '(' Expr ')'
        Expr   <- Term (('+' / '-') Term)*
        Term   <- Factor (('*' / '/') Factor)*
        Factor <- Number / '(' Expr ')'
        Ident  <- [a-zA-Z]+
        Number <- [0-9]+

    Every node's (x, y) position is precomputed by hand below (in-order
    leaf placement + parent-is-average-of-children), so the "layout" is
    just a lookup table -- no generic tree-layout algorithm needed.
    """

    # node sizing
    RULE_W, RULE_H = 1.3, 0.55  # Call / Expr / Term / Factor
    LIT_W, LIT_H = 0.8, 0.55  # '(' '+' '*' ')'
    VAL_W, VAL_H = 1.5, 0.75  # Ident/print, Number/3, Number/4, Number/2

    def construct(self):
        s = "print(3+4*2)"

        title = Text("Building a Parse Tree:  print(3+4*2)", font_size=30).to_edge(UP)
        self.play(Write(title))

        grammar = (
            VGroup(
                Text("Call   <- Ident '(' Expr ')'", font_size=20),
                Text("Expr   <- Term (('+' / '-') Term)*", font_size=20),
                Text("Term   <- Factor (('*' / '/') Factor)*", font_size=20),
                Text("Factor <- Number / '(' Expr ')'", font_size=20),
            )
            .arrange(DOWN, aligned_edge=LEFT)
            .next_to(title, DOWN, buff=0.35)
        )
        self.play(FadeIn(grammar))
        self.wait(1)
        self.play(FadeOut(title), FadeOut(grammar))

        # ---- input row, pinned near the top ----
        chargroup, boxes = char_boxes(s, y=3.0)
        self.play(FadeIn(chargroup))

        cursor = make_cursor()
        cursor.move_to(boundary_point(boxes, 0))
        self.play(FadeIn(cursor))

        # ---- running "title" sits directly under the expression; the tree
        # ---- is laid out below THIS, not the expression itself.
        caption = Text("parse Call(): create root node", font_size=26)
        caption.next_to(chargroup, DOWN, buff=0.5)
        self.play(FadeIn(caption))

        def set_caption(txt, color=WHITE):
            new = Text(txt, font_size=26, color=color).move_to(caption.get_center())
            self.play(Transform(caption, new), run_time=0.5)

        def move_cursor(pos):
            self.play(cursor.animate.move_to(boundary_point(boxes, pos)), run_time=0.35)

        def consume(indices):
            anims = [boxes[i].animate.set_fill(GREEN, opacity=0.4) for i in indices]
            self.play(*anims, run_time=0.35)
            move_cursor(indices[-1] + 1)

        # ---- tree node factory: everything is placed at precomputed coords ----
        nodes = {}

        def add_node(key, label, x, y, parent_key, color, w, h):
            rect = RoundedRectangle(
                corner_radius=0.08,
                width=w,
                height=h,
                color=color,
                fill_color=color,
                fill_opacity=0.18,
            )
            txt = Text(label, font_size=20, line_spacing=0.8).move_to(rect.get_center())
            node = VGroup(rect, txt).move_to([x, y, 0])
            nodes[key] = node
            anims = [FadeIn(node, scale=0.85)]
            if parent_key is not None:
                parent = nodes[parent_key]
                edge = Line(
                    parent.get_bottom(), node.get_top(), color=GREY_B, stroke_width=2
                )
                anims.append(Create(edge))
            self.play(*anims, run_time=0.5)

        RW, RH = self.RULE_W, self.RULE_H
        LW, LH = self.LIT_W, self.LIT_H
        VW, VH = self.VAL_W, self.VAL_H

        # 5 tree depths, stacked below the title with a fixed gap between
        # each row (title -> Call -> {Ident,(,Expr,)} -> {Term,+,Term} ->
        # {Factor,Factor,*,Factor} -> {Number,Number,Number})
        GAP = 0.9
        TOP = caption.get_bottom()[1] - 0.55
        LEVELS = [TOP - i * GAP for i in range(5)]

        # ================= build the tree, in true recursive-descent order =================

        add_node("Call", "Call", -1.07, LEVELS[0], None, BLUE_D, RW, RH)

        set_caption("Call: parse Ident -> matches 'print'")
        add_node("Ident", "Ident\nprint", -5.6, LEVELS[1], "Call", ORANGE, VW, VH)
        consume(range(0, 5))

        set_caption("Call: match literal '('")
        add_node("LitOpen", "'('", -4.0, LEVELS[1], "Call", GREY_B, LW, LH)
        consume([5])

        set_caption("Call: parse Expr (the argument)")
        add_node("Expr", "Expr", -0.27, LEVELS[1], "Call", BLUE_D, RW, RH)

        set_caption("Expr: parse first Term")
        add_node("Term_A", "Term", -2.4, LEVELS[2], "Expr", BLUE_D, RW, RH)

        set_caption("Term: parse Factor")
        add_node("Factor_A", "Factor", -2.4, LEVELS[3], "Term_A", BLUE_D, RW, RH)

        set_caption("Factor: Number matches '3'")
        add_node("Num3", "Number\n3", -2.4, LEVELS[4], "Factor_A", YELLOW, VW, VH)
        consume([6])

        set_caption("Term loop: peek '*' -> sees '+', stop (nothing consumed)")
        self.play(Indicate(boxes[7], color=RED), run_time=0.5)

        set_caption("Expr loop: match '+'")
        add_node("LitPlus", "'+'", -0.8, LEVELS[2], "Expr", GREY_B, LW, LH)
        consume([7])

        set_caption("Expr: parse second Term")
        add_node("Term_B", "Term", 2.4, LEVELS[2], "Expr", BLUE_D, RW, RH)

        set_caption("Term: parse Factor")
        add_node("Factor_B1", "Factor", 0.8, LEVELS[3], "Term_B", BLUE_D, RW, RH)

        set_caption("Factor: Number matches '4'")
        add_node("Num4", "Number\n4", 0.8, LEVELS[4], "Factor_B1", YELLOW, VW, VH)
        consume([8])

        set_caption("Term loop: match '*'")
        add_node("LitStar", "'*'", 2.4, LEVELS[3], "Term_B", GREY_B, LW, LH)
        consume([9])

        set_caption("Term: parse another Factor")
        add_node("Factor_B2", "Factor", 4.0, LEVELS[3], "Term_B", BLUE_D, RW, RH)

        set_caption("Factor: Number matches '2'")
        add_node("Num2", "Number\n2", 4.0, LEVELS[4], "Factor_B2", YELLOW, VW, VH)
        consume([10])

        set_caption("Call: match literal ')'")
        add_node("LitClose", "')'", 5.6, LEVELS[1], "Call", GREY_B, LW, LH)
        consume([11])

        # ================= evaluate bottom-up =================
        set_caption("Parse complete -- evaluate the tree bottom-up", color=GREEN)
        self.wait(0.4)

        new_call_label = Text("Call\n(prints 11)", font_size=18, line_spacing=0.8)
        new_call_label.move_to(nodes["Call"][1].get_center())
        self.play(
            Transform(nodes["Call"][1], new_call_label),
            nodes["Call"][0].animate.set_fill(GREEN, opacity=0.25),
        )

        set_caption("3 + 4*2 = 11   ->   print(11)", color=YELLOW)
        self.wait(2)
