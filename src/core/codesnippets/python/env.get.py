class Environment:
    """
    A dictionary-backed variable scope.

    Scopes are linked by *parent* — lookup walks the chain outward
    (like CPython's LEGB rule, minus global/builtin distinctions).
    """

    def __init__(self, parent: "Environment" = None):
        self.vars: dict = {}
        self.parent: Environment = parent

    def get(self, name: str, line: int = None) -> Any:
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name, line)
        raise PyRuntimeError(f"NameError: name '{name}' is not defined", line)

    def set(self, name: str, value: Any):
        """Always sets in the *current* scope (like Python assignment)."""
        self.vars[name] = value

    def assign(self, name: str, value: Any, line: int = None):
        """
        Assign to the nearest scope that already owns *name*.
        Falls back to the current scope (new variable).
        """
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent and self.parent._owns(name):
            self.parent.assign(name, value, line)
            return
        self.vars[name] = value

    def _owns(self, name: str) -> bool:
        if name in self.vars:
            return True
        return self.parent._owns(name) if self.parent else False
