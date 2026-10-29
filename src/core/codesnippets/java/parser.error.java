        private Token expect(TT tt, String msg) {
            if (!check(tt)) {
                Token got = cur();
                String desc = msg.isEmpty()
                        ? "expected '" + tt.text + "', got '" + got.type().text + "' (" + pyRepr(got.value()) + ")"
                        : msg;
                throw new ParseError("SyntaxError: " + desc, got.line());
            }
            return advance();
        }

        private ParseError err(String msg) { return new ParseError("SyntaxError: " + msg, cur().line()); }
