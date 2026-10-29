        private void handleIndentation() {
            int indent = 0;
            while (cur() == ' ' || cur() == '\t') {
                indent = cur() == '\t' ? (indent / 8 + 1) * 8 : indent + 1;
                advance();
            }
            if (pos >= source.length()) return;

            char ch = cur();
            // blank or comment-only line: skip entirely (also handles CRLF)
            if (ch == '\n' || ch == '\r' || ch == '#') {
                if (ch == '#') while (cur() != '\n' && cur() != '\0') advance();
                if (cur() == '\r') advance();
                if (cur() == '\n') advance();
                return;
            }

            atLineStart = false;
            int current = indentStack.get(indentStack.size() - 1);
            if (indent > current) {
                indentStack.add(indent);
                tokens.add(new Token(TT.INDENT, indent, line, 1));
            } else if (indent < current) {
                while (indentStack.size() > 1 && indentStack.get(indentStack.size() - 1) > indent) {
                    indentStack.remove(indentStack.size() - 1);
                    tokens.add(new Token(TT.DEDENT, indent, line, 1));
                }
                if (indentStack.get(indentStack.size() - 1) != indent)
                    throw err("IndentationError: unindent does not match any outer indentation level");
            }
        }
