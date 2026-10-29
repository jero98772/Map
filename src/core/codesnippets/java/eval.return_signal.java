    static final class ReturnSignal extends RuntimeException {
        final Object value;

        ReturnSignal(Object value) {
            super(null, null, false, false); // no stack trace: cheap to throw
            this.value = value;
        }
    }
