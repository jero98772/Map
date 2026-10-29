        private void nextToken() {
            if (atLineStart && parenDepth == 0) { handleIndentation(); return; }

            char ch = cur();
            if (ch == ' ' || ch == '\t' || ch == '\r') { advance(); return; }
            if (ch == '\n') {
                int ln = line, cl = col;
                advance();
                if (parenDepth == 0) {
                    tokens.add(new Token(TT.NEWLINE, "\n", ln, cl));
                    atLineStart = true;
                }
                return;
            }
            if (ch == '#') {
                while (cur() != '\n' && cur() != '\0') advance();
                return;
            }
            if (ch == '"' || ch == '\'') { readString(); return; }
            if (Character.isDigit(ch)) { readNumber(); return; }
            if (Character.isLetter(ch) || ch == '_') { readName(); return; }
            readOperator();
        }
