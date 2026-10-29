#[derive(Debug, Clone)]
pub enum Stmt {
    FuncDef {
        name: String,
        params: Vec<String>,
        body: Vec<Stmt>,
        line: usize,
    },
    Assign {
        target: String,
        value: Expr,
        line: usize,
    },
    AugAssign {
        target: String,
        op: String,
        value: Expr,
        line: usize,
    },
    ExprStmt {
        expr: Expr,
        #[allow(dead_code)]
        line: usize,
    },
    Return {
        value: Option<Expr>,
        #[allow(dead_code)]
        line: usize,
    },
    If {
        test: Expr,
        body: Vec<Stmt>,
        orelse: Vec<Stmt>,
        #[allow(dead_code)]
        line: usize,
    },
    While {
        test: Expr,
        body: Vec<Stmt>,
        #[allow(dead_code)]
        line: usize,
    },
    For {
        target: String,
        iter: Expr,
        body: Vec<Stmt>,
        line: usize,
    },
}
