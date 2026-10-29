#[derive(Debug, Clone)]
pub enum Expr {
    Int(i64, usize),
    Float(f64, usize),
    Str(String, usize),
    Bool(bool, usize),
    NoneLit(usize),
    Name(String, usize),
    List(Vec<Expr>, usize),
    Subscript {
        value: Box<Expr>,
        index: Box<Expr>,
        line: usize,
    },
    BinOp {
        left: Box<Expr>,
        op: String,
        right: Box<Expr>,
        line: usize,
    },
    UnaryOp {
        op: String,
        operand: Box<Expr>,
        line: usize,
    },
    Compare {
        left: Box<Expr>,
        op: String,
        right: Box<Expr>,
        line: usize,
    },
    BoolOp {
        op: String,
        values: Vec<Expr>,
        line: usize,
    },
    Call {
        func: Box<Expr>,
        args: Vec<Expr>,
        line: usize,
    },
    MethodCall {
        obj: Box<Expr>,
        method: String,
        args: Vec<Expr>,
        line: usize,
    },
}
