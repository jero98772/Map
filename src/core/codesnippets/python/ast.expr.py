class BinOp(ASTNode):  # ast.BinOp(left, op, right)
    left: ASTNode = None  # op ∈ {+,-,*,/,//,%,**}
    op: str = ""
    right: ASTNode = None


@dataclass
class UnaryOp(ASTNode):  # ast.UnaryOp(op, operand)
    op: str = ""  # op ∈ {+, -, not}
    operand: ASTNode = None


@dataclass
class Compare(ASTNode):  # ast.Compare(left, ops, comparators)
    left: ASTNode = None  # op ∈ {==,!=,<,<=,>,>=}
    op: str = ""
    right: ASTNode = None


@dataclass
class BoolOp(ASTNode):  # ast.BoolOp(op, values)
    op: str = ""  # 'and' | 'or'
    values: List[ASTNode] = field(default_factory=list)


@dataclass
class Call(ASTNode):  # ast.Call(func, args, keywords)
    func: ASTNode = None
    args: List[ASTNode] = field(default_factory=list)
