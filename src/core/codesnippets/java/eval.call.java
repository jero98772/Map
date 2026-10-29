        private Object evalCall(Call n, Environment env) {
            Object callee = eval(n.func(), env);
            List<Object> args = new ArrayList<>();
            for (Node a : n.args()) args.add(eval(a, env));

            if (callee instanceof Builtin b) {
                try {
                    return b.fn().apply(args);
                } catch (PyRuntimeError e) {
                    // attach the call-site line to builtin errors that have none
                    if (e.line == 0) throw new PyRuntimeError(e.msg, n.line());
                    throw e;
                }
            }

            if (callee instanceof PyFunction f) {
                FuncDef fn = f.node;
                if (args.size() != fn.params().size())
                    throw rt("TypeError: " + fn.name() + "() takes " + fn.params().size()
                            + " argument(s) but " + args.size() + " given", n.line());
                Environment callEnv = new Environment(f.closure);
                for (int i = 0; i < args.size(); i++) callEnv.set(fn.params().get(i), args.get(i));
                try {
                    execStmts(fn.body(), callEnv);
                } catch (ReturnSignal ret) {
                    return ret.value;
                }
                return null;
            }

            throw rt("TypeError: '" + typeName(callee) + "' object is not callable", n.line());
        }
