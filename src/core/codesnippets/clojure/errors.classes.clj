(defn- format-error [type-name message line]
  (str type-name ": " message (when line (str " [line " line "]"))))

(defn- format-error-colored [type-name message line]
  (str "\033[91m" type-name "\033[0m: " message (when line (str " [line " line "]"))))

(defn py-error
  "Build an ex-info representing a Py* error (Lexer/Parse/Runtime).
   The exception's message is colorized (red type label), mirroring the
   original PyError.__str__; ex-data carries the plain fields for callers
   that want an uncolored rendering (the original's .plain())."
  [type-name message line]
  (ex-info (format-error-colored type-name message line)
           {:py-error true
            :error-type type-name
            :message message
            :line line
            :plain (format-error type-name message line)}))

(defn lexer-error [message line] (py-error "LexerError" message line))
(defn parse-error [message line] (py-error "ParseError" message line))
(defn runtime-error [message line] (py-error "PyRuntimeError" message line))

(defn py-error? [e]
  (and (instance? clojure.lang.ExceptionInfo e) (:py-error (ex-data e))))
