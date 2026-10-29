    pub fn new() -> Self {
        let globals = Env::new(None);
        for name in builtins::NAMES {
            globals.set(name, Value::Builtin(name.to_string()));
        }
        Interpreter { globals }
    }
