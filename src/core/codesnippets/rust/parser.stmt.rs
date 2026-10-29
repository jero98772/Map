    fn stmt(&mut self) -> PResult<Stmt> {
        self.skip_newlines();
        if self.matches(&[Tag::Def]) {
            return self.func_def();
        }
        if self.matches(&[Tag::If]) {
            return self.if_stmt();
        }
        if self.matches(&[Tag::While]) {
            return self.while_stmt();
        }
        if self.matches(&[Tag::For]) {
            return self.for_stmt();
        }
        self.simple_stmt()
    }

    fn simple_stmt(&mut self) -> PResult<Stmt> {
        let node = if self.check(&[Tag::Return]) {
            self.advance();
            self.return_stmt()?
        } else if self.check(&[Tag::Name]) && self.peek_tag(1) == Tag::Equal {
            self.assign()?
        } else if self.check(&[Tag::Name])
            && matches!(
                self.peek_tag(1),
                Tag::PlusEqual | Tag::MinusEqual | Tag::StarEqual | Tag::SlashEqual
            )
        {
            self.aug_assign()?
        } else {
            let line = self.cur().line;
            Stmt::ExprStmt { expr: self.expr()?, line }
        };

        if self.check(&[Tag::Newline]) {
            self.advance();
        } else if !self.check(&[Tag::Eof, Tag::Dedent]) {
            let got = self.cur().kind.tag().human().to_string();
            return self.err(&format!("expected newline after statement, got '{}'", got));
        }
        Ok(node)
    }
