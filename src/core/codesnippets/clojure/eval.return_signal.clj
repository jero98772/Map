(defn return-signal
  "Internal control-flow signal used to unwind the call stack on 'return'."
  [value]
  (ex-info "::return-signal::" {:return-signal true :value value}))

(defn return-signal? [e]
  (and (instance? clojure.lang.ExceptionInfo e) (:return-signal (ex-data e))))
