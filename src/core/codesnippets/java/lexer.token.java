    record Token(TT type, Object value, int line, int col) {
        @Override
        public String toString() {
            return "Token(" + type.name() + ", " + pyRepr(value) + ", " + line + ":" + col + ")";
        }
    }
