@dataclass
class BinOp(ASTNode):
    left: ASTNode = None
    op: str = ""
    right: ASTNode = None


@dataclass
class UnaryOp(ASTNode):
    op: str = ""
    operand: ASTNode = None


@dataclass
class Compare(ASTNode):
    left: ASTNode = None
    op: str = ""
    right: ASTNode = None


@dataclass
class BoolOp(ASTNode):
    op: str = ""
    values: List[ASTNode] = field(default_factory=list)


@dataclass
class Call(ASTNode):
    func: ASTNode = None
    args: List[ASTNode] = field(default_factory=list)
