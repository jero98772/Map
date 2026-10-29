    def _exec_Return(self, node: Return, env: Environment):
        value = self._eval(node.value, env) if node.value is not None else None
        raise ReturnSignal(value)

    def _exec_If(self, node: If, env: Environment):
        if _ep_bool(self._eval(node.test, env)):
            self._exec_stmts(node.body, env)
        elif node.orelse:
            self._exec_stmts(node.orelse, env)

    def _exec_While(self, node: While, env: Environment):
        while _ep_bool(self._eval(node.test, env)):
            self._exec_stmts(node.body, env)

    def _exec_For(self, node: For, env: Environment):
        iterable = self._eval(node.iter, env)
        if not isinstance(iterable, (list, str)):
            raise PyRuntimeError(
                f"TypeError: '{_type_name(iterable)}' object is not iterable", node.line
            )
        for item in iterable:
            env.set(node.target, item)
            self._exec_stmts(node.body, env)
