    try:
        if show_ast:
            run_source_with_ast(source, filename=filepath)
        else:
            run_source(source, filename=filepath)
    except (LexerError, ParseError, PyRuntimeError) as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"\033[91mInternalError\033[0m: {e}")
        sys.exit(1)
