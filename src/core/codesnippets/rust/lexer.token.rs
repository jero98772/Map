#[derive(Debug, Clone)]
pub struct Token {
    pub kind: TokKind,
    pub line: usize,
    pub col: usize,
}
