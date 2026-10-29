@dataclass
class ASTNode:
    line: int = 0


@dataclass
class Program(ASTNode):
    body: List[ASTNode] = field(default_factory=list)
