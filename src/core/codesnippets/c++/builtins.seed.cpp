    Interpreter() {
        globals = std::make_shared<Environment>();
        for (const auto& [name, fn] : BUILTINS) {
            globals->set(name, Value::ofBuiltin(fn, name));
        }
    }
