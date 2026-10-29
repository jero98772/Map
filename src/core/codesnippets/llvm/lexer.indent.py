    def _handle_indentation(self):
        indent = 0
        while self._cur() in (" ", "\t"):
            indent = (indent // 8 + 1) * 8 if self._cur() == "\t" else indent + 1
            self._advance()
        ch = self._cur()
        if ch in ("\n", "\r", "\0") or ch == "#":
            if ch == "#":
                while self._cur() not in ("\n", "\0"):
                    self._advance()
            if self._cur() == "\n":
                self._advance()
            return
        self.at_line_start = False
        current = self.indent_stack[-1]
        if indent > current:
            self.indent_stack.append(indent)
            self.tokens.append(Token(TT.INDENT, indent, self.line, 1))
        elif indent < current:
            while len(self.indent_stack) > 1 and self.indent_stack[-1] > indent:
                self.indent_stack.pop()
                self.tokens.append(Token(TT.DEDENT, indent, self.line, 1))
            if self.indent_stack[-1] != indent:
                self._err(
                    "IndentationError: unindent does not match any outer indentation level"
                )
