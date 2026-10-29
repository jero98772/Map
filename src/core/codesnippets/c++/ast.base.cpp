enum class NodeType {
    Program,
    IntLiteral, FloatLiteral, StringLiteral, BoolLiteral, NoneLiteral,
    Name, ListLiteral, Subscript, BinOp, UnaryOp, Compare, BoolOp, Call,
    Assign, AugAssign, ExprStmt, Return, If, While, For, FuncDef
};

struct ASTNode {
    NodeType type;
    int line = 0;

    // Literal payloads
    long long intVal = 0;
    double floatVal = 0.0;
    std::string strVal;       // StringLiteral value, or BinOp/UnaryOp/Compare/BoolOp op,
                               // or Name id, or Assign/AugAssign/For target,
                               // or FuncDef name
    bool boolVal = false;     // BoolLiteral value

    // Children (meaning depends on `type`)
    std::shared_ptr<ASTNode> a; // left / value / test / func / iter / operand
    std::shared_ptr<ASTNode> b; // right / index

    std::vector<std::shared_ptr<ASTNode>> body;    // Program.body, If.body, While.body,
                                                     // For.body, FuncDef.body
    std::vector<std::shared_ptr<ASTNode>> orelse;   // If.orelse
    std::vector<std::shared_ptr<ASTNode>> elts;     // ListLiteral.elts / Call.args / BoolOp.values
    std::vector<std::string> params;                // FuncDef.params

    explicit ASTNode(NodeType t, int ln = 0) : type(t), line(ln) {}
};
