    fn comparison(&mut self) -> PResult<Expr> {
        let mut node = self.sum()?;
        while self.check(&[
            Tag::EqEqual,
            Tag::NotEqual,
            Tag::Less,
            Tag::LessEqual,
            Tag::Greater,
            Tag::GreaterEqual,
        ]) {
            let op_tok = self.advance();
            let op = op_tok.kind.tag().human().to_string();
            let right = self.sum()?;
            let ln = node.line();
            node = Expr::Compare {
                left: Box::new(node),
                op,
                right: Box::new(right),
                line: ln,
            };
        }
        Ok(node)
    }

    fn sum(&mut self) -> PResult<Expr> {
        let mut node = self.term()?;
        while self.check(&[Tag::Plus, Tag::Minus]) {
            let op = self.advance().kind.tag().human().to_string();
            let right = self.term()?;
            let ln = node.line();
            node = Expr::BinOp {
                left: Box::new(node),
                op,
                right: Box::new(right),
                line: ln,
            };
        }
        Ok(node)
    }
