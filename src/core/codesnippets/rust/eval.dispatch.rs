    fn exec_stmts(&self, stmts: &[Stmt], env: &Rc<Env>) -> ExecResult {
        for stmt in stmts {
            self.exec(stmt, env)?;
        }
        Ok(())
    }

    fn exec(&self, node: &Stmt, env: &Rc<Env>) -> ExecResult {
        match node {
            Stmt::FuncDef { name, params, body, .. } => {
                let f = PyFunction {
                    name: name.clone(),
                    params: params.clone(),
                    body: body.clone(),
                    closure: env.clone(),
                };
                env.set(name, Value::Function(Rc::new(f)));
                Ok(())
            }
