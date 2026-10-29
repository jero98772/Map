        private Node comparison() {
            Node node = sum();
            while (check(TT.EQEQUAL, TT.NOTEQUAL, TT.LESS, TT.LESSEQUAL, TT.GREATER, TT.GREATEREQUAL)) {
                String op = advance().type().text;
                Node right = sum();
                node = new Compare(node, op, right, node.line());
            }
            return node;
        }

        private Node sum() {
            Node node = term();
            while (check(TT.PLUS, TT.MINUS)) {
                String op = advance().type().text;
                Node right = term();
                node = new BinOp(node, op, right, node.line());
            }
            return node;
        }
