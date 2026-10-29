    const Token& expect(TT tt, const std::string& msg = "") {
        if (!check(tt)) {
            const Token& got = cur();
            std::string desc = msg.empty()
                ? ("expected '" + ttValue(tt) + "', got '" + ttValue(got.type) +
                   "' (" + got.value.repr() + ")")
                : msg;
            throw ParseError("SyntaxError: " + desc, got.line);
        }
        return advance();
    }

    [[noreturn]] void err(const std::string& msg) {
        throw ParseError("SyntaxError: " + msg, cur().line);
    }
