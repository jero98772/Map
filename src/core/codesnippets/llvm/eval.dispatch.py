    def stmts(self, ss):
        for s in ss:
            getattr(self, "st_" + type(s).__name__)(s)

    def ex(self, n):
        return getattr(self, "ex_" + type(n).__name__)(n)
