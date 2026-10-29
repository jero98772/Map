(defn- handle-indentation! [st]
  (let [indent (atom 0)]
    (while (contains? #{\space \tab} (cur st))
      (reset! indent (if (= (cur st) \tab)
                       (* (+ (quot @indent 8) 1) 8)
                       (inc @indent)))
      (adv! st))
    (let [ch (cur st)]
      (if (or (contains? #{\newline \return \u0000} ch) (= ch \#))
        (do
          (when (= ch \#)
            (while (not (contains? #{\newline \u0000} (cur st))) (adv! st)))
          (when (= (cur st) \newline) (adv! st)))
        (do
          (swap! st assoc :at-line-start false)
          (let [current (peek (:indent-stack @st))]
            (cond
              (> @indent current)
              (do (swap! st update :indent-stack conj @indent)
                  (emit! st :indent @indent (:line @st) 1))

              (< @indent current)
              (do
                (while (and (> (count (:indent-stack @st)) 1)
                            (> (peek (:indent-stack @st)) @indent))
                  (swap! st update :indent-stack pop)
                  (emit! st :dedent @indent (:line @st) 1))
                (when (not= (peek (:indent-stack @st)) @indent)
                  (lex-err! st "IndentationError: unindent does not match any outer indentation level")))

              :else nil)))))))
