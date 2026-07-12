from manim import *

# ---------- palette ----------
KEYWORD = "#FF7A5C"  # def / return
NAME = "#4DABF7"  # identifiers
NUMBER = "#69DB7C"  # numeric literals
OP = "#FFD43B"  # operators
PUNCT = "#ADB5BD"  # punctuation
ACCENT = "#B983FF"  # structural / headers
BG_CARD = "#20242C"

config.background_color = "#14171C"


def chip(label, color, sub=None, w=None, h=0.62):
    """A small rounded rectangle token chip with a label (and optional sub-label)."""
    txt = Text(label, font="Monospace", font_size=26, color=WHITE, weight=BOLD)
    width = w if w else max(txt.width + 0.5, 0.9)
    box = RoundedRectangle(
        corner_radius=0.1,
        width=width,
        height=h,
        fill_color=color,
        fill_opacity=0.22,
        stroke_color=color,
        stroke_width=2.5,
    )
    txt.move_to(box.get_center())
    grp = VGroup(box, txt)
    if sub:
        sub_txt = Text(sub, font="Monospace", font_size=14, color=color)
        sub_txt.next_to(box, DOWN, buff=0.08)
        grp.add(sub_txt)
    return grp


def card(text, color=ACCENT, w=4.6, h=0.65):
    box = RoundedRectangle(
        corner_radius=0.08,
        width=w,
        height=h,
        fill_color=BG_CARD,
        fill_opacity=1,
        stroke_color=color,
        stroke_width=2.5,
    )
    txt = Text(text, font="Monospace", font_size=24, color=color, weight=BOLD)
    txt.move_to(box)
    return VGroup(box, txt)


def chapter_title(scene, text):
    title = Text(text, font_size=34, color=ACCENT, weight=BOLD)
    title.to_edge(UP, buff=0.35)
    line = (
        Line(LEFT, RIGHT, color=ACCENT, stroke_width=1.5).match_width(title).scale(1.4)
    )
    line.next_to(title, DOWN, buff=0.12)
    scene.play(FadeIn(title, shift=DOWN * 0.2), Create(line), run_time=0.6)
    return VGroup(title, line)


