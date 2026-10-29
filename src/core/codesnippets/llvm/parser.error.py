    def _expect(self, tt: TT, msg: str = "") -> Token:
        if not self._check(tt):
            got = self._cur()
            desc = (
                msg or f"expected '{tt.value}', got '{got.type.value}' ({got.value!r})"
            )
            raise ParseError(f"SyntaxError: {desc}", got.line)
        return self._advance()

    def _err(self, msg: str):
        raise ParseError(f"SyntaxError: {msg}", self._cur().line)
