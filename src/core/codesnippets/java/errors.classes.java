    static class PyError extends RuntimeException {
        final String msg;
        final int line;

        PyError(String message, int line) {
            super(message);
            this.msg = message;
            this.line = line;
        }

        private String loc() {
            return line > 0 ? " [line " + line + "]" : "";
        }

        String plain() {
            return getClass().getSimpleName() + ": " + msg + loc();
        }

        @Override
        public String toString() {
            return "\033[91m" + getClass().getSimpleName() + "\033[0m: " + msg + loc();
        }
    }

    /** Illegal character or unterminated literal. */
    static class LexerError extends PyError {
        LexerError(String m, int line) { super(m, line); }
    }

    /** Token stream violates the grammar. */
    static class ParseError extends PyError {
        ParseError(String m, int line) { super(m, line); }
    }

    /** Type error, undefined name, wrong arity, etc. */
    static class PyRuntimeError extends PyError {
        PyRuntimeError(String m, int line) { super(m, line); }
    }

    static PyRuntimeError rt(String msg) { return new PyRuntimeError(msg, 0); }
    static PyRuntimeError rt(String msg, int line) { return new PyRuntimeError(msg, line); }
