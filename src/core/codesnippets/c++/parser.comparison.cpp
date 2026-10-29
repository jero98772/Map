    ASTPtr comparison() {
        auto node = sum();
        while (checkAny({TT::EQEQUAL, TT::NOTEQUAL, TT::LESS, TT::LESSEQUAL,
                          TT::GREATER, TT::GREATEREQUAL})) {
            const Token& op = advance();
            auto right = sum();
            auto cmp = makeNode(NodeType::Compare, node->line);
            cmp->a = node;
            cmp->strVal = op.value.s;
            cmp->b = right;
            node = cmp;
        }
        return node;
    }

    ASTPtr sum() {
        auto node = term();
        while (checkAny({TT::PLUS, TT::MINUS})) {
            std::string op = advance().value.s;
            auto right = term();
            auto bin = makeNode(NodeType::BinOp, node->line);
            bin->a = node;
            bin->strVal = op;
            bin->b = right;
            node = bin;
        }
        return node;
    }
