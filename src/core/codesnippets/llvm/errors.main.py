def main():
    args = sys.argv[1:]
    show_ast = "--ast" in args
    emit_ir = "--emit-ir" in args
    compile_mode = "--compile" in args or "-c" in args
    opt = 0 if "--no-opt" in args else 2

    out_path, files, i = None, [], 0
    while i < len(args):
        a = args[i]
        if a == "-o" and i + 1 < len(args):
            out_path = args[i + 1]
            i += 1
        elif not a.startswith("-"):
            files.append(a)
        i += 1

    if compile_mode and not files:
        print("Usage: python py_llvm.py --compile script.ep [-o output]")
        sys.exit(1)

    if not files:
        repl(Backend(opt=opt, emit_ir=emit_ir))
        return

    path = files[0]
    if not os.path.exists(path):
        print(f"\033[91mFileNotFoundError\033[0m: No such file: {path!r}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as fh:
        source = fh.read()
    try:
        if compile_mode:
            out_path = out_path or os.path.splitext(os.path.basename(path))[0]
            if show_ast:
                _print_ast(Parser(Lexer(source).tokenize()).parse())
            compile_executable(source, out_path, opt=opt, emit_ir=emit_ir)
            print(f"compiled {path} -> {out_path}")
        else:
            run_source(source, Backend(opt=opt, emit_ir=emit_ir), show_ast)
    except (LexerError, ParseError, PyRuntimeError, PyError) as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"\033[91mInternalError\033[0m: {e}")
        sys.exit(1)
