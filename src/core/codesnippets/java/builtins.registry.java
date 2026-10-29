    static final Map<String, Builtin> BUILTINS = new LinkedHashMap<>();

    static void reg(String name, Fn fn) { BUILTINS.put(name, new Builtin(name, fn)); }
