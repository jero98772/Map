    def _next_token(self):
        if self.at_line_start and self.paren_depth == 0:
            self._handle_indentation()
            return
        ch = self._cur()
        if ch in (" ", "\t"):
            self._advance()
        elif ch == "\n":
            ln, cl = self._here()
            self._advance()
            if self.paren_depth == 0:
                self.tokens.append(Token(TT.NEWLINE, "\n", ln, cl))
                self.at_line_start = True
        elif ch == "\r":
            self._advance()
        elif ch == "#":
            while self._cur() not in ("\n", "\0"):
                self._advance()
        elif ch in ('"', "'"):
            self._read_string()
        elif ch.isdigit():
            self._read_number()
        elif ch.isalpha() or ch == "_":
            self._read_name()
        else:
            self._read_operator()
