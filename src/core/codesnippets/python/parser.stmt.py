    def _stmt(self) -> ASTNode:
        self._skip_newlines()
        if self._match(TT.DEF):
            return self._func_def()
        if self._match(TT.IF):
            return self._if_stmt()
        if self._match(TT.WHILE):
            return self._while_stmt()
        if self._match(TT.FOR):
            return self._for_stmt()
        return self._simple_stmt()

    # ── Simple statements ────────────────────────────────────────────────────

    def _simple_stmt(self) -> ASTNode:
        if self._check(TT.RETURN):
            self._advance()
            node = self._return_stmt()
        elif self._check(TT.NAME) and self._peek(1).type == TT.EQUAL:
            node = self._assign()
        elif self._check(TT.NAME) and self._peek(1).type in (
            TT.PLUSEQUAL,
            TT.MINEQUAL,
            TT.STAREQUAL,
            TT.SLASHEQUAL,
        ):
            node = self._aug_assign()
        else:
            node = ExprStmt(expr=self._expr(), line=self._cur().line)

        if self._check(TT.NEWLINE):
            self._advance()
        elif not self._check(TT.EOF, TT.DEDENT):
            self._err(
                f"expected newline after statement, got {self._cur().type.value!r}"
            )
        return node
