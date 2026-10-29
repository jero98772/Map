        private void execStmts(List<Node> stmts, Environment env) {
            for (Node s : stmts) exec(s, env);
        }

        private void exec(Node node, Environment env) {
            switch (node) {
                case FuncDef n -> env.set(n.name(), new PyFunction(n, env));
                case Assign n -> env.set(n.target(), eval(n.value(), env));
