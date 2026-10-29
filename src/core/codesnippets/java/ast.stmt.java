    // Statements
    record Assign(String target, Node value, int line) implements Node {}
    record AugAssign(String target, String op, Node value, int line) implements Node {}
    record ExprStmt(Node expr, int line) implements Node {}
    record Return(Node value, int line) implements Node {}
    record If(Node test, List<Node> body, List<Node> orelse, int line) implements Node {}
    record While(Node test, List<Node> body, int line) implements Node {}
    record For(String target, Node iter, List<Node> body, int line) implements Node {}
    record FuncDef(String name, List<String> params, List<Node> body, int line) implements Node {}
