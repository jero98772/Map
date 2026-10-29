        List<Token> tokenize() {
            while (pos < source.length()) nextToken();
            closeAllIndents();
            if (!tokens.isEmpty()) {
                TT last = tokens.get(tokens.size() - 1).type();
                if (last != TT.NEWLINE && last != TT.DEDENT)
                    tokens.add(new Token(TT.NEWLINE, "\n", line, col));
            }
            tokens.add(new Token(TT.EOF, null, line, col));
            return tokens;
        }
