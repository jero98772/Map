    def _comparison(self) -> ASTNode:
        node = self._sum()
        while self._check(
            TT.EQEQUAL, TT.NOTEQUAL, TT.LESS, TT.LESSEQUAL, TT.GREATER, TT.GREATEREQUAL
        ):
            op = self._advance()
            right = self._sum()
            node = Compare(left=node, op=op.value, right=right, line=node.line)
        return node

    def _sum(self) -> ASTNode:
        node = self._term()
        while self._check(TT.PLUS, TT.MINUS):
            op = self._advance().value
            right = self._term()
            node = BinOp(left=node, op=op, right=right, line=node.line)
        return node
