    fn eval_call(&self, callee: &Value, args: Vec<Value>, line: usize) -> Result<Value, PyError> {
        match callee {
            Value::Builtin(name) => builtins::call(name, &args),
            Value::Function(f) => {
                let arity = f.params.len();
                if args.len() != arity {
                    return Err(PyError::Runtime(
                        format!(
                            "TypeError: {}() takes {} argument(s) but {} given",
                            f.name,
                            arity,
                            args.len()
                        ),
                        Some(line),
                    ));
                }
                let call_env = Env::new(Some(f.closure.clone()));
                for (param, val) in f.params.iter().zip(args.into_iter()) {
                    call_env.set(param, val);
                }
                match self.exec_stmts(&f.body, &call_env) {
                    Ok(()) => Ok(Value::None),
                    Err(Flow::Return(v)) => Ok(v),
                    Err(Flow::Error(e)) => Err(e),
                }
            }
            other => Err(PyError::Runtime(
                format!("TypeError: '{}' object is not callable", type_name(other)),
                Some(line),
            )),
        }
    }
