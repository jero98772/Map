struct TokenValue {
    enum class Kind { NONE, INT, FLOAT, STR } kind = Kind::NONE;
    long long i = 0;
    double f = 0.0;
    std::string s;

    TokenValue() = default;
    static TokenValue none() { return TokenValue{}; }
    static TokenValue ofInt(long long v) { TokenValue t; t.kind = Kind::INT; t.i = v; return t; }
    static TokenValue ofFloat(double v) { TokenValue t; t.kind = Kind::FLOAT; t.f = v; return t; }
    static TokenValue ofStr(std::string v) { TokenValue t; t.kind = Kind::STR; t.s = std::move(v); return t; }

    std::string repr() const {
        switch (kind) {
            case Kind::NONE: return "None";
            case Kind::INT: return std::to_string(i);
            case Kind::FLOAT: {
                std::ostringstream oss;
                oss << f;
                return oss.str();
            }
            case Kind::STR: return "'" + s + "'";
        }
        return "";
    }
};

struct Token {
    TT type;
    TokenValue value;
    int line;
    int col;

    std::string repr() const {
        return "Token(" + ttName(type) + ", " + value.repr() + ", " +
               std::to_string(line) + ":" + std::to_string(col) + ")";
    }
};
