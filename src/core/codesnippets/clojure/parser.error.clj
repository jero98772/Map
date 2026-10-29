(defn- p-err! [ps msg]
  (throw (parse-error (str "SyntaxError: " msg) (:line (p-cur ps)))))

(defn- p-expect!
  ([ps tt] (p-expect! ps tt nil))
  ([ps tt msg]
   (if (p-check ps tt)
     (p-advance! ps)
     (let [got (p-cur ps)
           desc (or msg (str "expected '" (tt-str tt) "', got '" (tt-str (:type got))
                              "' (" (pr-str (:value got)) ")"))]
       (throw (parse-error (str "SyntaxError: " desc) (:line got)))))))
