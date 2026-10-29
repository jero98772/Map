static Value builtin_print(const std::vector<Value>& args) {
    for (size_t i = 0; i < args.size(); ++i) {
        if (i) std::cout << " ";
        std::cout << epStr(args[i]);
    }
    std::cout << "\n";
    return Value::none();
}
