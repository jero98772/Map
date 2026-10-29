        private Node stmt() {
            skipNewlines();
            if (match(TT.DEF)) return funcDef();
            if (match(TT.IF)) return ifStmt();
            if (match(TT.WHILE)) return whileStmt();
            if (match(TT.FOR)) return forStmt();
            return simpleStmt();
        }

        private Node simpleStmt() {
            Node node;
            if (check(TT.RETURN)) {
                advance();
                node = returnStmt();
            } else if (check(TT.NAME) && peek(1).type() == TT.EQUAL) {
                node = assign();
            } else if (check(TT.NAME) && (peek(1).type() == TT.PLUSEQUAL || peek(1).type() == TT.MINEQUAL
                    || peek(1).type() == TT.STAREQUAL || peek(1).type() == TT.SLASHEQUAL)) {
                node = augAssign();
            } else {
                Node e = expr();
                node = new ExprStmt(e, cur().line());
            }

            if (check(TT.NEWLINE)) advance();
            else if (!check(TT.EOF, TT.DEDENT))
                throw err("expected newline after statement, got " + pyRepr(cur().type().text));
            return node;
        }
