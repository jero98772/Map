(defmulti exec-node (fn [node _env] (type node)))
(defmulti eval-node (fn [node _env] (type node)))

(defn exec-stmts [stmts env]
  (doseq [s stmts] (exec-node s env)))
