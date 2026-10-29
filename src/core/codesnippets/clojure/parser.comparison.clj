(def ^:private compare-ops [:eqequal :notequal :less :lessequal :greater :greaterequal])

(defn- p-comparison [ps]
  (loop [node (p-sum ps)]
    (if (apply p-check ps compare-ops)
      (let [op (p-advance! ps)
            right (p-sum ps)]
        (recur (->Compare node (:value op) right (:line node))))
      node)))

(defn- p-sum [ps]
  (loop [node (p-term ps)]
    (if (p-check ps :plus :minus)
      (let [op (:value (p-advance! ps))
            right (p-term ps)]
        (recur (->BinOp node op right (:line node))))
      node)))
