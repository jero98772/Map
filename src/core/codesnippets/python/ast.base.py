@dataclass
class ASTNode:
    line: int = 0

    def __repr__(self):
        parts = [f"{k}={v!r}" for k, v in self.__dict__.items() if k != "line"]
        return f"{type(self).__name__}({', '.join(parts)})"


# ── Root ──────────────────────────────────────────────────────────────────────
@dataclass
class Program(ASTNode):  # CPython: ast.Module
    body: List[ASTNode] = field(default_factory=list)
