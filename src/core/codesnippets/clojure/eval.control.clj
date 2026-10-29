(defmethod exec-node Return [node env]
  (let [value (when (:value node) (eval-node (:value node) env))]
    (throw (return-signal value))))

(defmethod exec-node If [node env]
  (if (ep-bool (eval-node (:test node) env))
    (exec-stmts (:body node) env)
    (when (seq (:orelse node)) (exec-stmts (:orelse node) env))))

(defmethod exec-node While [node env]
  (while (ep-bool (eval-node (:test node) env))
    (exec-stmts (:body node) env)))

(defmethod exec-node For [node env]
  (let [iterable (eval-node (:iter node) env)]
    (cond
      (py-list? iterable)
      (doseq [item @iterable]
        (env-set! env (:target node) item)
        (exec-stmts (:body node) env))

      (string? iterable)
      (doseq [item (map str iterable)]
        (env-set! env (:target node) item)
        (exec-stmts (:body node) env))

      :else
      (throw (runtime-error (str "TypeError: '" (type-name iterable) "' object is not iterable") (:line node))))))
