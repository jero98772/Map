#[derive(Debug, Clone)]
pub enum PyError {
    Lexer(String, Option<usize>),
    Parse(String, Option<usize>),
    Runtime(String, Option<usize>),
}

impl PyError {
    fn label(&self) -> &'static str {
        match self {
            PyError::Lexer(..) => "LexerError",
            PyError::Parse(..) => "ParseError",
            PyError::Runtime(..) => "PyRuntimeError",
        }
    }

    fn message(&self) -> &str {
        match self {
            PyError::Lexer(m, _) | PyError::Parse(m, _) | PyError::Runtime(m, _) => m,
        }
    }

    fn line(&self) -> Option<usize> {
        match self {
            PyError::Lexer(_, l) | PyError::Parse(_, l) | PyError::Runtime(_, l) => *l,
        }
    }

    /// Colorless rendering (used when writing to non-tty sinks, tests, etc).
    #[allow(dead_code)]
    pub fn plain(&self) -> String {
        let loc = match self.line() {
            Some(l) => format!(" [line {}]", l),
            Option::None => String::new(),
        };
        format!("{}: {}{}", self.label(), self.message(), loc)
    }
}
