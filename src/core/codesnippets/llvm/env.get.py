def _scan(stmts):
    """
    Collect (assigned names, augmented names, nested FuncDefs) of a statement list,
    without descending into function bodies.
    """
    assigned, aug, defs = set(), set(), []

    def walk(ss):
        for s in ss:
            if isinstance(s, Assign):
                assigned.add(s.target)
            elif isinstance(s, AugAssign):
                aug.add(s.target)
            elif isinstance(s, For):
                assigned.add(s.target)
                walk(s.body)
            elif isinstance(s, While):
                walk(s.body)
            elif isinstance(s, If):
                walk(s.body)
                walk(s.orelse)
            elif isinstance(s, FuncDef):
                defs.append(s)

    walk(stmts)
    return assigned, aug, defs

    def var_ptr(self, name):
        if name in self.locals:
            return self.locals[name]
        return self.be.slot_ptr(self, name)

    def load_checked(self, ptr, name, line):
        v = self.b.load(ptr)
        bad = self.b.icmp_signed("==", self.tag(v), c32(T_UNDEF))
        err, ok = self._new("undef"), self._new("defined")
        self.b.cbranch(bad, err, ok)
        self.b.position_at_end(err)
        self.call_rt(
            "rt_raise",
            [
                self.be.str_handle(self, f"NameError: name '{name}' is not defined"),
                c32(line),
            ],
        )
        self.b.branch(self.unwind())
        self.b.position_at_end(ok)
        return v
