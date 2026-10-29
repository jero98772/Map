    fn expect(&mut self, tag: Tag, msg: Option<&str>) -> PResult<Token> {
        if !self.check(&[tag]) {
            let got = self.cur();
            let desc = match msg {
                Some(m) => m.to_string(),
                Option::None => format!(
                    "expected '{}', got '{}' ({})",
                    tag.human(),
                    got.kind.tag().human(),
                    got.kind.describe_quoted()
                ),
            };
            return Err(PyError::Parse(format!("SyntaxError: {}", desc), Some(got.line)));
        }
        Ok(self.advance())
    }

    fn err<T>(&self, msg: &str) -> PResult<T> {
        Err(PyError::Parse(format!("SyntaxError: {}", msg), Some(self.cur().line)))
    }
