def _builtin_print(args):
    print(*(_ep_str(a) for a in args))
    return None
