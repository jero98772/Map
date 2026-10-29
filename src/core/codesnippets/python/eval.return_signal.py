class ReturnSignal(Exception):
    """Internal signal used to unwind the call stack on 'return'."""

    def __init__(self, value):
        self.value = value
