        Interpreter() {
            for (Map.Entry<String, Builtin> e : BUILTINS.entrySet()) globals.set(e.getKey(), e.getValue());
        }
