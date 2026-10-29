class PyError(Exception):
    """Base class for all Py errors."""

    def __init__(self, message: str, line: int = None):
        self.message = message
        self.line = line
        super().__init__(str(self))

    def __str__(self) -> str:
        loc = f" [line {self.line}]" if self.line else ""
        label = f"\033[91m{type(self).__name__}\033[0m"
        return f"{label}: {self.message}{loc}"

    def plain(self) -> str:
        loc = f" [line {self.line}]" if self.line else ""
        return f"{type(self).__name__}: {self.message}{loc}"


class LexerError(PyError):
    """Illegal character or unterminated literal."""


class ParseError(PyError):
    """Token stream violates the grammar."""


class PyRuntimeError(PyError):
    """Type error, undefined name, wrong arity, etc."""
