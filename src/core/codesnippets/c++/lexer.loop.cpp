    std::vector<Token> tokenize() {
        while (pos_ < source_.size()) {
            nextToken();
        }
        closeAllIndents();
        if (!tokens_.empty() && tokens_.back().type != TT::NEWLINE &&
            tokens_.back().type != TT::DEDENT) {
            tokens_.push_back({TT::NEWLINE, TokenValue::ofStr("\n"), line_, col_});
        }
        tokens_.push_back({TT::EOF_, TokenValue::none(), line_, col_});
        return tokens_;
    }
