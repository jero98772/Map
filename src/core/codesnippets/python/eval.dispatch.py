    def _exec_stmts(self, stmts: List[ASTNode], env: Environment):
        for stmt in stmts:
            self._exec(stmt, env)

    def _exec(self, node: ASTNode, env: Environment):
        name = type(node).__name__
        method = getattr(self, f"_exec_{name}", None)
        if method is None:
            raise PyRuntimeError(
                f"InternalError: no exec handler for {name}", node.line
            )
        method(node, env)
