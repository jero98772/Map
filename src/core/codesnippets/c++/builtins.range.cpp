static Value builtin_range(const std::vector<Value>& args) {
    if (args.size() < 1 || args.size() > 3)
        throw EduPyRuntimeError("TypeError: range() takes 1-3 arguments");
    std::vector<long long> iargs;
    for (const auto& a : args) {
        if (!a.isIntOrFloat() && a.kind != Value::Kind::BOOL)
            throw EduPyRuntimeError("TypeError: range() arguments must be integers");
        iargs.push_back(a.asLong());
    }
    long long start = 0, stop = 0, step = 1;
    if (iargs.size() == 1) { stop = iargs[0]; }
    else if (iargs.size() == 2) { start = iargs[0]; stop = iargs[1]; }
    else { start = iargs[0]; stop = iargs[1]; step = iargs[2]; }

    if (step == 0) throw EduPyRuntimeError("ValueError: range() arg 3 must not be zero");

    std::vector<Value> out;
    if (step > 0) {
        for (long long v = start; v < stop; v += step) out.push_back(Value::ofInt(v));
    } else {
        for (long long v = start; v > stop; v += step) out.push_back(Value::ofInt(v));
    }
    return Value::ofList(std::move(out));
}
