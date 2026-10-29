int main(int argc, char** argv) {
    std::vector<std::string> args(argv + 1, argv + argc);

    if (args.empty()) {
        repl();
        return 0;
    }

    bool showAst = false;
    std::vector<std::string> files;
    for (const auto& a : args) {
        if (a == "--ast") showAst = true;
        else if (a.rfind("--", 0) != 0) files.push_back(a);
    }

    if (files.empty()) {
        std::cout << "Usage: edupy [script.ep] [--ast]\n";
        return 1;
    }

    const std::string& filepath = files[0];
    std::ifstream fh(filepath);
    if (!fh) {
        std::cout << "\033[91mFileNotFoundError\033[0m: No such file: '" << filepath << "'\n";
        return 1;
    }

    std::ostringstream ss;
    ss << fh.rdbuf();
    std::string source = ss.str();

    try {
        if (showAst) {
            runSourceWithAst(source);
        } else {
            Interpreter interp;
            runSource(source, interp);
        }
    } catch (const EduPyError& e) {
        std::cout << e.colored() << "\n";
        return 1;
    } catch (const ReturnException&) {
        std::cout << "\033[91mEduPyRuntimeError\033[0m: 'return' outside function\n";
        return 1;
    } catch (const std::exception& e) {
        std::cout << "\033[91mInternalError\033[0m: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
