    ASTPtr stmt() {
        skipNewlines();
        if (match(TT::DEF)) return funcDef();
        if (match(TT::IF)) return ifStmt();
        if (match(TT::WHILE)) return whileStmt();
        if (match(TT::FOR)) return forStmt();
        return simpleStmt();
    }

    ASTPtr simpleStmt() {
        ASTPtr node;
        if (check(TT::RETURN)) {
            advance();
            node = returnStmt();
        } else if (check(TT::NAME) && peek(1).type == TT::EQUAL) {
            node = assignStmt();
        } else if (check(TT::NAME) &&
                   (peek(1).type == TT::PLUSEQUAL || peek(1).type == TT::MINEQUAL ||
                    peek(1).type == TT::STAREQUAL || peek(1).type == TT::SLASHEQUAL)) {
            node = augAssignStmt();
        } else {
            auto e = expr();
            node = makeNode(NodeType::ExprStmt, e->line);
            node->a = e;
        }

        if (check(TT::NEWLINE)) {
            advance();
        } else if (!check(TT::EOF_) && !check(TT::DEDENT)) {
            err("expected newline after statement, got '" + ttValue(cur().type) + "'");
        }
        return node;
    }
