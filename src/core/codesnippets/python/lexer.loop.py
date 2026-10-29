    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            self._next_token()
        self._close_all_indents()
        if self.tokens and self.tokens[-1].type not in (TT.NEWLINE, TT.DEDENT):
            self.tokens.append(Token(TT.NEWLINE, "\n", self.line, self.col))
        self.tokens.append(Token(TT.EOF, None, self.line, self.col))
        return self.tokens
