            case NodeType::Return: {
                Value value = node->a ? eval(node->a, env) : Value::none();
                throw ReturnException{value};
            }
            case NodeType::If: {
                if (epBool(eval(node->a, env))) {
                    execStmts(node->body, env);
                } else if (!node->orelse.empty()) {
                    execStmts(node->orelse, env);
                }
                return;
            }
            case NodeType::While: {
                while (epBool(eval(node->a, env))) {
                    execStmts(node->body, env);
                }
                return;
            }
            case NodeType::For: {
                Value iterable = eval(node->a, env);
                if (iterable.kind == Value::Kind::LIST) {
                    // Copy to avoid iterator invalidation if the list is
                    // mutated during the loop (matches Python's behavior of
                    // iterating a snapshot when append happens via builtin,
                    // though Python itself iterates live; we choose snapshot
                    // for safety/parity with simple scripts).
                    auto items = *iterable.list;
                    for (const auto& item : items) {
                        env->set(node->strVal, item);
                        execStmts(node->body, env);
                    }
                } else if (iterable.kind == Value::Kind::STR) {
                    for (char c : iterable.s) {
                        env->set(node->strVal, Value::ofStr(std::string(1, c)));
                        execStmts(node->body, env);
                    }
                } else {
                    throw EduPyRuntimeError(
                        "TypeError: '" + typeName(iterable) + "' object is not iterable", node->line);
                }
                return;
            }
