            Stmt::Return { value, .. } => {
                let v = match value {
                    Some(e) => self.eval(e, env)?,
                    Option::None => Value::None,
                };
                Err(Flow::Return(v))
            }
            Stmt::If { test, body, orelse, .. } => {
                if ep_bool(&self.eval(test, env)?) {
                    self.exec_stmts(body, env)
                } else if !orelse.is_empty() {
                    self.exec_stmts(orelse, env)
                } else {
                    Ok(())
                }
            }
            Stmt::While { test, body, .. } => {
                while ep_bool(&self.eval(test, env)?) {
                    self.exec_stmts(body, env)?;
                }
                Ok(())
            }
            Stmt::For { target, iter, body, line } => {
                let iterable = self.eval(iter, env)?;
                match iterable {
                    Value::List(l) => {
                        // Snapshot to allow mutation of the list during iteration,
                        // matching Python's "iterate over a copy of the reference" feel
                        // is not quite right — but avoids holding a live borrow
                        // across arbitrary body execution.
                        let items: Vec<Value> = l.borrow().clone();
                        for item in items {
                            env.set(target, item);
                            self.exec_stmts(body, env)?;
                        }
                        Ok(())
                    }
                    Value::Str(s) => {
                        for ch in s.chars() {
                            env.set(target, Value::Str(ch.to_string()));
                            self.exec_stmts(body, env)?;
                        }
                        Ok(())
                    }
                    other => Err(Flow::Error(PyError::Runtime(
                        format!("TypeError: '{}' object is not iterable", type_name(&other)),
                        Some(*line),
                    ))),
                }
            }
