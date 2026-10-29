    fn next_token(&mut self) -> Result<(), PyError> {
        if self.at_line_start && self.paren_depth == 0 {
            return self.handle_indentation();
        }

        let ch = self.cur();

        if ch == ' ' || ch == '\t' {
            self.advance();
            return Ok(());
        }
        if ch == '\n' {
            let (ln, cl) = self.here();
            self.advance();
            if self.paren_depth == 0 {
                self.tokens.push(Token::new(TokKind::Newline, ln, cl));
                self.at_line_start = true;
            }
            return Ok(());
        }
        if ch == '\r' {
            self.advance();
            return Ok(());
        }
        if ch == '#' {
            while self.cur() != '\n' && self.cur() != '\0' {
                self.advance();
            }
            return Ok(());
        }
        if ch == '"' || ch == '\'' {
            return self.read_string();
        }
        if ch.is_ascii_digit() {
            return self.read_number();
        }
        if ch.is_alphabetic() || ch == '_' {
            return self.read_name();
        }
        self.read_operator()
    }
