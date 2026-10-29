(defmethod eval-node Call [n e]
  (let [callee (eval-node (:func n) e)
        args (mapv #(eval-node % e) (:args n))]
    (cond
      (and (fn? callee) (not (instance? PyFunction callee)))
      (callee args)

      (instance? PyFunction callee)
      (let [fn-node (:node callee)
            arity (count (:params fn-node))]
        (when (not= (count args) arity)
          (throw (runtime-error (str "TypeError: " (:name fn-node) "() takes " arity
                                      " argument(s) but " (count args) " given") (:line n))))
        (let [call-env (new-env (:closure callee))]
          (doseq [[p v] (map vector (:params fn-node) args)]
            (env-set! call-env p v))
          (try
            (exec-stmts (:body fn-node) call-env)
            nil
            (catch clojure.lang.ExceptionInfo ex
              (if (return-signal? ex) (:value (ex-data ex)) (throw ex))))))

      :else
      (throw (runtime-error (str "TypeError: '" (type-name callee) "' object is not callable") (:line n))))))
