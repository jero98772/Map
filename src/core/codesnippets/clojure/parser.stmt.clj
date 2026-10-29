(defn- p-stmt [ps]
  (p-skip-newlines! ps)
  (cond
    (p-match ps :def) (p-func-def ps)
    (p-match ps :if) (p-if-stmt ps)
    (p-match ps :while) (p-while-stmt ps)
    (p-match ps :for) (p-for-stmt ps)
    :else (p-simple-stmt ps)))

(defn- p-simple-stmt [ps]
  (let [node
        (cond
          (p-check ps :return)
          (do (p-advance! ps) (p-return-stmt ps))

          (and (p-check ps :name) (= (:type (p-peek ps 1)) :equal))
          (p-assign ps)

          (and (p-check ps :name)
               (contains? #{:plusequal :minequal :starequal :slashequal} (:type (p-peek ps 1))))
          (p-aug-assign ps)

          :else (->ExprStmt (p-expr ps) (:line (p-cur ps))))]
    (cond
      (p-check ps :newline) (p-advance! ps)
      (p-check ps :eof :dedent) nil
      :else (p-err! ps (str "expected newline after statement, got " (pr-str (tt-str (:type (p-cur ps)))))))
    node))
