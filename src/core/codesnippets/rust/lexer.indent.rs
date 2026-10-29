    fn handle_indentation(&mut self) -> Result<(), PyError> {
        let mut indent = 0usize;
        while self.cur() == ' ' || self.cur() == '\t' {
            if self.cur() == '\t' {
                indent = (indent / 8 + 1) * 8;
            } else {
                indent += 1;
            }
            self.advance();
        }

        let ch = self.cur();
        // blank or comment line — skip entirely
        if ch == '\n' || ch == '\r' || ch == '\0' || ch == '#' {
            if ch == '#' {
                while self.cur() != '\n' && self.cur() != '\0' {
                    self.advance();
                }
            }
            if self.cur() == '\n' {
                self.advance();
            }
            return Ok(());
        }

        self.at_line_start = false;
        let current = *self.indent_stack.last().unwrap();

        if indent > current {
            self.indent_stack.push(indent);
            self.tokens.push(Token::new(TokKind::Indent, self.line, 1));
        } else if indent < current {
            while self.indent_stack.len() > 1 && *self.indent_stack.last().unwrap() > indent {
                self.indent_stack.pop();
                self.tokens.push(Token::new(TokKind::Dedent, self.line, 1));
            }
            if *self.indent_stack.last().unwrap() != indent {
                return self.err("IndentationError: unindent does not match any outer indentation level");
            }
        }
        Ok(())
    }
