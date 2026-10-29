    def st_If(self, n):
        cond = self.truthy(self.ex(n.test))
        then, end = self._new("then"), self._new("endif")
        els = self._new("else") if n.orelse else end
        self.b.cbranch(cond, then, els)
        self.b.position_at_end(then)
        self.stmts(n.body)
        if not self.b.block.is_terminated:
            self.b.branch(end)
        if n.orelse:
            self.b.position_at_end(els)
            self.stmts(n.orelse)
            if not self.b.block.is_terminated:
                self.b.branch(end)
        self.b.position_at_end(end)

    def _for_range(self, n):
        """`for i in range(...)` -> plain native counter loop (no list, no runtime calls)."""
        b = self.b
        vals = [self.ex(a) for a in n.iter.args]
        all_int = ir.Constant(I1, 1)
        for v in vals:
            all_int = b.and_(all_int, b.icmp_signed("==", self.tag(v), c32(T_INT)))
        bad, good = self._new("rbad"), self._new("rok")
        b.cbranch(all_int, good, bad)
        b.position_at_end(bad)
        self.call_rt(
            "rt_raise",
            [
                self.be.str_handle(
                    self, "TypeError: range() arguments must be integers"
                ),
                c32(n.line),
            ],
        )
        b.branch(self.unwind())
        b.position_at_end(good)

        pays = [self.pay(v) for v in vals]
        start, stop, step = (
            (c64(0), pays[0], c64(1))
            if len(pays) == 1
            else (pays[0], pays[1], c64(1))
            if len(pays) == 2
            else tuple(pays)
        )
        if len(pays) == 3:
            zero, okb = self._new("rzero"), self._new("rstep")
            b.cbranch(b.icmp_signed("==", step, c64(0)), zero, okb)
            b.position_at_end(zero)
            self.call_rt(
                "rt_raise",
                [
                    self.be.str_handle(
                        self, "ValueError: range() arg 3 must not be zero"
                    ),
                    c32(n.line),
                ],
            )
            b.branch(self.unwind())
            b.position_at_end(okb)

        idx = self.eb.alloca(I64)
        b.store(start, idx)
        cond_b, body, end = self._new("rcond"), self._new("rbody"), self._new("rend")
        b.branch(cond_b)
        b.position_at_end(cond_b)
        i = b.load(idx)
        c = b.select(
            b.icmp_signed(">", step, c64(0)),
            b.icmp_signed("<", i, stop),
            b.icmp_signed(">", i, stop),
        )
        b.cbranch(c, body, end)
        b.position_at_end(body)
        b.store(self.mk(T_INT, b.load(idx)), self.var_ptr(n.target))
        self.stmts(n.body)
        if not self.b.block.is_terminated:
            self.b.store(self.b.add(self.b.load(idx), step), idx)
            self.b.branch(cond_b)
        self.b.position_at_end(end)
