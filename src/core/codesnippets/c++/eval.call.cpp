            case NodeType::Call: {
                Value callee = eval(node->a, env);
                std::vector<Value> args;
                args.reserve(node->elts.size());
                for (const auto& a : node->elts) args.push_back(eval(a, env));

                if (callee.kind == Value::Kind::BUILTIN) {
                    return callee.builtin(args);
                }

                if (callee.kind == Value::Kind::FUNC) {
                    const auto& fn = callee.func;
                    const ASTPtr& fnNode = fn->node;
                    size_t arity = fnNode->params.size();
                    if (args.size() != arity) {
                        throw EduPyRuntimeError(
                            "TypeError: " + fnNode->strVal + "() takes " + std::to_string(arity) +
                            " argument(s) but " + std::to_string(args.size()) + " given", node->line);
                    }
                    auto callEnv = std::make_shared<Environment>(fn->closure);
                    for (size_t i = 0; i < arity; ++i) {
                        callEnv->set(fnNode->params[i], args[i]);
                    }
                    try {
                        execStmts(fnNode->body, callEnv);
                    } catch (ReturnException& ret) {
                        return ret.value;
                    }
                    return Value::none();
                }

                throw EduPyRuntimeError(
                    "TypeError: '" + typeName(callee) + "' object is not callable", node->line);
            }
