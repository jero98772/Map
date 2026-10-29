    def _eval_Call(self, node: Call, env: Environment) -> Any:
        callee = self._eval(node.func, env)
        args = [self._eval(a, env) for a in node.args]

        if callable(callee) and not isinstance(callee, PyFunction):
            return callee(args)

        if isinstance(callee, PyFunction):
            fn = callee.node
            arity = len(fn.params)
            if len(args) != arity:
                raise PyRuntimeError(
                    f"TypeError: {fn.name}() takes {arity} argument(s) but {len(args)} given",
                    node.line,
                )
            call_env = Environment(parent=callee.closure)
            for param, val in zip(fn.params, args):
                call_env.set(param, val)
            result = None
            try:
                self._exec_stmts(fn.body, call_env)
            except ReturnSignal as ret:
                result = ret.value
            return result

        raise PyRuntimeError(
            f"TypeError: '{_type_name(callee)}' object is not callable", node.line
        )
