    sealed interface Node {
        int line();
    }

    // Root
    record Program(List<Node> body, int line) implements Node {}
