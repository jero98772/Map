class Environment : public std::enable_shared_from_this<Environment> {
public:
    std::unordered_map<std::string, Value> vars;
    std::shared_ptr<Environment> parent;

    explicit Environment(std::shared_ptr<Environment> p = nullptr) : parent(std::move(p)) {}

    Value get(const std::string& name, int line = 0) {
        auto it = vars.find(name);
        if (it != vars.end()) return it->second;
        if (parent) return parent->get(name, line);
        throw EduPyRuntimeError("NameError: name '" + name + "' is not defined", line);
    }

    // Always sets in the *current* scope (like Python assignment)
    void set(const std::string& name, const Value& value) {
        vars[name] = value;
    }

    // Assign to the nearest scope that already owns *name*.
    // Falls back to the current scope (new variable).
    void assign(const std::string& name, const Value& value, int line = 0) {
        if (vars.find(name) != vars.end()) {
            vars[name] = value;
            return;
        }
        if (parent && parent->owns(name)) {
            parent->assign(name, value, line);
            return;
        }
        vars[name] = value;
    }

    bool owns(const std::string& name) const {
        if (vars.find(name) != vars.end()) return true;
        return parent ? parent->owns(name) : false;
    }
};