class PythonExecutionJourney(Scene):
    def construct(self):
        self.intro()
        self.stage_source()
        self.stage_tokenize()
        self.stage_parse()
        self.stage_ast()
        self.stage_semantic()
        self.stage_bytecode()
        self.stage_vm()
        self.stage_memory()
        self.stage_recap()

    # ---------------------------------------------------------- SCENE CLEAR
    def clear_scene(self, keep=None, run_time=0.5):
        """Fade out EVERY mobject currently on screen except anything in `keep`.
        This guarantees no artifact from one stage can bleed into the next,
        regardless of whether that stage remembered to fade it out itself."""
        keep = keep or []
        keep_ids = set()
        for k in keep:
            for m in k.get_family():
                keep_ids.add(id(m))
        to_fade = [m for m in self.mobjects if id(m) not in keep_ids]
        if to_fade:
            self.play(*[FadeOut(m) for m in to_fade], run_time=run_time)

    # ---------------------------------------------------------------- INTRO
    def intro(self):
        title = Text("How Python Really Runs Your Code", font_size=48, weight=BOLD)
        title.set_color_by_gradient(NAME, ACCENT, NUMBER)
        sub = Text(
            "def add(a, b):  return a + b", font="Monospace", font_size=28, color=GRAY_B
        )
        sub.next_to(title, DOWN, buff=0.5)
        self.play(FadeIn(title, scale=1.15), run_time=1.0)
        self.play(FadeIn(sub, shift=UP * 0.2), run_time=0.7)
        self.wait(0.8)
        self.clear_scene()

    # ------------------------------------------------------------ 1. SOURCE
    def stage_source(self):
        head = chapter_title(self, "1 · Source Code")

        code_str = "def add(a, b):\n    return a + b\n\nprint(add(5, 3))"
        code = Code(
            code_string=code_str,
            language="python",
            formatter_style="monokai",
            background="window",
            add_line_numbers=True,
        )
        code.scale(1.05)
        code.move_to(ORIGIN)

        self.play(FadeIn(code, shift=UP * 0.3), run_time=1.2)
        self.wait(0.6)

        self.play(code.animate.scale(0.55).to_edge(UP, buff=1.15), run_time=0.6)
        self.wait(0.3)
        self.clear_scene()

    # -------------------------------------------------------- 2. TOKENIZE
    def stage_tokenize(self):
        head = chapter_title(self, "2 · Tokenization")

        # tokens grouped by the actual source line they came from, so the
        # layout mirrors the code structure instead of an arbitrary grid.
        lines_spec = [
            (
                1,
                [
                    ("def", KEYWORD),
                    ("add", NAME),
                    ("(", PUNCT),
                    ("a", NAME),
                    (",", PUNCT),
                    ("b", NAME),
                    (")", PUNCT),
                    (":", PUNCT),
                ],
            ),
            (2, [("return", KEYWORD), ("a", NAME), ("+", OP), ("b", NAME)]),
            (
                4,
                [
                    ("print", NAME),
                    ("(", PUNCT),
                    ("add", NAME),
                    ("(", PUNCT),
                    ("5", NUMBER),
                    (",", PUNCT),
                    ("3", NUMBER),
                    (")", PUNCT),
                    (")", PUNCT),
                ],
            ),
        ]

        rows = VGroup()
        for line_no, toks in lines_spec:
            row_chips = VGroup(*[chip(t, c, h=0.56) for t, c in toks])
            row_chips.arrange(RIGHT, buff=0.16)
            row_chips.scale(0.72)
            num_lbl = Text(str(line_no), font="Monospace", font_size=20, color=GRAY_D)
            row = VGroup(num_lbl, row_chips)
            row.arrange(RIGHT, buff=0.3)
            rows.add(row)

        rows.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        rows.move_to(ORIGIN).shift(UP * 0.1)

        gutter = Line(
            rows.get_left() + LEFT * 0.15 + UP * 0.35,
            rows.get_left() + LEFT * 0.15 + DOWN * (rows.height + 0.1),
            color=GRAY_E,
            stroke_width=1.5,
        )

        self.play(FadeIn(gutter), run_time=0.3)
        for row in rows:
            num_lbl, row_chips = row
            self.play(FadeIn(num_lbl, shift=RIGHT * 0.1), run_time=0.2)
            self.play(
                LaggedStart(
                    *[FadeIn(c, shift=UP * 0.5) for c in row_chips],
                    lag_ratio=0.12,
                    run_time=0.9
                )
            )
            self.wait(0.1)
        self.wait(0.3)

        legend = (
            VGroup(
                self._legend_dot("keyword", KEYWORD),
                self._legend_dot("name", NAME),
                self._legend_dot("number", NUMBER),
                self._legend_dot("operator", OP),
                self._legend_dot("punctuation", PUNCT),
            )
            .arrange(RIGHT, buff=0.55)
            .scale(0.8)
        )
        legend.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(legend, shift=UP * 0.15), run_time=0.6)
        self.wait(0.8)

        self.clear_scene()

    def _legend_dot(self, label, color):
        dot = Dot(color=color, radius=0.09)
        txt = Text(label, font_size=20, color=GRAY_B)
        txt.next_to(dot, RIGHT, buff=0.15)
        return VGroup(dot, txt)

    # ---------------------------------------------------------- 3. PARSER
    def stage_parse(self):
        head = chapter_title(self, "3 · PEG Parser")

        rule = Text(
            "function_def := 'def' NAME '(' parameters ')' ':' suite",
            font="Monospace",
            font_size=22,
            t2c={"function_def": KEYWORD, "parameters": ACCENT, "suite": NUMBER},
        )
        rule.to_edge(UP, buff=1.1)
        self.play(FadeIn(rule, shift=DOWN * 0.1), run_time=0.5)

        line1 = VGroup(
            *[
                chip(t, c)
                for t, c in [
                    ("def", KEYWORD),
                    ("add", NAME),
                    ("(", PUNCT),
                    ("a", NAME),
                    (",", PUNCT),
                    ("b", NAME),
                    (")", PUNCT),
                    (":", PUNCT),
                ]
            ]
        )
        line1.arrange(RIGHT, buff=0.15).scale(0.78)

        line2 = VGroup(
            *[
                chip(t, c)
                for t, c in [("return", KEYWORD), ("a", NAME), ("+", OP), ("b", NAME)]
            ]
        )
        line2.arrange(RIGHT, buff=0.15).scale(0.78)

        lines = VGroup(line1, line2).arrange(DOWN, buff=0.65, aligned_edge=LEFT)
        lines.next_to(rule, DOWN, buff=0.6)

        self.play(FadeIn(lines, shift=UP * 0.2), run_time=0.7)
        self.wait(0.2)

        # robotic arm = a small triangle that swoops down and groups tokens
        arm = Triangle(color=ACCENT, fill_opacity=1).scale(0.15).rotate(PI)
        arm.move_to(line1.get_top() + UP * 0.45)
        self.play(FadeIn(arm), run_time=0.25)

        # step 1: match the parameter list  ( a , b )
        params_box = SurroundingRectangle(
            line1[2:7], color=ACCENT, buff=0.1, corner_radius=0.08
        )
        params_lbl = Text("parameters", font_size=18, color=ACCENT, weight=BOLD)
        params_lbl.next_to(params_box, DOWN, buff=0.15)
        self.play(
            arm.animate.move_to(line1[2:7].get_top() + UP * 0.3),
            Create(params_box),
            run_time=0.6,
        )
        self.play(FadeIn(params_lbl, shift=UP * 0.1), run_time=0.35)
        self.wait(0.2)

        # step 2: match the binary expression  a + b
        expr_box = SurroundingRectangle(
            line2[1:4], color=OP, buff=0.1, corner_radius=0.08
        )
        expr_lbl = Text("BinaryExpression", font_size=18, color=OP, weight=BOLD)
        expr_lbl.next_to(expr_box, DOWN, buff=0.15)
        self.play(
            arm.animate.move_to(line2[1:4].get_top() + UP * 0.3),
            Create(expr_box),
            run_time=0.6,
        )
        self.play(FadeIn(expr_lbl, shift=UP * 0.1), run_time=0.35)
        self.wait(0.2)

        # step 3: RETURN + BinaryExpression -> return_stmt
        return_stmt_box = SurroundingRectangle(
            VGroup(line2[0], expr_box, expr_lbl),
            color=NUMBER,
            buff=0.16,
            corner_radius=0.1,
        )
        return_stmt_lbl = Text("return_stmt", font_size=18, color=NUMBER, weight=BOLD)
        return_stmt_lbl.next_to(return_stmt_box, RIGHT, buff=0.25)
        self.play(Create(return_stmt_box), run_time=0.5)
        self.play(FadeIn(return_stmt_lbl, shift=LEFT * 0.1), run_time=0.35)
        self.play(FadeOut(arm), run_time=0.25)
        self.wait(0.3)
        self.play(FadeOut(rule), run_time=0.3)

        # step 4: wrap everything into the final nested structure
        suite_box = SurroundingRectangle(
            VGroup(line2, return_stmt_box, return_stmt_lbl),
            color=NUMBER,
            buff=0.22,
            corner_radius=0.12,
        )
        suite_lbl = Text("suite", font_size=18, color=NUMBER, weight=BOLD)
        suite_lbl.next_to(suite_box, DOWN, buff=0.15)
        self.play(Create(suite_box), FadeIn(suite_lbl, shift=UP * 0.1), run_time=0.6)

        func_box = SurroundingRectangle(
            VGroup(line1, params_box, params_lbl, suite_box, suite_lbl),
            color=KEYWORD,
            buff=0.35,
            corner_radius=0.15,
        )
        func_lbl = Text("function_definition", font_size=22, color=KEYWORD, weight=BOLD)
        func_lbl.next_to(func_box, UP, buff=0.2)
        self.play(Create(func_box), FadeIn(func_lbl, shift=DOWN * 0.1), run_time=0.7)
        self.wait(1.0)

        self.clear_scene()

    # ------------------------------------------------------------- 4. AST
    def stage_ast(self):
        head = chapter_title(self, "4 · Abstract Syntax Tree")

        def node(label, color=ACCENT, fs=22):
            txt = Text(label, font_size=fs, color=WHITE, weight=BOLD)
            box = RoundedRectangle(
                corner_radius=0.09,
                width=txt.width + 0.5,
                height=0.55,
                fill_color=color,
                fill_opacity=0.85,
                stroke_color=color,
                stroke_width=2,
            )
            txt.move_to(box)
            return VGroup(box, txt)

        # ---- leaves
        n_a1 = node("a", NAME, 18)
        n_b1 = node("b", NAME, 18)
        n_a2 = node("Name(a)", NAME, 16)
        n_b2 = node("Name(b)", NAME, 16)
        n_5 = node("5", NUMBER, 18)
        n_3 = node("3", NUMBER, 18)

        n_args = node("arguments", ACCENT, 16)
        n_binop = node("BinOp(+)", OP, 16)
        n_return = node("Return", KEYWORD, 16)
        n_funcdef = node("FunctionDef(add)", KEYWORD, 18)

        n_add_call = node("Call(add)", NAME, 16)
        n_print_call = node("Call(print)", NAME, 16)
        n_expr = node("Expr", ACCENT, 16)
        n_module = node("Module", ACCENT, 22)

        # ---- layout (hand-placed coordinates)
        n_module.move_to(UP * 3.0)
        n_funcdef.move_to(UP * 1.9 + LEFT * 3.2)
        n_expr.move_to(UP * 1.9 + RIGHT * 3.2)

        n_args.move_to(UP * 0.7 + LEFT * 4.6)
        n_return.move_to(UP * 0.7 + LEFT * 2.0)
        n_a1.move_to(DOWN * 0.5 + LEFT * 5.3)
        n_b1.move_to(DOWN * 0.5 + LEFT * 4.0)
        n_binop.move_to(DOWN * 0.5 + LEFT * 2.0)
        n_a2.move_to(DOWN * 1.7 + LEFT * 2.9)
        n_b2.move_to(DOWN * 1.7 + LEFT * 1.1)

        n_print_call.move_to(DOWN * 0.5 + RIGHT * 3.2)
        n_add_call.move_to(DOWN * 1.7 + RIGHT * 3.2)
        n_5.move_to(DOWN * 2.9 + RIGHT * 2.3)
        n_3.move_to(DOWN * 2.9 + RIGHT * 4.1)

        def edge(a, b):
            return Line(a.get_bottom(), b.get_top(), color=GRAY_D, stroke_width=2)

        whole = VGroup(
            n_module,
            n_funcdef,
            n_expr,
            n_args,
            n_return,
            n_a1,
            n_b1,
            n_binop,
            n_a2,
            n_b2,
            n_print_call,
            n_add_call,
            n_5,
            n_3,
        )
        whole.scale(0.68).move_to(ORIGIN).shift(DOWN * 0.2)

        # leaves fly up first, then parents appear, matching "children before parents"
        leaves = VGroup(n_a1, n_b1, n_a2, n_b2, n_5, n_3)
        self.play(
            LaggedStart(
                *[FadeIn(l, shift=UP * 0.6) for l in leaves],
                lag_ratio=0.15,
                run_time=1.3
            )
        )

        mids = VGroup(n_args, n_binop, n_add_call)
        mid_edges = VGroup(
            edge(n_args, n_a1),
            edge(n_args, n_b1),
            edge(n_binop, n_a2),
            edge(n_binop, n_b2),
            edge(n_add_call, n_5),
            edge(n_add_call, n_3),
        )
        self.play(
            LaggedStart(*[Create(e) for e in mid_edges], lag_ratio=0.1, run_time=0.8),
            LaggedStart(
                *[FadeIn(m, shift=UP * 0.4) for m in mids], lag_ratio=0.15, run_time=0.8
            ),
        )

        upper = VGroup(n_return, n_print_call)
        upper_edges = VGroup(edge(n_return, n_binop), edge(n_print_call, n_add_call))
        self.play(
            LaggedStart(*[Create(e) for e in upper_edges], lag_ratio=0.1, run_time=0.6),
            LaggedStart(
                *[FadeIn(u, shift=UP * 0.4) for u in upper], lag_ratio=0.2, run_time=0.6
            ),
        )

        top = VGroup(n_funcdef, n_expr)
        top_edges = VGroup(
            edge(n_funcdef, n_args),
            edge(n_funcdef, n_return),
            edge(n_expr, n_print_call),
        )
        self.play(
            LaggedStart(*[Create(e) for e in top_edges], lag_ratio=0.1, run_time=0.6),
            LaggedStart(
                *[FadeIn(t, shift=UP * 0.4) for t in top], lag_ratio=0.2, run_time=0.6
            ),
        )

        root_edges = VGroup(edge(n_module, n_funcdef), edge(n_module, n_expr))
        self.play(Create(root_edges), FadeIn(n_module, shift=UP * 0.4), run_time=0.7)

        self.wait(1.0)
        self.ast_group = VGroup(whole, mid_edges, upper_edges, top_edges, root_edges)
        self.clear_scene(keep=[self.ast_group])

    # -------------------------------------------------------- 5. SEMANTIC
    def stage_semantic(self):
        head = chapter_title(self, "5 · Semantic Analysis")

        self.play(
            self.ast_group.animate.scale(0.72).to_edge(LEFT, buff=0.6), run_time=0.8
        )

        table_title = Text("Symbol Table", font_size=24, color=ACCENT, weight=BOLD)
        rows = VGroup(
            self._row("add", "Function", KEYWORD),
            self._row("a", "Parameter", NAME),
            self._row("b", "Parameter", NAME),
        ).arrange(DOWN, buff=0.28, aligned_edge=LEFT)

        table_box = SurroundingRectangle(
            rows, color=GRAY_B, buff=0.3, corner_radius=0.1
        )
        table = VGroup(table_box, rows)
        table_title.next_to(table_box, UP, buff=0.2)
        group = VGroup(table_title, table).to_edge(RIGHT, buff=0.9).shift(UP * 0.8)

        self.play(
            FadeIn(table_title, shift=DOWN * 0.1), Create(table_box), run_time=0.5
        )
        for r in rows:
            self.play(FadeIn(r, shift=LEFT * 0.2), run_time=0.4)
        self.wait(0.3)

        checks_title = Text("Verifying: return a + b", font_size=22, color=GRAY_B)
        checks_title.next_to(table, DOWN, buff=0.55).align_to(table, LEFT)
        checks = VGroup(
            self._check("a exists"),
            self._check("b exists"),
            self._check('"+" is valid'),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        checks.next_to(checks_title, DOWN, buff=0.25).align_to(checks_title, LEFT)

        self.play(FadeIn(checks_title, shift=UP * 0.1), run_time=0.4)
        for c in checks:
            self.play(Write(c[0]), FadeIn(c[1], scale=1.3), run_time=0.45)
        self.wait(0.9)

        self.clear_scene()

    def _row(self, name, kind, color):
        n = Text(name, font="Monospace", font_size=22, color=color, weight=BOLD)
        arrow = Text("→", font_size=22, color=GRAY_B)
        k = Text(kind, font_size=22, color=WHITE)
        return VGroup(n, arrow, k).arrange(RIGHT, buff=0.2)

    def _check(self, label):
        txt = Text(label, font="Monospace", font_size=22, color=WHITE)
        mark = Text("✔", font_size=24, color=NUMBER, weight=BOLD)
        mark.next_to(txt, RIGHT, buff=0.25)
        return VGroup(txt, mark)

    # -------------------------------------------------------- 6. BYTECODE
    def stage_bytecode(self):
        head = chapter_title(self, "6 · Bytecode Generation")

        add_instrs = ["LOAD_FAST a", "LOAD_FAST b", "BINARY_OP +", "RETURN_VALUE"]
        main_instrs = [
            "LOAD_GLOBAL print",
            "LOAD_GLOBAL add",
            "LOAD_CONST 5",
            "LOAD_CONST 3",
            "CALL add",
            "CALL print",
        ]

        add_label = Text(
            "add(a, b):", font="Monospace", font_size=22, color=KEYWORD, weight=BOLD
        )
        add_cards = VGroup(*[card(i, ACCENT, w=3.6) for i in add_instrs])
        add_cards.arrange(DOWN, buff=0.18)
        add_group = VGroup(add_label, add_cards).arrange(DOWN, buff=0.25)
        add_group.to_edge(LEFT, buff=1.0).shift(UP * 0.1)

        main_label = Text(
            "__main__:", font="Monospace", font_size=22, color=KEYWORD, weight=BOLD
        )
        main_cards = VGroup(*[card(i, NAME, w=4.2) for i in main_instrs])
        main_cards.arrange(DOWN, buff=0.18)
        main_group = VGroup(main_label, main_cards).arrange(DOWN, buff=0.25)
        main_group.to_edge(RIGHT, buff=1.0).shift(UP * 0.1)

        self.play(FadeIn(add_label, shift=DOWN * 0.1), run_time=0.4)
        self.play(
            LaggedStart(
                *[FadeIn(c, shift=RIGHT * 0.3) for c in add_cards],
                lag_ratio=0.2,
                run_time=1.4
            )
        )
        self.play(FadeIn(main_label, shift=DOWN * 0.1), run_time=0.4)
        self.play(
            LaggedStart(
                *[FadeIn(c, shift=LEFT * 0.3) for c in main_cards],
                lag_ratio=0.2,
                run_time=1.8
            )
        )
        self.wait(0.8)

        self.add_group = add_group
        self.main_group = main_group
        self.add_cards = add_cards
        self.main_cards = main_cards
        self.clear_scene(keep=[self.add_group, self.main_group])

    # -------------------------------------------------------------- 7. VM
    def stage_vm(self):
        head = chapter_title(self, "7 · Python Virtual Machine")

        # Only __main__'s instruction list stays on screen throughout; add()'s
        # bytecode is hidden until we actually step inside that call, which
        # avoids the two lists ever competing for the same vertical space.
        self.play(
            self.main_group.animate.scale(0.7).to_corner(UL, buff=0.4),
            FadeOut(self.add_group),
            run_time=0.6,
        )

        stack_title = Text("Evaluation Stack", font_size=24, color=ACCENT, weight=BOLD)
        stack_title.to_edge(RIGHT, buff=1.4).shift(UP * 3.0)
        floor = Line(RIGHT * 1.8, RIGHT * 6.6, color=GRAY_D, stroke_width=3)
        floor.next_to(stack_title, DOWN, buff=3.4)
        self.play(FadeIn(stack_title), Create(floor), run_time=0.5)

        stack = []  # list of mobjects, bottom to top

        def push(value, color, base_x):
            box = card(str(value), color, w=1.3, h=0.6)
            if stack:
                box.next_to(stack[-1], UP, buff=0.12)
            else:
                box.move_to(floor.get_center() + UP * 0.42)
            box.move_to([base_x, box.get_center()[1], 0])
            stack.append(box)
            self.play(FadeIn(box, shift=UP * 0.5), run_time=0.45)

        def pop():
            box = stack.pop()
            self.play(FadeOut(box, shift=DOWN * 0.4), run_time=0.35)
            return box

        def highlight(cards, i):
            return cards[i][0].animate.set_stroke(width=5).set_fill(opacity=0.15)

        def unhighlight(cards, i):
            return cards[i][0].animate.set_stroke(width=2.5).set_fill(opacity=0)

        base_x = 4.3

        # __main__: LOAD_GLOBAL print, LOAD_GLOBAL add  -> represented as name chips
        self.play(highlight(self.main_cards, 0))
        gp = chip("print", NAME, w=1.3)
        gp.move_to([base_x, floor.get_center()[1] + 0.42, 0])
        self.play(FadeIn(gp, shift=UP * 0.4), run_time=0.4)
        stack.append(gp)
        self.play(unhighlight(self.main_cards, 0))

        self.play(highlight(self.main_cards, 1))
        ga = chip("add", KEYWORD, w=1.3)
        ga.next_to(stack[-1], UP, buff=0.12)
        self.play(FadeIn(ga, shift=UP * 0.4), run_time=0.4)
        stack.append(ga)
        self.play(unhighlight(self.main_cards, 1))

        self.play(highlight(self.main_cards, 2))
        push(5, NUMBER, base_x)
        self.play(unhighlight(self.main_cards, 2))

        self.play(highlight(self.main_cards, 3))
        push(3, NUMBER, base_x)
        self.play(unhighlight(self.main_cards, 3))

        # CALL add  -> pop 3, 5, "add" name; open a new frame; run add's bytecode
        self.play(highlight(self.main_cards, 4))
        arg_b = pop()
        arg_a = pop()
        callee = pop()
        self.wait(0.15)

        frame_box = RoundedRectangle(
            corner_radius=0.1,
            width=3.0,
            height=1.7,
            stroke_color=ACCENT,
            stroke_width=3,
            fill_color=BG_CARD,
            fill_opacity=1,
        )
        frame_lbl = Text("Frame: add()", font_size=20, color=ACCENT, weight=BOLD)
        frame_lbl.next_to(frame_box, UP, buff=0.1)
        frame_vars = VGroup(
            Text("a = 5", font="Monospace", font_size=20, color=NAME),
            Text("b = 3", font="Monospace", font_size=20, color=NAME),
        ).arrange(DOWN, buff=0.2)
        frame_vars.move_to(frame_box)
        frame = VGroup(frame_box, frame_lbl, frame_vars)
        frame.move_to(LEFT * 1.0 + DOWN * 0.3)
        self.play(FadeIn(frame, scale=0.9), run_time=0.6)
        self.wait(0.2)

        # bring add()'s bytecode back in, docked just under its frame
        small_add = self.add_group.copy().scale(0.5)
        small_add.next_to(frame, DOWN, buff=0.45)
        self.play(FadeIn(small_add, shift=UP * 0.2), run_time=0.5)
        small_cards = small_add[1]
        self.wait(0.2)

        # run add's instructions against a mini local stack near the frame
        local_stack = []
        local_base_x = frame.get_center()[0] + 2.3

        def local_push(value, color):
            box = card(str(value), color, w=1.1, h=0.55)
            if local_stack:
                box.next_to(local_stack[-1], UP, buff=0.1)
            else:
                box.move_to([local_base_x, frame_box.get_bottom()[1] + 0.4, 0])
            local_stack.append(box)
            self.play(FadeIn(box, shift=UP * 0.3), run_time=0.4)

        def local_pop():
            box = local_stack.pop()
            self.play(FadeOut(box, shift=DOWN * 0.3), run_time=0.3)
            return box

        self.play(highlight(small_cards, 0))
        local_push(5, NAME)
        self.play(unhighlight(small_cards, 0))

        self.play(highlight(small_cards, 1))
        local_push(3, NAME)
        self.play(unhighlight(small_cards, 1))

        self.play(highlight(small_cards, 2))
        v2 = local_pop()
        v1 = local_pop()
        result = card("8", NUMBER, w=1.1, h=0.55)
        result.move_to([local_base_x, frame_box.get_bottom()[1] + 0.4, 0])
        self.play(FadeIn(result, shift=UP * 0.3), run_time=0.5)
        local_stack.append(result)
        self.play(unhighlight(small_cards, 2))

        self.play(highlight(small_cards, 3))
        self.wait(0.2)
        # frame destroyed, only 8 escapes back to caller's stack
        ret_val = local_stack.pop()
        self.play(
            FadeOut(frame),
            FadeOut(small_add),
            ret_val.animate.move_to([base_x, floor.get_center()[1] + 0.42, 0]),
            run_time=0.7,
        )
        stack.append(ret_val)
        self.wait(0.2)
        self.play(unhighlight(self.main_cards, 4))

        # CALL print -> pop 8 and "print", show console output
        self.play(highlight(self.main_cards, 5))
        arg = pop()
        printer = pop()
        console = Text(
            ">>> 8", font="Monospace", font_size=34, color=NUMBER, weight=BOLD
        )
        console.to_edge(DOWN, buff=0.7)
        self.play(FadeIn(console, shift=UP * 0.3), run_time=0.7)
        self.play(unhighlight(self.main_cards, 5))
        self.wait(1.0)

        self.clear_scene()

    # ---------------------------------------------------------- 8. MEMORY
    def stage_memory(self):
        head = chapter_title(self, "8 · Memory & Return")

        frame_box = RoundedRectangle(
            corner_radius=0.12,
            width=3.6,
            height=2.0,
            stroke_color=ACCENT,
            stroke_width=3,
            fill_color=BG_CARD,
            fill_opacity=1,
        )
        frame_lbl = Text("Frame #1", font_size=26, color=ACCENT, weight=BOLD)
        frame_lbl.next_to(frame_box, UP, buff=0.15)
        rows = VGroup(
            Text("a  →  5", font="Monospace", font_size=24, color=NAME),
            Text("b  →  3", font="Monospace", font_size=24, color=NAME),
        ).arrange(DOWN, buff=0.3)
        rows.move_to(frame_box)
        frame = VGroup(frame_box, frame_lbl, rows)
        frame.move_to(ORIGIN)

        self.play(FadeIn(frame, scale=0.9), run_time=0.7)
        self.wait(0.6)

        destroyed = Text("Frame destroyed", font_size=26, color=GRAY_B, slant=ITALIC)
        destroyed.move_to(frame_lbl)
        self.play(
            Transform(frame_lbl, destroyed),
            frame_box.animate.set_stroke(color=GRAY_D),
            rows.animate.set_opacity(0.15),
            run_time=0.6,
        )

        result = card("8", NUMBER, w=1.3, h=0.8)
        result.move_to(frame_box.get_center())
        self.play(FadeIn(result), run_time=0.3)

        target = Text(
            ">>> 8", font="Monospace", font_size=48, color=NUMBER, weight=BOLD
        )
        target.move_to(DOWN * 2.3)

        self.play(
            FadeOut(frame_box),
            FadeOut(frame_lbl),
            FadeOut(rows),
            result.animate.move_to(target.get_center()).scale(1.4),
            run_time=0.9,
        )
        self.play(FadeOut(result), FadeIn(target, scale=1.3), run_time=0.5)
        self.wait(1.0)

        self.clear_scene()

    # ----------------------------------------------------------- 9. RECAP
    def stage_recap(self):
        title = Text("The Full Journey", font_size=36, color=ACCENT, weight=BOLD)
        title.to_edge(UP, buff=0.4)
        self.play(FadeIn(title, shift=DOWN * 0.2), run_time=0.5)

        labels = [
            "Source Code",
            "Tokenizer",
            "PEG Parser",
            "AST Builder",
            "Semantic Analyzer",
            "Bytecode",
            "Python VM",
        ]
        colors = [WHITE, KEYWORD, ACCENT, NUMBER, NAME, OP, KEYWORD]
        boxes = VGroup(*[card(l, c, w=3.6, h=0.55) for l, c in zip(labels, colors)])
        boxes.arrange(DOWN, buff=0.14)
        boxes.scale(0.82)
        boxes.next_to(title, DOWN, buff=0.35)

        arrows = VGroup(
            *[
                Arrow(
                    boxes[i].get_bottom(),
                    boxes[i + 1].get_top(),
                    buff=0.04,
                    stroke_width=2.5,
                    color=GRAY_B,
                    max_tip_length_to_length_ratio=0.25,
                )
                for i in range(len(boxes) - 1)
            ]
        )

        self.play(FadeIn(boxes[0], shift=DOWN * 0.15), run_time=0.35)
        for i in range(1, len(boxes)):
            self.play(
                GrowArrow(arrows[i - 1]),
                FadeIn(boxes[i], shift=DOWN * 0.15),
                run_time=0.35,
            )

        final_arrow = Arrow(
            boxes[-1].get_bottom(),
            boxes[-1].get_bottom() + DOWN * 0.9,
            buff=0.04,
            stroke_width=2.5,
            color=GRAY_B,
            max_tip_length_to_length_ratio=0.25,
        )
        output = Text("8", font="Monospace", font_size=40, color=NUMBER, weight=BOLD)
        output.next_to(final_arrow, DOWN, buff=0.1)
        self.play(GrowArrow(final_arrow), FadeIn(output, scale=1.3), run_time=0.5)
        self.wait(1.4)

        self.clear_scene()
