    def emit_return(self, val):
        if self.is_main:
            self.b.ret_void()
        else:
            self._dec_depth(self.b)
            self.b.ret(val)

    def st_Return(self, n):
        if self.is_main:
            raise PyRuntimeError("SyntaxError: 'return' outside function", n.line)
        v = self.ex(n.value) if n.value is not None else NONE_C
        self.emit_return(v)
        self.b.position_at_end(self._new("after_ret"))  # dead code lands here
