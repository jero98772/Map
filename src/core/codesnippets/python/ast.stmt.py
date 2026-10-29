class Assign(ASTNode):  # ast.Assign(targets, value)
    target: str = ""
    value: ASTNode = None


@dataclass
class AugAssign(ASTNode):  # ast.AugAssign(target, op, value)
    target: str = ""
    op: str = ""
    value: ASTNode = None


@dataclass
class ExprStmt(ASTNode):  # ast.Expr(value)
    expr: ASTNode = None


@dataclass
class Return(ASTNode):  # ast.Return(value)
    value: Optional[ASTNode] = None


@dataclass
class If(ASTNode):  # ast.If(test, body, orelse)
    test: ASTNode = None
    body: List[ASTNode] = field(default_factory=list)
    orelse: List[ASTNode] = field(default_factory=list)


@dataclass
class While(ASTNode):  # ast.While(test, body, orelse)
    test: ASTNode = None
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class For(ASTNode):  # ast.For(target, iter, body)
    target: str = ""
    iter: ASTNode = None
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class FuncDef(ASTNode):  # ast.FunctionDef(name, args, body)
    name: str = ""
    params: List[str] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)
