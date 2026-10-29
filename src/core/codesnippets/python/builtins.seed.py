    def __init__(self):
        self.globals = Environment()
        for name, fn in BUILTINS.items():
            self.globals.set(name, fn)
