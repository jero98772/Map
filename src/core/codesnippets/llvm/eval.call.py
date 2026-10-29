    def ex_Call(self, n):
        if not isinstance(n.func, Name):
            raise PyRuntimeError(
                "TypeError: the LLVM backend can only call named functions", n.line
            )
        name = n.func.id
        if name in self.locals or (
            name in self.global_names and name not in self.be.funcs
        ):
            raise PyRuntimeError(
                f"TypeError: cannot call variable '{name}' (only named functions are callable)",
                n.line,
            )

        # user-defined function -> direct native call
        if name in self.be.funcs:
            mangled, arity = self.be.funcs[name]
            vals = [self.ex(a) for a in n.args]
            if len(vals) != arity:
                self.raise_rt(
                    f"TypeError: {name}() takes {arity} argument(s) but {len(vals)} given",
                    n.line,
                )
                return NONE_C
            res = self.b.call(self.get_fn(mangled, arity), vals)
            self.check()
            return res

        # builtin -> runtime call
        if name in BUILTINS:
            vals = [self.ex(a) for a in n.args]
            out = self._tmp()
            self.call_rt(
                "rt_call_builtin",
                [
                    self.be.builtin_id(name),
                    c32(len(vals)),
                    self._pack_args(vals),
                    out,
                    c32(n.line),
                ],
            )
            self.check()
            return self.b.load(out)

        self.raise_rt(f"NameError: name '{name}' is not defined", n.line)
        return NONE_C
