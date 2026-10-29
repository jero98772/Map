class EduPyError : public std::exception {
public:
    std::string message;
    int line; // 0 means "no line"

    EduPyError(std::string msg, int ln = 0) : message(std::move(msg)), line(ln) {}

    virtual std::string typeName() const { return "EduPyError"; }

    // Colorized (for terminal display)
    std::string colored() const {
        std::string loc = line ? (" [line " + std::to_string(line) + "]") : "";
        return "\033[91m" + typeName() + "\033[0m: " + message + loc;
    }

    // Plain (no ANSI codes)
    std::string plain() const {
        std::string loc = line ? (" [line " + std::to_string(line) + "]") : "";
        return typeName() + ": " + message + loc;
    }

    const char* what() const noexcept override { return message.c_str(); }
};

class LexerError : public EduPyError {
public:
    using EduPyError::EduPyError;
    std::string typeName() const override { return "LexerError"; }
};

class ParseError : public EduPyError {
public:
    using EduPyError::EduPyError;
    std::string typeName() const override { return "ParseError"; }
};

class EduPyRuntimeError : public EduPyError {
public:
    using EduPyError::EduPyError;
    std::string typeName() const override { return "EduPyRuntimeError"; }
};
