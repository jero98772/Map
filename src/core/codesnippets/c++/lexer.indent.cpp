    void handleIndentation() {
        int indent = 0;
        while (cur() == ' ' || cur() == '\t') {
            if (cur() == '\t') {
                indent = (indent / 8 + 1) * 8;
            } else {
                indent += 1;
            }
            advance();
        }

        char ch = cur();
        // blank or comment line - skip entirely
        if (ch == '\n' || ch == '\r' || ch == '\0' || ch == '#') {
            if (ch == '#') {
                while (cur() != '\n' && cur() != '\0') advance();
            }
            if (cur() == '\n') advance();
            return;
        }

        at_line_start_ = false;
        int current = indent_stack_.back();

        if (indent > current) {
            indent_stack_.push_back(indent);
            tokens_.push_back({TT::INDENT, TokenValue::ofInt(indent), line_, 1});
        } else if (indent < current) {
            while (indent_stack_.size() > 1 && indent_stack_.back() > indent) {
                indent_stack_.pop_back();
                tokens_.push_back({TT::DEDENT, TokenValue::ofInt(indent), line_, 1});
            }
            if (indent_stack_.back() != indent) {
                err("IndentationError: unindent does not match any outer indentation level");
            }
        }
    }
