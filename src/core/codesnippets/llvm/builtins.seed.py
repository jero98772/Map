    def _rt_call_builtin(self, name_h, n, args, out, line):
        fn = BUILTINS[HEAP.get(name_h)]
        try:
            put(out, fn([decode(args[i].tag, args[i].pay) for i in range(n)]), line)
        except PyRuntimeError as e:
            if e.line is None:
                e.line = line
            raise
