def _builtin_range(args):
    if not (1 <= len(args) <= 3):
        raise PyRuntimeError("TypeError: range() takes 1–3 arguments")
    iargs = []
    for a in args:
        if not isinstance(a, (int, float)):
            raise PyRuntimeError("TypeError: range() arguments must be integers")
        iargs.append(int(a))
    return list(range(*iargs))
