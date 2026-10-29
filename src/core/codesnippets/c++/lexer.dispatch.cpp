    void nextToken() {
        if (at_line_start_ && paren_depth_ == 0) {
            handleIndentation();
            return;
        }

        char ch = cur();

        if (ch == ' ' || ch == '\t') {
            advance();
            return;
        }
        if (ch == '\n') {
            auto [ln, cl] = here();
            advance();
            if (paren_depth_ == 0) {
                tokens_.push_back({TT::NEWLINE, TokenValue::ofStr("\n"), ln, cl});
                at_line_start_ = true;
            }
            return;
        }
        if (ch == '\r') {
            advance();
            return;
        }
        if (ch == '#') {
            while (cur() != '\n' && cur() != '\0') advance();
            return;
        }
        if (ch == '"' || ch == '\'') {
            readString();
            return;
        }
        if (isdigit((unsigned char)ch)) {
            readNumber();
            return;
        }
        if (isalpha((unsigned char)ch) || ch == '_') {
            readName();
            return;
        }
        readOperator();
    }
