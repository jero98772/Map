    static final class Environment {
        final Map<String, Object> vars = new HashMap<>(); // containsKey needed: None is null
        final Environment parent;

        Environment(Environment parent) { this.parent = parent; }

        Object get(String name, int line) {
            for (Environment e = this; e != null; e = e.parent)
                if (e.vars.containsKey(name)) return e.vars.get(name);
            throw rt("NameError: name '" + name + "' is not defined", line);
        }

        /** Always sets in the current scope. */
        void set(String name, Object value) { vars.put(name, value); }

        /** Assign to the nearest scope that already owns name; else current scope. */
        void assign(String name, Object value) {
            for (Environment e = this; e != null; e = e.parent) {
                if (e.vars.containsKey(name)) { e.vars.put(name, value); return; }
            }
            vars.put(name, value);
        }
    }
