                case Return n -> throw new ReturnSignal(n.value() != null ? eval(n.value(), env) : null);
                case If n -> {
                    if (epBool(eval(n.test(), env))) execStmts(n.body(), env);
                    else if (!n.orelse().isEmpty()) execStmts(n.orelse(), env);
                }
                case While n -> {
                    while (epBool(eval(n.test(), env))) execStmts(n.body(), env);
                }
                case For n -> {
                    Object it = eval(n.iter(), env);
                    if (it instanceof String s) {
                        for (String ch : codePoints(s)) {
                            env.set(n.target(), ch);
                            execStmts(n.body(), env);
                        }
                    } else if (it instanceof List<?>) {
                        List<Object> lst = asList(it);
                        for (int i = 0; i < lst.size(); i++) { // live iteration, like Python
                            env.set(n.target(), lst.get(i));
                            execStmts(n.body(), env);
                        }
                    } else {
                        throw rt("TypeError: '" + typeName(it) + "' object is not iterable", n.line());
                    }
                }
