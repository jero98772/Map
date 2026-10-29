@dataclass
class Assign(ASTNode):
    target: str = ""
    value: ASTNode = None


@dataclass
class AugAssign(ASTNode):
    target: str = ""
    op: str = ""
    value: ASTNode = None


@dataclass
class ExprStmt(ASTNode):
    expr: ASTNode = None


@dataclass
class Return(ASTNode):
    value: Optional[ASTNode] = None


@dataclass
class If(ASTNode):
    test: ASTNode = None
    body: List[ASTNode] = field(default_factory=list)
    orelse: List[ASTNode] = field(default_factory=list)


@dataclass
class While(ASTNode):
    test: ASTNode = None
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class For(ASTNode):
    target: str = ""
    iter: ASTNode = None
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class FuncDef(ASTNode):
    name: str = ""
    params: List[str] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)
