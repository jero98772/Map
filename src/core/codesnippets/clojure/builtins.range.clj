(defn builtin-range [args]
  (when-not (<= 1 (count args) 3) (throw (runtime-error "TypeError: range() takes 1–3 arguments" nil)))
  (doseq [a args]
    (when-not (numericish? a) (throw (runtime-error "TypeError: range() arguments must be integers" nil))))
  (let [iargs (map #(long (->numval %)) args)]
    (atom (vec (apply range iargs)))))
