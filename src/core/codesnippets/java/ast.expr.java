    // Expressions
    record Name(String id, int line) implements Node {}
    record ListLiteral(List<Node> elts, int line) implements Node {}
    record Subscript(Node value, Node index, int line) implements Node {}
    record BinOp(Node left, String op, Node right, int line) implements Node {}
    record UnaryOp(String op, Node operand, int line) implements Node {}
    record Compare(Node left, String op, Node right, int line) implements Node {}
    record BoolOp(String op, List<Node> values, int line) implements Node {}
    record Call(Node func, List<Node> args, int line) implements Node {}
    record MethodCall(Node obj, String method, List<Node> args, int line) implements Node {}
