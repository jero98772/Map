    void execStmts(const std::vector<ASTPtr>& stmts, const std::shared_ptr<Environment>& env) {
        for (const auto& stmt : stmts) exec(stmt, env);
    }

    void exec(const ASTPtr& node, const std::shared_ptr<Environment>& env) {
        switch (node->type) {
            case NodeType::FuncDef: {
                auto fn = std::make_shared<EduPyFunction>();
                fn->node = node;
                fn->closure = env;
                env->set(node->strVal, Value::ofFunc(fn));
                return;
            }
