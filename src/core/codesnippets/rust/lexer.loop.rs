    pub fn tokenize(mut self) -> Result<Vec<Token>, PyError> {
        while self.pos < self.src.len() {
            self.next_token()?;
        }
        self.close_all_indents();
        let needs_newline = !matches!(
            self.tokens.last().map(|t| &t.kind),
            Some(TokKind::Newline) | Some(TokKind::Dedent)
        );
        if needs_newline {
            self.tokens.push(Token::new(TokKind::Newline, self.line, self.col));
        }
        self.tokens.push(Token::new(TokKind::Eof, self.line, self.col));
        Ok(self.tokens)
    }
